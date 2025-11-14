"""
Views para Classifier API - Refatorado com Services Layer
Endpoints para classificação de emails com IA
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample
import logging

from .services.email_classification_service import EmailClassificationService
from .services.summary_service import SummaryService
from .services.batch_service import BatchProcessingService
from .utils.file_handler import FileTextExtractor
from .email_scripts import EmailClassifier
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


classification_service = EmailClassificationService()
summary_service = SummaryService()
batch_service = BatchProcessingService()


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
                email_text, error = FileTextExtractor.extract_text(uploaded_file)
                
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
                
                email_text, parsed_email, parsed_name = classification_service.extract_first_email_from_thread(email_text)
                sender_email = request.data.get('sender_email') or parsed_email
                sender_name = request.data.get('sender_name') or parsed_name
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

            result = classification_service.classify_email(email_text, sender_email, sender_name)

            try:
                from analytics.views import save_email_analytics
                analytics_data = {
                    **result,
                    'email_text': email_text,
                }
                save_email_analytics(
                    classification_result=analytics_data,
                    processing_time=result['processing_time_ms'],
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
                email_text, error = FileTextExtractor.extract_text(uploaded_file)
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

            response_data = summary_service.generate_summary(email_text, max_sentences)

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
            emails_list = []

            if request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                
                file_validation = batch_service.validate_file(uploaded_file)
                if not file_validation['valid']:
                    return Response(
                        ResponseHelper.format_error_response(file_validation['error']),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    extracted_text, error = FileTextExtractor.extract_text(uploaded_file)
                    
                    if error:
                        return Response(
                            ResponseHelper.format_error_response(error),
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    parsed_emails = classification_service.parse_thread(extracted_text)
                    
                    if parsed_emails and len(parsed_emails) > 0:
                        emails_list = [email_data.get('body', '') for email_data in parsed_emails if email_data.get('body', '').strip()]
                        if len(parsed_emails) > 1:
                            logger.info(f"Thread detectada: {len(emails_list)} emails separados encontrados")
                    else:
                        uploaded_file.seek(0)
                        file_content = uploaded_file.read()
                        emails_list = batch_service.parse_file_to_emails(file_content, uploaded_file.name)
                        logger.info(f"Usando parser de arquivo: {len(emails_list)} emails encontrados")
                        
                except Exception as e:
                    return Response(
                        ResponseHelper.format_error_response(f'Erro ao processar arquivo: {str(e)}'),
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                serializer = BatchEmailInputSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(
                        ResponseHelper.format_error_response('Dados de entrada inválidos', serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                emails_list = serializer.validated_data['emails']

            email_validation = batch_service.validate_emails(emails_list)
            if not email_validation['valid']:
                return Response(
                    ResponseHelper.format_error_response(email_validation['error']),
                    status=status.HTTP_400_BAD_REQUEST
                )

            response_data = batch_service.process_batch(emails_list)

            output_serializer = BatchEmailOutputSerializer(data=response_data)
            if output_serializer.is_valid():
                return Response(ResponseHelper.format_success_response(output_serializer.data), status=status.HTTP_200_OK)
            else:
                logger.warning(f"Batch output validation failed: {output_serializer.errors}")
                return Response(ResponseHelper.format_success_response(response_data), status=status.HTTP_200_OK)

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
