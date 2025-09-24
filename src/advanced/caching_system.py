"""
Multi-level Caching System
Implements memory, Redis, and disk caching for optimal performance
"""

import redis
import json
import hashlib
import time
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class MemoryCache:
    """In-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if entry.expires_at and datetime.now() > entry.expires_at:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return None
        
        # Update access tracking
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        
        # Update access order for LRU
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in memory cache"""
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            access_count=1,
            last_accessed=datetime.now()
        )
        
        self.cache[key] = entry
        
        # Enforce max size with LRU eviction
        if len(self.cache) > self.max_size:
            self._evict_lru()
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self.access_order:
            lru_key = self.access_order[0]
            del self.cache[lru_key]
            self.access_order.remove(lru_key)
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all entries"""
        self.cache.clear()
        self.access_order.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {'size': 0, 'hit_rate': 0.0}
        
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'total_accesses': total_accesses,
            'avg_accesses': total_accesses / len(self.cache) if self.cache else 0
        }

class DiskCache:
    """Disk-based cache using pickle serialization"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                entry = pickle.load(f)
            
            # Check expiration
            if entry.expires_at and datetime.now() > entry.expires_at:
                cache_file.unlink()
                return None
            
            return entry.value
        except Exception as e:
            logger.warning(f"Error reading disk cache for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in disk cache"""
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        cache_file = self.cache_dir / f"{key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            logger.warning(f"Error writing disk cache for key {key}: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete entry from disk cache"""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all entries"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'size': len(cache_files),
            'total_size_bytes': total_size,
            'cache_dir': str(self.cache_dir)
        }

class MultiLevelCache:
    """Multi-level cache combining memory, Redis, and disk"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 disk_cache_dir: str = "./cache", memory_max_size: int = 1000):
        """
        Initialize multi-level cache
        
        Args:
            redis_url: Redis connection URL
            disk_cache_dir: Directory for disk cache
            memory_max_size: Maximum size for memory cache
        """
        self.memory_cache = MemoryCache(max_size=memory_max_size)
        self.disk_cache = DiskCache(cache_dir=disk_cache_dir)
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
            self.redis_available = True
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.redis_client = None
            self.redis_available = False
        
        self.default_ttl = 3600  # 1 hour
        self.stats = {
            'memory_hits': 0,
            'redis_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'total_requests': 0
        }
    
    def get_cache_key(self, query: str, context_hash: str = "", 
                     user_id: str = "") -> str:
        """Generate cache key from query and context"""
        key_string = f"{query}:{context_hash}:{user_id}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (multi-level)"""
        self.stats['total_requests'] += 1
        
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            self.stats['memory_hits'] += 1
            return value
        
        # Try Redis
        if self.redis_available:
            try:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    value = json.loads(redis_value)
                    # Populate memory cache
                    self.memory_cache.set(key, value)
                    self.stats['redis_hits'] += 1
                    return value
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Try disk cache
        value = self.disk_cache.get(key)
        if value is not None:
            # Populate memory cache
            self.memory_cache.set(key, value)
            self.stats['disk_hits'] += 1
            return value
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in all cache levels"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Set in memory cache
        self.memory_cache.set(key, value, ttl)
        
        # Set in Redis
        if self.redis_available:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Set in disk cache
        self.disk_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete from all cache levels"""
        memory_deleted = self.memory_cache.delete(key)
        disk_deleted = self.disk_cache.delete(key)
        
        if self.redis_available:
            try:
                redis_deleted = self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
                redis_deleted = False
        else:
            redis_deleted = True
        
        return memory_deleted or disk_deleted or redis_deleted
    
    def clear(self) -> None:
        """Clear all cache levels"""
        self.memory_cache.clear()
        self.disk_cache.clear()
        
        if self.redis_available:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
    
    def cache_query(self, query: str, context: List[str], response: Dict[str, Any], 
                   user_id: str = "", ttl: Optional[int] = None) -> str:
        """Cache query response"""
        context_hash = hashlib.md5(json.dumps(context).encode()).hexdigest()
        key = self.get_cache_key(query, context_hash, user_id)
        self.set(key, response, ttl)
        return key
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.stats['total_requests']
        
        if total_requests == 0:
            hit_rate = 0.0
        else:
            hits = self.stats['memory_hits'] + self.stats['redis_hits'] + self.stats['disk_hits']
            hit_rate = hits / total_requests
        
        return {
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'memory_hits': self.stats['memory_hits'],
            'redis_hits': self.stats['redis_hits'],
            'disk_hits': self.stats['disk_hits'],
            'misses': self.stats['misses'],
            'memory_stats': self.memory_cache.stats(),
            'disk_stats': self.disk_cache.stats(),
            'redis_available': self.redis_available
        }
    
    def warm_cache(self, queries: List[str], responses: List[Dict[str, Any]], 
                   ttl: Optional[int] = None) -> None:
        """Warm cache with pre-computed responses"""
        for query, response in zip(queries, responses):
            key = self.get_cache_key(query)
            self.set(key, response, ttl)
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries (memory cache only)"""
        # Memory cache cleanup is handled automatically
        # Disk cache cleanup would require scanning all files
        # Redis cleanup is handled automatically with TTL
        return 0

class CacheManager:
    """High-level cache manager with intelligent caching strategies"""
    
    def __init__(self, multi_level_cache: MultiLevelCache):
        self.cache = multi_level_cache
        self.cache_strategies = {
            'aggressive': {'ttl': 7200, 'preload': True},  # 2 hours
            'moderate': {'ttl': 3600, 'preload': False},  # 1 hour
            'conservative': {'ttl': 1800, 'preload': False}  # 30 minutes
        }
        self.current_strategy = 'moderate'
    
    def set_strategy(self, strategy: str) -> None:
        """Set caching strategy"""
        if strategy in self.cache_strategies:
            self.current_strategy = strategy
            logger.info(f"Cache strategy set to: {strategy}")
        else:
            logger.warning(f"Unknown cache strategy: {strategy}")
    
    def get_strategy_config(self) -> Dict[str, Any]:
        """Get current strategy configuration"""
        return self.cache_strategies[self.current_strategy]
    
    def cache_with_strategy(self, key: str, value: Any, 
                          custom_ttl: Optional[int] = None) -> None:
        """Cache with current strategy"""
        config = self.get_strategy_config()
        ttl = custom_ttl or config['ttl']
        self.cache.set(key, value, ttl)
    
    def should_cache(self, query: str, response: Dict[str, Any]) -> bool:
        """Determine if response should be cached"""
        # Don't cache if response indicates error
        if 'error' in response:
            return False
        
        # Don't cache very short responses
        if len(response.get('answer', '')) < 50:
            return False
        
        # Don't cache responses with low confidence
        if response.get('confidence', 1.0) < 0.5:
            return False
        
        return True
    
    def get_cached_response(self, query: str, context: List[str], 
                           user_id: str = "") -> Optional[Dict[str, Any]]:
        """Get cached response if available"""
        context_hash = hashlib.md5(json.dumps(context).encode()).hexdigest()
        key = self.cache.get_cache_key(query, context_hash, user_id)
        return self.cache.get(key)
    
    def cache_response(self, query: str, context: List[str], 
                      response: Dict[str, Any], user_id: str = "") -> str:
        """Cache response with appropriate strategy"""
        if not self.should_cache(query, response):
            return ""
        
        context_hash = hashlib.md5(json.dumps(context).encode()).hexdigest()
        key = self.cache.get_cache_key(query, context_hash, user_id)
        
        config = self.get_strategy_config()
        self.cache.cache_query(query, context, response, user_id, config['ttl'])
        
        return key
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        stats = self.cache.get_cache_stats()
        
        # Calculate additional metrics
        if stats['total_requests'] > 0:
            memory_hit_rate = stats['memory_hits'] / stats['total_requests']
            redis_hit_rate = stats['redis_hits'] / stats['total_requests']
            disk_hit_rate = stats['disk_hits'] / stats['total_requests']
        else:
            memory_hit_rate = redis_hit_rate = disk_hit_rate = 0.0
        
        return {
            **stats,
            'memory_hit_rate': memory_hit_rate,
            'redis_hit_rate': redis_hit_rate,
            'disk_hit_rate': disk_hit_rate,
            'current_strategy': self.current_strategy,
            'strategy_config': self.get_strategy_config()
        }
