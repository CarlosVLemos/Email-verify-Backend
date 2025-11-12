from functools import wraps
from django.core.cache import cache
from django.utils.encoding import force_str
import hashlib
import json


def cache_response(timeout=300, cache_alias='default', key_prefix='view'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            query_params = dict(request.query_params)
            
            cache_key_data = {
                'view': view_func.__name__,
                'params': query_params,
                'prefix': key_prefix
            }
            
            cache_key_str = json.dumps(cache_key_data, sort_keys=True)
            cache_key = hashlib.md5(
                force_str(cache_key_str).encode('utf-8')
            ).hexdigest()
            
            cache_key = f'{key_prefix}:{cache_key}'
            
            cached_response = cache.get(cache_key, None, version=None)
            
            if cached_response is not None:
                return cached_response
            
            response = view_func(self, request, *args, **kwargs)
            
            if response.status_code == 200:
                cache.set(cache_key, response, timeout, version=None)
            
            return response
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    from django_redis import get_redis_connection
    
    conn = get_redis_connection("default")
    keys = conn.keys(f"*{pattern}*")
    
    if keys:
        conn.delete(*keys)
        return len(keys)
    return 0
