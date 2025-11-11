from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from transformers import pipeline
import logging
import json
import pdfplumber
import docx  # python-docx para arquivos .docx
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

# Configura o logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class EmailClassifierView(TemplateView):
    """
    Lida com a renderização da página e a classificação de emails.
    Suporta texto direto, arquivos .txt, .pdf e .docx
    """
    template_name = 'classifier/index.html'
    
    # Carrega o modelo de classificação zero-shot uma vez para a classe
    classifier = None
    
    @classmethod
    def get_classifier(cls):
        """Carrega o modelo de classificação apenas quando necessário"""
        if cls.classifier is None:
            try:
                cls.classifier = pipeline(
                    "zero-shot-classification", 
                    model="facebook/bart-large-mnli"
                )
                logger.info("Modelo de classificação carregado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao carregar o modelo de NLP: {e}")
        return cls.classifier

    def get(self, request, *args, **kwargs):
        """
        Renderiza a página HTML com o formulário.
        """
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
        summary="Classifica o texto de um email como Produtivo ou Improdutivo",
        description="""
        Este endpoint classifica um email em duas categorias: **Produtivo** ou **Improdutivo**.
        
        Você pode enviar o texto do email de duas maneiras:
        
        1.  **Corpo da Requisição (JSON):**
            - `Content-Type: application/json`
            - Corpo: `{ "email_text": "O texto do seu email aqui..." }`
        
        2.  **Upload de Arquivo (Multipart):**
            - `Content-Type: multipart/form-data`
            - Corpo: Um campo `file` com um arquivo do tipo `.txt`, `.pdf`, ou `.docx`.
            
        A API retornará a classificação, um nível de confiança (0 a 100) e uma sugestão de resposta.
        """,
        # Descreve os possíveis corpos da requisição
        request={
            "application/json": inline_serializer(
                name="EmailTextPayload",
                fields={
                    "email_text": serializers.CharField(help_text="O texto do email a ser classificado.")
                }
            ),
            "multipart/form-data": inline_serializer(
                name="EmailFilePayload",
                fields={
                    "file": serializers.FileField(help_text="Arquivo de email (.txt, .pdf, .docx) para classificar.")
                }
            )
        },
        # Descreve as possíveis respostas
        responses={
            200: inline_serializer(
                name="ClassificationSuccess",
                fields={
                    "classification": serializers.CharField(help_text="Resultado da classificação ('Produtivo' ou 'Improdutivo')."),
                    "confidence": serializers.FloatField(help_text="Confiança da classificação em porcentagem (ex: 99.87)."),
                    "suggested_response": serializers.CharField(help_text="Uma sugestão de resposta baseada na classificação."),
                }
            ),
            400: inline_serializer(
                name="ClassificationError400",
                fields={
                    "error": serializers.CharField(help_text="Descrição do erro (ex: 'Nenhum texto de email fornecido.').")
                }
            ),
            500: inline_serializer(
                name="ClassificationError500",
                fields={
                    "error": serializers.CharField(default="Ocorreu um erro ao processar o email."),
                    "details": serializers.CharField(help_text="Detalhes técnicos do erro.")
                }
            ),
            503: inline_serializer(
                name="ClassificationError503",
                fields={
                    "error": serializers.CharField(default="Modelo de classificação não está disponível.")
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Recebe o texto do email (via JSON ou upload de arquivo), 
        classifica e retorna o resultado em JSON.
        """
        email_text = ''
        
        # Verifica se um arquivo foi enviado
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            email_text, error = self.extract_text_from_file(uploaded_file)
            
            if error:
                return JsonResponse({'error': error}, status=400)
            
            if not email_text:
                return JsonResponse(
                    {'error': 'O arquivo está vazio ou não contém texto extraível.'},
                    status=400
                )
        
        # Se nenhum arquivo foi enviado, tenta obter o texto do corpo do JSON
        else:
            try:
                data = json.loads(request.body)
                email_text = data.get('email_text', '').strip()
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'JSON inválido ou nenhum dado fornecido.'},
                    status=400
                )
        
        # Valida se há texto para processar
        if not email_text:
            return JsonResponse(
                {'error': 'Nenhum texto de email fornecido.'}, 
                status=400
            )
        
        # Obtém o classificador
        classifier = self.get_classifier()
        
        if not classifier:
            return JsonResponse(
                {'error': 'Modelo de classificação não está disponível.'}, 
                status=503
            )
        
        # Processa a classificação
        try:
            candidate_labels = ["Produtivo", "Improdutivo"]
            classification_result = classifier(email_text, candidate_labels)
            
            classification = classification_result['labels'][0]
            confidence = classification_result['scores'][0]
            
            # Define a resposta sugerida baseada na classificação
            if classification == "Produtivo":
                suggested_response = (
                    "Obrigado pelo seu email. Estamos analisando sua solicitação "
                    "e retornaremos em breve."
                )
            else:
                suggested_response = "Obrigado pela sua mensagem!"
            
            return JsonResponse({
                'classification': classification,
                'confidence': round(confidence * 100, 2),  # Confiança em %
                'suggested_response': suggested_response
            })
            
        except Exception as e:
            logger.error(f"Erro durante a classificação do email: {e}")
            return JsonResponse(
                {'error': 'Ocorreu um erro ao processar o email.', 'details': str(e)}, 
                status=500
            )