"""
Models para Analytics - Dashboard de Email Intelligence
Armazena dados agregados para visualizações e métricas
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class EmailAnalytics(models.Model):
    """
    Modelo principal para armazenar dados de análise de cada email processado
    Permite rastreamento completo e análise de padrões
    """
    
    # Identificação única
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Dados do email
    sender_email = models.EmailField(blank=True, null=True, help_text="Email do remetente")
    sender_name = models.CharField(max_length=200, blank=True, null=True, help_text="Nome do remetente")
    sender_domain = models.CharField(max_length=100, blank=True, null=True, help_text="Domínio do remetente")
    
    # Classificação obtida
    category = models.CharField(max_length=50, help_text="Categoria principal: Produtivo/Improdutivo")
    subcategory = models.CharField(max_length=100, help_text="Subcategoria detalhada")
    tone = models.CharField(max_length=30, help_text="Tom: Positivo/Negativo/Neutro")
    urgency = models.CharField(max_length=30, help_text="Urgência: Alta/Média/Baixa")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Score de confiança da classificação (0-1)"
    )
    
    # Análise de conteúdo
    word_count = models.PositiveIntegerField(help_text="Número de palavras do email")
    char_count = models.PositiveIntegerField(help_text="Número de caracteres")
    has_attachments = models.BooleanField(default=False, help_text="Possui anexos mencionados")
    attachment_score = models.IntegerField(default=0, help_text="Score da análise de anexos")
    
    # Palavras-chave detectadas (JSON array)
    keywords_detected = models.JSONField(
        default=list, 
        help_text="Lista de palavras-chave encontradas no email"
    )
    
    # Métricas temporais
    processing_time_ms = models.PositiveIntegerField(
        default=0, 
        help_text="Tempo de processamento em milissegundos"
    )
    processed_at = models.DateTimeField(default=timezone.now, help_text="Timestamp do processamento")
    email_date = models.DateTimeField(blank=True, null=True, help_text="Data original do email")
    
    # Contexto adicional
    source = models.CharField(
        max_length=50, 
        choices=[
            ('single', 'Processamento Individual'),
            ('batch', 'Processamento em Lote'),
            ('api', 'API Externa'),
        ],
        default='single',
        help_text="Origem do processamento"
    )
    
    # Dados técnicos (JSON flexível)
    technical_data = models.JSONField(
        default=dict,
        help_text="Dados técnicos adicionais (IPs, headers, etc.)"
    )
    
    class Meta:
        verbose_name = "Email Analytics"
        verbose_name_plural = "Email Analytics"
        ordering = ['-processed_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['subcategory']),
            models.Index(fields=['processed_at']),
            models.Index(fields=['sender_domain']),
            models.Index(fields=['urgency']),
        ]
    
    def __str__(self):
        return f"{self.category} - {self.subcategory} ({self.processed_at.strftime('%d/%m/%Y %H:%M')})"


class CategoryStats(models.Model):
    """
    Estatísticas agregadas por categoria
    Atualizado periodicamente para performance do dashboard
    """
    
    category = models.CharField(max_length=50, help_text="Categoria principal")
    subcategory = models.CharField(max_length=100, help_text="Subcategoria")
    
    # Contadores
    total_count = models.PositiveIntegerField(default=0, help_text="Total de emails nesta categoria")
    last_7_days = models.PositiveIntegerField(default=0, help_text="Emails nos últimos 7 dias")
    last_30_days = models.PositiveIntegerField(default=0, help_text="Emails nos últimos 30 dias")
    
    # Métricas
    avg_confidence = models.FloatField(default=0.0, help_text="Confiança média da categoria")
    avg_processing_time = models.FloatField(default=0.0, help_text="Tempo médio de processamento (ms)")
    
    # Tendências
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('increasing', 'Crescendo'),
            ('decreasing', 'Diminuindo'),
            ('stable', 'Estável'),
        ],
        default='stable',
        help_text="Direção da tendência"
    )
    trend_percentage = models.FloatField(default=0.0, help_text="Percentual da mudança")
    
    # Última atualização
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category Statistics"
        verbose_name_plural = "Category Statistics"
        unique_together = ['category', 'subcategory']
        ordering = ['-total_count']
    
    def __str__(self):
        return f"{self.category} > {self.subcategory} ({self.total_count})"


class SenderStats(models.Model):
    """
    Estatísticas por remetente/domínio
    Para análise de produtividade por fonte
    """
    
    sender_identifier = models.CharField(
        max_length=200, 
        help_text="Email ou domínio do remetente"
    )
    sender_type = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email Específico'),
            ('domain', 'Domínio'),
        ],
        help_text="Tipo de identificador"
    )
    
    # Contadores por categoria
    productive_count = models.PositiveIntegerField(default=0)
    unproductive_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    
    # Métricas de produtividade
    productivity_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Taxa de produtividade (%)"
    )
    
    # Urgência
    high_urgency_count = models.PositiveIntegerField(default=0)
    medium_urgency_count = models.PositiveIntegerField(default=0)
    low_urgency_count = models.PositiveIntegerField(default=0)
    
    # Tom
    positive_tone_count = models.PositiveIntegerField(default=0)
    negative_tone_count = models.PositiveIntegerField(default=0)
    neutral_tone_count = models.PositiveIntegerField(default=0)
    
    # Primeira e última interação
    first_seen = models.DateTimeField(help_text="Primeiro email processado")
    last_seen = models.DateTimeField(help_text="Último email processado")
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sender Statistics"
        verbose_name_plural = "Sender Statistics"
        unique_together = ['sender_identifier', 'sender_type']
        ordering = ['-productivity_rate', '-total_count']
    
    def __str__(self):
        return f"{self.sender_identifier} ({self.productivity_rate:.1f}% produtivo)"


class KeywordFrequency(models.Model):
    """
    Frequência de palavras-chave por categoria
    Para análise de padrões linguísticos
    """
    
    keyword = models.CharField(max_length=100, help_text="Palavra-chave")
    category = models.CharField(max_length=50, help_text="Categoria associada")
    
    # Contadores
    frequency = models.PositiveIntegerField(default=1, help_text="Frequência total")
    last_7_days_freq = models.PositiveIntegerField(default=0)
    last_30_days_freq = models.PositiveIntegerField(default=0)
    
    # Estatísticas
    avg_confidence_when_present = models.FloatField(
        default=0.0,
        help_text="Confiança média quando esta palavra está presente"
    )
    
    # Context tracking
    contexts = models.JSONField(
        default=list,
        help_text="Contextos onde esta palavra aparece mais"
    )
    
    # Metadata
    first_detected = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Keyword Frequency"
        verbose_name_plural = "Keyword Frequencies"
        unique_together = ['keyword', 'category']
        ordering = ['-frequency']
        indexes = [
            models.Index(fields=['keyword']),
            models.Index(fields=['category']),
            models.Index(fields=['-frequency']),
        ]
    
    def __str__(self):
        return f'"{self.keyword}" in {self.category} ({self.frequency}x)'


class TimeSeriesData(models.Model):
    """
    Dados de série temporal para gráficos de tendência
    Agregado por dia/hora para performance
    """
    
    date = models.DateField(help_text="Data de referência")
    hour = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        help_text="Hora (0-23) para granularidade horária"
    )
    
    # Contadores básicos
    total_emails = models.PositiveIntegerField(default=0)
    productive_emails = models.PositiveIntegerField(default=0)
    unproductive_emails = models.PositiveIntegerField(default=0)
    
    # Por urgência
    high_urgency = models.PositiveIntegerField(default=0)
    medium_urgency = models.PositiveIntegerField(default=0)
    low_urgency = models.PositiveIntegerField(default=0)
    
    # Por tom
    positive_tone = models.PositiveIntegerField(default=0)
    negative_tone = models.PositiveIntegerField(default=0)
    neutral_tone = models.PositiveIntegerField(default=0)
    
    # Métricas calculadas
    productivity_rate = models.FloatField(default=0.0)
    avg_confidence = models.FloatField(default=0.0)
    avg_processing_time = models.FloatField(default=0.0)
    
    # Granularidade
    granularity = models.CharField(
        max_length=10,
        choices=[
            ('hourly', 'Por Hora'),
            ('daily', 'Por Dia'),
        ],
        default='daily'
    )
    
    class Meta:
        verbose_name = "Time Series Data"
        verbose_name_plural = "Time Series Data"
        unique_together = ['date', 'hour', 'granularity']
        ordering = ['-date', '-hour']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['granularity']),
        ]
    
    def __str__(self):
        if self.granularity == 'hourly':
            return f"{self.date} {self.hour:02d}:00 ({self.total_emails} emails)"
        return f"{self.date} ({self.total_emails} emails)"
