"""
Views para Analytics API - Refatorado com utilitários
Endpoints para alimentar dashboards e visualizações
"""
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta

# Novos imports dos utilitários
from .utils.request_helpers import (
    AnalyticsRequestHelper, AnalyticsResponseHelper, 
    AnalyticsErrorHandler, with_error_handling
)
from .utils.query_helpers import AnalyticsQueryBuilder, AnalyticsFormatter
from .utils.services import AnalyticsService


class DashboardOverviewView(View):
    """
    Endpoint principal do dashboard - Refatorado
    GET /analytics/dashboard/overview/
    """
    
    @with_error_handling('dashboard_overview')
    def get(self, request):
        """Retorna visão geral das métricas"""
        
        # Extrai parâmetros com validação
        days, date_from = AnalyticsRequestHelper.get_date_filter(request, default_days=30)
        
        # Busca estatísticas de produtividade (query otimizada)
        productivity_stats = AnalyticsQueryBuilder.get_productivity_stats(date_from)
        
        # Busca top categorias (baseado no período)
        period_field = 'last_30_days' if days >= 30 else 'last_7_days'
        top_categories = list(AnalyticsQueryBuilder.get_top_categories(
            period_field=period_field, 
            limit=5
        ))
        
        # Busca top remetentes produtivos
        top_senders = list(AnalyticsQueryBuilder.get_top_senders(
            min_emails=5,
            limit=10,
            order_by='productivity_rate'
        ))
        
        # Monta response com helpers
        overview_data = {
            'overview': {
                'total_emails': productivity_stats['total_count'],
                'productive_emails': productivity_stats['productive'],
                'unproductive_emails': productivity_stats['unproductive'],
                'productivity_rate': AnalyticsResponseHelper.safe_round(productivity_stats['productivity_rate']),
                'avg_confidence': AnalyticsResponseHelper.safe_round(productivity_stats['avg_confidence'], 3),
                'avg_processing_time': AnalyticsResponseHelper.safe_round(productivity_stats['avg_processing_time']),
                'attachment_rate': AnalyticsResponseHelper.safe_round(productivity_stats['attachment_rate']),
                'period_days': days,
                'last_updated': timezone.now().isoformat(),
            },
            'top_categories': top_categories,
            'top_senders': top_senders
        }
        
        return AnalyticsResponseHelper.create_success_response(overview_data)


class ProductivityTrendView(View):
    """
    Endpoint para dados de tendência de produtividade - Refatorado
    GET /analytics/dashboard/trends/
    """
    
    @with_error_handling('productivity_trends')
    def get(self, request):
        """Retorna dados de série temporal"""
        
        # Extrai parâmetros com validação
        days, date_from = AnalyticsRequestHelper.get_date_filter(request, default_days=30)
        granularity = AnalyticsRequestHelper.get_granularity_param(request)
        
        # Busca dados de timeline (query otimizada)
        timeline_raw = AnalyticsQueryBuilder.get_timeline_data(date_from, granularity)
        
        # Formata dados para response
        timeline_data = []
        for item in timeline_raw:
            formatted_item = {
                'date': item['date'].isoformat(),
                'hour': item['hour'] if granularity == 'hourly' else 0,
                'total_emails': item['total_emails'],
                'productive_emails': item['productive_emails'],
                'unproductive_emails': item['unproductive_emails'],
                'productivity_rate': AnalyticsResponseHelper.safe_round(item['productivity_rate']),
                'avg_confidence': AnalyticsResponseHelper.safe_round(item['avg_confidence'], 3),
                'label': AnalyticsFormatter.format_timeline_label(
                    item['date'], item['hour'], granularity
                )
            }
            timeline_data.append(formatted_item)
        
        # Calcula análise de tendência
        trend_analysis = AnalyticsFormatter.calculate_trend_analysis(timeline_data)
        
        # Monta response
        response_data = {
            'timeline': timeline_data,
            'period': f'{days} days',
            'granularity': granularity,
            'trend_analysis': trend_analysis
        }
        
        return AnalyticsResponseHelper.create_success_response(response_data)


