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

from .email_scripts import EmailClassifier, EmailResponseGenerator

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
            # Classifica o email usando a nova arquitetura
            classification = self.email_classifier.classify(email_text)
            
            # Gera resposta automática
            suggested_response = self.response_generator.generate_response(
                classification['categoria'],
                classification['subcategoria'],
                classification['tom'],
                classification['urgencia']
            )
            
            logger.info(f"Email classificado: {classification['subcategoria']} - {classification['categoria']} | {classification.get('reasoning', '')}")
            
            return JsonResponse({
                'topic': classification['subcategoria'],
                'category': classification['categoria'],
                'confidence': classification.get('confianca', 0.85),
                'tone': classification['tom'],
                'urgency': classification['urgencia'],
                'suggested_response': suggested_response
            })
            
        except Exception as e:
            logger.error(f"Erro durante a classificação do email: {e}")
            return JsonResponse(
                {'error': 'Ocorreu um erro ao processar o email.', 'details': str(e)}, 
                status=500
            )