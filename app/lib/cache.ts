// APOLLO-GUIDED Advanced Caching System
interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
  hits: number;
}

class ApolloCache {
  private cache = new Map<string, CacheItem<any>>();
  private maxSize = 1000;
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T, ttl: number = this.defaultTTL): void {
    // Remove oldest items if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
      hits: 0
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Increment hit count
    item.hits++;
    return item.data;
  }

  has(key: string): boolean {
    const item = this.cache.get(key);
    if (!item) return false;
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  // Get cache statistics
  getStats() {
    const items = Array.from(this.cache.values());
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate: items.reduce((sum, item) => sum + item.hits, 0) / items.length || 0,
      memoryUsage: process.memoryUsage().heapUsed
    };
  }

  // Clean expired items
  cleanup(): number {
    const now = Date.now();
    let cleaned = 0;
    
    const keysToDelete: string[] = [];
    
    this.cache.forEach((item, key) => {
      if (now - item.timestamp > item.ttl) {
        keysToDelete.push(key);
        cleaned++;
      }
    });
    
    keysToDelete.forEach(key => this.cache.delete(key));
    
    return cleaned;
  }
}

// Singleton cache instance
export const apolloCache = new ApolloCache();

// Cache decorator for functions
export function cached<T extends (...args: any[]) => any>(
  fn: T,
  keyGenerator?: (...args: Parameters<T>) => string,
  ttl?: number
): T {
  return ((...args: Parameters<T>) => {
    const key = keyGenerator ? keyGenerator(...args) : `fn_${fn.name}_${JSON.stringify(args)}`;
    
    // Try to get from cache
    const cached = apolloCache.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    // Execute function and cache result
    const result = fn(...args);
    
    // Handle promises
    if (result instanceof Promise) {
      return result.then((res) => {
        apolloCache.set(key, res, ttl);
        return res;
      });
    }

    apolloCache.set(key, result, ttl);
    return result;
  }) as T;
}

// Cache middleware for API routes
export function withCache<T extends (...args: any[]) => any>(handler: T, ttl: number = 5 * 60 * 1000): T {
  return (async (req: any, res: any) => {
    const cacheKey = `api_${req.url}_${JSON.stringify(req.query)}`;
    
    // Try cache first
    const cached = apolloCache.get(cacheKey);
    if (cached) {
      return res.json(cached);
    }

    // Execute handler
    const result = await handler(req, res);
    
    // Cache successful responses
    if (res.statusCode === 200) {
      apolloCache.set(cacheKey, result, ttl);
    }
    
    return result;
  }) as T;
}

// Auto-cleanup every 5 minutes
setInterval(() => {
  const cleaned = apolloCache.cleanup();
  if (cleaned > 0) {
    console.log(`🧹 APOLLO Cache: Cleaned ${cleaned} expired items`);
  }
}, 5 * 60 * 1000);
