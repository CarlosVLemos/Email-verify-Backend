"""
Processador em lote otimizado para Render
Lida com múltiplos emails de forma eficiente
"""
import json
import re
import csv
import io
from typing import List, Dict, Union, Iterator
from django.http import JsonResponse, StreamingHttpResponse
from .email_classifier import EmailClassifier
from .attachment_analyzer import AttachmentAnalyzer
import time
import gc
class BatchEmailProcessor:
    def __init__(self):
        self.classifier = EmailClassifier()
        self.attachment_analyzer = AttachmentAnalyzer()
        self.max_emails_per_batch = 50
        self.max_file_size_mb = 5
        self.chunk_size = 10  
    def process_batch(self, emails: List[str], request_id: str = None) -> Iterator[Dict]:
        total_emails = len(emails)
        processed = 0
        for i in range(0, total_emails, self.chunk_size):
            chunk = emails[i:i + self.chunk_size]
            chunk_results = []
            for email_text in chunk:
                try:
                    result = self._process_single_email(email_text.strip(), processed + 1)
                    chunk_results.append(result)
                    processed += 1
                    yield {
                        'type': 'progress',
                        'processed': processed,
                        'total': total_emails,
                        'percentage': round((processed / total_emails) * 100, 1)
                    }
                except Exception as e:
                    error_result = {
                        'email_id': processed + 1,
                        'email_preview': email_text[:100] + '...' if len(email_text) > 100 else email_text,
                        'error': str(e),
                        'status': 'error'
                    }
                    chunk_results.append(error_result)
                    processed += 1
            yield {
                'type': 'chunk_complete',
                'results': chunk_results,
                'chunk_index': i // self.chunk_size
            }
            gc.collect()
        yield {
            'type': 'complete',
            'total_processed': processed,
            'success': True
        }
    def _process_single_email(self, email_text: str, email_id: int) -> Dict:
        if not email_text or len(email_text.strip()) < 10:
            raise ValueError("Email muito curto ou vazio")
        start_time = time.time()
        classification = self.classifier.classify(email_text)
        attachment_analysis = self.attachment_analyzer.analyze(email_text)
        suggested_response = self._generate_suggested_response(classification, email_text)
        processing_time = time.time() - start_time
        result = {
            'email_id': email_id,
            'email_preview': self._create_preview(email_text),
            'email_full_text': email_text,
            'classification': classification,
            'attachment_analysis': attachment_analysis,
            'suggested_response': suggested_response,
            'word_count': len(email_text.split()),
            'char_count': len(email_text),
            'status': 'success',
            'processed_at': time.time(),
            'processing_time_ms': int(processing_time * 1000)
        }
        try:
            from analytics.views import save_email_analytics
            analytics_data = {
                'sender_email': None,  
                'sender_name': None,
                'sender_domain': None,
                'category': classification.get('categoria'),
                'subcategory': classification.get('subcategoria'),
                'tone': classification.get('tom'),
                'urgency': classification.get('urgencia'),
                'confidence_score': classification.get('confianca', 0.85),
                'word_count': len(email_text.split()),
                'char_count': len(email_text),
                'has_attachments': attachment_analysis.get('has_attachments_mentioned', False),
                'attachment_score': attachment_analysis.get('score', 0),
                'keywords_detected': classification.get('palavras_chave_detectadas', []),
                'technical_data': {
                    'batch_id': f"batch_{int(time.time())}",
                    'email_id': email_id,
                    'method': 'batch_processing'
                }
            }
            save_email_analytics(analytics_data, int(processing_time * 1000), source='batch')
        except Exception as e:
            print(f"Warning: Falha ao salvar analytics para email {email_id}: {e}")
        return result
    def _create_preview(self, text: str, max_chars: int = 120) -> str:
        text = re.sub(r'\s+', ' ', text.strip())
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rsplit(' ', 1)[0] + '...'
    def _generate_suggested_response(self, classification: Dict, email_text: str) -> str:
        categoria = classification.get('categoria', '').lower()
        subcategoria = classification.get('subcategoria', '').lower()
        tom = classification.get('tom', '').lower()
        urgencia = classification.get('urgencia', '').lower()
        if categoria == 'improdutivo':
            if 'spam' in subcategoria:
                return "Email identificado como spam. Não requer resposta."
            elif 'marketing' in subcategoria:
                return "Conteúdo promocional recebido. Arquivado para referência."
            else:
                return "Obrigado pelo seu contato. Mensagem recebida e arquivada."
        elif categoria == 'produtivo':
            base_response = "Obrigado pelo seu contato. "
            if urgencia == 'alta':
                base_response += "Recebemos sua mensagem urgente e nossa equipe está analisando com prioridade máxima. "
            elif urgencia == 'média':
                base_response += "Recebemos sua mensagem e nossa equipe está analisando. "
            else:
                base_response += "Recebemos sua mensagem. "
            if 'suporte' in subcategoria:
                base_response += "Nossa equipe técnica irá investigar o problema reportado e retornará com uma solução."
            elif 'solicitação' in subcategoria:
                base_response += "Sua solicitação foi encaminhada para o setor responsável e retornaremos em breve."
            elif 'dúvida' in subcategoria:
                base_response += "Sua dúvida será esclarecida por nossa equipe e retornaremos com as informações solicitadas."
            elif 'comunicação' in subcategoria:
                base_response += "Recebemos a atualização do projeto e nossa equipe está alinhada com as próximas etapas."
            else:
                base_response += "Retornaremos com uma resposta apropriada em breve."
            if urgencia == 'alta':
                base_response += " Tempo estimado: até 2 horas."
            elif urgencia == 'média':
                base_response += " Tempo estimado: até 24 horas."
            else:
                base_response += " Tempo estimado: até 48 horas."
            return base_response
        return "Obrigado pelo seu contato. Sua mensagem foi recebida e será analisada adequadamente."
