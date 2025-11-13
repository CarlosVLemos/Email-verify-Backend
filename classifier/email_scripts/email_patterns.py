"""
Padrões de palavras-chave para classificação de emails
Separado para facilitar manutenção e evitar código duplicado
"""

class EmailPatterns:
    """Contém todos os padrões de classificação organizados por categoria"""
    
    PRODUTIVO = {
        'urgente': [
            'urgente', 'emergência', 'emergencial', 'crítico', 'crítica', 'imediato', 'imediata',
            'agora', 'hoje', 'já', 'asap', 'prioridade máxima', 'prioridade alta', 'sem demora', 
            'rapidamente', 'o mais rápido possível', 'com urgência', 'pressa', 'tempo esgotando',
            'prazo vencendo', 'deadline', 'não pode esperar', 'situação grave', 'caso grave',
            'precisa ser hoje', 'para ontem', 'super urgente', 'muito urgente'
        ],
        'suporte_tecnico': [
            'problema', 'erro', 'bug', 'falha', 'não funciona', 'quebrou', 'travou', 'parou',
            'suporte técnico', 'assistência técnica', 'help desk', 'sistema fora', 'fora do ar',
            'login', 'senha', 'password', 'acesso negado', 'sem acesso', 'bloqueado',
            'conexão', 'servidor', 'instalação', 'configuração', 'update', 'atualização',
            'backup', 'restaurar', 'recovery', 'manutenção', 'erro 404', 'erro 500',
            'não carrega', 'lento', 'travando', 'crashou', 'não abre', 'não salva',
            'perdeu dados', 'corrompido', 'vírus', 'malware', 'antivírus', 'firewall',
            'rede', 'internet', 'wi-fi', 'wifi', 'conectividade', 'offline', 'online',
            'banco de dados', 'database', 'sql', 'query', 'tabela', 'campo',
            'api', 'integração', 'webhook', 'ssl', 'certificado', 'https', 'segurança',
            'backup perdido', 'não sincroniza', 'versão antiga', 'incompatível'
        ],
        'solicitacao': [
            'solicito', 'preciso', 'necessito', 'gostaria', 'poderia', 'favor', 'pedido',
            'requisição', 'demanda', 'requerer', 'pedir', 'solicitar', 'requer',
            'por favor', 'se possível', 'quando possível', 'me ajude', 'ajuda',
            'orientação', 'direcionamento', 'informação', 'dados', 'relatório',
            'documento', 'arquivo', 'planilha', 'acesso a', 'permissão para',
            'autorização', 'liberação', 'aprovação', 'validação', 'confirmação',
            'orçamento', 'cotação', 'proposta', 'contrato', 'acordo',
            'reunião', 'agendamento', 'marcar', 'agendar', 'disponibilidade',
            'treinamento', 'capacitação', 'curso', 'workshop', 'tutorial',
            'manual', 'guia', 'passo a passo', 'instruções', 'procedimento'
        ],
        'reclamacao': [
            'reclamação', 'reclamar', 'insatisfeito', 'insatisfação', 'descontente',
            'irritado', 'chateado', 'decepcionado', 'decepção', 'frustrado', 'frustração',
            'inaceitável', 'absurdo', 'revoltante', 'revolta', 'indignado', 'indignação',
            'péssimo atendimento', 'mau atendimento', 'atendimento ruim', 'mal atendido',
            'demora excessiva', 'muito tempo', 'esperando há', 'sem retorno',
            'não resolveram', 'não solucionaram', 'problema não resolvido',
            'qualidade baixa', 'baixa qualidade', 'defeituoso', 'com defeito',
            'não funciona direito', 'funcionamento irregular', 'instável',
            'cobrança indevida', 'cobrança errada', 'valor incorreto', 'preço abusivo',
            'falta de comunicação', 'não informaram', 'falta transparência',
            'descaso', 'negligência', 'irresponsabilidade', 'incompetência',
            'prejudicado', 'lesado', 'enganado', 'ludibriado', 'mentira'
        ],
        'duvida': [
            'dúvida', 'duvida', 'pergunta', 'questão', 'questionamento', 
            'como', 'quando', 'onde', 'por que', 'porque', 'qual', 'quais',
            'não entendo', 'não compreendo', 'não sei', 'desconheço',
            'explicar', 'esclarecer', 'esclarecimento', 'orientação', 'direcionamento',
            'me tire uma dúvida', 'poderia esclarecer', 'gostaria de saber',
            'informação sobre', 'detalhes sobre', 'mais informações',
            'como funciona', 'como usar', 'como fazer', 'modo de usar',
            'passo a passo', 'tutorial', 'instruções', 'manual',
            'o que significa', 'significado de', 'definição de',
            'diferença entre', 'comparação', 'qual melhor', 'recomendação',
            'sugestão', 'opinião', 'parecer', 'avaliação', 'análise'
        ],
        'felicitacoes': [
            'parabéns pelo projeto', 'parabéns pela conquista', 'parabéns pelo sucesso',
            'felicitações pelo trabalho', 'felicitações pela promoção', 
            'parabenizo pela conquista', 'parabenizo pelo resultado',
            'sucesso merecido', 'excelente resultado', 'ótimo desempenho',
            'trabalho excepcional', 'dedicação admirável', 'esforço reconhecido',
            'conquista importante', 'marco alcançado', 'objetivo atingido',
            'meta cumprida', 'resultado fantástico', 'performance excelente',
            'parabéns pela graduação', 'parabéns pela formatura', 'parabéns pelo casamento',
            'parabéns pelo nascimento', 'parabéns pelo aniversário', 'parabéns pela promoção',
            'parabéns pela nova casa', 'parabéns pelo novo emprego', 'parabéns pela aposentadoria',
            'felicitações sinceras', 'felicitações calorosas', 'meus cumprimentos',
            'reconhecimento merecido', 'orgulho do resultado', 'inspirador',
            'exemplo a seguir', 'referência na área', 'profissional exemplar'
        ],
        'comunicacao_trabalho': [
            'status do projeto', 'progresso do projeto', 'atualização do projeto', 'update do projeto',
            'andamento', 'desenvolvimento', 'evolução', 'status', 'progresso', 'avanço',
            'equipe', 'time', 'grupo de trabalho', 'colaboradores', 'membros',
            'coordenação', 'coordenar', 'organizar', 'planejar', 'programar',
            'ação necessária', 'ação requerida', 'próximos passos', 'próximas etapas',
            'prazo', 'deadline', 'cronograma', 'agenda', 'planejamento',
            'responsabilidade', 'responsável por', 'encarregado de', 'designado para',
            'tarefa', 'task', 'atividade', 'demanda', 'entrega', 'deliverable',
            'meta', 'objetivo', 'alvo', 'resultado esperado', 'expectativa',
            'projeto atlas', 'projeto', 'iniciativa', 'programa', 'campanha',
            'reunião de acompanhamento', 'follow-up', 'followup', 'alinhamento',
            'situação atual', 'estado atual', 'ponto de situação', 'report',
            'relatório de progresso', 'relatório de status', 'resumo executivo',
            'milestone', 'marco', 'etapa concluída', 'fase finalizada',
            'implementação', 'execução', 'realização', 'operacionalização',
            'recursos necessários', 'recursos alocados', 'orçamento', 'budget',
            'stakeholders', 'partes interessadas', 'envolvidos', 'participantes'
        ]
    }
    
    IMPRODUTIVO = {
        'entretenimento': [
            # Conteúdo recreativo/diversão
            'meme', 'memes', 'vídeo engraçado', 'vídeo hilário', 'chorei de rir',
            'piada', 'piadas', 'zueira', 'zoeira', 'risada', 'humor',
            'gatinho', 'gatinhos', 'gato', 'gatos', 'cachorro', 'cachorros', 'pet',
            'fofo', 'fofinho', 'cute', 'gracinha', 'amor', 'amorzinho',
            'nada a ver com trabalho', 'pausa no café', 'vale a pausa', 'distração',
            'alegrar seu dia', 'para relaxar', 'descontrair', 'dar risada',
            'momento de lazer', 'intervalo', 'descanso mental',
            'viu esse vídeo', 'viu esse meme', 'viu essa foto',
            'compartilhando', 'compartilhar', 'achei engraçado',
            'não resisti', 'tinha que compartilhar', 'muito bom',
            'receita de bolo', 'dica de filme', 'série nova', 'música',
            'jogo', 'game', 'gameplay', 'diversão', 'entretenimento'
        ],
        'spam': [
            'ganhe dinheiro', 'dinheiro grátis', 'renda extra', 'milhões de reais',
            'prêmio em dinheiro', 'sortudo', 'vencedor', 'contemplado', 'grande prêmio',
            'loteria', 'mega sena', 'sorteio internacional', 'herança milionária',
            'fortuna esperando', 'beneficiário', 'herdeiro', 'testamento',
            'banco central', 'reserva internacional', 'fundo de investimento',
            'transferência urgente', 'liberação de valores', 'resgate imediato',
            'clique aqui', 'clique agora', 'confirme agora', 'prazo limitado',
            'oportunidade única', 'não perca', 'últimas horas', 'resgatar prêmio',
            'oferta expira', 'tempo limitado', 'apenas hoje', 'promoção relâmpago',
            'últimas vagas', 'últimas unidades', 'estoque limitado', 'queima de estoque',
            'desconto imperdível', 'preço promocional', 'liquidação total',
            'r$', 'reais', '$$', 'taxa de liberação', 'pequena taxa', 'taxa administrativa',
            'transferência', 'reembolsado', 'cashback', 'pix grátis', 'cartão pré-pago',
            'iphone', 'celular grátis', 'smartphone novo', 'tablet grátis',
            'vale-compras', 'cupom desconto', 'gift card', 'cartão presente',
            'você foi sorteado', 'endereço sorteado', 'lista privilegiada', 'cliente vip',
            'promoção anual', 'fidelidade', 'campanha recente', 'sorteio automático',
            'sistema aleatório', 'base de dados', 'endereços selecionados',
            'fantástica', 'incrível', 'mudou de vida', 'garantido', 'suporte 24h',
            'sem custo', 'totalmente grátis', 'zero taxa', 'isento de impostos',
            'bit.ly', 'tinyurl', 'encurtador', 'link suspeito', 'clique no link',
            'baixe agora', 'download grátis', 'instale já', 'acesse o site',
            'cadastre-se já', 'registre-se agora', 'crie sua conta',
            'auxílio emergencial', 'pis/pasep', 'fgts liberado', 'ir restituição',
            'serasa limpo', 'cpf regularizado', 'score aumentado', 'crédito aprovado',
            'empréstimo pré-aprovado', 'cartão sem anuidade', 'conta digital',
            'congratulations', 'winner', 'lottery', 'prize', 'claim', 'beneficiary',
            'inheritance', 'million dollars', 'usd', 'euros', 'pounds',
            'click here', 'urgent', 'confidential', 'business proposal'
        ],
        'marketing': [

            'mega promoção', 'super promoção', 'promoção imperdível', 'último dia',
            'oferta especial', 'promoção exclusiva', 'desconto imperdível', 'liquidação',
            '70% desconto', '50% desconto', 'desconto de', '% off',
            'aproveite antes que acabe', 'últimas horas', 'hoje é o último dia',
            'compre agora', 'adquira já', 'aproveite a oferta', 'não perca',
            'acesse agora', 'clique para comprar', 'visite nosso site',
            'últimas peças', 'últimas vagas', 'oferta limitada', 'tempo limitado',
            'carrinho de compras', 'finalizar compra', 'checkout', 'adicionar ao carrinho',
            'frete grátis', 'entrega gratuita', 'parcelamento sem juros', 'à vista',
            'cashback', 'pontos de fidelidade', 'programa de recompensas',
            'newsletter', 'boletim informativo', 'novidades da loja', 'novidades do site',
            'inscreva-se', 'cadastre-se', 'receba ofertas', 'seja o primeiro',
            'curtir', 'compartilhar', 'seguir nas redes', 'like', 'comentar',
            'catálogo', 'vitrine virtual', 'showroom online', 'lançamento do produto',
            'nova coleção', 'temporada', 'black friday', 'cyber monday',
            'dia das mães', 'dia dos pais', 'natal', 'ano novo',
            'webinar gratuito', 'workshop pago', 'curso online', 'treinamento comercial',
            'evento de lançamento', 'feira virtual', 'exposição online',
            'descadastrar', 'unsubscribe', 'cancelar inscrição', 'parar de receber',
            'política de privacidade comercial', 'termos comerciais', 'lgpd marketing',
            'patrocinado', 'anúncio', 'publicidade', 'propaganda', 'divulgação comercial'
        ],
        'agradecimento': [
            'muito obrigado pela ajuda', 'obrigado pelo suporte', 'obrigada pelo atendimento',
            'agradeço', 'agradecimento', 'gratidão', 'grato pela atenção', 'grata',
            'reconhecimento', 'muito grato', 'imensamente grato', 'eternamente grato',
            'do fundo do coração', 'sinceros agradecimentos', 'profunda gratidão',
            'não tenho palavras', 'sem palavras para agradecer', 'deus abençoe',
            'que deus abençoe', 'muito gentil', 'muita gentileza', 'bondade',
            'generosidade', 'dedicação', 'paciência', 'compreensão', 'apoio',
            'ajuda valiosa', 'contribuição importante', 'fez a diferença',
            'salvou minha vida', 'resolveu meu problema', 'tirou um peso',
            'aliviou minha preocupação', 'tranquilizou', 'acalmou'
        ]
    }
    
    TOM = {
        'positivo': [
            'ótimo', 'excelente', 'obrigado', 'obrigada', 'parabéns', 'satisfeito', 'satisfeita',
            'feliz', 'alegre', 'contente', 'bom', 'boa', 'maravilhoso', 'maravilhosa',
            'fantástico', 'fantástica', 'perfeito', 'perfeita', 'incrível', 'espetacular',
            'sensacional', 'admirável', 'impressionante', 'surpreendente', 'excepcional',
            'extraordinário', 'magnífico', 'sublime', 'divino', 'formidável',
            'gratidão', 'reconhecimento', 'apreço', 'valorização', 'elogio',
            'felicitações', 'cumprimentos', 'congratulações', 'sucesso', 'conquista',
            'vitória', 'triunfo', 'realização', 'êxito', 'glória',
            'adorei', 'amei', 'gostei muito', 'aprovei', 'recomendo',
            'super', 'mega', 'ultra', 'hiper', 'top', 'show', 'demais',
            'legal', 'bacana', 'massa', 'maneiro', 'genial', 'brilliant'
        ],
        'negativo': [
            'ruim', 'péssimo', 'péssima', 'problema', 'erro', 'insatisfeito', 'insatisfeita',
            'horrível', 'terrível', 'inaceitável', 'frustrante', 'irritante', 'chateado', 'chateada',
            'decepcionado', 'decepcionada', 'descontente', 'indignado', 'indignada',
            'revoltado', 'revoltada', 'furioso', 'furiosa', 'nervoso', 'nervosa',
            'estressado', 'estressada', 'aborrecido', 'aborrecida', 'desanimado', 'desanimada',
            'triste', 'melancólico', 'deprimido', 'angustiado', 'preocupado', 'preocupada',
            'ansioso', 'ansiosa', 'tenso', 'tensa', 'aflito', 'aflita',
            'absurdo', 'inadmissível', 'intolerável', 'revoltante', 'indignante',
            'lamentável', 'deplorável', 'vergonhoso', 'constrangedor', 'embaraçoso',
            'desastroso', 'catastrófico', 'caótico', 'complicado', 'difícil',
            'impossível', 'impraticável', 'inviável', 'irrealizável', 'falho',
            'defeituoso', 'prejudicial', 'nocivo', 'danoso', 'negativo'
        ]
    }
    
    URGENCIA = {
        'alta': [
            'urgente', 'emergência', 'emergencial', 'crítico', 'crítica', 'imediato', 'imediata',
            'agora', 'já', 'hoje', 'asap', 'rapidamente', 'sem demora', 'o mais rápido possível',
            'com urgência', 'pressa', 'tempo esgotando', 'prazo vencendo', 'deadline vencendo',
            'não pode esperar', 'situação grave', 'caso grave', 'precisa ser hoje',
            'para ontem', 'super urgente', 'muito urgente', 'extremamente urgente',
            'máxima prioridade', 'prioridade máxima', 'prioridade alta', 'alta prioridade',
            'situação crítica', 'estado crítico', 'condição crítica', 'momento crítico',
            'crise', 'catástrofe', 'desastre', 'calamidade', 'tragédia',
            'prazo até', 'deadline até', 'vence hoje', 'vence amanhã', 'expira hoje',
            'expira amanhã', 'limite hoje', 'limite amanhã', 'fim do prazo',
            'último dia', 'data limite', 'data final', 'encerramento hoje'
        ],
        'media': [
            'importante', 'necessário', 'necessária', 'breve', 'logo', 'em breve',
            'prioridade', 'significativo', 'significativa', 'relevante', 'essencial',
            'fundamental', 'crucial', 'vital', 'indispensável', 'imprescindível',
            'quando possível', 'se possível', 'assim que possível', 'na primeira oportunidade',
            'preferencialmente', 'de preferência', 'seria bom', 'seria interessante',
            'convém', 'recomenda-se', 'sugere-se', 'aconselhável', 'desejável',
            'prazo', 'deadline', 'cronograma', 'agenda', 'data prevista',
            'até sexta', 'até segunda', 'esta semana', 'próxima semana',
            'ação necessária', 'ação requerida', 'resposta necessária', 'feedback necessário',
            'coordenação necessária', 'decisão necessária', 'aprovação necessária'
        ],
        'baixa': [
            'quando der', 'sem pressa', 'no seu tempo', 'quando puder',
            'tranquilo', 'calma', 'relaxe', 'sem stress', 'sem pressão',
            'eventualmente', 'futuramente', 'mais tarde', 'depois',
            'não é urgente', 'pode esperar', 'sem urgência'
        ]
    }

    FELICITACOES_GENUINAS = [
        'parabéns pelo', 'parabéns pela', 'felicitações pelo', 'felicitações pela',
        'parabenizo pelo', 'parabenizo pela', 'cumprimentos pelo', 'cumprimentos pela',
        'meus parabéns pelo', 'meus parabéns pela', 'congratulo pelo', 'congratulo pela'
    ]
    
    CONTEXTOS_PROFISSIONAIS = [
        'projeto', 'trabalho', 'conquista', 'sucesso', 'resultado', 'desempenho',
        'graduação', 'formatura', 'promoção', 'novo emprego', 'aposentadoria',
        'casamento', 'nascimento', 'aniversário', 'nova casa', 'empresa',
        'negócio', 'carreira', 'profissional', 'acadêmico', 'pessoal'
    ]
    
    SPAM_SUSPEITO_FORTE = [
        'você foi sorteado', 'ganhou um prêmio', 'contemplado com',
        'vencedor de', 'beneficiário de', 'herdeiro de', 'sorteio automático',
        'clique para resgatar', 'confirme seus dados', 'taxa de liberação'
    ]
    
    # 🆕 Padrões de contexto com REGEX para detecção precisa
    CONTEXT_PATTERNS = {
        'marketing_strong': [
            r'\d+%\s*(de\s*)?desconto',  # "50% desconto", "70% de desconto"
            r'desconto\s+de\s+\d+%',      # "desconto de 50%"
            r'compre\s+\d+\s+leve\s+\d+', # "compre 1 leve 2"
            r'frete\s+gr[aá]tis',         # "frete grátis"
            r'por\s+apenas\s+R?\$?\s*\d+', # "por apenas R$ 99"
            r'[uú]ltimas?\s+unidades?',   # "últimas unidades"
            r'mega\s+promo[çc][aã]o',     # "mega promoção"
            r'super\s+oferta',            # "super oferta"
            r'oferta\s+imperd[ií]vel',    # "oferta imperdível"
            r'at[eé]\s+\d+%\s+off',       # "até 70% off"
        ],
        'marketing_negative': [  # Indicadores de que NÃO é marketing comercial
            r'reuni[aã]o\s+(de|do|sobre)\s+trabalho',
            r'projeto\s+(interno|da\s+empresa)',
            r'equipe\s+(de|do)\s+\w+',  # "equipe de desenvolvimento"
            r'discuss[aã]o\s+sobre',
            r'planejamento\s+de',
        ],
        'spam_strong': [
            r'voc[eê]\s+ganhou',          # "você ganhou"
            r'parab[eé]ns!?\s+voc[eê]\s+foi\s+selecionado',
            r'clique\s+aqui\s+(agora|j[aá])',
            r'confirme\s+seus\s+dados',
            r'atualize\s+suas\s+informa[çc][õo]es',
            r'sua\s+conta\s+foi\s+bloqueada',
            r'taxa\s+de\s+libera[çc][aã]o',
        ],
        'work_context': [  # Contexto de trabalho genuíno
            r'(nossa|nosso)\s+(equipe|time|projeto)',
            r'reuni[aã]o\s+(de|sobre|do)',
            r'prazo\s+(de\s+entrega|do\s+projeto)',
            r'apresenta[çc][aã]o\s+para',
            r'(sprint|retrospectiva|planning)',
            r'demanda\s+(urgente|priorit[aá]ria)',
        ],
        'entertainment_strong': [
            r'(meme|gatinhos?|v[ií]deo)\s+(engra[çc]ado|fofo)',
            r'chorei\s+de\s+rir',
            r'nada\s+a\s+ver\s+com\s+trabalho',
            r'vale\s+a\s+pausa',
            r'alegrar\s+seu\s+dia',
        ]
    }

    @classmethod
    def check_regex_patterns(cls, text: str, pattern_category: str) -> tuple:
        """
        Verifica padrões regex em uma categoria
        
        Returns:
            (matches_count, matched_patterns)
        """
        import re
        patterns = cls.CONTEXT_PATTERNS.get(pattern_category, [])
        matches = []
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        
        return len(matches), matches

    @classmethod
    def get_all_spam_keywords(cls):
        return cls.IMPRODUTIVO['spam']
    
    @classmethod
    def get_all_productive_keywords(cls):
        all_keywords = []
        for keywords in cls.PRODUTIVO.values():
            all_keywords.extend(keywords)
        return all_keywords
    
    @classmethod
    def is_genuine_congratulation(cls, text):
        text_lower = text.lower()
        has_genuine_pattern = any(pattern in text_lower for pattern in cls.FELICITACOES_GENUINAS)
        has_professional_context = any(context in text_lower for context in cls.CONTEXTOS_PROFISSIONAIS)
        has_spam_pattern = any(spam in text_lower for spam in cls.SPAM_SUSPEITO_FORTE)
        return has_genuine_pattern and has_professional_context and not has_spam_pattern
    
    @classmethod
    def has_suspicious_spam_patterns(cls, text):
        text_lower = text.lower()
        spam_count = sum(1 for spam in cls.SPAM_SUSPEITO_FORTE if spam in text_lower)
        return spam_count >= 2
    
    @classmethod
    def get_context_score(cls, text, category):
        text_lower = text.lower()
        
        if category in cls.PRODUTIVO:
            keywords = cls.PRODUTIVO[category]
        elif category in cls.IMPRODUTIVO:
            keywords = cls.IMPRODUTIVO[category]
        else:
            return 0
            
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        word_count = len(text_lower.split())
        if word_count == 0:
            return 0
            
        return (matches / word_count) * 100