"""
Serializers para Classifier API
Validação de entrada e formatação de saída
"""
from rest_framework import serializers


class EmailTextInputSerializer(serializers.Serializer):
    """Serializer para entrada de texto de email"""
    email_text = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=10,
        max_length=50000,
        help_text="Texto do email para classificar (mínimo 10 caracteres)",
        error_messages={
            'required': 'O campo email_text é obrigatório',
            'blank': 'O texto do email não pode estar vazio',
            'min_length': 'O texto deve ter pelo menos 10 caracteres',
            'max_length': 'O texto não pode exceder 50000 caracteres'
        }
    )


class EmailFileInputSerializer(serializers.Serializer):
    """Serializer para upload de arquivo"""
    file = serializers.FileField(
        required=True,
        help_text="Arquivo de email (.txt, .pdf, .docx)",
        error_messages={
            'required': 'Arquivo é obrigatório',
            'invalid': 'Arquivo inválido'
        }
    )


class AttachmentAnalysisSerializer(serializers.Serializer):
    """Serializer para análise de anexos"""
    has_attachments_mentioned = serializers.BooleanField(help_text="Se anexos foram mencionados no texto")
    attachment_keywords = serializers.ListField(
        child=serializers.CharField(),
        help_text="Palavras-chave relacionadas a anexos detectadas"
    )
    score = serializers.IntegerField(help_text="Score de relevância dos anexos (0-10)")


class EmailClassificationOutputSerializer(serializers.Serializer):
    """Serializer para saída de classificação de email"""
    topic = serializers.CharField(
        help_text="Subcategoria classificada (ex: 'Suporte Técnico', 'Agradecimento', 'Spam')"
    )
    category = serializers.CharField(
        help_text="Categoria principal: 'Produtivo', 'Social' ou 'Improdutivo'"
    )
    confidence = serializers.FloatField(
        allow_null=True,
        help_text="Score de confiança da classificação (0.0-1.0). Null para classificador baseado em regras"
    )
    tone = serializers.CharField(
        help_text="Tom detectado no email: 'Positivo', 'Negativo' ou 'Neutro'"
    )
    urgency = serializers.CharField(
        help_text="Nível de urgência: 'Alta', 'Média' ou 'Baixa'"
    )
    suggested_response = serializers.CharField(
        help_text="Sugestão de resposta automática baseada na análise"
    )
    attachment_analysis = AttachmentAnalysisSerializer(
        help_text="Análise de anexos mencionados no email"
    )
    word_count = serializers.IntegerField(
        help_text="Quantidade total de palavras no email"
    )
    char_count = serializers.IntegerField(
        help_text="Quantidade total de caracteres"
    )
    processing_time_ms = serializers.IntegerField(
        help_text="Tempo de processamento em milissegundos"
    )
    sender_email = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text="Email do remetente (se fornecido)"
    )
    sender_name = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Nome do remetente (se fornecido)"
    )


class SummaryInputSerializer(serializers.Serializer):
    """Serializer para entrada de resumo executivo"""
    email_text = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=100,
        max_length=50000,
        help_text="Texto do email para resumir (mínimo 100 caracteres para melhor resultado)",
        error_messages={
            'required': 'O campo email_text é obrigatório',
            'blank': 'O texto do email não pode estar vazio',
            'min_length': 'Para gerar um resumo útil, o texto deve ter pelo menos 100 caracteres',
            'max_length': 'O texto não pode exceder 50000 caracteres'
        }
    )
    max_sentences = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=10,
        help_text="Número máximo de frases no resumo (1-10, padrão: 3)",
        error_messages={
            'min_value': 'max_sentences deve ser pelo menos 1',
            'max_value': 'max_sentences não pode exceder 10'
        }
    )


class SummaryOutputSerializer(serializers.Serializer):
    """Serializer para saída de resumo executivo"""
    summary = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de frases que compõem o resumo"
    )
    key_points = serializers.ListField(
        child=serializers.CharField(),
        help_text="Pontos-chave extraídos (prazos, valores, ações requeridas)"
    )
    relevance_score = serializers.FloatField(
        help_text="Score de relevância do resumo (0.0-1.0)"
    )
    word_reduction = serializers.FloatField(
        help_text="Percentual de redução de palavras em relação ao original"
    )
    original_word_count = serializers.IntegerField(
        help_text="Quantidade de palavras no texto original"
    )
    summary_word_count = serializers.IntegerField(
        help_text="Quantidade de palavras no resumo gerado"
    )


class BatchEmailInputSerializer(serializers.Serializer):
    """Serializer para entrada de processamento em lote"""
    emails = serializers.ListField(
        child=serializers.CharField(min_length=10),
        required=True,
        min_length=1,
        max_length=50,
        help_text="Lista de textos de email para processar (máximo 50 emails)",
        error_messages={
            'required': 'A lista de emails é obrigatória',
            'min_length': 'Forneça pelo menos 1 email para processar',
            'max_length': 'O limite é de 50 emails por requisição'
        }
    )


class BatchEmailResultSerializer(serializers.Serializer):
    """Serializer para resultado individual de batch"""
    email_id = serializers.IntegerField(help_text="ID do email no batch")
    status = serializers.CharField(help_text="Status do processamento: 'success' ou 'error'")
    classification = EmailClassificationOutputSerializer(
        required=False,
        help_text="Resultado da classificação (se sucesso)"
    )
    error = serializers.CharField(
        required=False,
        help_text="Mensagem de erro (se falha)"
    )
    preview = serializers.CharField(
        help_text="Prévia do texto do email (primeiras palavras)"
    )


class BatchEmailOutputSerializer(serializers.Serializer):
    """Serializer para saída de processamento em lote"""
    request_id = serializers.CharField(
        help_text="ID único da requisição de batch"
    )
    total_emails = serializers.IntegerField(
        help_text="Total de emails processados"
    )
    successful = serializers.IntegerField(
        help_text="Quantidade de emails processados com sucesso"
    )
    failed = serializers.IntegerField(
        help_text="Quantidade de emails que falharam"
    )
    total_time_ms = serializers.IntegerField(
        help_text="Tempo total de processamento em milissegundos"
    )
    avg_time_per_email_ms = serializers.FloatField(
        help_text="Tempo médio por email em milissegundos"
    )
    results = serializers.ListField(
        child=BatchEmailResultSerializer(),
        help_text="Lista de resultados individuais"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respostas de erro padronizadas"""
    error = serializers.CharField(help_text="Mensagem de erro principal")
    details = serializers.CharField(
        required=False,
        help_text="Detalhes adicionais do erro (apenas em modo debug)"
    )
    field_errors = serializers.DictField(
        required=False,
        help_text="Erros específicos de campos (validação)"
    )


class HealthCheckSerializer(serializers.Serializer):
    """Serializer para health check da API"""
    status = serializers.CharField(help_text="Status da API: 'healthy' ou 'unhealthy'")
    version = serializers.CharField(help_text="Versão da API")
    timestamp = serializers.DateTimeField(help_text="Timestamp da verificação")
    services = serializers.DictField(
        help_text="Status de serviços dependentes (analytics, etc)"
    )


class ResponseHelper:
    """Classe auxiliar para formatação de respostas"""
    @staticmethod
    def format_error_response(error_message, field_errors=None):
        response = {'error': error_message}
        if field_errors:
            response['field_errors'] = field_errors
        return response

    @staticmethod
    def format_success_response(data):
        return data
