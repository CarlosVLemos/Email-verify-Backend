"""
Admin para Analytics
Interface administrativa para visualizar dados de analytics
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    EmailAnalytics, CategoryStats, SenderStats,
    KeywordFrequency, TimeSeriesData
)


@admin.register(EmailAnalytics)
class EmailAnalyticsAdmin(admin.ModelAdmin):
    """Admin para EmailAnalytics com filtros e busca"""
    
    list_display = [
        'id', 'category', 'subcategory', 'sender_domain_display', 
        'confidence_score_display', 'urgency', 'tone', 'processed_at_display'
    ]
    list_filter = [
        'category', 'subcategory', 'urgency', 'tone', 
        'has_attachments', 'source', 'processed_at'
    ]
    search_fields = [
        'sender_email', 'sender_domain', 'keywords_detected'
    ]
    readonly_fields = [
        'id', 'processed_at', 'processing_time_ms'
    ]
    date_hierarchy = 'processed_at'
    ordering = ['-processed_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'processed_at', 'source')
        }),
        ('Remetente', {
            'fields': ('sender_email', 'sender_name', 'sender_domain')
        }),
        ('Classificação', {
            'fields': (
                'category', 'subcategory', 'tone', 'urgency', 
                'confidence_score', 'keywords_detected'
            )
        }),
        ('Conteúdo', {
            'fields': (
                'word_count', 'char_count', 'has_attachments', 
                'attachment_score'
            )
        }),
        ('Performance', {
            'fields': ('processing_time_ms',)
        }),
        ('Dados Técnicos', {
            'fields': ('technical_data',),
            'classes': ('collapse',)
        }),
    )
    
    def sender_domain_display(self, obj):
        """Exibe domínio com cor baseada na produtividade"""
        if not obj.sender_domain:
            return '-'
        
        color = '#28a745' if obj.category == 'Produtivo' else '#dc3545'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.sender_domain
        )
    sender_domain_display.short_description = 'Domínio'
    
    def confidence_score_display(self, obj):
        """Exibe score de confiança com barra de progresso"""
        percentage = int(obj.confidence_score * 100)
        color = '#28a745' if percentage >= 70 else '#ffc107' if percentage >= 50 else '#dc3545'
        
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 4px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 4px; '
            'text-align: center; color: white; font-size: 12px; line-height: 20px;">{:.1f}%</div></div>',
            percentage, color, obj.confidence_score * 100
        )
    confidence_score_display.short_description = 'Confiança'
    
    def processed_at_display(self, obj):
        """Formata data de processamento"""
        return obj.processed_at.strftime('%d/%m/%Y %H:%M')
    processed_at_display.short_description = 'Processado em'


@admin.register(CategoryStats)
class CategoryStatsAdmin(admin.ModelAdmin):
    """Admin para CategoryStats"""
    
    list_display = [
        'category', 'subcategory', 'total_count', 'last_7_days',
        'last_30_days', 'avg_confidence_display', 'trend_display', 'updated_at'
    ]
    list_filter = ['category', 'trend_direction']
    search_fields = ['category', 'subcategory']
    readonly_fields = ['updated_at']
    ordering = ['-total_count']
    
    def avg_confidence_display(self, obj):
        """Exibe confiança média formatada"""
        return f"{obj.avg_confidence:.1f}%"
    avg_confidence_display.short_description = 'Confiança Média'
    
    def trend_display(self, obj):
        """Exibe tendência com ícone"""
        icons = {
            'increasing': '📈',
            'decreasing': '📉',
            'stable': '➡️'
        }
        icon = icons.get(obj.trend_direction, '❓')
        return f"{icon} {obj.trend_percentage:+.1f}%"
    trend_display.short_description = 'Tendência'


@admin.register(SenderStats)
class SenderStatsAdmin(admin.ModelAdmin):
    """Admin para SenderStats"""
    
    list_display = [
        'sender_identifier', 'sender_type', 'total_count',
        'productivity_rate_display', 'urgency_summary', 'last_seen'
    ]
    list_filter = ['sender_type', 'productivity_rate']
    search_fields = ['sender_identifier']
    readonly_fields = ['first_seen', 'last_seen', 'updated_at']
    ordering = ['-productivity_rate', '-total_count']
    
    def productivity_rate_display(self, obj):
        """Exibe taxa de produtividade com cor"""
        rate = obj.productivity_rate
        if rate >= 70:
            color = '#28a745'
        elif rate >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    productivity_rate_display.short_description = 'Produtividade'
    
    def urgency_summary(self, obj):
        """Resumo de urgência"""
        total = obj.high_urgency_count + obj.medium_urgency_count + obj.low_urgency_count
        if total == 0:
            return '-'
        
        high_pct = (obj.high_urgency_count / total) * 100
        return f"🔴{obj.high_urgency_count} 🟡{obj.medium_urgency_count} 🟢{obj.low_urgency_count}"
    urgency_summary.short_description = 'Urgência (🔴🟡🟢)'


@admin.register(KeywordFrequency)
class KeywordFrequencyAdmin(admin.ModelAdmin):
    """Admin para KeywordFrequency"""
    
    list_display = [
        'keyword', 'category', 'frequency', 'last_7_days_freq',
        'avg_confidence_when_present', 'trend_indicator'
    ]
    list_filter = ['category']
    search_fields = ['keyword']
    readonly_fields = ['first_detected', 'last_updated']
    ordering = ['-frequency']
    
    def trend_indicator(self, obj):
        """Indica se a palavra está em alta"""
        if obj.last_7_days_freq > 0:
            trend_ratio = (obj.last_7_days_freq * 7) / max(obj.frequency, 1)
            if trend_ratio > 1.5:
                return "📈 Alta"
            elif trend_ratio > 0.8:
                return "➡️ Estável"
            else:
                return "📉 Baixa"
        return "💤 Inativa"
    trend_indicator.short_description = 'Tendência'


@admin.register(TimeSeriesData)
class TimeSeriesDataAdmin(admin.ModelAdmin):
    """Admin para TimeSeriesData"""
    
    list_display = [
        'date_time_display', 'total_emails', 'productivity_rate_display',
        'avg_confidence', 'granularity'
    ]
    list_filter = ['granularity', 'date']
    date_hierarchy = 'date'
    ordering = ['-date', '-hour']
    
    def date_time_display(self, obj):
        """Formata data/hora baseado na granularidade"""
        if obj.granularity == 'hourly':
            return f"{obj.date.strftime('%d/%m/%Y')} {obj.hour:02d}:00"
        return obj.date.strftime('%d/%m/%Y')
    date_time_display.short_description = 'Data/Hora'
    
    def productivity_rate_display(self, obj):
        """Exibe taxa de produtividade formatada"""
        return f"{obj.productivity_rate:.1f}%"
    productivity_rate_display.short_description = 'Produtividade'


admin.site.site_header = "Analytics - Dashboard de Email Intelligence"
admin.site.site_title = "Analytics Admin"
admin.site.index_title = "Painel de Analytics"
