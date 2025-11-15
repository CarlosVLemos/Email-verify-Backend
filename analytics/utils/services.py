"""
Service layer para Analytics
Centraliza lógica de negócio e orchestração de dados
"""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
import logging
import json
logger = logging.getLogger(__name__)
class EmailAnalyticsData:
    """
    Classe para encapsular e validar dados de email antes de salvar
    Facilita manutenção e validações futuras
    """
    def __init__(self, classification_result, processing_time=0, source='single', request_data=None):
        """
        Inicializa dados de analytics a partir do resultado de classificação
        Args:
            classification_result: Dict com resultado da classificação
            processing_time: Tempo de processamento em ms
            source: Origem ('single', 'batch', 'api')
            request_data: Dados adicionais do request (opcional)
        """
        self.classification_result = classification_result or {}
        self.processing_time = processing_time
        self.source = source
        self.request_data = request_data or {}
        self.sender_email = self._extract_sender_email()
        self.sender_name = self._extract_sender_name()
        self.sender_domain = self._extract_sender_domain()
        self.category = self._extract_category()
        self.subcategory = self._extract_subcategory()
        self.tone = self._extract_tone()
        self.urgency = self._extract_urgency()
        self.confidence_score = self._extract_confidence()
        self.word_count = self._extract_word_count()
        self.char_count = self._extract_char_count()
        self.has_attachments = self._extract_attachments()
        self.attachment_score = self._extract_attachment_score()
        self.keywords_detected = self._extract_keywords()
        self.technical_data = self._build_technical_data()
    def _extract_sender_email(self):
        """Extrai email do remetente com validação flexível"""
        return self.classification_result.get('sender_email') or self.request_data.get('sender_email')
    def _extract_sender_name(self):
        """Extrai nome do remetente"""
        return self.classification_result.get('sender_name') or self.request_data.get('sender_name')
    def _extract_sender_domain(self):
        """Extrai domínio do remetente"""
        domain = self.classification_result.get('sender_domain') or self.request_data.get('sender_domain')
        if not domain and self.sender_email:
            try:
                domain = self.sender_email.split('@')[1].lower()
            except (IndexError, AttributeError):
                pass
        return domain
    def _extract_category(self):
        """Extrai categoria com validação"""
        category = self.classification_result.get('categoria') or self.classification_result.get('category')
        if category:
            category_lower = category.lower()
            if 'improdutiv' in category_lower or 'unproductiv' in category_lower:
                return 'Improdutivo'
            elif 'produtiv' in category_lower:
                return 'Produtivo'
        return category or 'Não Classificado'
    def _extract_subcategory(self):
        """Extrai subcategoria"""
        return (self.classification_result.get('subcategoria') or 
                self.classification_result.get('subcategory') or 
                self.classification_result.get('topic') or 
                'Não Especificado')
    def _extract_tone(self):
        """Extrai tom com padronização"""
        tone = self.classification_result.get('tom') or self.classification_result.get('tone')
        if tone:
            tone_lower = tone.lower()
            if 'positiv' in tone_lower:
                return 'Positivo'
            elif 'negativ' in tone_lower:
                return 'Negativo'
            elif 'neutr' in tone_lower:
                return 'Neutro'
        return tone or 'Neutro'
    def _extract_urgency(self):
        """Extrai urgência com padronização"""
        urgency = (self.classification_result.get('urgencia') or 
                  self.classification_result.get('urgency'))
        if urgency:
            urgency_lower = urgency.lower()
            if 'alta' in urgency_lower or 'high' in urgency_lower or 'urgent' in urgency_lower:
                return 'Alta'
            elif 'média' in urgency_lower or 'media' in urgency_lower or 'medium' in urgency_lower:
                return 'Média'
            elif 'baixa' in urgency_lower or 'low' in urgency_lower:
                return 'Baixa'
        return urgency or 'Baixa'
    def _extract_confidence(self):
        """Extrai confidence score com validação"""
        confidence = (self.classification_result.get('confianca') or 
                     self.classification_result.get('confidence') or 
                     self.classification_result.get('confidence_score'))
        try:
            confidence = float(confidence or 0)
            return max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            return 0.85  
    def _extract_word_count(self):
        """Extrai contagem de palavras"""
        word_count = self.classification_result.get('word_count')
        if word_count is not None:
            return max(0, int(word_count))
        text = (self.classification_result.get('text') or 
                self.classification_result.get('email_text') or '')
        return len(text.split()) if text else 0
    def _extract_char_count(self):
        """Extrai contagem de caracteres"""
        char_count = self.classification_result.get('char_count')
        if char_count is not None:
            return max(0, int(char_count))
        text = (self.classification_result.get('text') or 
                self.classification_result.get('email_text') or '')
        return len(text) if text else 0
    def _extract_attachments(self):
        """Extrai informação sobre anexos"""
        has_attachments = (
            self.classification_result.get('has_attachments') or
            self.classification_result.get('has_attachments_mentioned') or
            bool(self.classification_result.get('attachment_analysis', {}).get('has_attachments_mentioned'))
        )
        return bool(has_attachments)
    def _extract_attachment_score(self):
        """Extrai score de anexos"""
        score = (
            self.classification_result.get('attachment_score') or
            self.classification_result.get('attachment_analysis', {}).get('score') or
            0
        )
        try:
            return max(0, int(score))
        except (ValueError, TypeError):
            return 0
    def _extract_keywords(self):
        """Extrai palavras-chave detectadas"""
        keywords = (
            self.classification_result.get('palavras_chave_detectadas') or
            self.classification_result.get('keywords_detected') or
            self.classification_result.get('keywords') or
            []
        )
        if isinstance(keywords, str):
            keywords = [keywords]
        elif not isinstance(keywords, list):
            keywords = []
        return [str(kw).lower().strip() for kw in keywords[:10] if kw]
    def _build_technical_data(self):
        """Constrói dados técnicos adicionais"""
        technical = {
            'processing_time_ms': self.processing_time,
            'source': self.source,
            'timestamp': timezone.now().isoformat(),
        }
        if self.request_data:
            technical.update({
                'user_agent': self.request_data.get('user_agent'),
                'ip_address': self.request_data.get('ip_address'),
                'method': self.request_data.get('method', 'unknown'),
            })
        if self.source == 'batch':
            technical['batch_id'] = self.request_data.get('batch_id')
            technical['email_id'] = self.request_data.get('email_id')
        return technical
    def is_valid(self):
        """
        Valida se os dados estão minimamente corretos
        Returns: (is_valid, errors)
        """
        errors = []
        if not self.category:
            errors.append('Category is required')
        if not self.subcategory:
            errors.append('Subcategory is required')
        if not (0 <= self.confidence_score <= 1):
            errors.append('Confidence score must be between 0 and 1')
        if self.word_count < 0:
            errors.append('Word count cannot be negative')
        return len(errors) == 0, errors
    def to_dict(self):
        """Converte para dict para facilitar debugging"""
        return {
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'sender_domain': self.sender_domain,
            'category': self.category,
            'subcategory': self.subcategory,
            'tone': self.tone,
            'urgency': self.urgency,
            'confidence_score': self.confidence_score,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'has_attachments': self.has_attachments,
            'attachment_score': self.attachment_score,
            'keywords_detected': self.keywords_detected,
            'technical_data': self.technical_data,
        }
