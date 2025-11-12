"""
Views para Classifier API - 100% Django REST Framework
Endpoints para classificação de emails com IA
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample
import logging
import time
import uuid
import pdfplumber
import docx

from .email_scripts import (
    EmailClassifier,
    EmailResponseGenerator,
    AttachmentAnalyzer,
    ExecutiveSummarizer
)
from .email_scripts.batch_processor import BatchEmailProcessor
from .serializers import (
    EmailTextInputSerializer,
    EmailClassificationOutputSerializer,
    SummaryInputSerializer,
    SummaryOutputSerializer,
    BatchEmailInputSerializer,
    BatchEmailOutputSerializer,
    ErrorResponseSerializer,
    HealthCheckSerializer,
    ResponseHelper,
)

logger = logging.getLogger(__name__)


class EmailClassifierAPIView(APIView):
    """
    Endpoint principal para classificação de emails
    
    Analisa o conteúdo de um email e retorna:
    - Categoria e subcategoria
    - Tom emocional
    - Nível de urgência
    - Sugestão de resposta automática
    - Análise de anexos mencionados
    """
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email_classifier = EmailClassifier()
        self.response_generator = EmailResponseGenerator()
        self.attachment_analyzer = AttachmentAnalyzer()
    
    def extract_text_from_file(self, uploaded_file):
        """
        Extrai texto de diferentes formatos de arquivo
        
        Args:
            uploaded_file: Arquivo enviado via request
            
        Returns:
            tuple: (texto_extraído, erro)
        """
        try:
            filename = uploaded_file.name.lower()
            
            if filename.endswith('.pdf'):
                text = ''
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + '\n'
                return text.strip(), None
                
            elif filename.endswith('.txt'):
                try:
                    text = uploaded_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    text = uploaded_file.read().decode('latin-1')
                return text.strip(), None
                
            elif filename.endswith('.docx') or filename.endswith('.doc'):
                doc = docx.Document(uploaded_file)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                return text.strip(), None
                
            else:
                return None, 'Formato de arquivo não suportado. Use .txt, .pdf ou .docx'
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {uploaded_file.name}: {e}")
            return None, f'Erro ao ler arquivo: {str(e)}'
    
    @extend_schema(
        summary="Classificar Email",
        description="""
        Este endpoint realiza a classificação de emails com base em IA e regras inteligentes.

        Campos esperados:
        - `email_text` (string): Texto do email a ser classificado.
        - `file` (arquivo, opcional): Arquivo contendo o texto do email. Formatos suportados: .txt, .pdf, .docx.
        - `sender_email` (string, opcional): Email do remetente.
        - `sender_name` (string, opcional): Nome do remetente.
        """,
        request={
            'application/json': EmailTextInputSerializer,
            'multipart/form-data': OpenApiExample(
                'Upload de Arquivo',
                value={'file': 'arquivo.txt'},
                request_only=True,
            )
        },
        responses={
            200: EmailClassificationOutputSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Exemplo de Requisição',
                value={
                    "email_text": "Olá, estou tendo problemas com o login no sistema. Poderia me ajudar?"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Exemplo de Resposta',
                value={
                    "topic": "Suporte Técnico",
                    "category": "Produtivo",
                    "confidence": None,
                    "tone": "Neutro",
                    "urgency": "Média",
                    "suggested_response": "Olá! Agradecemos por entrar em contato. Vou ajudá-lo com o problema de login...",
                    "attachment_analysis": {
                        "has_attachments_mentioned": False,
                        "attachment_keywords": [],
                        "score": 0
                    },
                    "word_count": 12,
                    "char_count": 78,
                    "processing_time_ms": 234
                },
                response_only=True,
            ),
        ],
        tags=['Email Classification']
    )
    def post(self, request):
        """Classifica email e retorna análise completa"""
        try:
            email_text = ''
            sender_email = None
            sender_name = None

            if request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                email_text, error = self.extract_text_from_file(uploaded_file)
                if error:
                    return Response(
                        ResponseHelper.format_error_response(error),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if not email_text:
                    return Response(
                        ResponseHelper.format_error_response('O arquivo está vazio ou não contém texto extraível'),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                sender_email = request.data.get('sender_email')
                sender_name = request.data.get('sender_name')
            else:
                serializer = EmailTextInputSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(
                        ResponseHelper.format_error_response('Dados de entrada inválidos', serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                email_text = serializer.validated_data['email_text']
                sender_email = request.data.get('sender_email')
                sender_name = request.data.get('sender_name')

            start_time = time.time()

            classification = self.email_classifier.classify(email_text)
            attachment_analysis = self.attachment_analyzer.analyze(email_text)
            suggested_response = self.response_generator.generate(
                email_text,
                classification['topic'],
                classification['tone']
            )

            processing_time = int((time.time() - start_time) * 1000)

            result = {
                'topic': classification['topic'],
                'category': classification['category'],
                'confidence': classification.get('confidence'),
                'tone': classification['tone'],
                'urgency': classification['urgency'],
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

            try:
                from analytics.views import save_email_analytics
                analytics_data = {
                    **result,
                    'sender_email': sender_email,
                    'sender_name': sender_name,
                    'email_text': email_text,
                }
                save_email_analytics(
                    classification_result=analytics_data,
                    processing_time=processing_time,
                    source='api',
                    request_data={
                        'user_agent': request.META.get('HTTP_USER_AGENT'),
                        'ip_address': request.META.get('REMOTE_ADDR'),
                        'method': 'POST',
                    }
                )
            except Exception as e:
                logger.warning(f"Falha ao salvar analytics: {e}")

            output_serializer = EmailClassificationOutputSerializer(data=result)
            if output_serializer.is_valid():
                return Response(ResponseHelper.format_success_response(output_serializer.data), status=status.HTTP_200_OK)
            else:
                logger.warning(f"Output validation failed: {output_serializer.errors}")
                return Response(ResponseHelper.format_success_response(result), status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro na classificação: {e}", exc_info=True)
            return Response(
                ResponseHelper.format_error_response('Erro interno no processamento', str(e) if logger.getEffectiveLevel() <= logging.DEBUG else None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExecutiveSummaryAPIView(APIView):
    """
    Gera resumo executivo de emails longos
    
    Ideal para emails extensos (>100 palavras), extrai:
    - Frases mais importantes
    - Pontos-chave (prazos, valores, ações)
    - Score de relevância
    """
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.summarizer = ExecutiveSummarizer()
    
    @extend_schema(
        summary="Resumo Executivo",
        description="""
        Este endpoint gera um resumo executivo de emails longos.

        Campos esperados:
        - `email_text` (string): Texto do email a ser resumido.
        - `max_sentences` (inteiro, opcional): Número máximo de frases no resumo (padrão: 3).
        - `file` (arquivo, opcional): Arquivo contendo o texto do email. Formatos suportados: .txt, .pdf, .docx.
        """,
        request=SummaryInputSerializer,
        responses={
            200: SummaryOutputSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Exemplo de Requisição',
                value={
                    "email_text": "Email muito longo com várias informações importantes sobre projeto, prazos, valores e ações necessárias...",
                    "max_sentences": 3
                },
                request_only=True,
            ),
            OpenApiExample(
                'Exemplo de Resposta',
                value={
                    "summary": [
                        "O projeto precisa ser entregue até sexta-feira.",
                        "O orçamento aprovado é de R$ 15.000.",
                        "É necessário revisar os documentos antes da reunião."
                    ],
                    "key_points": [
                        "Prazo: sexta-feira",
                        "Orçamento: R$ 15.000",
                        "Ação: revisar documentos"
                    ],
                    "relevance_score": 0.85,
                    "word_reduction": 75.5,
                    "original_word_count": 250,
                    "summary_word_count": 61
                },
                response_only=True,
            ),
        ],
        tags=['Email Classification']
    )
    def post(self, request):
        """Gera resumo executivo de email"""
        try:
            email_text = ''
            max_sentences = 3

            if request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                classifier_view = EmailClassifierAPIView()
                email_text, error = classifier_view.extract_text_from_file(uploaded_file)
                if error:
                    return Response(
                        ResponseHelper.format_error_response(error),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                max_sentences = int(request.data.get('max_sentences', 3))
            else:
                serializer = SummaryInputSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(
                        ResponseHelper.format_error_response('Dados de entrada inválidos', serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                email_text = serializer.validated_data['email_text']
                max_sentences = serializer.validated_data.get('max_sentences', 3)

            result = self.summarizer.summarize(email_text, max_sentences)
            summary_words = sum(len(sentence.split()) for sentence in result['summary'])

            response_data = {
                'summary': result['summary'],
                'key_points': result['key_points'],
                'relevance_score': round(result['relevance_score'], 3),
                'word_reduction': round(result['word_reduction'], 2),
                'original_word_count': result['original_word_count'],
                'summary_word_count': summary_words
            }

            output_serializer = SummaryOutputSerializer(data=response_data)
            if output_serializer.is_valid():
                return Response(ResponseHelper.format_success_response(output_serializer.data), status=status.HTTP_200_OK)
            else:
                logger.warning(f"Summary output validation failed: {output_serializer.errors}")
                return Response(ResponseHelper.format_success_response(response_data), status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}", exc_info=True)
            return Response(
                ResponseHelper.format_error_response('Erro ao gerar resumo', str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchEmailAPIView(APIView):
    """
    Processa múltiplos emails em lote
    
    Otimizado para processar até 50 emails de uma vez com:
    - Processamento paralelo por chunks
    - Tracking individual de cada email
    - Métricas agregadas de performance
    """
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.processor = BatchEmailProcessor()
    
    @extend_schema(
        summary="Processamento em Lote",
        description="""
        Este endpoint processa múltiplos emails em lote.

        Campos esperados:
        - `emails` (lista de strings): Lista de textos de emails a serem processados.
        - `file` (arquivo, opcional): Arquivo contendo os emails. Formatos suportados: .txt, .csv, .json.
        """,
        request={
            'application/json': BatchEmailInputSerializer,
            'multipart/form-data': OpenApiExample(
                'Upload de Arquivo',
                value={'file': 'emails.txt'},
                request_only=True,
            )
        },
        responses={
            200: BatchEmailOutputSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Exemplo de Requisição',
                value={
                    "emails": [
                        "Olá, preciso de ajuda com o sistema de login.",
                        "Obrigado pela ajuda de ontem!",
                        "Quando teremos a próxima reunião?"
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                'Exemplo de Resposta',
                value={
                    "request_id": "abc12345",
                    "total_emails": 3,
                    "successful": 3,
                    "failed": 0,
                    "total_time_ms": 1250,
                    "avg_time_per_email_ms": 416.67,
                    "results": [
                        {
                            "email_id": 1,
                            "status": "success",
                            "classification": {
                                "topic": "Suporte Técnico",
                                "category": "Produtivo",
                                "tone": "Neutro",
                                "urgency": "Média"
                            },
                            "preview": "Olá, preciso de ajuda..."
                        },
                        {
                            "email_id": 2,
                            "status": "success",
                            "classification": {
                                "topic": "Agradecimento",
                                "category": "Social",
                                "tone": "Positivo",
                                "urgency": "Baixa"
                            },
                            "preview": "Obrigado pela ajuda..."
                        },
                        {
                            "email_id": 3,
                            "status": "success",
                            "classification": {
                                "topic": "Dúvida",
                                "category": "Produtivo",
                                "tone": "Neutro",
                                "urgency": "Média"
                            },
                            "preview": "Quando teremos a..."
                        }
                    ]
                },
                response_only=True,
            ),
        ],
        tags=['Email Classification']
    )
    def post(self, request):
        """Processa emails em lote"""
        try:
            request_id = str(uuid.uuid4())[:8]

            if request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                result = self.processor.process_file(uploaded_file, request_id)
            else:
                serializer = BatchEmailInputSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(
                        ResponseHelper.format_error_response('Dados de entrada inválidos', serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                emails_list = serializer.validated_data['emails']
                result = self.processor.process_list(emails_list, request_id)

            if result.get('status') == 'error':
                return Response(
                    ResponseHelper.format_error_response(result.get('message', 'Erro no processamento')),
                    status=status.HTTP_400_BAD_REQUEST
                )

            output_serializer = BatchEmailOutputSerializer(data=result)
            if output_serializer.is_valid():
                return Response(ResponseHelper.format_success_response(output_serializer.data), status=status.HTTP_200_OK)
            else:
                logger.warning(f"Batch output validation failed: {output_serializer.errors}")
                return Response(ResponseHelper.format_success_response(result), status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro no batch: {e}", exc_info=True)
            return Response(
                ResponseHelper.format_error_response('Erro no processamento em lote', str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckAPIView(APIView):
    """
    Health check da API
    
    Verifica o status de saúde de todos os componentes
    """
    
    @extend_schema(
        summary="Health Check",
        description="""
        Este endpoint verifica o status de saúde da API.

        Campos esperados:
        - Nenhum campo é necessário para esta requisição.

        Resposta:
        - `status` (string): Status geral da API (healthy/unhealthy).
        - `version` (string): Versão da API.
        - `timestamp` (string): Timestamp atual.
        - `services` (objeto): Status dos serviços internos (database, analytics, classifier).
        """,
        responses={
            200: HealthCheckSerializer,
        },
        examples=[
            OpenApiExample(
                'Exemplo de Resposta',
                value={
                    "status": "healthy",
                    "version": "1.0.0",
                    "timestamp": "2025-11-11T10:30:00Z",
                    "services": {
                        "database": "healthy",
                        "analytics": "healthy",
                        "classifier": "healthy"
                    }
                },
                response_only=True,
            ),
        ],
        tags=['System']
    )
    def get(self, request):
        """Retorna status de saúde da API"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "unhealthy"

        try:
            from analytics.models import EmailAnalytics
            EmailAnalytics.objects.count()
            analytics_status = "healthy"
        except Exception as e:
            logger.error(f"Analytics health check failed: {e}")
            analytics_status = "unhealthy"

        try:
            classifier = EmailClassifier()
            test_result = classifier.classify("Test email")
            classifier_status = "healthy" if test_result else "unhealthy"
        except Exception as e:
            logger.error(f"Classifier health check failed: {e}")
            classifier_status = "unhealthy"

        overall_status = "healthy" if all([
            db_status == "healthy",
            analytics_status == "healthy",
            classifier_status == "healthy"
        ]) else "unhealthy"

        health_data = {
            "status": overall_status,
            "version": "1.0.0",
            "timestamp": timezone.now(),
            "services": {
                "database": db_status,
                "analytics": analytics_status,
                "classifier": classifier_status
            }
        }

        serializer = HealthCheckSerializer(data=health_data)
        if serializer.is_valid():
            return Response(ResponseHelper.format_success_response(serializer.data), status=status.HTTP_200_OK)
        else:
            return Response(ResponseHelper.format_success_response(health_data), status=status.HTTP_200_OK)
