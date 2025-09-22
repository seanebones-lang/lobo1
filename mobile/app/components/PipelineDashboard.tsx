'use client'

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Database, Zap, MessageCircle, TrendingUp, Users, Clock, CheckCircle } from 'lucide-react';

interface PipelineStats {
  name: string;
  status: string;
  requests: number;
  avgResponseTime: number;
  successRate: number;
  lastActivity: string;
}

interface SystemStatus {
  timestamp: string;
  status: string;
  pipelines: {
    api: Array<{
      name: string;
      config: any;
      status: string;
      lastChecked: string;
    }>;
    rag: {
      totalPipelines: number;
      availablePipelines: string[];
      knowledgeBaseSize: number;
      status: string;
    };
  };
  cache: {
    size: number;
    keys: string[];
  };
  uptime: number;
  memory: any;
  version: string;
}

export default function PipelineDashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/pipelines/status');
      if (!response.ok) throw new Error('Failed to fetch system status');
      
      const data = await response.json();
      setSystemStatus(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const formatMemory = (bytes: number) => {
    const mb = bytes / 1024 / 1024;
    return `${mb.toFixed(2)} MB`;
  };

  const pipelineIcons = {
    tattoo_knowledge: <Database className="w-5 h-5" />,
    customer_service: <Users className="w-5 h-5" />,
    sales: <TrendingUp className="w-5 h-5" />,
    conversation: <MessageCircle className="w-5 h-5" />,
    analytics: <Activity className="w-5 h-5" />
  };

  if (loading) {
    return (
      <div className="pipeline-dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apollo-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pipeline-dashboard">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">Error loading pipeline status: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pipeline-dashboard">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h2 className="text-3xl font-bold gradient-text mb-2">APOLLO Pipeline Dashboard</h2>
        <p className="text-gray-400">Real-time system status and performance metrics</p>
      </motion.div>

      {/* System Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
      >
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <h3 className="text-lg font-semibold">System Status</h3>
          </div>
          <p className="text-2xl font-bold text-green-400 capitalize">
            {systemStatus?.status || 'Unknown'}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            Last updated: {new Date(systemStatus?.timestamp || '').toLocaleTimeString()}
          </p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-6 h-6 text-blue-400" />
            <h3 className="text-lg font-semibold">Uptime</h3>
          </div>
          <p className="text-2xl font-bold text-blue-400">
            {systemStatus ? formatUptime(systemStatus.uptime) : '0d 0h 0m'}
          </p>
          <p className="text-sm text-gray-400 mt-1">System uptime</p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-6 h-6 text-purple-400" />
            <h3 className="text-lg font-semibold">Knowledge Base</h3>
          </div>
          <p className="text-2xl font-bold text-purple-400">
            {systemStatus?.pipelines.rag.knowledgeBaseSize || 0}
          </p>
          <p className="text-sm text-gray-400 mt-1">Knowledge items</p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="w-6 h-6 text-yellow-400" />
            <h3 className="text-lg font-semibold">Memory Usage</h3>
          </div>
          <p className="text-2xl font-bold text-yellow-400">
            {systemStatus ? formatMemory(systemStatus.memory.heapUsed) : '0 MB'}
          </p>
          <p className="text-sm text-gray-400 mt-1">Heap memory</p>
        </div>
      </motion.div>

      {/* API Pipelines */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-8"
      >
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          API Pipelines
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {systemStatus?.pipelines.api.map((pipeline, index) => (
            <motion.div
              key={pipeline.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              className="glass-card p-4"
            >
              <div className="flex items-center gap-3 mb-3">
                {pipelineIcons[pipeline.name as keyof typeof pipelineIcons] || <Activity className="w-5 h-5" />}
                <h4 className="font-semibold capitalize">
                  {pipeline.name.replace('_', ' ')}
                </h4>
                <div className={`w-2 h-2 rounded-full ml-auto ${
                  pipeline.status === 'active' ? 'bg-green-400' : 'bg-red-400'
                }`} />
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Rate Limit:</span>
                  <span className="text-white">{pipeline.config.rateLimit}/min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Timeout:</span>
                  <span className="text-white">{pipeline.config.timeout}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Cache:</span>
                  <span className="text-white">{pipeline.config.cache ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Analytics:</span>
                  <span className="text-white">{pipeline.config.analytics ? 'Enabled' : 'Disabled'}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* RAG Pipelines */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mb-8"
      >
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          RAG Pipelines
        </h3>
        <div className="glass-card p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Available Pipelines</h4>
              <div className="space-y-2">
                {systemStatus?.pipelines.rag.availablePipelines.map((pipeline) => (
                  <div key={pipeline} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400" />
                    <span className="capitalize">{pipeline.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2">Knowledge Distribution</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Tattoo Knowledge:</span>
                  <span className="text-white">30%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Customer Service:</span>
                  <span className="text-white">30%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sales:</span>
                  <span className="text-white">30%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Conversation:</span>
                  <span className="text-white">10%</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2">Cache Status</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Cache Size:</span>
                  <span className="text-white">{systemStatus?.cache.size || 0} items</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* System Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="glass-card p-6"
      >
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          System Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-2">Version & Build</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Version:</span>
                <span className="text-white">{systemStatus?.version || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Build:</span>
                <span className="text-white">APOLLO-1.0.0-RAG</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Environment:</span>
                <span className="text-white">Production</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2">Performance</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Memory:</span>
                <span className="text-white">{systemStatus ? formatMemory(systemStatus.memory.heapTotal) : '0 MB'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">External:</span>
                <span className="text-white">{systemStatus ? formatMemory(systemStatus.memory.external) : '0 MB'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">RSS:</span>
                <span className="text-white">{systemStatus ? formatMemory(systemStatus.memory.rss) : '0 MB'}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
