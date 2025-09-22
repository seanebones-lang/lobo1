// APOLLO-GUIDED Offline Support System
import React from 'react';
interface OfflineConfig {
  enableOfflineMode: boolean;
  maxOfflineDataSize: number; // in MB
  syncOnReconnect: boolean;
  cacheStrategy: 'aggressive' | 'conservative' | 'balanced';
  offlineTimeout: number; // in minutes
}

interface OfflineData {
  key: string;
  data: any;
  timestamp: number;
  ttl: number;
  priority: 'high' | 'medium' | 'low';
  syncRequired: boolean;
}

class ApolloOfflineManager {
  private config: OfflineConfig;
  private offlineData: Map<string, OfflineData> = new Map();
  private isOffline: boolean = false;
  private offlineStartTime: number = 0;
  private listeners: Map<string, Function[]> = new Map();

  constructor(config: Partial<OfflineConfig> = {}) {
    this.config = {
      enableOfflineMode: true,
      maxOfflineDataSize: 50, // 50MB
      syncOnReconnect: true,
      cacheStrategy: 'balanced',
      offlineTimeout: 60, // 60 minutes
      ...config
    };

    this.setupEventListeners();
    this.loadOfflineData();
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return;
    
    // Online/offline detection
    window.addEventListener('online', () => {
      this.handleOnline();
    });

    window.addEventListener('offline', () => {
      this.handleOffline();
    });

    // Page visibility change
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && navigator.onLine) {
        this.handleOnline();
      }
    });

    // Before unload - save offline data
    window.addEventListener('beforeunload', () => {
      this.saveOfflineData();
    });

    // Periodic cleanup
    setInterval(() => {
      this.cleanupExpiredData();
    }, 5 * 60 * 1000); // Every 5 minutes
  }

  private handleOffline(): void {
    this.isOffline = true;
    this.offlineStartTime = Date.now();
    this.emit('offline');
    console.log('🌊 APOLLO Offline: Entering offline mode');
  }

  private handleOnline(): void {
    const wasOffline = this.isOffline;
    this.isOffline = false;
    
    if (wasOffline) {
      const offlineDuration = Date.now() - this.offlineStartTime;
      console.log(`🌊 APOLLO Offline: Back online after ${Math.round(offlineDuration / 1000)}s`);
      
      this.emit('online', { duration: offlineDuration });
      
      if (this.config.syncOnReconnect) {
        this.syncOfflineData();
      }
    }
  }

  // Store data for offline access
  storeOfflineData(
    key: string,
    data: any,
    options: {
      ttl?: number;
      priority?: 'high' | 'medium' | 'low';
      syncRequired?: boolean;
    } = {}
  ): void {
    if (!this.config.enableOfflineMode) return;

    const offlineItem: OfflineData = {
      key,
      data,
      timestamp: Date.now(),
      ttl: options.ttl || 24 * 60 * 60 * 1000, // 24 hours default
      priority: options.priority || 'medium',
      syncRequired: options.syncRequired || false
    };

    this.offlineData.set(key, offlineItem);
    this.emit('dataStored', { key, data: offlineItem });

    // Check storage limits
    this.enforceStorageLimits();
  }

  // Get data from offline storage
  getOfflineData(key: string): any | null {
    const item = this.offlineData.get(key);
    
    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.offlineData.delete(key);
      return null;
    }

    return item.data;
  }

  // Check if data exists in offline storage
  hasOfflineData(key: string): boolean {
    const item = this.offlineData.get(key);
    return item ? Date.now() - item.timestamp <= item.ttl : false;
  }

  // Get all offline data by priority
  getOfflineDataByPriority(priority: 'high' | 'medium' | 'low'): OfflineData[] {
    return Array.from(this.offlineData.values())
      .filter(item => item.priority === priority && !this.isExpired(item));
  }

  // Get data that needs syncing
  getSyncRequiredData(): OfflineData[] {
    return Array.from(this.offlineData.values())
      .filter(item => item.syncRequired && !this.isExpired(item));
  }

  // Sync offline data when back online
  private async syncOfflineData(): Promise<void> {
    const syncData = this.getSyncRequiredData();
    
    if (syncData.length === 0) {
      console.log('🌊 APOLLO Offline: No data to sync');
      return;
    }

    console.log(`🌊 APOLLO Offline: Syncing ${syncData.length} items`);

    try {
      // Convert to sync items format
      const syncItems = syncData.map(item => ({
        id: item.key,
        type: this.extractTypeFromKey(item.key),
        data: item.data,
        timestamp: item.timestamp,
        version: 1,
        deviceId: this.getDeviceId(),
        userId: this.getUserId(),
        status: 'pending' as const
      }));

      // Send to sync API
      const response = await fetch('/api/sync/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          items: syncItems,
          deviceId: this.getDeviceId(),
          userId: this.getUserId()
        })
      });

      if (response.ok) {
        const result = await response.json();
        this.handleSyncResult(result);
      } else {
        throw new Error(`Sync failed: ${response.status}`);
      }

    } catch (error) {
      console.error('🌊 APOLLO Offline: Sync failed:', error);
      this.emit('syncError', error);
    }
  }

  // Handle sync result
  private handleSyncResult(result: any): void {
    const { synced, conflicts, errors } = result;

    // Mark synced items as no longer requiring sync
    synced.forEach((itemId: string) => {
      const item = this.offlineData.get(itemId);
      if (item) {
        item.syncRequired = false;
      }
    });

    // Handle conflicts
    if (conflicts.length > 0) {
      this.emit('syncConflicts', conflicts);
    }

    // Handle errors
    if (errors.length > 0) {
      this.emit('syncErrors', errors);
    }

    this.emit('syncComplete', { synced: synced.length, conflicts: conflicts.length, errors: errors.length });
  }

  // Extract type from key
  private extractTypeFromKey(key: string): string {
    const parts = key.split('_');
    return parts[0] || 'unknown';
  }

  // Get device ID
  private getDeviceId(): string {
    return localStorage.getItem('apollo_device_id') || 'unknown';
  }

  // Get user ID
  private getUserId(): string {
    return localStorage.getItem('apollo_user_id') || 'unknown';
  }

  // Get auth token
  private getAuthToken(): string {
    return localStorage.getItem('apollo_auth_token') || '';
  }

  // Enforce storage limits
  private enforceStorageLimits(): void {
    const currentSize = this.calculateStorageSize();
    const maxSizeBytes = this.config.maxOfflineDataSize * 1024 * 1024;

    if (currentSize > maxSizeBytes) {
      this.cleanupOldData();
    }
  }

  // Calculate current storage size
  private calculateStorageSize(): number {
    let size = 0;
    this.offlineData.forEach(item => {
      size += JSON.stringify(item).length * 2; // Rough estimate
    });
    return size;
  }

  // Clean up old data
  private cleanupOldData(): void {
    const items = Array.from(this.offlineData.entries())
      .map(([key, item]) => ({ key, item }))
      .sort((a, b) => {
        // Sort by priority (high first) then by timestamp (oldest first)
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        const priorityDiff = priorityOrder[a.item.priority] - priorityOrder[b.item.priority];
        if (priorityDiff !== 0) return priorityDiff;
        return a.item.timestamp - b.item.timestamp;
      });

    // Remove low priority items first
    const itemsToRemove = Math.floor(items.length * 0.3); // Remove 30%
    for (let i = 0; i < itemsToRemove; i++) {
      this.offlineData.delete(items[i].key);
    }

    console.log(`🌊 APOLLO Offline: Cleaned up ${itemsToRemove} items`);
  }

  // Clean up expired data
  private cleanupExpiredData(): void {
    const now = Date.now();
    let cleaned = 0;

    this.offlineData.forEach((item, key) => {
      if (this.isExpired(item)) {
        this.offlineData.delete(key);
        cleaned++;
      }
    });

    if (cleaned > 0) {
      console.log(`🌊 APOLLO Offline: Cleaned up ${cleaned} expired items`);
    }
  }

  // Check if item is expired
  private isExpired(item: OfflineData): boolean {
    return Date.now() - item.timestamp > item.ttl;
  }

  // Save offline data to localStorage
  private saveOfflineData(): void {
    try {
      const data = Array.from(this.offlineData.entries());
      localStorage.setItem('apollo_offline_data', JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save offline data:', error);
    }
  }

  // Load offline data from localStorage
  private loadOfflineData(): void {
    if (typeof window === 'undefined') return;
    
    try {
      const saved = localStorage.getItem('apollo_offline_data');
      if (saved) {
        const data = JSON.parse(saved);
        this.offlineData = new Map(data);
        console.log(`🌊 APOLLO Offline: Loaded ${this.offlineData.size} offline items`);
      }
    } catch (error) {
      console.error('Failed to load offline data:', error);
    }
  }

  // Event system
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // Get offline status
  getOfflineStatus(): {
    isOffline: boolean;
    offlineDuration: number;
    dataCount: number;
    syncRequiredCount: number;
    storageSize: number;
  } {
    return {
      isOffline: this.isOffline,
      offlineDuration: this.isOffline ? Date.now() - this.offlineStartTime : 0,
      dataCount: this.offlineData.size,
      syncRequiredCount: this.getSyncRequiredData().length,
      storageSize: this.calculateStorageSize()
    };
  }

  // Clear all offline data
  clearOfflineData(): void {
    this.offlineData.clear();
    localStorage.removeItem('apollo_offline_data');
    this.emit('dataCleared');
  }

  // Force sync
  async forceSync(): Promise<void> {
    await this.syncOfflineData();
  }
}

// Singleton instance
export const apolloOffline = new ApolloOfflineManager();

// React hook for offline status
export function useOfflineStatus() {
  const [status, setStatus] = React.useState(apolloOffline.getOfflineStatus());

  React.useEffect(() => {
    const updateStatus = () => setStatus(apolloOffline.getOfflineStatus());
    
    apolloOffline.on('offline', updateStatus);
    apolloOffline.on('online', updateStatus);
    apolloOffline.on('dataStored', updateStatus);
    apolloOffline.on('syncComplete', updateStatus);
    
    return () => {
      apolloOffline.off('offline', updateStatus);
      apolloOffline.off('online', updateStatus);
      apolloOffline.off('dataStored', updateStatus);
      apolloOffline.off('syncComplete', updateStatus);
    };
  }, []);

  return {
    ...status,
    storeData: (key: string, data: any, options?: any) => apolloOffline.storeOfflineData(key, data, options),
    getData: (key: string) => apolloOffline.getOfflineData(key),
    hasData: (key: string) => apolloOffline.hasOfflineData(key),
    forceSync: () => apolloOffline.forceSync(),
    clearData: () => apolloOffline.clearOfflineData()
  };
}
