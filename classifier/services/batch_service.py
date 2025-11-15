"""
Service para processamento em lote de emails
"""
import logging
import time
import uuid
from ..email_scripts.batch_processor import BatchEmailProcessor, BatchFileParser, BatchValidator
from .email_classification_service import EmailClassificationService
logger = logging.getLogger(__name__)
class BatchProcessingService:
    """Service para processamento em lote"""
    def __init__(self):
        self.processor = BatchEmailProcessor()
        self.classification_service = EmailClassificationService()
    def process_batch(self, emails_list, request_id=None):
        """
        Processa múltiplos emails em lote
        Args:
            emails_list: Lista de textos de emails
            request_id: ID da requisição (opcional)
        Returns:
            dict: Resultado do processamento em lote
        """
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        results = []
        successful = 0
        failed = 0
        for result_data in self.processor.process_batch(emails_list, request_id):
            if result_data['type'] == 'chunk_complete':
                for item in result_data['results']:
                    if item['status'] == 'success':
                        successful += 1
                        attachment_raw = item.get('attachment_analysis', {})
                        attachment_analysis = {
                            'has_attachments_mentioned': attachment_raw.get('has_attachments_mentioned', False),
                            'attachment_keywords': attachment_raw.get('mentions', []),
                            'score': attachment_raw.get('mention_count', 0)
                        }
                        results.append({
                            'email_id': item['email_id'],
                            'status': 'success',
                            'topic': item['classification']['subcategoria'],
                            'category': item['classification']['categoria'],
                            'confidence': item['classification'].get('confianca'),
                            'tone': item['classification']['tom'],
                            'urgency': item['classification']['urgencia'],
                            'suggested_response': item.get('suggested_response', ''),
                            'attachment_analysis': attachment_analysis,
                            'word_count': item.get('word_count', 0),
                            'char_count': item.get('char_count', 0),
                            'processing_time_ms': item.get('processing_time_ms', 0),
                            'sender_email': None,
                            'sender_name': None,
                            'preview': item['email_preview']
                        })
                    else:
                        failed += 1
                        results.append({
                            'email_id': item['email_id'],
                            'status': 'error',
                            'error': item.get('error', 'Erro desconhecido'),
                            'preview': item.get('email_preview', '')
                        })
        total_time = int((time.time() - start_time) * 1000)
        return {
            'request_id': request_id,
            'total_emails': len(emails_list),
            'successful': successful,
            'failed': failed,
            'total_time_ms': total_time,
            'avg_time_per_email_ms': round(total_time / len(emails_list), 2) if emails_list else 0,
            'results': results
        }
    def parse_file_to_emails(self, file_content, filename):
        """
        Parse arquivo para lista de emails
        Args:
            file_content: Conteúdo do arquivo
            filename: Nome do arquivo
        Returns:
            list: Lista de emails extraídos
        """
        return BatchFileParser.parse_file(file_content, filename)
    def validate_file(self, uploaded_file):
        """
        Valida arquivo para batch processing
        Args:
            uploaded_file: Arquivo enviado
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        return BatchValidator.validate_file(uploaded_file)
    def validate_emails(self, emails_list):
        """
        Valida lista de emails
        Args:
            emails_list: Lista de textos
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        return BatchValidator.validate_emails(emails_list)
