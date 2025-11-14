"""
Gerador de respostas automáticas para emails classificados
Responsabilidade única: gerar respostas baseadas na classificação
"""


class EmailResponseGenerator:
    """Gera respostas automáticas personalizadas baseadas na classificação do email"""
    
    def __init__(self):
        self.response_templates = {
            
            'Urgente': {
                'Alta': "Recebemos sua mensagem urgente e nossa equipe foi imediatamente notificada. Entraremos em contato o mais rápido possível.",
                'Média': "Sua mensagem foi registrada com prioridade. Nossa equipe entrará em contato em breve.",
                'Baixa': "Mensagem recebida e registrada. Retornaremos assim que possível."
            },
            'Suporte Técnico': {
                'Alta': "Recebemos sua solicitação de suporte técnico urgente. Nossa equipe técnica foi notificada e entrará em contato imediatamente.",
                'Média': "Obrigado pelo contato. Nossa equipe de suporte técnico analisará sua questão e retornará em breve.", 
                'Baixa': "Sua solicitação de suporte foi recebida. Retornaremos com uma solução assim que possível."
            },
            'Reclamação': {
                'Alta': "Lamentamos profundamente o inconveniente causado. Sua questão foi marcada como prioridade máxima e nossa equipe especializada entrará em contato imediatamente.",
                'Média': "Lamentamos o inconveniente. Sua reclamação foi registrada e nossa equipe entrará em contato em breve para resolver a questão.",
                'Baixa': "Obrigado pelo seu feedback. Registramos sua observação e trabalharemos para melhorar."
            },
            
            
            'Dúvida': "Obrigado pela sua pergunta. Nossa equipe analisará sua dúvida e retornará com esclarecimentos detalhados em breve.",
            'Solicitação': "Recebemos sua solicitação e estamos analisando. Retornaremos com uma resposta assim que possível.",
            'Felicitações': "Muito obrigado pelas felicitações! Ficamos honrados com o reconhecimento e satisfeitos em saber que nosso trabalho foi bem-sucedido.",
            'Agradecimento': "Ficamos muito felizes com seu agradecimento! É uma grande satisfação saber que pudemos ajudá-lo.",
            'Marketing': "Obrigado pelo interesse demonstrado. Nossa equipe comercial poderá entrar em contato para mais detalhes.",
            'Informativo': "Obrigado pela informação. Registramos seu comunicado e tomaremos as medidas apropriadas se necessário.",
            'Spam': "Email identificado como spam - nenhuma resposta será enviada.",
            'Urgente': {
                'Alta': "Recebemos sua mensagem urgente e nossa equipe foi imediatamente notificada. Entraremos em contato o mais rápido possível.",
                'Média': "Sua mensagem foi registrada com prioridade. Nossa equipe entrará em contato em breve.",
                'Baixa': "Mensagem recebida e registrada. Retornaremos assim que possível."
            },
            'Suporte Técnico': {
                'Alta': "Recebemos sua solicitação de suporte técnico urgente. Nossa equipe técnica foi notificada e entrará em contato imediatamente.",
                'Média': "Obrigado pelo contato. Nossa equipe de suporte técnico analisará sua questão e retornará em breve.",
                'Baixa': "Sua solicitação de suporte foi recebida. Retornaremos com uma solução assim que possível."
            },
            'Reclamação': {
                'Alta': "Lamentamos profundamente o inconveniente causado. Sua questão foi marcada como prioridade máxima e nossa equipe especializada entrará em contato imediatamente.",
                'Média': "Lamentamos o inconveniente. Sua reclamação foi registrada e nossa equipe entrará em contato em breve para resolver a questão.",
                'Baixa': "Obrigado pelo seu feedback. Registramos sua observação e trabalharemos para melhorar."
            },
            'Nova Categoria': "Adicionamos uma nova categoria para respostas mais específicas."
        }
    
    def generate_response(self, categoria, subcategoria, tom, urgencia):
        """
        Gera resposta automática baseada na classificação
        
        Args:
            categoria: 'Produtivo' ou 'Improdutivo'
            subcategoria: Tipo específico do email
            tom: 'Positivo', 'Negativo' ou 'Neutro'
            urgencia: 'Alta', 'Média' ou 'Baixa'
            
        Returns:
            str: Resposta automática personalizada
        """
        
        
        if subcategoria == 'Spam':
            return "Email identificado como spam - nenhuma resposta será enviada."
        
        
        if subcategoria in ['Urgente', 'Suporte Técnico', 'Reclamação']:
            
            base_response = self.response_templates[subcategoria].get(
                urgencia, 
                self.response_templates[subcategoria]['Baixa']
            )
        else:
            
            base_response = self.response_templates.get(
                subcategoria, 
                self._get_default_response(categoria)
            )
        
        
        return self._personalize_response(base_response, categoria, subcategoria, tom, urgencia)
    
    def _get_default_response(self, categoria):
        """Retorna resposta padrão baseada na categoria principal"""
        if categoria == 'Produtivo':
            return "Obrigado pelo seu contato. Recebemos sua mensagem e nossa equipe está analisando. Retornaremos com uma resposta apropriada em breve."
        else:
            return "Obrigado pela sua mensagem. Ficamos felizes com seu contato e continuamos à disposição para qualquer necessidade futura."
    
    def _personalize_response(self, base_response, categoria, subcategoria, tom, urgencia):
        """Personaliza a resposta baseada no contexto"""
        response = base_response
        
        
        if tom == 'Negativo' and categoria == 'Produtivo' and subcategoria != 'Reclamação':
            if 'Lamentamos' not in response:
                response = "Lamentamos qualquer inconveniente. " + response
        
        
        elif tom == 'Positivo' and categoria == 'Improdutivo':
            response = response.replace("Obrigado", "Muito obrigado")
        
        
        if urgencia == 'Alta' and subcategoria not in ['Urgente', 'Suporte Técnico', 'Reclamação', 'Felicitações']:
            response = response.replace("em breve", "com prioridade")
        
        
        if subcategoria == 'Felicitações' and urgencia == 'Alta':
            pass
            
        return response
    
    def get_response_type(self, subcategoria):
        """
        Retorna o tipo de resposta para métricas/analytics
        
        Returns:
            str: 'automated', 'no_response', 'escalated'
        """
        if subcategoria == 'Spam':
            return 'no_response'
        elif subcategoria in ['Urgente', 'Reclamação']:
            return 'escalated'
        else:
            return 'automated'