class BatchFileParser:
    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> List[str]:
        try:
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                content = file_content.decode('latin1')
            file_ext = filename.lower().split('.')[-1]
            if file_ext == 'json':
                return BatchFileParser._parse_json(content)
            elif file_ext == 'csv':
                return BatchFileParser._parse_csv(content)
            else:
                return BatchFileParser._parse_text(content)
        except Exception as e:
            raise ValueError(f"Erro ao processar arquivo {filename}: {str(e)}")
    @staticmethod
    def _parse_json(content: str) -> List[str]:
        data = json.loads(content)
        if isinstance(data, list):
            return [str(item) for item in data if str(item).strip()]
        elif isinstance(data, dict):
            for key in ['emails', 'messages', 'content', 'text']:
                if key in data and isinstance(data[key], list):
                    return [str(item) for item in data[key] if str(item).strip()]
            return [str(value) for value in data.values() if str(value).strip()]
        else:
            return [str(data)] if str(data).strip() else []
    @staticmethod
    def _parse_csv(content: str) -> List[str]:
        emails = []
        reader = csv.reader(io.StringIO(content))
        for row_num, row in enumerate(reader):
            if row_num == 0:  
                if any(header in str(row).lower() for header in ['email', 'message', 'content', 'text']):
                    continue
            email_text = ' '.join(cell.strip() for cell in row if cell.strip())
            if email_text and len(email_text) > 10:
                emails.append(email_text)
        return emails
    @staticmethod
    def _parse_text(content: str) -> List[str]:
        separators = ['\n\n\n', '\n---\n', '\n***\n', '\n===\n']
        emails = [content]  
        for sep in separators:
            if sep in content:
                emails = content.split(sep)
                break
        if len(emails) == 1 and len(content) > 500:
            potential_emails = content.split('\n\n')
            emails = [email.strip() for email in potential_emails if len(email.strip()) > 50]
        return [email.strip() for email in emails if email.strip() and len(email.strip()) > 10]
class BatchValidator:
    @staticmethod
    def validate_file(file) -> Dict[str, Union[bool, str]]:
        max_size = 5 * 1024 * 1024  
        allowed_extensions = ['txt', 'csv', 'json']
        if file.size > max_size:
            return {
                'valid': False,
                'error': f'Arquivo muito grande. Máximo permitido: 5MB. Tamanho: {file.size/1024/1024:.1f}MB'
            }
        file_ext = file.name.lower().split('.')[-1]
        if file_ext not in allowed_extensions:
            return {
                'valid': False,
                'error': f'Formato não suportado. Use: {", ".join(allowed_extensions)}'
            }
        return {'valid': True}
    @staticmethod
    def validate_emails(emails: List[str]) -> Dict[str, Union[bool, str, int]]:
        max_emails = 50
        if not emails:
            return {'valid': False, 'error': 'Nenhum email válido encontrado'}
        if len(emails) > max_emails:
            return {
                'valid': False,
                'error': f'Muitos emails. Máximo: {max_emails}. Encontrados: {len(emails)}'
            }
        valid_emails = [email for email in emails if len(email.strip()) >= 10]
        if len(valid_emails) == 0:
            return {'valid': False, 'error': 'Nenhum email com tamanho mínimo (10 caracteres)'}
        return {
            'valid': True,
            'total_emails': len(valid_emails),
            'filtered_count': len(emails) - len(valid_emails)
        }