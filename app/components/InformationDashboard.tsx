'use client'

import React, { useState, useEffect } from 'react';
import { 
  Wifi, 
  WifiOff, 
  Database, 
  RotateCcw, 
  AlertCircle, 
  CheckCircle, 
  Clock,
  HardDrive,
  Activity,
  RefreshCw
} from 'lucide-react';

interface InformationDashboardProps {
  className?: string;
}

export default function InformationDashboard({ className = '' }: InformationDashboardProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [connectionStatus, setConnectionStatus] = useState({
    isConnected: navigator.onLine,
    latency: 0,
    quality: 'good'
  });
  const [syncStatus, setSyncStatus] = useState({
    pendingItems: 0,
    errorItems: 0,
    conflictItems: 0
  });
  const [offlineStatus, setOfflineStatus] = useState({
    isOffline: !navigator.onLine,
    dataCount: 0,
    storageSize: 0
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 1000));
      setConnectionStatus({
        isConnected: navigator.onLine,
        latency: Math.floor(Math.random() * 100) + 50,
        quality: 'good'
      });
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getConnectionStatusColor = () => {
    if (!connectionStatus.isConnected) return 'text-red-500';
    if (connectionStatus.quality === 'excellent') return 'text-green-500';
    if (connectionStatus.quality === 'good') return 'text-yellow-500';
    return 'text-orange-500';
  };

  const getSyncStatusColor = () => {
    if (syncStatus.errorItems > 0) return 'text-red-500';
    if (syncStatus.pendingItems > 0) return 'text-yellow-500';
    return 'text-green-500';
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  return (
    <div className={`information-dashboard ${className}`}>
      <div className="dashboard-header">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-apollo-500" />
            Information Access & Connectivity
          </h2>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={`refresh-button ${isRefreshing ? 'spinning' : ''}`}
          >
            <RefreshCw />
            Refresh
          </button>
        </div>
        <p className="text-gray-400 text-sm mt-1">
          Last updated: {lastUpdate.toLocaleTimeString()}
        </p>
      </div>

      <div className="dashboard-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
        
        {/* Connection Status */}
        <div className="dashboard-card">
          <div className="card-header">
            <div className="flex items-center gap-2">
              {connectionStatus.isConnected ? (
                <Wifi className="w-5 h-5 text-green-500" />
              ) : (
                <WifiOff className="w-5 h-5 text-red-500" />
              )}
              <h3 className="text-lg font-semibold text-white">Connection</h3>
            </div>
            <div className={`status-indicator ${getConnectionStatusColor()}`}>
              {connectionStatus.isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className={getConnectionStatusColor()}>
                  {connectionStatus.isConnected ? 'Online' : 'Offline'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Quality:</span>
                <span className="capitalize">{connectionStatus.quality}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Latency:</span>
                <span>{connectionStatus.latency}ms</span>
              </div>
            </div>
          </div>
        </div>

        {/* Data Sync Status */}
        <div className="dashboard-card">
          <div className="card-header">
            <div className="flex items-center gap-2">
              <RotateCcw className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-white">Data Sync</h3>
            </div>
            <div className={`status-indicator ${getSyncStatusColor()}`}>
              {syncStatus.errorItems > 0 ? 'Error' : 
               syncStatus.pendingItems > 0 ? 'Syncing' : 'Synced'}
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Queue length:</span>
                <span>{syncStatus.pendingItems + syncStatus.errorItems}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Pending:</span>
                <span className="text-yellow-500">{syncStatus.pendingItems}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Errors:</span>
                <span className="text-red-500">{syncStatus.errorItems}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Conflicts:</span>
                <span className="text-orange-500">{syncStatus.conflictItems}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Offline Status */}
        <div className="dashboard-card">
          <div className="card-header">
            <div className="flex items-center gap-2">
              <HardDrive className="w-5 h-5 text-purple-500" />
              <h3 className="text-lg font-semibold text-white">Offline Storage</h3>
            </div>
            <div className={`status-indicator ${offlineStatus.isOffline ? 'text-orange-500' : 'text-green-500'}`}>
              {offlineStatus.isOffline ? 'Offline' : 'Online'}
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Data count:</span>
                <span>{offlineStatus.dataCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Storage size:</span>
                <span>{formatBytes(offlineStatus.storageSize)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Sync required:</span>
                <span className="text-yellow-500">0</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="dashboard-card">
          <div className="card-header">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-green-500" />
              <h3 className="text-lg font-semibold text-white">System Health</h3>
            </div>
            <div className="status-indicator text-green-500">
              Healthy
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Cache hit rate:</span>
                <span className="text-green-500">95%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">API response time:</span>
                <span className="text-green-500">120ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Memory usage:</span>
                <span className="text-green-500">45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Uptime:</span>
                <span className="text-green-500">99.9%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard-card">
          <div className="card-header">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="quick-actions-container">
              <button
                onClick={() => console.log('Force sync clicked')}
                className="quick-action-button quick-action-primary"
              >
                <RotateCcw />
                Force Sync
              </button>
              <button
                onClick={() => console.log('Reconnect clicked')}
                className="quick-action-button quick-action-success"
              >
                <Wifi />
                Reconnect
              </button>
              <button
                onClick={() => console.log('Clear data clicked')}
                className="quick-action-button quick-action-destructive"
              >
                <HardDrive />
                Clear Offline Data
              </button>
            </div>
          </div>
        </div>

        {/* Alerts & Notifications */}
        <div className="dashboard-card">
          <div className="card-header">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Alerts</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="space-y-2">
              {syncStatus.errorItems > 0 && (
                <div className="flex items-center gap-2 text-red-500">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm">{syncStatus.errorItems} sync errors</span>
                </div>
              )}
              {syncStatus.conflictItems > 0 && (
                <div className="flex items-center gap-2 text-orange-500">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm">{syncStatus.conflictItems} sync conflicts</span>
                </div>
              )}
              {offlineStatus.isOffline && (
                <div className="flex items-center gap-2 text-orange-500">
                  <WifiOff className="w-4 h-4" />
                  <span className="text-sm">Working offline</span>
                </div>
              )}
              {syncStatus.errorItems === 0 && syncStatus.conflictItems === 0 && !offlineStatus.isOffline && (
                <div className="flex items-center gap-2 text-green-500">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm">All systems operational</span>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
