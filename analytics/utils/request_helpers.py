"""
Utilitários base para filtros e parâmetros comuns
Centraliza lógica repetitiva de request processing
"""
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsRequestHelper:
    """Helper para processar parâmetros comuns de request"""
    
    @staticmethod
    def get_date_filter(request, default_days=30):
        """
        Extrai filtro de data dos parâmetros de request
        Returns: (days, date_from) tuple
        """
        try:
            days = int(request.GET.get('days', default_days))
            if days < 1:
                logger.warning(f"Days parameter too small: {days}, using 1")
                days = 1
            elif days > 365:
                logger.warning(f"Days parameter too large: {days}, using 365")
                days = 365
                
            date_from = timezone.now() - timedelta(days=days)
            return days, date_from
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid days parameter: {e}, using default {default_days}")
            days = default_days
            date_from = timezone.now() - timedelta(days=days)
            return days, date_from
    
    @staticmethod
    def get_pagination_params(request, default_page=1, default_per_page=50, max_per_page=100):
        """
        Extrai parâmetros de paginação com validação
        Returns: (page, per_page) tuple
        """
        try:
            page = max(1, int(request.GET.get('page', default_page)))
        except (ValueError, TypeError):
            logger.warning("Invalid page parameter, using 1")
            page = 1
        
        try:
            per_page = int(request.GET.get('per_page', default_per_page))
            per_page = max(1, min(per_page, max_per_page))  # Entre 1 e max_per_page
        except (ValueError, TypeError):
            logger.warning(f"Invalid per_page parameter, using {default_per_page}")
            per_page = default_per_page
        
        return page, per_page
    
    @staticmethod
    def get_limit_param(request, default_limit=20, max_limit=100):
        """
        Extrai parâmetro limit com validação
        Returns: limit int
        """
        try:
            limit = int(request.GET.get('limit', default_limit))
            limit = max(1, min(limit, max_limit))
            return limit
        except (ValueError, TypeError):
            logger.warning(f"Invalid limit parameter, using {default_limit}")
            return default_limit
    
    @staticmethod
    def get_granularity_param(request, allowed=['daily', 'hourly'], default='daily'):
        """
        Extrai parâmetro granularity com validação
        Returns: granularity string
        """
        granularity = request.GET.get('granularity', default)
        if granularity not in allowed:
            logger.warning(f"Invalid granularity '{granularity}', using '{default}'")
            return default
        return granularity
    
    @staticmethod
    def get_min_emails_param(request, default_min=3):
        """
        Extrai parâmetro min_emails para filtros de volume
        Returns: min_emails int
        """
        try:
            min_emails = max(1, int(request.GET.get('min_emails', default_min)))
            return min_emails
        except (ValueError, TypeError):
            logger.warning(f"Invalid min_emails parameter, using {default_min}")
            return default_min


class AnalyticsResponseHelper:
    """Helper para padronizar responses da API"""
    
    @staticmethod
    def create_success_response(data, extra_fields=None):
        """
        Cria response JSON padronizada de sucesso
        """
        response = {
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
        }
        if isinstance(data, dict):
            response.update(data)
        else:
            response['data'] = data
        
        if extra_fields:
            response.update(extra_fields)
        
        return JsonResponse(response)
    
    @staticmethod
    def create_error_response(message, status_code=400, details=None):
        """
        Cria response JSON padronizada de erro
        """
        response = {
            'status': 'error',
            'error': message,
            'timestamp': timezone.now().isoformat(),
        }
        
        if details:
            response['details'] = details
        
        logger.error(f"API Error: {message} (status: {status_code})")
        return JsonResponse(response, status=status_code)
    
    @staticmethod
    def safe_round(value, decimals=2, default=0.0):
        """
        Arredonda valor de forma segura
        """
        try:
            if value is None:
                return default
            return round(float(value), decimals)
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def safe_percentage(numerator, denominator, decimals=2, default=0.0):
        """
        Calcula percentual de forma segura
        """
        try:
            if denominator == 0:
                return default
            return round((numerator / denominator) * 100, decimals)
        except (TypeError, ValueError, ZeroDivisionError):
            return default


class AnalyticsErrorHandler:
    """Tratamento centralizado de erros para analytics"""
    
    @staticmethod
    def handle_view_error(error, view_name, request_params=None):
        """
        Trata erros de views de forma padronizada
        """
        error_msg = f"Error in {view_name}"
        
        logger.error(
            f"{error_msg}: {str(error)}",
            extra={
                'view': view_name,
                'params': request_params,
                'error_type': type(error).__name__
            },
            exc_info=True
        )
        
        return AnalyticsResponseHelper.create_error_response(
            message=f"Erro interno no endpoint {view_name}",
            status_code=500,
            details=str(error) if logger.getEffectiveLevel() <= logging.DEBUG else None
        )
    
    @staticmethod
    def handle_validation_error(errors, view_name):
        """
        Trata erros de validação
        """
        logger.warning(f"Validation error in {view_name}: {errors}")
        return AnalyticsResponseHelper.create_error_response(
            message="Parâmetros inválidos fornecidos",
            status_code=400,
            details=errors
        )


def with_error_handling(view_name):
    """
    Decorator para adicionar tratamento de erro automático
    """
    def decorator(view_method):
        def wrapper(self, request, *args, **kwargs):
            try:
                return view_method(self, request, *args, **kwargs)
            except Exception as e:
                return AnalyticsErrorHandler.handle_view_error(
                    error=e,
                    view_name=view_name,
                    request_params=dict(request.GET.items())
                )
        return wrapper
    return decorator