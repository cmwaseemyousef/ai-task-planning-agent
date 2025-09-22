"""
Caching system for external API calls
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps
import pickle

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    Simple in-memory cache with TTL support
    """
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache with default TTL in seconds"""
        self.cache = {}
        self.default_ttl = default_ttl
        self.enabled = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        
        if not self.enabled:
            logger.info("Cache is disabled")
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function name and arguments"""
        # Create a string representation of arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        
        # Create hash
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if not self.enabled:
            return None
            
        if key in self.cache:
            item, expiry = self.cache[key]
            if datetime.now() < expiry:
                logger.debug(f"Cache hit for key: {key[:10]}...")
                return item
            else:
                # Remove expired item
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key[:10]}...")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache"""
        if not self.enabled:
            return
            
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
        logger.debug(f"Cache set for key: {key[:10]}... (TTL: {ttl}s)")
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired items and return count"""
        if not self.enabled:
            return 0
            
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items() 
            if now >= expiry
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'enabled': self.enabled,
            'total_items': len(self.cache),
            'default_ttl': self.default_ttl
        }

# Global cache instance
cache = SimpleCache(default_ttl=int(os.getenv("CACHE_TTL", 3600)))

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (None for default)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            cache_key = cache._generate_key(func_name, *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            try:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        # Add cache control methods
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: cache.get_stats()
        
        return wrapper
    return decorator

class PersistentCache:
    """
    Persistent cache using file system
    """
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 86400):
        """Initialize persistent cache"""
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.enabled = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        
        if self.enabled:
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from persistent cache"""
        if not self.enabled:
            return None
            
        file_path = self._get_file_path(key)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                if datetime.now() < data['expiry']:
                    logger.debug(f"Persistent cache hit for key: {key[:10]}...")
                    return data['value']
                else:
                    # Remove expired file
                    os.remove(file_path)
                    logger.debug(f"Persistent cache expired for key: {key[:10]}...")
        
        except Exception as e:
            logger.error(f"Error reading from persistent cache: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in persistent cache"""
        if not self.enabled:
            return
            
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        file_path = self._get_file_path(key)
        
        try:
            data = {
                'value': value,
                'expiry': expiry,
                'created': datetime.now()
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"Persistent cache set for key: {key[:10]}... (TTL: {ttl}s)")
        
        except Exception as e:
            logger.error(f"Error writing to persistent cache: {e}")
    
    def clear(self) -> None:
        """Clear all persistent cache"""
        if not self.enabled:
            return
            
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
            logger.info("Persistent cache cleared")
        except Exception as e:
            logger.error(f"Error clearing persistent cache: {e}")

# Global persistent cache instance
persistent_cache = PersistentCache()

def persistent_cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for persistent caching
    
    Args:
        ttl: Time to live in seconds (None for default)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            cache_key = cache._generate_key(func_name, *args, **kwargs)
            
            # Try to get from persistent cache
            result = persistent_cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            try:
                result = func(*args, **kwargs)
                persistent_cache.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"Error in persistent cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator