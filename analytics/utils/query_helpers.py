"""
Query helpers para Analytics
Centraliza queries comuns e otimizações de performance
"""
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsQueryBuilder:
    """Builder para queries comuns de analytics"""
    
    @staticmethod
    def get_emails_in_period(date_from, base_queryset=None):
        """
        Retorna queryset de emails no período especificado
        """
        from analytics.models import EmailAnalytics
        
        if base_queryset is None:
            base_queryset = EmailAnalytics.objects.all()
        
        return base_queryset.filter(processed_at__gte=date_from)
    
    @staticmethod
    def get_productivity_stats(date_from):
        """
        Calcula estatísticas básicas de produtividade
        Returns: dict com métricas agregadas
        """
        from analytics.models import EmailAnalytics
        
        try:
            stats = EmailAnalytics.objects.filter(
                processed_at__gte=date_from
            ).aggregate(
                total_count=Count('id'),
                productive=Count('id', filter=Q(category='Produtivo')),
                unproductive=Count('id', filter=Q(category='Improdutivo')),
                avg_confidence=Avg('confidence_score'),
                avg_processing_time=Avg('processing_time_ms'),
                avg_word_count=Avg('word_count'),
                emails_with_attachments=Count('id', filter=Q(has_attachments=True))
            )
            
            # Calcula métricas derivadas
            total = stats['total_count'] or 0
            productive = stats['productive'] or 0
            unproductive = stats['unproductive'] or 0
            
            stats['productivity_rate'] = (productive / max(total, 1)) * 100 if total > 0 else 0
            stats['attachment_rate'] = (stats['emails_with_attachments'] / max(total, 1)) * 100 if total > 0 else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating productivity stats: {e}")
            return {
                'total_count': 0,
                'productive': 0,
                'unproductive': 0,
                'productivity_rate': 0,
                'avg_confidence': 0,
                'avg_processing_time': 0,
                'avg_word_count': 0,
                'attachment_rate': 0
            }
    
    @staticmethod
    def get_top_categories(period_field='last_30_days', limit=10):
        """
        Retorna top categorias por período
        """
        from analytics.models import CategoryStats
        
        try:
            return CategoryStats.objects.filter(
                **{f'{period_field}__gt': 0}
            ).order_by(f'-{period_field}').values(
                'category', 'subcategory', 'total_count',
                period_field, 'trend_direction', 'avg_confidence'
            )[:limit]
        except Exception as e:
            logger.error(f"Error getting top categories: {e}")
            return []
    
    @staticmethod
    def get_top_senders(min_emails=5, limit=20, order_by='productivity_rate'):
        """
        Retorna top remetentes por critério especificado
        """
        from analytics.models import SenderStats
        
        try:
            return SenderStats.objects.filter(
                total_count__gte=min_emails
            ).order_by(f'-{order_by}').values(
                'sender_identifier', 'sender_type', 'productivity_rate',
                'total_count', 'productive_count', 'unproductive_count',
                'first_seen', 'last_seen'
            )[:limit]
        except Exception as e:
            logger.error(f"Error getting top senders: {e}")
            return []
    
    @staticmethod
    def get_timeline_data(date_from, granularity='daily'):
        """
        Retorna dados de série temporal para gráficos
        """
        from analytics.models import TimeSeriesData
        
        try:
            return TimeSeriesData.objects.filter(
                date__gte=date_from.date(),
                granularity=granularity
            ).order_by('date', 'hour').values(
                'date', 'hour', 'total_emails', 'productive_emails',
                'unproductive_emails', 'productivity_rate', 'avg_confidence'
            )
        except Exception as e:
            logger.error(f"Error getting timeline data: {e}")
            return []
    
    @staticmethod
    def get_keyword_insights(category, limit=20, period_field='frequency'):
        """
        Retorna insights de palavras-chave por categoria
        """
        from analytics.models import KeywordFrequency
        
        try:
            return KeywordFrequency.objects.filter(
                category=category
            ).order_by(f'-{period_field}').values(
                'keyword', 'frequency', 'last_7_days_freq',
                'last_30_days_freq', 'avg_confidence_when_present'
            )[:limit]
        except Exception as e:
            logger.error(f"Error getting keyword insights: {e}")
            return []
    
    @staticmethod
    def get_domains_summary(min_emails=5, limit=15):
        """
        Retorna resumo agregado por domínios
        """
        from analytics.models import SenderStats
        
        try:
            return SenderStats.objects.filter(
                sender_type='domain',
                total_count__gte=min_emails
            ).values('sender_identifier').annotate(
                total_emails=Sum('total_count'),
                avg_productivity=Avg('productivity_rate'),
                total_productive=Sum('productive_count'),
                total_unproductive=Sum('unproductive_count')
            ).order_by('-total_emails')[:limit]
        except Exception as e:
            logger.error(f"Error getting domains summary: {e}")
            return []
    
    @staticmethod
    def get_performance_distribution(date_from):
        """
        Calcula distribuição de performance (tempo de processamento e confiança)
        """
        from analytics.models import EmailAnalytics
        
        try:
            # Ranges de tempo de processamento
            processing_ranges = [
                (0, 100, '< 100ms'),
                (100, 500, '100-500ms'),
                (500, 1000, '500ms-1s'),
                (1000, 5000, '1-5s'),
                (5000, float('inf'), '> 5s')
            ]
            
            # Ranges de confiança
            confidence_ranges = [
                (0.0, 0.5, 'Baixa (< 50%)'),
                (0.5, 0.7, 'Média (50-70%)'),
                (0.7, 0.9, 'Alta (70-90%)'),
                (0.9, 1.0, 'Muito Alta (> 90%)')
            ]
            
            base_queryset = EmailAnalytics.objects.filter(processed_at__gte=date_from)
            total_emails = base_queryset.count()
            
            # Calcula distribuições
            processing_dist = []
            for min_time, max_time, label in processing_ranges:
                if max_time == float('inf'):
                    count = base_queryset.filter(processing_time_ms__gte=min_time).count()
                else:
                    count = base_queryset.filter(
                        processing_time_ms__gte=min_time,
                        processing_time_ms__lt=max_time
                    ).count()
                
                percentage = (count / max(total_emails, 1)) * 100
                processing_dist.append({
                    'range': label,
                    'count': count,
                    'percentage': round(percentage, 2)
                })
            
            confidence_dist = []
            for min_conf, max_conf, label in confidence_ranges:
                count = base_queryset.filter(
                    confidence_score__gte=min_conf,
                    confidence_score__lt=max_conf
                ).count()
                
                percentage = (count / max(total_emails, 1)) * 100
                confidence_dist.append({
                    'range': label,
                    'count': count,
                    'percentage': round(percentage, 2)
                })
            
            return {
                'processing_distribution': processing_dist,
                'confidence_distribution': confidence_dist,
                'total_emails': total_emails
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance distribution: {e}")
            return {
                'processing_distribution': [],
                'confidence_distribution': [],
                'total_emails': 0
            }


class AnalyticsFormatter:
    """Formatadores para dados de analytics"""
    
    @staticmethod
    def format_timeline_label(date, hour, granularity):
        """
        Formata label para timeline baseado na granularidade
        """
        try:
            if granularity == 'hourly':
                return f"{date.strftime('%d/%m')} {hour:02d}h"
            return date.strftime('%d/%m/%Y')
        except Exception as e:
            logger.warning(f"Error formatting timeline label: {e}")
            return str(date)
    
    @staticmethod
    def calculate_trend_analysis(timeline_data):
        """
        Calcula análise de tendência baseada nos dados de timeline
        """
        try:
            if len(timeline_data) < 2:
                return {
                    'total_change': 0,
                    'trend_direction': 'stable',
                    'best_period': {},
                    'worst_period': {}
                }
            
            # Compara primeiro e último período
            first_rate = timeline_data[0].get('productivity_rate', 0)
            last_rate = timeline_data[-1].get('productivity_rate', 0)
            total_change = last_rate - first_rate
            
            # Determina direção da tendência
            if total_change > 2:
                trend_direction = 'increasing'
            elif total_change < -2:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
            
            # Encontra melhor e pior período
            best_period = max(timeline_data, key=lambda x: x.get('productivity_rate', 0))
            worst_period = min(timeline_data, key=lambda x: x.get('productivity_rate', 0))
            
            return {
                'total_change': round(total_change, 2),
                'trend_direction': trend_direction,
                'best_period': best_period,
                'worst_period': worst_period
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend analysis: {e}")
            return {
                'total_change': 0,
                'trend_direction': 'stable',
                'best_period': {},
                'worst_period': {}
            }