class AnalyticsService:
    """
    Service principal para orchestrar salvamento e agregação de analytics
    """
    def __init__(self):
        self.aggregator = AnalyticsAggregator()
    def save_email_analytics(self, classification_result, processing_time=0, source='single', request_data=None):
        """
        Salva analytics de email com validação e tratamento de erro
        Returns: (analytics_instance, success, errors)
        """
        try:
            email_data = EmailAnalyticsData(
                classification_result=classification_result,
                processing_time=processing_time,
                source=source,
                request_data=request_data
            )
            is_valid, validation_errors = email_data.is_valid()
            if not is_valid:
                logger.warning(f"Analytics data validation warnings: {validation_errors}")
            with transaction.atomic():
                analytics = self._create_email_analytics(email_data)
                self.aggregator.update_all_stats(analytics)
                logger.info(f"Analytics saved successfully: {analytics.id}")
                return analytics, True, []
        except Exception as e:
            logger.error(f"Error saving email analytics: {e}", exc_info=True)
            return None, False, [str(e)]
    def _create_email_analytics(self, email_data):
        """Cria registro principal de EmailAnalytics"""
        from analytics.models import EmailAnalytics
        return EmailAnalytics.objects.create(
            sender_email=email_data.sender_email,
            sender_name=email_data.sender_name,
            sender_domain=email_data.sender_domain,
            category=email_data.category,
            subcategory=email_data.subcategory,
            tone=email_data.tone,
            urgency=email_data.urgency,
            confidence_score=email_data.confidence_score,
            word_count=email_data.word_count,
            char_count=email_data.char_count,
            has_attachments=email_data.has_attachments,
            attachment_score=email_data.attachment_score,
            keywords_detected=email_data.keywords_detected,
            processing_time_ms=email_data.processing_time,
            source=email_data.source,
            technical_data=email_data.technical_data
        )
class AnalyticsAggregator:
    """
    Responsável por atualizar todas as estatísticas agregadas
    """
    def update_all_stats(self, email_analytics):
        """
        Atualiza todas as estatísticas agregadas em uma operação
        """
        try:
            self._update_category_stats(email_analytics)
            self._update_sender_stats(email_analytics)
            self._update_keyword_frequency(email_analytics)
            self._update_time_series_data(email_analytics)
        except Exception as e:
            logger.error(f"Error updating aggregated stats: {e}", exc_info=True)
    def _update_category_stats(self, email_analytics):
        """Atualiza estatísticas de categoria"""
        from analytics.models import CategoryStats
        try:
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
        except Exception as e:
            logger.error(f"Error updating category stats: {e}")
    def _update_sender_stats(self, email_analytics):
        """Atualiza estatísticas de remetente"""
        from analytics.models import SenderStats
        if not email_analytics.sender_domain:
            return
        try:
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
            sender_stats.refresh_from_db()
            sender_stats.productivity_rate = (
                sender_stats.productive_count / max(sender_stats.total_count, 1)
            ) * 100
            sender_stats.save()
        except Exception as e:
            logger.error(f"Error updating sender stats: {e}")
    def _update_keyword_frequency(self, email_analytics):
        """Atualiza frequência de palavras-chave"""
        from analytics.models import KeywordFrequency
        try:
            for keyword in email_analytics.keywords_detected:
                if not keyword or len(keyword.strip()) < 2:
                    continue
                kw_freq, created = KeywordFrequency.objects.get_or_create(
                    keyword=keyword.lower().strip(),
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
        except Exception as e:
            logger.error(f"Error updating keyword frequency: {e}")
    def _update_time_series_data(self, email_analytics):
        """Atualiza dados de série temporal"""
        from analytics.models import TimeSeriesData
        try:
            today = email_analytics.processed_at.date()
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
            daily_data.refresh_from_db()
            daily_data.productivity_rate = (
                daily_data.productive_emails / max(daily_data.total_emails, 1)
            ) * 100
            daily_data.save()
        except Exception as e:
            logger.error(f"Error updating time series data: {e}")