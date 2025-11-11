"""
Serializers para a API de Analytics
Transforma dados dos models em JSON para o dashboard
"""
try:
    from rest_framework import serializers
    HAS_DRF = True
except ImportError:
    from django.forms import ModelForm
    HAS_DRF = False

from django.db import models
from .models import (
    EmailAnalytics, CategoryStats, SenderStats, 
    KeywordFrequency, TimeSeriesData
)


class EmailAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer completo para EmailAnalytics"""
    
    class Meta:
        model = EmailAnalytics
        fields = [
            'id', 'sender_email', 'sender_name', 'sender_domain',
            'category', 'subcategory', 'tone', 'urgency', 'confidence_score',
            'word_count', 'char_count', 'has_attachments', 'attachment_score',
            'keywords_detected', 'processing_time_ms', 'processed_at',
            'email_date', 'source', 'technical_data'
        ]
        read_only_fields = ['id', 'processed_at']


class EmailAnalyticsSummarySerializer(serializers.ModelSerializer):
    """Serializer resumido para listas e dashboards"""
    
    class Meta:
        model = EmailAnalytics
        fields = [
            'id', 'category', 'subcategory', 'tone', 'urgency',
            'confidence_score', 'processed_at', 'sender_domain'
        ]


class CategoryStatsSerializer(serializers.ModelSerializer):
    """Serializer para estatísticas de categoria"""
    
    percentage_of_total = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoryStats
        fields = [
            'category', 'subcategory', 'total_count', 'last_7_days',
            'last_30_days', 'avg_confidence', 'avg_processing_time',
            'trend_direction', 'trend_percentage', 'percentage_of_total',
            'updated_at'
        ]
    
    def get_percentage_of_total(self, obj):
        """Calcula percentual do total geral"""
        total_all = CategoryStats.objects.aggregate(
            total=models.Sum('total_count')
        )['total'] or 1
        return round((obj.total_count / total_all) * 100, 2)


class SenderStatsSerializer(serializers.ModelSerializer):
    """Serializer para estatísticas de remetente"""
    
    class Meta:
        model = SenderStats
        fields = [
            'sender_identifier', 'sender_type', 'productive_count',
            'unproductive_count', 'total_count', 'productivity_rate',
            'high_urgency_count', 'medium_urgency_count', 'low_urgency_count',
            'positive_tone_count', 'negative_tone_count', 'neutral_tone_count',
            'first_seen', 'last_seen', 'updated_at'
        ]


class KeywordFrequencySerializer(serializers.ModelSerializer):
    """Serializer para frequência de palavras-chave"""
    
    class Meta:
        model = KeywordFrequency
        fields = [
            'keyword', 'category', 'frequency', 'last_7_days_freq',
            'last_30_days_freq', 'avg_confidence_when_present',
            'contexts', 'first_detected', 'last_updated'
        ]


class TimeSeriesDataSerializer(serializers.ModelSerializer):
    """Serializer para dados de série temporal"""
    
    datetime_label = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSeriesData
        fields = [
            'date', 'hour', 'total_emails', 'productive_emails',
            'unproductive_emails', 'high_urgency', 'medium_urgency',
            'low_urgency', 'positive_tone', 'negative_tone', 'neutral_tone',
            'productivity_rate', 'avg_confidence', 'avg_processing_time',
            'granularity', 'datetime_label'
        ]
    
    def get_datetime_label(self, obj):
        """Gera label formatado para gráficos"""
        if obj.granularity == 'hourly':
            return f"{obj.date.strftime('%d/%m')} {obj.hour:02d}h"
        return obj.date.strftime('%d/%m/%Y')


# Serializers específicos para Dashboard

class DashboardOverviewSerializer(serializers.Serializer):
    """Serializer para visão geral do dashboard"""
    
    total_emails = serializers.IntegerField()
    productive_emails = serializers.IntegerField()
    unproductive_emails = serializers.IntegerField()
    productivity_rate = serializers.FloatField()
    
    avg_confidence = serializers.FloatField()
    avg_processing_time = serializers.FloatField()
    
    top_categories = CategoryStatsSerializer(many=True, read_only=True)
    top_senders = SenderStatsSerializer(many=True, read_only=True)
    
    time_period = serializers.CharField()
    last_updated = serializers.DateTimeField()


class ProductivityTrendSerializer(serializers.Serializer):
    """Serializer para tendência de produtividade"""
    
    timeline = TimeSeriesDataSerializer(many=True, source='data')
    period = serializers.CharField()
    granularity = serializers.CharField()
    
    # Estatísticas do período
    total_change = serializers.FloatField()
    trend_direction = serializers.CharField()
    best_day = serializers.DictField()
    worst_day = serializers.DictField()


class CategoryDistributionSerializer(serializers.Serializer):
    """Serializer para distribuição de categorias (gráfico pizza)"""
    
    categories = CategoryStatsSerializer(many=True)
    total_emails = serializers.IntegerField()
    period = serializers.CharField()


class SenderAnalysisSerializer(serializers.Serializer):
    """Serializer para análise de remetentes"""
    
    top_productive = SenderStatsSerializer(many=True)
    top_unproductive = SenderStatsSerializer(many=True)
    domains_summary = serializers.ListField(child=serializers.DictField())
    period = serializers.CharField()


class KeywordInsightsSerializer(serializers.Serializer):
    """Serializer para insights de palavras-chave"""
    
    productive_keywords = KeywordFrequencySerializer(many=True)
    unproductive_keywords = KeywordFrequencySerializer(many=True)
    trending_keywords = KeywordFrequencySerializer(many=True)
    period = serializers.CharField()


class PerformanceMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de performance do sistema"""
    
    avg_processing_time = serializers.FloatField()
    total_processed = serializers.IntegerField()
    processing_distribution = serializers.ListField(child=serializers.DictField())
    confidence_distribution = serializers.ListField(child=serializers.DictField())
    
    system_health = serializers.DictField()
    period = serializers.CharField()