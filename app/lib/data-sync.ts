// APOLLO-GUIDED Data Synchronization System
import React from 'react';
interface SyncItem {
  id: string;
  type: 'appointment' | 'customer' | 'artist' | 'message' | 'analytics';
  data: any;
  timestamp: number;
  version: number;
  deviceId: string;
  userId: string;
  status: 'pending' | 'synced' | 'conflict' | 'error';
}

interface SyncConfig {
  maxRetries: number;
  retryDelay: number;
  batchSize: number;
  conflictResolution: 'server' | 'client' | 'manual';
  offlineMode: boolean;
}

class ApolloDataSync {
  private syncQueue: SyncItem[] = [];
  private config: SyncConfig;
  private isOnline: boolean = navigator.onLine;
  private syncInProgress: boolean = false;
  private deviceId: string;
  private userId: string | null = null;

  constructor(config: Partial<SyncConfig> = {}) {
    this.config = {
      maxRetries: 3,
      retryDelay: 1000,
      batchSize: 50,
      conflictResolution: 'server',
      offlineMode: false,
      ...config
    };

    this.deviceId = this.generateDeviceId();
    this.setupEventListeners();
    this.startPeriodicSync();
  }

  private generateDeviceId(): string {
    if (typeof window === 'undefined') {
      return `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    try {
      let deviceId = localStorage.getItem('apollo_device_id');
      if (!deviceId) {
        deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('apollo_device_id', deviceId);
      }
      return deviceId;
    } catch (error) {
      // Fallback if localStorage is not available
      return `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return;
    
    // Online/offline detection
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.processSyncQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });

