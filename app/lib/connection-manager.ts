// APOLLO-GUIDED Connection Manager for Enhanced Information Access
import React from 'react';
interface ConnectionConfig {
  maxReconnectAttempts: number;
  reconnectDelay: number;
  heartbeatInterval: number;
  timeoutDuration: number;
  enableOfflineMode: boolean;
  enableDataSync: boolean;
}

interface ConnectionStatus {
  isConnected: boolean;
  isOnline: boolean;
  lastConnected: number;
  reconnectAttempts: number;
  connectionQuality: 'excellent' | 'good' | 'poor' | 'offline';
  latency: number;
  dataSyncStatus: 'synced' | 'syncing' | 'pending' | 'error';
}

class ApolloConnectionManager {
  private config: ConnectionConfig;
  private status: ConnectionStatus;
  private ws: WebSocket | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private listeners: Map<string, Function[]> = new Map();
  private messageQueue: any[] = [];
  private isDestroyed: boolean = false;

  constructor(config: Partial<ConnectionConfig> = {}) {
    this.config = {
      maxReconnectAttempts: 5,
      reconnectDelay: 1000,
      heartbeatInterval: 30000,
      timeoutDuration: 10000,
      enableOfflineMode: true,
      enableDataSync: true,
      ...config
    };

    this.status = {
      isConnected: false,
      isOnline: navigator.onLine,
      lastConnected: 0,
      reconnectAttempts: 0,
      connectionQuality: 'offline',
      latency: 0,
      dataSyncStatus: 'pending'
    };

    this.setupEventListeners();
    this.initializeConnection();
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return;
    
    // Online/offline detection
    window.addEventListener('online', () => {
      this.status.isOnline = true;
      this.emit('online');
      this.initializeConnection();
    });

    window.addEventListener('offline', () => {
      this.status.isOnline = false;
      this.status.connectionQuality = 'offline';
      this.emit('offline');
      this.disconnect();
    });

    // Page visibility change
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.status.isOnline) {
        this.initializeConnection();
      }
    });

    // Before unload
    window.addEventListener('beforeunload', () => {
      this.disconnect();
    });
  }

  private async initializeConnection(): Promise<void> {
    if (this.isDestroyed || !this.status.isOnline) return;

    try {
      await this.connect();
      this.status.reconnectAttempts = 0;
      this.status.lastConnected = Date.now();
      this.emit('connected');
    } catch (error) {
      console.error('APOLLO Connection Error:', error);
      this.handleConnectionError();
    }
  }

  private async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = this.getWebSocketUrl();
      this.ws = new WebSocket(wsUrl);

      const timeout = setTimeout(() => {
        reject(new Error('Connection timeout'));
      }, this.config.timeoutDuration);

      this.ws.onopen = () => {
        clearTimeout(timeout);
        this.status.isConnected = true;
        this.status.connectionQuality = 'excellent';
        this.startHeartbeat();
        this.processMessageQueue();
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event);
      };

      this.ws.onclose = (event) => {
        clearTimeout(timeout);
        this.status.isConnected = false;
        this.stopHeartbeat();
        
        if (!event.wasClean && this.status.isOnline) {
          this.scheduleReconnect();
        }
        
        this.emit('disconnected', event);
      };

      this.ws.onerror = (error) => {
        clearTimeout(timeout);
        reject(error);
      };
    });
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/api/ws`;
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      
      // Update connection quality based on message timing
      this.updateConnectionQuality();
      
      // Handle different message types
      switch (data.type) {
        case 'heartbeat':
          this.handleHeartbeat(data);
          break;
        case 'data_sync':
          this.handleDataSync(data);
          break;
        case 'real_time_update':
          this.handleRealTimeUpdate(data);
          break;
        case 'notification':
          this.handleNotification(data);
          break;
        default:
          this.emit('message', data);
      }
    } catch (error) {
      console.error('Message parsing error:', error);
    }
  }

  private handleHeartbeat(data: any): void {
    this.status.latency = Date.now() - data.timestamp;
    this.emit('heartbeat', data);
  }

  private handleDataSync(data: any): void {
    this.status.dataSyncStatus = data.status;
    this.emit('dataSync', data);
  }

  private handleRealTimeUpdate(data: any): void {
    this.emit('realTimeUpdate', data);
  }

  private handleNotification(data: any): void {
    this.emit('notification', data);
  }

  private updateConnectionQuality(): void {
    if (this.status.latency < 100) {
      this.status.connectionQuality = 'excellent';
    } else if (this.status.latency < 300) {
      this.status.connectionQuality = 'good';
    } else {
      this.status.connectionQuality = 'poor';
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send({
        type: 'heartbeat',
        timestamp: Date.now()
      });
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.status.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.status.reconnectAttempts++;
    const delay = this.config.reconnectDelay * Math.pow(2, this.status.reconnectAttempts - 1);
    
    this.reconnectTimer = setTimeout(() => {
      this.initializeConnection();
    }, delay);

    this.emit('reconnecting', { attempts: this.status.reconnectAttempts, delay });
  }

  private handleConnectionError(): void {
    this.status.isConnected = false;
    this.status.connectionQuality = 'offline';
    this.emit('error');
    
    if (this.status.isOnline) {
      this.scheduleReconnect();
    }
  }

  // Send message through WebSocket
  send(data: any): void {
    if (this.status.isConnected && this.ws) {
      this.ws.send(JSON.stringify(data));
    } else {
      // Queue message for later
      this.messageQueue.push(data);
    }
  }

  // Process queued messages
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.status.isConnected) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  // Subscribe to events
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  // Unsubscribe from events
  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  // Emit events
  private emit(event: string, data?: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // Get connection status
  getStatus(): ConnectionStatus {
    return { ...this.status };
  }

  // Force reconnection
  async reconnect(): Promise<void> {
    this.disconnect();
    await this.initializeConnection();
  }

  // Disconnect
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.stopHeartbeat();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    this.status.isConnected = false;
    this.status.connectionQuality = 'offline';
  }

  // Destroy connection manager
  destroy(): void {
    this.isDestroyed = true;
    this.disconnect();
    this.listeners.clear();
    this.messageQueue = [];
  }

  // Subscribe to real-time data updates
  subscribeToData(type: string, callback: Function): void {
    this.send({
      type: 'subscribe',
      dataType: type
    });
    
    this.on(`data_${type}`, callback);
  }

  // Unsubscribe from real-time data updates
  unsubscribeFromData(type: string, callback: Function): void {
    this.send({
      type: 'unsubscribe',
      dataType: type
    });
    
    this.off(`data_${type}`, callback);
  }

  // Request data sync
  requestDataSync(dataType?: string): void {
    this.send({
      type: 'request_sync',
      dataType
    });
  }

  // Send real-time update
  sendRealTimeUpdate(type: string, data: any): void {
    this.send({
      type: 'real_time_update',
      updateType: type,
      data,
      timestamp: Date.now()
    });
  }
}

// Singleton instance
export const apolloConnection = new ApolloConnectionManager();

// React hook for connection status
export function useConnection() {
  const [status, setStatus] = React.useState(apolloConnection.getStatus());

  React.useEffect(() => {
    const updateStatus = () => setStatus(apolloConnection.getStatus());
    
    apolloConnection.on('connected', updateStatus);
    apolloConnection.on('disconnected', updateStatus);
    apolloConnection.on('reconnecting', updateStatus);
    apolloConnection.on('error', updateStatus);
    
    return () => {
      apolloConnection.off('connected', updateStatus);
      apolloConnection.off('disconnected', updateStatus);
      apolloConnection.off('reconnecting', updateStatus);
      apolloConnection.off('error', updateStatus);
    };
  }, []);

  return {
    ...status,
    reconnect: () => apolloConnection.reconnect(),
    send: (data: any) => apolloConnection.send(data),
    subscribe: (type: string, callback: Function) => apolloConnection.subscribeToData(type, callback),
    unsubscribe: (type: string, callback: Function) => apolloConnection.unsubscribeFromData(type, callback)
  };
}
