"""
Views para Analytics API
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


class DashboardOverviewView(View):
    """
    Endpoint principal do dashboard
    GET /analytics/dashboard/overview/
    """
    
    def get(self, request):
        """Retorna visão geral das métricas"""
        
        # Parâmetros de filtro
        days = int(request.GET.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Métricas gerais
        total_emails = EmailAnalytics.objects.filter(processed_at__gte=date_from).count()
        
        productivity_stats = EmailAnalytics.objects.filter(
            processed_at__gte=date_from
        ).aggregate(
            productive=Count('id', filter=Q(category='Produtivo')),
            unproductive=Count('id', filter=Q(category='Improdutivo')),
            avg_confidence=Avg('confidence_score'),
            avg_processing_time=Avg('processing_time_ms')
        )
        
        productive_emails = productivity_stats['productive'] or 0
        unproductive_emails = productivity_stats['unproductive'] or 0
        productivity_rate = (productive_emails / max(total_emails, 1)) * 100
        
        # Top categorias
        top_categories = list(CategoryStats.objects.filter(
            last_30_days__gt=0
        ).order_by('-last_30_days')[:5].values(
            'category', 'subcategory', 'total_count', 
            'last_30_days', 'trend_direction'
        ))
        
        # Top remetentes produtivos
        top_senders = list(SenderStats.objects.filter(
            total_count__gte=5
        ).order_by('-productivity_rate')[:10].values(
            'sender_identifier', 'sender_type', 'productivity_rate',
            'total_count', 'productive_count'
        ))
        
        return JsonResponse({
            'overview': {
                'total_emails': total_emails,
                'productive_emails': productive_emails,
                'unproductive_emails': unproductive_emails,
                'productivity_rate': round(productivity_rate, 2),
                'avg_confidence': round(productivity_stats['avg_confidence'] or 0, 3),
                'avg_processing_time': round(productivity_stats['avg_processing_time'] or 0, 2),
                'period_days': days,
                'last_updated': timezone.now().isoformat(),
            },
            'top_categories': top_categories,
            'top_senders': top_senders,
            'status': 'success'
        })


class ProductivityTrendView(View):
    """
    Endpoint para dados de tendência de produtividade
    GET /analytics/dashboard/trends/
    """
    
    def get(self, request):
        """Retorna dados de série temporal"""
        
        # Parâmetros
        days = int(request.GET.get('days', 30))
        granularity = request.GET.get('granularity', 'daily')
        
        date_from = timezone.now() - timedelta(days=days)
        
        # Busca dados de série temporal
        queryset = TimeSeriesData.objects.filter(
            date__gte=date_from.date(),
            granularity=granularity
        ).order_by('date', 'hour')
        
        timeline_data = []
        for item in queryset:
            timeline_data.append({
                'date': item.date.isoformat(),
                'hour': item.hour if granularity == 'hourly' else 0,
                'total_emails': item.total_emails,
                'productive_emails': item.productive_emails,
                'unproductive_emails': item.unproductive_emails,
                'productivity_rate': item.productivity_rate,
                'avg_confidence': item.avg_confidence,
                'label': self._format_timeline_label(item, granularity)
            })
        
        # Calcula tendência
        if len(timeline_data) >= 2:
            first_rate = timeline_data[0]['productivity_rate']
            last_rate = timeline_data[-1]['productivity_rate']
            total_change = last_rate - first_rate
            trend_direction = 'increasing' if total_change > 0 else 'decreasing' if total_change < 0 else 'stable'
        else:
            total_change = 0
            trend_direction = 'stable'
        
        # Melhor e pior dia
        best_day = max(timeline_data, key=lambda x: x['productivity_rate']) if timeline_data else {}
        worst_day = min(timeline_data, key=lambda x: x['productivity_rate']) if timeline_data else {}
        
        return JsonResponse({
            'timeline': timeline_data,
            'period': f'{days} days',
            'granularity': granularity,
            'trend_analysis': {
                'total_change': round(total_change, 2),
                'trend_direction': trend_direction,
                'best_day': best_day,
                'worst_day': worst_day,
            },
            'status': 'success'
        })
    
    def _format_timeline_label(self, item, granularity):
        """Formata label para o timeline"""
        if granularity == 'hourly':
            return f"{item.date.strftime('%d/%m')} {item.hour:02d}h"
        return item.date.strftime('%d/%m/%Y')


class CategoryDistributionView(View):
    """
    Endpoint para distribuição de categorias
    GET /analytics/dashboard/categories/
    """
    
    def get(self, request):
        """Retorna distribuição de categorias para gráfico de pizza"""
        
        days = int(request.GET.get('days', 30))
        
        # Busca estatísticas de categoria
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
        
        # Calcula percentuais
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
        
        # Top produtivos
        top_productive = list(SenderStats.objects.filter(
            total_count__gte=min_emails,
            productivity_rate__gt=0
        ).order_by('-productivity_rate', '-total_count')[:limit].values(
            'sender_identifier', 'sender_type', 'productivity_rate',
            'total_count', 'productive_count', 'unproductive_count'
        ))
        
        # Top improdutivos
        top_unproductive = list(SenderStats.objects.filter(
            total_count__gte=min_emails,
            productivity_rate__lt=100
        ).order_by('productivity_rate', '-total_count')[:limit].values(
            'sender_identifier', 'sender_type', 'productivity_rate',
            'total_count', 'productive_count', 'unproductive_count'
        ))
        
        # Resumo por domínios
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
        
        # Keywords produtivas
        productive_keywords = list(KeywordFrequency.objects.filter(
            category='Produtivo'
        ).order_by('-frequency')[:limit].values(
            'keyword', 'frequency', 'avg_confidence_when_present',
            'last_7_days_freq', 'last_30_days_freq'
        ))
        
        # Keywords improdutivas
        unproductive_keywords = list(KeywordFrequency.objects.filter(
            category='Improdutivo'
        ).order_by('-frequency')[:limit].values(
            'keyword', 'frequency', 'avg_confidence_when_present',
            'last_7_days_freq', 'last_30_days_freq'
        ))
        
        # Keywords em trending (crescimento recente)
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
        
        # Métricas gerais de performance
        perf_stats = EmailAnalytics.objects.filter(
            processed_at__gte=date_from
        ).aggregate(
            avg_processing_time=Avg('processing_time_ms'),
            total_processed=Count('id'),
            avg_confidence=Avg('confidence_score'),
        )
        
        # Distribuição de tempos de processamento
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
        
        # Distribuição de confiança
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
        
        # Saúde do sistema
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
        
        # Define status da saúde
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
        
        # Filtros
        category = request.GET.get('category')
        days = int(request.GET.get('days', 30))
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)  # Máximo 100
        
        date_from = timezone.now() - timedelta(days=days)
        
        # Query base
        queryset = EmailAnalytics.objects.filter(
            processed_at__gte=date_from
        )
        
        if category:
            queryset = queryset.filter(category=category)
        
        # Ordenação
        queryset = queryset.order_by('-processed_at')
        
        # Paginação
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialização manual
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


# Função auxiliar para salvar analytics
def save_email_analytics(classification_result, processing_time=0, source='single'):
    """
    Salva dados de analytics após classificação
    Deve ser chamada pelo classifier
    """
    try:
        analytics = EmailAnalytics.objects.create(
            sender_email=classification_result.get('sender_email'),
            sender_name=classification_result.get('sender_name'),
            sender_domain=classification_result.get('sender_domain'),
            category=classification_result.get('category'),
            subcategory=classification_result.get('subcategory'),
            tone=classification_result.get('tone'),
            urgency=classification_result.get('urgency'),
            confidence_score=classification_result.get('confidence_score', 0.0),
            word_count=classification_result.get('word_count', 0),
            char_count=classification_result.get('char_count', 0),
            has_attachments=classification_result.get('has_attachments', False),
            attachment_score=classification_result.get('attachment_score', 0),
            keywords_detected=classification_result.get('keywords_detected', []),
            processing_time_ms=processing_time,
            source=source,
            technical_data=classification_result.get('technical_data', {})
        )
        
        # Atualiza estatísticas agregadas
        update_aggregated_stats(analytics)
        
        return analytics
        
    except Exception as e:
        print(f"Erro ao salvar analytics: {e}")
        return None


def update_aggregated_stats(email_analytics):
    """
    Atualiza estatísticas agregadas após novo email
    """
    try:
        # Atualiza CategoryStats
        cat_stats, created = CategoryStats.objects.get_or_create(
            category=email_analytics.category,
            subcategory=email_analytics.subcategory,
            defaults={
                'total_count': 0,
                'last_7_days': 0,
                'last_30_days': 0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0,
            }
        )
        
        cat_stats.total_count = F('total_count') + 1
        cat_stats.last_7_days = F('last_7_days') + 1
        cat_stats.last_30_days = F('last_30_days') + 1
        cat_stats.save()
        
        # Atualiza SenderStats se houver sender
        if email_analytics.sender_domain:
            sender_stats, created = SenderStats.objects.get_or_create(
                sender_identifier=email_analytics.sender_domain,
                sender_type='domain',
                defaults={
                    'total_count': 0,
                    'productive_count': 0,
                    'unproductive_count': 0,
                    'productivity_rate': 0.0,
                    'first_seen': email_analytics.processed_at,
                    'last_seen': email_analytics.processed_at,
                }
            )
            
            sender_stats.total_count = F('total_count') + 1
            if email_analytics.category == 'Produtivo':
                sender_stats.productive_count = F('productive_count') + 1
            else:
                sender_stats.unproductive_count = F('unproductive_count') + 1
            
            sender_stats.last_seen = email_analytics.processed_at
            sender_stats.save()
            
            # Recalcula taxa de produtividade
            sender_stats.refresh_from_db()
            sender_stats.productivity_rate = (
                sender_stats.productive_count / max(sender_stats.total_count, 1)
            ) * 100
            sender_stats.save()
        
        # Atualiza KeywordFrequency
        for keyword in email_analytics.keywords_detected:
            kw_freq, created = KeywordFrequency.objects.get_or_create(
                keyword=keyword.lower(),
                category=email_analytics.category,
                defaults={
                    'frequency': 0,
                    'last_7_days_freq': 0,
                    'last_30_days_freq': 0,
                    'avg_confidence_when_present': email_analytics.confidence_score,
                }
            )
            
            kw_freq.frequency = F('frequency') + 1
            kw_freq.last_7_days_freq = F('last_7_days_freq') + 1
            kw_freq.last_30_days_freq = F('last_30_days_freq') + 1
            kw_freq.save()
        
        # Atualiza TimeSeriesData
        today = email_analytics.processed_at.date()
        hour = email_analytics.processed_at.hour
        
        # Dados diários
        daily_data, created = TimeSeriesData.objects.get_or_create(
            date=today,
            hour=0,
            granularity='daily',
            defaults={
                'total_emails': 0,
                'productive_emails': 0,
                'unproductive_emails': 0,
            }
        )
        
        daily_data.total_emails = F('total_emails') + 1
        if email_analytics.category == 'Produtivo':
            daily_data.productive_emails = F('productive_emails') + 1
        else:
            daily_data.unproductive_emails = F('unproductive_emails') + 1
        
        daily_data.save()
        
        # Recalcula taxa de produtividade
        daily_data.refresh_from_db()
        daily_data.productivity_rate = (
            daily_data.productive_emails / max(daily_data.total_emails, 1)
        ) * 100
        daily_data.save()
        
    except Exception as e:
        print(f"Erro ao atualizar estatísticas agregadas: {e}")
