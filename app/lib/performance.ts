// APOLLO-GUIDED Performance Monitoring System
import { NextRequest, NextResponse } from 'next/server';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}

interface APIMetric {
  endpoint: string;
  method: string;
  duration: number;
  statusCode: number;
  timestamp: number;
  userId?: string;
}

class ApolloPerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private apiMetrics: APIMetric[] = [];
  private maxMetrics = 10000;

  // Record custom metric
  recordMetric(name: string, value: number, tags?: Record<string, string>) {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now(),
      tags
    };

    this.metrics.push(metric);

    // Keep only recent metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    console.log(`📊 APOLLO Metric: ${name} = ${value}`, tags);
  }

  // Record API performance
  recordAPICall(endpoint: string, method: string, duration: number, statusCode: number, userId?: string) {
    const apiMetric: APIMetric = {
      endpoint,
      method,
      duration,
      statusCode,
      timestamp: Date.now(),
      userId
    };

    this.apiMetrics.push(apiMetric);

    // Keep only recent API metrics
    if (this.apiMetrics.length > this.maxMetrics) {
      this.apiMetrics = this.apiMetrics.slice(-this.maxMetrics);
    }

    console.log(`🚀 APOLLO API: ${method} ${endpoint} - ${duration}ms - ${statusCode}`);
  }

  // Get performance summary
  getPerformanceSummary() {
    const now = Date.now();
    const lastHour = now - (60 * 60 * 1000);
    const last24Hours = now - (24 * 60 * 60 * 1000);

    const recentMetrics = this.metrics.filter(m => m.timestamp > lastHour);
    const recentAPIs = this.apiMetrics.filter(m => m.timestamp > lastHour);

    const avgResponseTime = recentAPIs.length > 0 
      ? recentAPIs.reduce((sum, api) => sum + api.duration, 0) / recentAPIs.length 
      : 0;

    const errorRate = recentAPIs.length > 0
      ? recentAPIs.filter(api => api.statusCode >= 400).length / recentAPIs.length
      : 0;

    const throughput = recentAPIs.length / 60; // requests per minute

    return {
      avgResponseTime: Math.round(avgResponseTime),
      errorRate: Math.round(errorRate * 100) / 100,
      throughput: Math.round(throughput * 100) / 100,
      totalRequests: recentAPIs.length,
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      uptime: process.uptime()
    };
  }

  // Get API performance by endpoint
  getAPIStats() {
    const endpointStats = new Map<string, {
      count: number;
      avgDuration: number;
      errorCount: number;
      lastCalled: number;
    }>();

    this.apiMetrics.forEach(api => {
      const key = `${api.method} ${api.endpoint}`;
      const existing = endpointStats.get(key) || {
        count: 0,
        avgDuration: 0,
        errorCount: 0,
        lastCalled: 0
      };

      existing.count++;
      existing.avgDuration = (existing.avgDuration + api.duration) / 2;
      if (api.statusCode >= 400) existing.errorCount++;
      if (api.timestamp > existing.lastCalled) existing.lastCalled = api.timestamp;

      endpointStats.set(key, existing);
    });

    return Array.from(endpointStats.entries()).map(([endpoint, stats]) => ({
      endpoint,
      ...stats,
      errorRate: stats.count > 0 ? stats.errorCount / stats.count : 0
    }));
  }

  // Get system health
  getSystemHealth() {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    const uptime = process.uptime();

    const health = {
      status: 'healthy' as 'healthy' | 'warning' | 'critical',
      memory: {
        used: memUsage.heapUsed,
        total: memUsage.heapTotal,
        percentage: (memUsage.heapUsed / memUsage.heapTotal) * 100
      },
      cpu: {
        user: cpuUsage.user,
        system: cpuUsage.system
      },
      uptime,
      metrics: this.getPerformanceSummary()
    };

    // Determine health status
    if (health.memory.percentage > 90) {
      health.status = 'critical';
    } else if (health.memory.percentage > 75) {
      health.status = 'warning';
    }

    return health;
  }

  // Performance middleware
  withPerformanceMonitoring(handler: Function) {
    return async (request: NextRequest, ...args: any[]) => {
      const startTime = Date.now();
      const startCpu = process.cpuUsage();

      try {
        const response = await handler(request, ...args);
        const duration = Date.now() - startTime;
        const cpuUsage = process.cpuUsage(startCpu);

        // Record API metric
        this.recordAPICall(
          request.nextUrl.pathname,
          request.method,
          duration,
          response.status || 200
        );

        // Record performance metric
        this.recordMetric('api_duration', duration, {
          endpoint: request.nextUrl.pathname,
          method: request.method
        });

        this.recordMetric('cpu_usage', cpuUsage.user + cpuUsage.system, {
          type: 'api_call'
        });

        return response;
      } catch (error) {
        const duration = Date.now() - startTime;
        
        this.recordAPICall(
          request.nextUrl.pathname,
          request.method,
          duration,
          500
        );

        this.recordMetric('api_error', 1, {
          endpoint: request.nextUrl.pathname,
          method: request.method,
          error: error instanceof Error ? error.message : 'Unknown error'
        });

        throw error;
      }
    };
  }

  // Memory monitoring
  startMemoryMonitoring() {
    setInterval(() => {
      const memUsage = process.memoryUsage();
      this.recordMetric('memory_heap_used', memUsage.heapUsed);
      this.recordMetric('memory_heap_total', memUsage.heapTotal);
      this.recordMetric('memory_external', memUsage.external);
      this.recordMetric('memory_rss', memUsage.rss);
    }, 30000); // Every 30 seconds
  }

  // CPU monitoring
  startCPUMonitoring() {
    let lastCpuUsage = process.cpuUsage();
    
    setInterval(() => {
      const currentCpuUsage = process.cpuUsage(lastCpuUsage);
      const totalCpuTime = currentCpuUsage.user + currentCpuUsage.system;
      
      this.recordMetric('cpu_user', currentCpuUsage.user);
      this.recordMetric('cpu_system', currentCpuUsage.system);
      this.recordMetric('cpu_total', totalCpuTime);
      
      lastCpuUsage = process.cpuUsage();
    }, 5000); // Every 5 seconds
  }

  // Start all monitoring
  startMonitoring() {
    this.startMemoryMonitoring();
    this.startCPUMonitoring();
    console.log('🔍 APOLLO Performance Monitoring: Started');
  }

  // Get all metrics for analysis
  getAllMetrics() {
    return {
      customMetrics: this.metrics,
      apiMetrics: this.apiMetrics,
      summary: this.getPerformanceSummary(),
      apiStats: this.getAPIStats(),
      systemHealth: this.getSystemHealth()
    };
  }
}

// Singleton instance
export const apolloPerformance = new ApolloPerformanceMonitor();

// Auto-start monitoring
apolloPerformance.startMonitoring();

// Performance decorator
export function withPerformanceTracking(target: any, propertyName: string, descriptor: PropertyDescriptor) {
  const method = descriptor.value;

  descriptor.value = async function (...args: any[]) {
    const startTime = Date.now();
    const startCpu = process.cpuUsage();

    try {
      const result = await method.apply(this, args);
      const duration = Date.now() - startTime;
      const cpuUsage = process.cpuUsage(startCpu);

      apolloPerformance.recordMetric(`${target.constructor.name}.${propertyName}`, duration);
      apolloPerformance.recordMetric('cpu_usage', cpuUsage.user + cpuUsage.system, {
        method: `${target.constructor.name}.${propertyName}`
      });

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      apolloPerformance.recordMetric(`${target.constructor.name}.${propertyName}_error`, duration);
      throw error;
    }
  };
}
