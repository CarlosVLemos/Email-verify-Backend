"""
Views para Analytics API - Refatorado com utilitários
Endpoints para alimentar dashboards e visualizações
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import (
    EmailAnalytics, CategoryStats, SenderStats, 
    KeywordFrequency, TimeSeriesData
)

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
    
    def get(self, request):
        """Retorna distribuição de categorias para gráfico de pizza"""
        
        days = int(request.GET.get('days', 30))
        if days >= 30:
            categories = CategoryStats.objects.filter(last_30_days__gt=0).order_by('-total_count')
        else:
            categories = CategoryStats.objects.filter(last_7_days__gt=0).order_by('-total_count')
        
        distribution_data = []
        total_emails = 0
        
        for cat in categories:
            count = cat.last_30_days if days >= 30 else cat.last_7_days
            total_emails += count
            
            distribution_data.append({
                'category': cat.category,
                'subcategory': cat.subcategory,
                'count': count,
                'avg_confidence': cat.avg_confidence,
                'trend_direction': cat.trend_direction,
                'trend_percentage': cat.trend_percentage,
            })
        for item in distribution_data:
            item['percentage'] = round((item['count'] / max(total_emails, 1)) * 100, 2)
        
        return JsonResponse({
            'categories': distribution_data,
            'total_emails': total_emails,
            'period': f'{days} days',
            'status': 'success'
        })


class SenderAnalysisView(View):
    """
    Endpoint para análise de remetentes
    GET /analytics/dashboard/senders/
    """
    
    def get(self, request):
        """Retorna análise de produtividade por remetente"""
        
        limit = int(request.GET.get('limit', 20))
        min_emails = int(request.GET.get('min_emails', 3))
        top_productive = list(SenderStats.objects.filter(
            total_count__gte=min_emails,
            productivity_rate__gt=0
        ).order_by('-productivity_rate', '-total_count')[:limit].values(
            'sender_identifier', 'sender_type', 'productivity_rate',
            'total_count', 'productive_count', 'unproductive_count'
        ))
        top_unproductive = list(SenderStats.objects.filter(
            total_count__gte=min_emails,
            productivity_rate__lt=100
        ).order_by('productivity_rate', '-total_count')[:limit].values(
            'sender_identifier', 'sender_type', 'productivity_rate',
            'total_count', 'productive_count', 'unproductive_count'
        ))
        domains_summary = list(SenderStats.objects.filter(
            sender_type='domain',
            total_count__gte=min_emails
        ).values('sender_identifier').annotate(
            total_emails=Sum('total_count'),
            avg_productivity=Avg('productivity_rate')
        ).order_by('-total_emails')[:15])
        
        return JsonResponse({
            'top_productive': top_productive,
            'top_unproductive': top_unproductive,
            'domains_summary': domains_summary,
            'filters': {
                'limit': limit,
                'min_emails': min_emails
            },
            'status': 'success'
        })


class KeywordInsightsView(View):
    """
    Endpoint para insights de palavras-chave
    GET /analytics/dashboard/keywords/
    """
    
    def get(self, request):
        """Retorna análise de palavras-chave mais frequentes"""
        
        limit = int(request.GET.get('limit', 20))
        days = int(request.GET.get('days', 30))
        
        freq_field = 'last_30_days_freq' if days >= 30 else 'last_7_days_freq'
        productive_keywords = list(KeywordFrequency.objects.filter(
            category='Produtivo'
        ).order_by('-frequency')[:limit].values(
            'keyword', 'frequency', 'avg_confidence_when_present',
            'last_7_days_freq', 'last_30_days_freq'
        ))
        unproductive_keywords = list(KeywordFrequency.objects.filter(
            category='Improdutivo'
        ).order_by('-frequency')[:limit].values(
            'keyword', 'frequency', 'avg_confidence_when_present',
            'last_7_days_freq', 'last_30_days_freq'
        ))
        trending_keywords = list(KeywordFrequency.objects.filter(
            last_7_days_freq__gt=0
        ).extra(
            select={'trend_ratio': 'last_7_days_freq * 7.0 / GREATEST(frequency, 1)'}
        ).order_by('-trend_ratio')[:limit].values(
            'keyword', 'category', 'frequency',
            'last_7_days_freq', 'avg_confidence_when_present'
        ))
        
        return JsonResponse({
            'productive_keywords': productive_keywords,
            'unproductive_keywords': unproductive_keywords,
            'trending_keywords': trending_keywords,
            'period': f'{days} days',
            'status': 'success'
        })


class PerformanceMetricsView(View):
    """
    Endpoint para métricas de performance do sistema
    GET /analytics/dashboard/performance/
    """
    
    def get(self, request):
        """Retorna métricas de performance e saúde do sistema"""
        
        days = int(request.GET.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        perf_stats = EmailAnalytics.objects.filter(
            processed_at__gte=date_from
        ).aggregate(
            avg_processing_time=Avg('processing_time_ms'),
            total_processed=Count('id'),
            avg_confidence=Avg('confidence_score'),
        )
        processing_ranges = [
            (0, 100, '< 100ms'),
            (100, 500, '100-500ms'),
            (500, 1000, '500ms-1s'),
            (1000, 5000, '1-5s'),
            (5000, float('inf'), '> 5s')
        ]
        
        processing_distribution = []
        for min_time, max_time, label in processing_ranges:
            count = EmailAnalytics.objects.filter(
                processed_at__gte=date_from,
                processing_time_ms__gte=min_time,
                processing_time_ms__lt=max_time
            ).count()
            
            processing_distribution.append({
                'range': label,
                'count': count,
                'percentage': round((count / max(perf_stats['total_processed'], 1)) * 100, 2)
            })
        confidence_ranges = [
            (0.0, 0.5, 'Baixa (< 50%)'),
            (0.5, 0.7, 'Média (50-70%)'),
            (0.7, 0.9, 'Alta (70-90%)'),
            (0.9, 1.0, 'Muito Alta (> 90%)')
        ]
        
        confidence_distribution = []
        for min_conf, max_conf, label in confidence_ranges:
            count = EmailAnalytics.objects.filter(
                processed_at__gte=date_from,
                confidence_score__gte=min_conf,
                confidence_score__lt=max_conf
            ).count()
            
            confidence_distribution.append({
                'range': label,
                'count': count,
                'percentage': round((count / max(perf_stats['total_processed'], 1)) * 100, 2)
            })
        system_health = {
            'status': 'healthy',
            'avg_processing_time': perf_stats['avg_processing_time'] or 0,
            'confidence_above_70': EmailAnalytics.objects.filter(
                processed_at__gte=date_from,
                confidence_score__gte=0.7
            ).count(),
            'total_processed_today': EmailAnalytics.objects.filter(
                processed_at__date=timezone.now().date()
            ).count(),
        }
        avg_time = perf_stats['avg_processing_time'] or 0
        if avg_time > 3000:
            system_health['status'] = 'degraded'
        elif avg_time > 5000:
            system_health['status'] = 'unhealthy'
        
        return JsonResponse({
            'avg_processing_time': round(perf_stats['avg_processing_time'] or 0, 2),
            'total_processed': perf_stats['total_processed'],
            'processing_distribution': processing_distribution,
            'confidence_distribution': confidence_distribution,
            'system_health': system_health,
            'period': f'{days} days',
            'status': 'success'
        })


class EmailAnalyticsListView(View):
    """
    Endpoint para listar emails processados
    GET /analytics/emails/
    """
    
    def get(self, request):
        """Lista emails com paginação e filtros"""

        category = request.GET.get('category')
        days = int(request.GET.get('days', 30))
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)  # Máximo 100
        
        date_from = timezone.now() - timedelta(days=days)
        queryset = EmailAnalytics.objects.filter(
            processed_at__gte=date_from
        )
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
                'confidence_score': email.confidence_score,
                'processed_at': email.processed_at.isoformat(),
                'keywords_detected': email.keywords_detected[:5],  # Primeiras 5
                'has_attachments': email.has_attachments,
            })
        
        return JsonResponse({
            'emails': emails,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'filters': {
                'category': category,
                'days': days
            },
            'status': 'success'
        })


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