class CategoryDistributionView(View):
    """
    Endpoint para distribuição de categorias
    GET /analytics/dashboard/categories/
    """
    
    @with_error_handling('category_distribution')
    def get(self, request):
        """Retorna distribuição de categorias para gráfico de pizza"""

        days, _ = AnalyticsRequestHelper.get_date_filter(request, default_days=30)
        period_field = 'last_30_days' if days >= 30 else 'last_7_days'
        categories_raw = list(AnalyticsQueryBuilder.get_top_categories(
            period_field=period_field,
            limit=50
        ))

        distribution_data = []
        total_emails = 0

        for cat in categories_raw:
            count = cat.get(period_field, 0) or 0
            total_emails += count
            distribution_data.append({
                'category': cat.get('category'),
                'subcategory': cat.get('subcategory'),
                'count': count,
                'avg_confidence': AnalyticsResponseHelper.safe_round(cat.get('avg_confidence'), 3),
                'trend_direction': cat.get('trend_direction'),
                'trend_percentage': AnalyticsResponseHelper.safe_round(cat.get('trend_percentage')),
            })

        for item in distribution_data:
            item['percentage'] = AnalyticsResponseHelper.safe_percentage(
                item['count'],
                total_emails
            )

        response_data = {
            'categories': distribution_data,
            'total_emails': total_emails,
            'period': f'{days} days'
        }

        return AnalyticsResponseHelper.create_success_response(response_data)


class SenderAnalysisView(View):
    """
    Endpoint para análise de remetentes
    GET /analytics/dashboard/senders/
    """
    
    @with_error_handling('sender_analysis')
    def get(self, request):
        """Retorna análise de produtividade por remetente"""

        limit = AnalyticsRequestHelper.get_limit_param(request, default_limit=20, max_limit=100)
        min_emails = AnalyticsRequestHelper.get_min_emails_param(request, default_min=3)

        productive_raw = list(AnalyticsQueryBuilder.get_sender_segment(
            min_emails=min_emails,
            limit=limit,
            segment='productive'
        ))
        unproductive_raw = list(AnalyticsQueryBuilder.get_sender_segment(
            min_emails=min_emails,
            limit=limit,
            segment='unproductive'
        ))
        domains_summary_raw = list(AnalyticsQueryBuilder.get_domains_summary(
            min_emails=min_emails,
            limit=15
        ))

        def _format_sender_list(items):
            formatted = []
            for item in items:
                formatted.append({
                    'sender_identifier': item.get('sender_identifier'),
                    'sender_type': item.get('sender_type'),
                    'productivity_rate': AnalyticsResponseHelper.safe_round(item.get('productivity_rate')), 
                    'total_count': item.get('total_count', 0),
                    'productive_count': item.get('productive_count', 0),
                    'unproductive_count': item.get('unproductive_count', 0),
                    'first_seen': item.get('first_seen'),
                    'last_seen': item.get('last_seen'),
                })
            return formatted

        top_productive = _format_sender_list(productive_raw)
        top_unproductive = _format_sender_list(unproductive_raw)

        domains_summary = []
        for domain in domains_summary_raw:
            domains_summary.append({
                'sender_identifier': domain.get('sender_identifier'),
                'total_emails': domain.get('total_emails', 0),
                'avg_productivity': AnalyticsResponseHelper.safe_round(domain.get('avg_productivity')),
                'total_productive': domain.get('total_productive', 0),
                'total_unproductive': domain.get('total_unproductive', 0),
            })

        response_data = {
            'top_productive': top_productive,
            'top_unproductive': top_unproductive,
            'domains_summary': domains_summary,
            'filters': {
                'limit': limit,
                'min_emails': min_emails
            }
        }

        return AnalyticsResponseHelper.create_success_response(response_data)


class KeywordInsightsView(View):
    """
    Endpoint para insights de palavras-chave
    GET /analytics/dashboard/keywords/
    """
    
    @with_error_handling('keyword_insights')
    def get(self, request):
        """Retorna análise de palavras-chave mais frequentes"""

        limit = AnalyticsRequestHelper.get_limit_param(request, default_limit=20, max_limit=100)
        days, _ = AnalyticsRequestHelper.get_date_filter(request, default_days=30)
        period_field = 'last_30_days_freq' if days >= 30 else 'last_7_days_freq'

        productive_raw = list(AnalyticsQueryBuilder.get_keyword_insights(
            category='Produtivo',
            limit=limit,
            period_field=period_field
        ))
        unproductive_raw = list(AnalyticsQueryBuilder.get_keyword_insights(
            category='Improdutivo',
            limit=limit,
            period_field=period_field
        ))
        trending_raw = list(AnalyticsQueryBuilder.get_trending_keywords(limit=limit))

        def _format_keyword_list(items):
            formatted = []
            for item in items:
                formatted.append({
                    'keyword': item.get('keyword'),
                    'frequency': item.get('frequency', 0),
                    'last_7_days_freq': item.get('last_7_days_freq', 0),
                    'last_30_days_freq': item.get('last_30_days_freq', 0),
                    'avg_confidence_when_present': AnalyticsResponseHelper.safe_round(
                        item.get('avg_confidence_when_present'),
                        3
                    ),
                })
            return formatted

        productive_keywords = _format_keyword_list(productive_raw)
        unproductive_keywords = _format_keyword_list(unproductive_raw)

        trending_keywords = []
        for item in trending_raw:
            trending_keywords.append({
                'keyword': item.get('keyword'),
                'category': item.get('category'),
                'frequency': item.get('frequency', 0),
                'last_7_days_freq': item.get('last_7_days_freq', 0),
                'avg_confidence_when_present': AnalyticsResponseHelper.safe_round(
                    item.get('avg_confidence_when_present'),
                    3
                ),
                'trend_ratio': AnalyticsResponseHelper.safe_round(item.get('trend_ratio'), 3)
            })

        response_data = {
            'productive_keywords': productive_keywords,
            'unproductive_keywords': unproductive_keywords,
            'trending_keywords': trending_keywords,
            'period': f'{days} days'
        }

        return AnalyticsResponseHelper.create_success_response(response_data)


