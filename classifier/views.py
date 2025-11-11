from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import json
import pdfplumber
import docx
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .email_scripts import EmailClassifier, EmailResponseGenerator, AttachmentAnalyzer, ExecutiveSummarizer
from .email_scripts.batch_processor import BatchEmailProcessor, BatchFileParser, BatchValidator

# Configura o logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class EmailClassifierView(TemplateView):
    """
    View principal para classificação de emails com IA.
    
    Responsabilidades:
    - Renderizar interface web
    - Processar uploads de arquivos
    - Orquestrar classificação e geração de resposta
    - Retornar resultados em JSON
    
    Suporta texto direto e arquivos .txt, .pdf, .docx
    """
    template_name = 'classifier/index.html'
    
    def __init__(self):
        super().__init__()
        self.email_classifier = EmailClassifier()
        self.response_generator = EmailResponseGenerator()
        self.attachment_analyzer = AttachmentAnalyzer()
    def get(self, request, *args, **kwargs):
        """Renderiza a página HTML com o formulário"""
        return super().get(request, *args, **kwargs)
    def extract_text_from_file(self, uploaded_file):
        """
        Extrai texto de diferentes tipos de arquivo.
        Retorna: (texto_extraído, erro)
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
                    # Tenta com latin-1 se UTF-8 falhar
                    uploaded_file.seek(0)
                    text = uploaded_file.read().decode('latin-1')
                return text.strip(), None
                
            elif filename.endswith('.docx') or filename.endswith('.doc'):
                doc = docx.Document(uploaded_file)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                return text.strip(), None
                
            else:
                return None, 'Formato de arquivo não suportado. Use .txt, .pdf ou .docx.'
                
        except Exception as e:
            logger.error(f"Erro ao processar o arquivo {uploaded_file.name}: {e}")
            return None, f'Erro ao ler o arquivo: {str(e)}'

    @extend_schema(
        summary="Classifica o texto de um email, detecta o tom e a urgência.",
        description="""
        Este endpoint realiza uma análise completa de um texto de email, fornecendo múltiplas camadas de classificação.
        
        **Funcionalidades:**
        1.  **Classificação de Tópico:** Categoriza o email em subcategorias detalhadas (ex: `Suporte Técnico`, `Spam`).
        2.  **Detecção de Tom:** Analisa o sentimento do texto (`Positivo`, `Negativo`, `Neutro`).
        3.  **Análise de Urgência:** Determina se o conteúdo sugere urgência (`Urgente`, `Não Urgente`).

        **Como Usar:**
        - **Via JSON:** Envie um corpo `{"email_text": "..."}` com `Content-Type: application/json`.
        - **Via Arquivo:** Envie um arquivo (`.txt`, `.pdf`, `.docx`) usando `Content-Type: multipart/form-data`.
        
        A API retornará uma estrutura JSON completa com todas as análises.
        """,
        request={
            "application/json": inline_serializer(
                name="EmailTextPayload",
                fields={"email_text": serializers.CharField(help_text="O texto do email a ser classificado.")}
            ),
            "multipart/form-data": inline_serializer(
                name="EmailFilePayload",
                fields={"file": serializers.FileField(help_text="Arquivo de email (.txt, .pdf, .docx).")}
            )
        },
        responses={
            200: inline_serializer(
                name="FullClassificationSuccess",
                fields={
                    "topic": serializers.CharField(help_text="Subcategoria classificada (ex: 'Dúvida', 'Agradecimento')."),
                    "category": serializers.CharField(help_text="Categoria principal ('Produtivo', 'Social', 'Improdutivo')."),
                    "confidence": serializers.FloatField(allow_null=True, help_text="Confiança da classificação (não aplicável para este modelo)."),
                    "tone": serializers.CharField(help_text="Tom detectado ('Positivo', 'Negativo', 'Neutro')."),
                    "urgency": serializers.CharField(help_text="Nível de urgência ('Urgente' ou 'Não Urgente')."),
                    "suggested_response": serializers.CharField(help_text="Sugestão de resposta baseada na análise."),
                }
            ),
            400: inline_serializer(name="Error400", fields={"error": serializers.CharField()}),
            500: inline_serializer(name="Error500", fields={"error": serializers.CharField(), "details": serializers.CharField()}),
            503: inline_serializer(name="Error503", fields={"error": serializers.CharField()})
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Recebe o texto do email, classifica e retorna resultado em JSON.
        Usa classificação baseada em regras para maior confiabilidade.
        """
        email_text = ''
        
        # Processa entrada (arquivo ou texto)
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            email_text, error = self.extract_text_from_file(uploaded_file)
            if error:
                return JsonResponse({'error': error}, status=400)
            if not email_text:
                return JsonResponse({'error': 'O arquivo está vazio ou não contém texto extraível.'}, status=400)
        else:
            try:
                data = json.loads(request.body)
                email_text = data.get('email_text', '').strip()
            except json.JSONDecodeError:
                return JsonResponse({'error': 'JSON inválido ou nenhum dado fornecido.'}, status=400)
        
        if not email_text:
            return JsonResponse({'error': 'Nenhum texto de email fornecido.'}, status=400)
        
        try:
            import time
            start_time = time.time()
            
            # Classifica o email usando a nova arquitetura
            classification = self.email_classifier.classify(email_text)
            
            # Analisa anexos mencionados (sempre ativo)
            attachment_analysis = self.attachment_analyzer.analyze(email_text)
            
            # Calcula tempo de processamento
            processing_time = int((time.time() - start_time) * 1000)  # em ms
            
            # Gera resposta automática
            suggested_response = self.response_generator.generate_response(
                classification['categoria'],
                classification['subcategoria'],
                classification['tom'],
                classification['urgencia']
            )
            
            # 🔥 NOVA FUNCIONALIDADE: Salva dados para analytics
            try:
                from analytics.views import save_email_analytics
                
                # Prepara dados para analytics
                analytics_data = {
                    'sender_email': None,  # Não disponível neste contexto
                    'sender_name': None,
                    'sender_domain': None,
                    'category': classification['categoria'],
                    'subcategory': classification['subcategoria'],
                    'tone': classification['tom'],
                    'urgency': classification['urgencia'],
                    'confidence_score': classification.get('confianca', 0.85),
                    'word_count': len(email_text.split()),
                    'char_count': len(email_text),
                    'has_attachments': attachment_analysis.get('has_attachments_mentioned', False),
                    'attachment_score': attachment_analysis.get('score', 0),
                    'keywords_detected': classification.get('palavras_chave_detectadas', []),
                    'technical_data': {
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'ip_address': request.META.get('REMOTE_ADDR', ''),
                        'method': 'single_classification',
                        'file_upload': 'file' in request.FILES,
                    }
                }
                
                # Salva analytics de forma assíncrona (não bloqueia resposta)
                save_email_analytics(analytics_data, processing_time, source='single')
                
            except Exception as analytics_error:
                # Analytics não deve afetar funcionamento principal
                logger.warning(f"Falha ao salvar analytics: {analytics_error}")
            
            logger.info(f"Email classificado: {classification['subcategoria']} - {classification['categoria']} | Anexos: {attachment_analysis['has_attachments_mentioned']} | Tempo: {processing_time}ms")
            
            return JsonResponse({
                'topic': classification['subcategoria'],
                'category': classification['categoria'],
                'confidence': classification.get('confianca', 0.85),
                'tone': classification['tom'],
                'urgency': classification['urgencia'],
                'suggested_response': suggested_response,
                'attachment_analysis': attachment_analysis,
                'processing_time_ms': processing_time  # 📊 Info adicional para usuário
            })
            
        except Exception as e:
            logger.error(f"Erro durante a classificação do email: {e}")
            return JsonResponse(
                {'error': 'Ocorreu um erro ao processar o email.', 'details': str(e)}, 
                status=500
            )


