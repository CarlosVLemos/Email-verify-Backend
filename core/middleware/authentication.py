"""
Autenticação via API Key - Simples e eficiente para o case
Sem complexidade de usuários, apenas validação de chave
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import secrets
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class APIKeyAuthentication(BaseAuthentication):
    """
    Autenticação via API Key no header X-API-Key
    
    Em desenvolvimento (DEBUG=True): Permite requests sem key
    Em produção (DEBUG=False): Exige key válida
    
    Usage:
        curl -H "X-API-Key: dev_test_key_123" \\
             -H "Content-Type: application/json" \\
             -d '{"email_text": "teste"}' \\
             http://localhost:8000/api/classifier/classify/
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            if settings.DEBUG:
                return (None, None)
            raise AuthenticationFailed('API Key obrigatória. Envie no header X-API-Key')
        
        if self.is_valid_api_key(api_key):
            return (None, api_key)
        
        raise AuthenticationFailed('API Key inválida')
    
    @staticmethod
    def is_valid_api_key(api_key: str) -> bool:
        """Valida se a key existe nas keys configuradas"""
        valid_keys = settings.API_KEYS
        return api_key in valid_keys


class OptionalAPIKeyAuthentication(APIKeyAuthentication):
    """
    Versão que SEMPRE permite acesso, mas rastreia se tem key
    Usado para endpoints públicos com rate limiting diferenciado
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return (None, None)
        
        if self.is_valid_api_key(api_key):
            return (None, api_key)
        
        return (None, None)


class OptionalAPIKeyAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'core.middleware.authentication.OptionalAPIKeyAuthentication'  # Caminho completo da classe
    name = 'OptionalAPIKeyAuthentication'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'name': 'X-API-Key',
            'in': 'header',
        }


def generate_api_key(prefix: str = "sk") -> str:
    """
    Gera uma API key segura
    
    Args:
        prefix: Prefixo da key (dev, prod, test)
    
    Returns:
        str: API key no formato 'prefix_xxxxx'
    
    Example:
        >>> generate_api_key("dev")
        'dev_a8f3j29fj2f9j23f9j23f9j23f'
    """