class PerformanceMetricsView(View):
    """
    Endpoint para métricas de performance do sistema
    GET /analytics/dashboard/performance/
    """
    
    @with_error_handling('performance_metrics')
    def get(self, request):
        """Retorna métricas de performance e saúde do sistema"""

        days, date_from = AnalyticsRequestHelper.get_date_filter(request, default_days=30)
        perf_stats = AnalyticsQueryBuilder.get_performance_stats(date_from)
        distribution = AnalyticsQueryBuilder.get_performance_distribution(date_from)

        avg_processing_time = AnalyticsResponseHelper.safe_round(
            perf_stats.get('avg_processing_time'),
            2
        )

        system_health = {
            'status': 'healthy',
            'avg_processing_time': avg_processing_time,
            'confidence_above_70': perf_stats.get('confidence_above_70', 0),
            'total_processed_today': perf_stats.get('total_processed_today', 0),
        }

        if avg_processing_time > 5000:
            system_health['status'] = 'unhealthy'
        elif avg_processing_time > 3000:
            system_health['status'] = 'degraded'

        response_data = {
            'avg_processing_time': avg_processing_time,
            'total_processed': perf_stats.get('total_processed', 0),
            'avg_confidence': AnalyticsResponseHelper.safe_round(perf_stats.get('avg_confidence'), 3),
            'processing_distribution': distribution.get('processing_distribution', []),
            'confidence_distribution': distribution.get('confidence_distribution', []),
            'system_health': system_health,
            'period': f'{days} days'
        }

        return AnalyticsResponseHelper.create_success_response(response_data)


class EmailAnalyticsListView(View):
    """
    Endpoint para listar emails processados
    GET /analytics/emails/
    """
    
    @with_error_handling('email_analytics_list')
    def get(self, request):
        """Lista emails com paginação e filtros"""

        category = request.GET.get('category')
        days, date_from = AnalyticsRequestHelper.get_date_filter(request, default_days=30)
        page, per_page = AnalyticsRequestHelper.get_pagination_params(request, default_page=1, default_per_page=50)

        queryset = AnalyticsQueryBuilder.get_emails_in_period(date_from)
        if category:
            queryset = queryset.filter(category=category)

        queryset = queryset.order_by('-processed_at')
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        emails = []
        for email in page_obj:
            emails.append({
                'id': str(email.id),
                'sender_email': email.sender_email,
                'sender_domain': email.sender_domain,
                'category': email.category,
                'subcategory': email.subcategory,
                'tone': email.tone,
                'urgency': email.urgency,
                'confidence_score': AnalyticsResponseHelper.safe_round(email.confidence_score, 3),
                'processed_at': email.processed_at.isoformat() if email.processed_at else None,
                'keywords_detected': (email.keywords_detected or [])[:5],
                'has_attachments': email.has_attachments,
            })

        response_data = {
            'emails': emails,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'filters': {
                'category': category,
                'days': days
            }
        }

        return AnalyticsResponseHelper.create_success_response(response_data)


# Instância global do service para reutilização
_analytics_service = AnalyticsService()


def save_email_analytics(classification_result, processing_time=0, source='single', request_data=None):
    """
    Salva dados de analytics após classificação - Refatorado
    Deve ser chamada pelo classifier
    
    Args:
        classification_result: Resultado da classificação
        processing_time: Tempo em ms
        source: Origem ('single', 'batch', 'api') 
        request_data: Dados do request (opcional)
    
    Returns:
        analytics_instance ou None se falhar
    """
    try:
        analytics, success, errors = _analytics_service.save_email_analytics(
            classification_result=classification_result,
            processing_time=processing_time,
            source=source,
            request_data=request_data
        )
        
        if success:
            return analytics
        else:
            # Loga erros mas não quebra o fluxo principal
            print(f"Warning: Falha ao salvar analytics: {errors}")
            return None
            
    except Exception as e:
        print(f"Erro crítico ao salvar analytics: {e}")
        return None


# NOTA: Função update_aggregated_stats foi movida para AnalyticsAggregator 
# no arquivo utils/services.py para melhor organização e reutilização.