@method_decorator(csrf_exempt, name='dispatch')
class ExecutiveSummaryView(TemplateView):
    """
    Endpoint opcional para gerar resumo executivo de emails longos.
    Usado sob demanda para economizar recursos.
    """
    
    def __init__(self):
        super().__init__()
        self.summarizer = ExecutiveSummarizer()
    
    @extend_schema(
        summary="Gera um resumo executivo de um email longo",
        description="""
        Este endpoint cria um resumo conciso de emails extensos, extraindo os pontos mais relevantes.
        
        **Funcionalidades:**
        1. **Resumo Inteligente:** Seleciona as frases mais importantes usando algoritmo de relevância
        2. **Pontos-Chave:** Extrai informações específicas como prazos, valores, ações requeridas
        3. **Redução de Palavras:** Mostra percentual de redução do texto original
        4. **Score de Relevância:** Indica qualidade do resumo gerado
        
        **Parâmetros opcionais:**
        - `max_sentences`: Número máximo de frases no resumo (padrão: 3)
        
        Ideal para emails com mais de 100 palavras.
        """,
        request={
            "application/json": inline_serializer(
                name="SummaryPayload",
                fields={
                    "email_text": serializers.CharField(help_text="Texto do email para resumir"),
                    "max_sentences": serializers.IntegerField(required=False, help_text="Máximo de frases no resumo (padrão: 3)")
                }
            ),
            "multipart/form-data": inline_serializer(
                name="SummaryFilePayload",
                fields={
                    "file": serializers.FileField(help_text="Arquivo de email (.txt, .pdf, .docx)"),
                    "max_sentences": serializers.IntegerField(required=False, help_text="Máximo de frases no resumo (padrão: 3)")
                }
            )
        },
        responses={
            200: inline_serializer(
                name="SummarySuccess",
                fields={
                    "summary": serializers.ListField(child=serializers.CharField(), help_text="Frases do resumo"),
                    "key_points": serializers.ListField(child=serializers.CharField(), help_text="Pontos-chave extraídos"),
                    "relevance_score": serializers.FloatField(help_text="Score de relevância (0-1)"),
                    "word_reduction": serializers.FloatField(help_text="Percentual de redução de palavras"),
                    "original_word_count": serializers.IntegerField(help_text="Quantidade de palavras originais"),
                    "summary_word_count": serializers.IntegerField(help_text="Quantidade de palavras do resumo")
                }
            ),
            400: inline_serializer(name="SummaryError400", fields={"error": serializers.CharField()}),
            500: inline_serializer(name="SummaryError500", fields={"error": serializers.CharField()})
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Gera resumo executivo de email longo.
        Endpoint opcional, chamado apenas quando necessário.
        """
        email_text = ''
        max_sentences = 3
        
        # Extrai parâmetros
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            classifier_view = EmailClassifierView()
            email_text, error = classifier_view.extract_text_from_file(uploaded_file)
            if error:
                return JsonResponse({'error': error}, status=400)
            max_sentences = int(request.POST.get('max_sentences', 3))
        else:
            try:
                data = json.loads(request.body)
                email_text = data.get('email_text', '').strip()
                max_sentences = int(data.get('max_sentences', 3))
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({'error': 'Dados inválidos fornecidos.'}, status=400)
        
        if not email_text:
            return JsonResponse({'error': 'Nenhum texto de email fornecido.'}, status=400)
        
        # Validação de parâmetros
        if max_sentences < 1 or max_sentences > 10:
            return JsonResponse({'error': 'max_sentences deve estar entre 1 e 10.'}, status=400)
        
        try:
            # Gera o resumo
            result = self.summarizer.summarize(email_text, max_sentences)
            
            # Adiciona estatísticas extras
            original_words = len(email_text.split())
            summary_words = sum(len(sentence.split()) for sentence in result['summary'])
            
            logger.info(f"Resumo gerado: {len(result['summary'])} frases, redução de {result['word_reduction']}%")
            
            return JsonResponse({
                'summary': result['summary'],
                'key_points': result['key_points'],
                'relevance_score': round(result['relevance_score'], 3),
                'word_reduction': result['word_reduction'],
                'original_word_count': original_words,
                'summary_word_count': summary_words
            })
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo executivo: {e}")
            return JsonResponse({'error': 'Erro ao processar resumo executivo.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch') 
class BatchEmailView(TemplateView):
    """
    View para processamento em lote de emails
    Otimizada para Render com streaming response
    """
    template_name = 'classifier/batch.html'
    
    def __init__(self):
        super().__init__()
        self.processor = BatchEmailProcessor()
    
    def get(self, request, *args, **kwargs):
        """Renderiza a página de batch processing"""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Processa múltiplos emails em lote",
        description="""
        Endpoint para processamento em lote de emails com otimizações para Render.
        
        **Métodos de Entrada:**
        1. **Arquivo:** Upload de .txt, .csv, .json (máx 5MB)
        2. **Texto:** Múltiplos emails separados por linha vazia
        
        **Limitações Render:**
        - Máximo 50 emails por batch
        - Processamento em chunks de 10
        - Timeout de 30s (com streaming)
        
        **Formatos Suportados:**
        - TXT: emails separados por linhas vazias
        - CSV: cada linha é um email
        - JSON: array de strings ou objeto com chave 'emails'
        """,
        request={
            "multipart/form-data": inline_serializer(
                name="BatchFilePayload", 
                fields={
                    "file": serializers.FileField(help_text="Arquivo com emails (.txt/.csv/.json)"),
                }
            ),
            "application/json": inline_serializer(
                name="BatchTextPayload",
                fields={
                    "emails": serializers.ListField(
                        child=serializers.CharField(),
                        help_text="Lista de emails para processar"
                    )
                }
            )
        },
        responses={
            200: inline_serializer(
                name="BatchSuccess",
                fields={
                    "request_id": serializers.CharField(help_text="ID da requisição"),
                    "total_emails": serializers.IntegerField(help_text="Total de emails a processar"),
                    "estimated_time": serializers.IntegerField(help_text="Tempo estimado em segundos"),
                    "results": serializers.ListField(
                        child=serializers.DictField(),
                        help_text="Resultados do processamento"
                    )
                }
            ),
            400: inline_serializer(name="BatchError400", fields={"error": serializers.CharField()}),
            413: inline_serializer(name="BatchError413", fields={"error": serializers.CharField()})
        }
    )
    def post(self, request, *args, **kwargs):
        """Processa batch de emails"""
        try:
            emails = []
            
            # Processa arquivo ou texto
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                
                # Valida arquivo
                validation = BatchValidator.validate_file(uploaded_file)
                if not validation['valid']:
                    return JsonResponse({'error': validation['error']}, status=400)
                
                # Parse do arquivo
                try:
                    emails = BatchFileParser.parse_file(uploaded_file.read(), uploaded_file.name)
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)
                    
            else:
                # Processa texto JSON
                try:
                    data = json.loads(request.body)
                    emails = data.get('emails', [])
                    if isinstance(emails, str):
                        # Se veio como string, divide por linhas vazias
                        emails = [email.strip() for email in emails.split('\n\n') if email.strip()]
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'JSON inválido.'}, status=400)
            
            # Valida emails
            validation = BatchValidator.validate_emails(emails)
            if not validation['valid']:
                return JsonResponse({'error': validation['error']}, status=400)
            
            # Filtra emails válidos
            valid_emails = [email for email in emails if len(email.strip()) >= 10]
            
            # Processa de forma síncrona (para Render)
            results = []
            total = len(valid_emails)
            
            for i, email_result in enumerate(self.processor.process_batch(valid_emails)):
                if email_result['type'] == 'chunk_complete':
                    results.extend(email_result['results'])
                elif email_result['type'] == 'complete':
                    break
            
            # Estatísticas finais
            successful = len([r for r in results if r.get('status') == 'success'])
            failed = len(results) - successful
            
            logger.info(f"Batch processado: {successful} sucessos, {failed} falhas")
            
            return JsonResponse({
                'request_id': f"batch_{int(time.time())}",
                'total_emails': total,
                'successful': successful,
                'failed': failed,
                'results': results,
                'processing_time_seconds': len(valid_emails) * 0.5,  # Estimativa
                'status': 'completed'
            })
            
        except Exception as e:
            logger.error(f"Erro no processamento batch: {e}")
            return JsonResponse({'error': 'Erro interno no processamento batch.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BatchResultsView(TemplateView):
    """View para exibir e gerenciar resultados do batch"""
    
    def post(self, request, *args, **kwargs):
        """Endpoint para ações nos resultados (copiar, editar, reprocessar)"""
        try:
            data = json.loads(request.body)
            action = data.get('action')
            email_id = data.get('email_id')
            
            if action == 'copy_response':
                # Retorna a resposta para cópia
                suggested_response = data.get('suggested_response', '')
                return JsonResponse({
                    'success': True,
                    'response_text': suggested_response,
                    'message': 'Resposta copiada com sucesso'
                })
                
            elif action == 'edit_classification':
                # Permite edição da classificação
                new_category = data.get('new_category')
                new_subcategory = data.get('new_subcategory')
                
                # Aqui você salvaria a edição (se tivesse banco)
                return JsonResponse({
                    'success': True,
                    'message': 'Classificação editada com sucesso',
                    'updated': {
                        'category': new_category,
                        'subcategory': new_subcategory
                    }
                })
                
            elif action == 'reprocess':
                # Reprocessa um email específico
                email_text = data.get('email_text', '')
                if not email_text:
                    return JsonResponse({'error': 'Texto do email não fornecido'}, status=400)
                
                processor = BatchEmailProcessor()
                result = processor._process_single_email(email_text, email_id)
                
                return JsonResponse({
                    'success': True,
                    'result': result,
                    'message': 'Email reprocessado com sucesso'
                })
            
            else:
                return JsonResponse({'error': 'Ação não reconhecida'}, status=400)
                
        except Exception as e:
            logger.error(f"Erro em ação de resultado: {e}")
            return JsonResponse({'error': 'Erro ao executar ação'}, status=500)


import time