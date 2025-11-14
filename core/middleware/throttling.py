"""
Rate Limiting inteligente - diferenciado por API Key
Protege a API de abuso sem necessidade de usuários
"""
from rest_framework.throttling import SimpleRateThrottle
import hashlib


class BurstRateThrottle(SimpleRateThrottle):
    scope = 'burst'
    
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return f'throttle_burst_{ident}'


class AnonRateThrottle(SimpleRateThrottle):
    scope = 'anon'
    
    def get_cache_key(self, request, view):
        if request.META.get('HTTP_X_API_KEY'):
            return None  # Não limita
        
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class APIKeyRateThrottle(SimpleRateThrottle):
    scope = 'api_key'
    
    def get_cache_key(self, request, view):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None  
        
        key_hash = hashlib.md5(api_key.encode()).hexdigest()
        return f'throttle_apikey_{key_hash}'
