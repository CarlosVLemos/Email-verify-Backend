"""
Padrões de palavras-chave para classificação de emails
Separado para facilitar manutenção e evitar código duplicado
"""

class EmailPatterns:
    """Contém todos os padrões de classificação organizados por categoria"""
    
    
    PRODUTIVO = {
        'urgente': [
            'urgente', 'emergência', 'crítico', 'imediato', 'agora', 'hoje',
            'asap', 'prioridade máxima', 'sem demora', 'rapidamente'
        ],
        'suporte_tecnico': [
            'problema', 'erro', 'bug', 'falha', 'não funciona', 'quebrou', 'travou',
            'suporte técnico', 'assistência técnica', 'sistema fora', 'login',
            'senha', 'acesso negado', 'conexão', 'servidor', 'instalação'
        ],
        'solicitacao': [
            'solicito', 'preciso', 'gostaria', 'poderia', 'favor', 'pedido',
            'requisição', 'demanda', 'necessito', 'requerer', 'pedir'
        ],
        'reclamacao': [
            'reclamação', 'insatisfeito', 'descontente', 'irritado', 'chateado',
            'decepcionado', 'inaceitável', 'absurdo', 'revoltante', 'péssimo atendimento'
        ],
        'duvida': [
            'dúvida', 'pergunta', 'questão', 'como', 'quando', 'onde', 'por que', 'qual',
            'não entendo', 'não sei', 'explicar', 'esclarecer', 'orientação'
        ],
        'felicitacoes': [
            'parabéns pelo projeto', 'felicitações pelo trabalho', 'parabenizo pela conquista',
            'sucesso merecido', 'excelente resultado', 'ótimo desempenho'
        ]
    }
    
    
    IMPRODUTIVO = {
        'spam': [
            
            'ganhe dinheiro', 'dinheiro grátis', 'renda extra', 'milhões de reais',
            'prêmio em dinheiro', 'sortudo', 'vencedor', 'contemplado', 'grande prêmio',
            
            
            'clique aqui', 'clique agora', 'confirme agora', 'prazo limitado',
            'oportunidade única', 'não perca', 'últimas horas', 'resgatar prêmio',
            
            
            'r$', 'reais', '$$', 'taxa de liberação', 'pequena taxa',
            'transferência', 'reembolsado', 'iphone', 'celular grátis',
            
            
            'você foi sorteado', 'endereço sorteado', 'lista privilegiada',
            'promoção anual', 'fidelidade', 'campanha recente', 'fantástica',
            'incrível', 'mudou de vida', 'garantido', 'suporte 24h',
            
            
            'https://', 'www.', '.com/', 'sitefake', 'claim', 'prize'
        ],
        'marketing': [
            'oferta', 'promoção', 'desconto', 'venda', 'produto', 'serviço',
            'comprar', 'newsletter', 'campanha', 'lançamento', 'novidade comercial',
            'oportunidade de negócio', 'investimento', 'catálogo'
        ],
        'agradecimento': [
            'muito obrigado pela ajuda', 'obrigado pelo suporte', 'agradeço',
            'gratidão', 'grato pela atenção', 'obrigada pelo atendimento'
        ]
    }
    
    
    TOM = {
        'positivo': [
            'ótimo', 'excelente', 'obrigado', 'parabéns', 'satisfeito', 
            'feliz', 'bom', 'maravilhoso', 'fantástico', 'perfeito'
        ],
        'negativo': [
            'ruim', 'péssimo', 'problema', 'erro', 'insatisfeito', 
            'horrível', 'terrível', 'inaceitável', 'frustrante'
        ]
    }
    
    
    URGENCIA = {
        'alta': [
            'urgente', 'emergência', 'crítico', 'imediato', 'agora', 
            'hoje', 'asap', 'rapidamente', 'sem demora'
        ],
        'media': [
            'importante', 'necessário', 'breve', 'logo', 'em breve'
        ]
    }

    @classmethod
    def get_all_spam_keywords(cls):
        """Retorna todas as palavras-chave de spam em uma lista única"""
        return cls.IMPRODUTIVO['spam']
    
    @classmethod
    def get_all_productive_keywords(cls):
        """Retorna todas as palavras-chave produtivas"""
        all_keywords = []
        for keywords in cls.PRODUTIVO.values():
            all_keywords.extend(keywords)
        return all_keywords