    // Visibility change (tab focus)
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.isOnline) {
        this.processSyncQueue();
      }
    });

    // Before unload (save pending changes)
    window.addEventListener('beforeunload', () => {
      this.savePendingChanges();
    });
  }

  // Add item to sync queue
  async syncItem(
    type: SyncItem['type'],
    data: any,
    userId: string,
    options: { immediate?: boolean; retry?: boolean } = {}
  ): Promise<SyncItem> {
    const syncItem: SyncItem = {
      id: `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      data,
      timestamp: Date.now(),
      version: 1,
      deviceId: this.deviceId,
      userId,
      status: 'pending'
    };

    this.syncQueue.push(syncItem);
    this.userId = userId;

    // Save to localStorage for offline access
    this.saveToLocalStorage(syncItem);

    if (options.immediate || this.isOnline) {
      await this.processSyncQueue();
    }

    return syncItem;
  }

  // Process sync queue
  private async processSyncQueue(): Promise<void> {
    if (this.syncInProgress || !this.isOnline || this.syncQueue.length === 0) {
      return;
    }

    this.syncInProgress = true;

    try {
      const pendingItems = this.syncQueue.filter(item => item.status === 'pending');
      const batches = this.chunkArray(pendingItems, this.config.batchSize);

      for (const batch of batches) {
        await this.syncBatch(batch);
      }

      // Clean up synced items
      this.syncQueue = this.syncQueue.filter(item => item.status !== 'synced');
      this.saveSyncQueue();

    } catch (error) {
      console.error('APOLLO Sync Error:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  // Sync a batch of items
  private async syncBatch(items: SyncItem[]): Promise<void> {
    try {
      const response = await fetch('/api/sync/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          items,
          deviceId: this.deviceId,
          userId: this.userId
        })
      });

      if (!response.ok) {
        throw new Error(`Sync failed: ${response.status}`);
      }

      const result = await response.json();
      this.handleSyncResponse(result);

    } catch (error) {
      console.error('Batch sync failed:', error);
      this.handleSyncError(items, error);
    }
  }

  // Handle sync response
  private handleSyncResponse(result: any): void {
    if (result.conflicts && result.conflicts.length > 0) {
      this.handleConflicts(result.conflicts);
    }

    if (result.synced && result.synced.length > 0) {
      result.synced.forEach((itemId: string) => {
        const item = this.syncQueue.find(i => i.id === itemId);
        if (item) {
          item.status = 'synced';
        }
      });
    }
  }

  // Handle sync conflicts
  private handleConflicts(conflicts: any[]): void {
    conflicts.forEach(conflict => {
      const item = this.syncQueue.find(i => i.id === conflict.itemId);
      if (item) {
        item.status = 'conflict';
        
        // Apply conflict resolution strategy
        if (this.config.conflictResolution === 'server') {
          item.data = conflict.serverData;
          item.status = 'synced';
        } else if (this.config.conflictResolution === 'client') {
          // Keep client data, increment version
          item.version++;
          item.status = 'pending';
        } else {
          // Manual resolution - notify user
          this.notifyConflict(conflict);
        }
      }
    });
  }

  // Handle sync errors
  private handleSyncError(items: SyncItem[], error: any): void {
    items.forEach(item => {
      item.status = 'error';
      // Implement retry logic
      this.scheduleRetry(item);
    });
  }

  // Schedule retry for failed items
  private scheduleRetry(item: SyncItem): void {
    setTimeout(() => {
      if (item.status === 'error') {
        item.status = 'pending';
        this.processSyncQueue();
      }
    }, this.config.retryDelay);
  }

  // Get data from local storage
  getLocalData(type: SyncItem['type'], userId: string): any[] {
    const key = `apollo_sync_${type}_${userId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  }

  // Save data to local storage
  private saveToLocalStorage(item: SyncItem): void {
    const key = `apollo_sync_${item.type}_${item.userId}`;
    const existing = this.getLocalData(item.type, item.userId);
    existing.push(item);
    localStorage.setItem(key, JSON.stringify(existing));
  }

  // Save sync queue
  private saveSyncQueue(): void {
    localStorage.setItem('apollo_sync_queue', JSON.stringify(this.syncQueue));
  }

  // Load sync queue
  private loadSyncQueue(): void {
    const saved = localStorage.getItem('apollo_sync_queue');
    if (saved) {
      this.syncQueue = JSON.parse(saved);
    }
  }

  // Save pending changes before unload
  private savePendingChanges(): void {
    this.saveSyncQueue();
  }

  // Start periodic sync
  private startPeriodicSync(): void {
    setInterval(() => {
      if (this.isOnline && this.syncQueue.length > 0) {
        this.processSyncQueue();
      }
    }, 30000); // Every 30 seconds
  }

  // Notify conflict to user
  private notifyConflict(conflict: any): void {
    // Implement user notification system
    console.warn('Sync conflict detected:', conflict);
    // Could emit custom event or show UI notification
  }

  // Get auth token
  private getAuthToken(): string {
    return localStorage.getItem('apollo_auth_token') || '';
  }

  // Utility: chunk array
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  // Get sync status
  getSyncStatus(): {
    isOnline: boolean;
    queueLength: number;
    pendingItems: number;
    errorItems: number;
    conflictItems: number;
  } {
    return {
      isOnline: this.isOnline,
      queueLength: this.syncQueue.length,
      pendingItems: this.syncQueue.filter(i => i.status === 'pending').length,
      errorItems: this.syncQueue.filter(i => i.status === 'error').length,
      conflictItems: this.syncQueue.filter(i => i.status === 'conflict').length
    };
  }

  // Force sync
  async forceSync(): Promise<void> {
    await this.processSyncQueue();
  }

  // Clear sync queue
  clearSyncQueue(): void {
    this.syncQueue = [];
    this.saveSyncQueue();
  }
}

// Singleton instance
export const apolloDataSync = new ApolloDataSync();

// Real-time sync hook for React components
export function useDataSync() {
  const [syncStatus, setSyncStatus] = React.useState(apolloDataSync.getSyncStatus());

  React.useEffect(() => {
    const interval = setInterval(() => {
      setSyncStatus(apolloDataSync.getSyncStatus());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    ...syncStatus,
    forceSync: () => apolloDataSync.forceSync(),
    clearQueue: () => apolloDataSync.clearSyncQueue()
  };
}
