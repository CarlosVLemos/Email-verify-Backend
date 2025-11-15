"""
Service layer para classificação de emails
Centraliza a lógica de negócio
"""
import logging
import time
from ..email_scripts import (
    EmailClassifier,
    EmailResponseGenerator,
    AttachmentAnalyzer,
    EmailThreadParser
)
logger = logging.getLogger(__name__)
class EmailClassificationService:
    """Service para classificação de emails"""
    def __init__(self):
        self.email_classifier = EmailClassifier()
        self.response_generator = EmailResponseGenerator()
        self.attachment_analyzer = AttachmentAnalyzer()
        self.thread_parser = EmailThreadParser()
    def classify_email(self, email_text, sender_email=None, sender_name=None):
        """
        Classifica um email completo
        Args:
            email_text: Texto do email
            sender_email: Email do remetente (opcional)
            sender_name: Nome do remetente (opcional)
        Returns:
            dict: Resultado completo da classificação
        """
        start_time = time.time()
        classification = self.email_classifier.classify(email_text)
        attachment_raw = self.attachment_analyzer.analyze(email_text)
        suggested_response = self.response_generator.generate_response(
            classification['categoria'],
            classification['subcategoria'],
            classification['tom'],
            classification['urgencia']
        )
        processing_time = int((time.time() - start_time) * 1000)
        attachment_analysis = {
            'has_attachments_mentioned': attachment_raw.get('has_attachments_mentioned', False),
            'attachment_keywords': attachment_raw.get('mentions', []),
            'score': attachment_raw.get('mention_count', 0)
        }
        result = {
            'topic': classification['subcategoria'],
            'category': classification['categoria'],
            'confidence': classification.get('confianca'),
            'tone': classification['tom'],
            'urgency': classification['urgencia'],
            'suggested_response': suggested_response,
            'attachment_analysis': attachment_analysis,
            'word_count': len(email_text.split()),
            'char_count': len(email_text),
            'processing_time_ms': processing_time,
        }
        if sender_email:
            result['sender_email'] = sender_email
        if sender_name:
            result['sender_name'] = sender_name
        return result
    def parse_thread(self, email_text):
        """
        Parse email thread e retorna emails individuais
        Args:
            email_text: Texto contendo possivelmente múltiplos emails
        Returns:
            list: Lista de dicts com informações de cada email
        """
        return self.thread_parser.parse(email_text)
    def extract_first_email_from_thread(self, email_text):
        """
        Extrai o primeiro email de uma thread
        Args:
            email_text: Texto da thread
        Returns:
            tuple: (email_text, sender_email, sender_name)
        """
        parsed_emails = self.parse_thread(email_text)
        if parsed_emails and len(parsed_emails) > 0:
            first_email = parsed_emails[0]
            return (
                first_email.get('body', email_text),
                first_email.get('from'),
                None
            )
        return email_text, None, None
