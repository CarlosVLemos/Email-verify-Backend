"""
Classificador de emails com lógica hierárquica
Responsabilidade única: classificar emails seguindo as regras de negócio
"""
from .email_patterns import EmailPatterns


class EmailClassifier:
    """
    Classificador hierárquico de emails que prioriza:
    1. Detecção de SPAM (prioridade máxima)
    2. Detecção de MARKETING
    3. Classificação PRODUTIVA/IMPRODUTIVA
    """
    
    def __init__(self):
        self.patterns = EmailPatterns()
        
    def classify(self, text):
        """
        Método principal de classificação
        Retorna dicionário com categoria, subcategoria, tom, urgência
        """
        text_lower = text.lower().strip()
        
        
        spam_result = self._check_spam(text_lower)
        if spam_result:
            return spam_result
            

        marketing_result = self._check_marketing(text_lower)  
        if marketing_result:
            return marketing_result
            
        
        thanks_result = self._check_simple_thanks(text_lower, text)
        if thanks_result:
            return thanks_result
            

        return self._classify_productive(text_lower, text)
    
    def _check_spam(self, text_lower):
        """Verifica se o email é spam usando múltiplos indicadores"""
        spam_score = 0
        
        for keyword in self.patterns.IMPRODUTIVO['spam']:
            if keyword in text_lower:
                spam_score += 3
                
        
        if spam_score >= 6:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Spam',
                'tom': 'Neutro',
                'urgencia': 'Baixa',
                'confianca': 0.95,
                'reasoning': f'Spam detectado (score: {spam_score})'
            }
        return None
    
    def _check_marketing(self, text_lower):
        """Verifica se é conteúdo de marketing"""
        marketing_score = sum(2 for keyword in self.patterns.IMPRODUTIVO['marketing'] if keyword in text_lower)
        
        
        if marketing_score >= 4:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Marketing', 
                'tom': self._detect_tone(text_lower),
                'urgencia': 'Baixa',
                'confianca': 0.85,
                'reasoning': 'Conteúdo comercial/marketing'
            }
        return None
    
    def _check_simple_thanks(self, text_lower, full_text):
        """Verifica se é apenas um agradecimento simples"""
        thanks_score = sum(2 for keyword in self.patterns.IMPRODUTIVO['agradecimento'] if keyword in text_lower)
        
        
        has_productive_content = any(
            keyword in text_lower 
            for keywords in self.patterns.PRODUTIVO.values()
            for keyword in keywords
        )
        
        
        if thanks_score >= 3 and not has_productive_content and len(full_text.split()) < 50:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Agradecimento',
                'tom': 'Positivo', 
                'urgencia': 'Baixa',
                'confianca': 0.90,
                'reasoning': 'Agradecimento simples sem solicitações'
            }
        return None
    
    def _classify_productive(self, text_lower, full_text):
        """Classifica emails produtivos (que requerem ação)"""
        category_scores = {}
        
        
        for categoria, keywords in self.patterns.PRODUTIVO.items():
            score = sum(2 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[categoria] = score
        
        
        structural = self._analyze_structure(text_lower)
        
        
        subcategoria = self._determine_subcategory(category_scores, structural)
        
        
        if category_scores or any(structural.values()):
            categoria = 'Produtivo'
        else:
            categoria = 'Improdutivo'
            subcategoria = 'Informativo'
            
        return {
            'categoria': categoria,
            'subcategoria': subcategoria,
            'tom': self._detect_tone(text_lower),
            'urgencia': self._detect_urgency(text_lower, structural.get('has_urgency', False)),
            'confianca': 0.85,
            'reasoning': f'Classificação produtiva baseada em: {list(category_scores.keys())}'
        }
    
    def _analyze_structure(self, text_lower):
        """Analisa características estruturais do email"""
        return {
            'has_questions': '?' in text_lower or any(q in text_lower for q in ['como', 'quando', 'onde', 'por que', 'qual']),
            'has_urgency': any(u in text_lower for u in self.patterns.URGENCIA['alta']),
            'has_technical_terms': any(t in text_lower for t in ['sistema', 'erro', 'bug', 'falha', 'login', 'servidor']),
            'has_complaint_tone': any(c in text_lower for c in self.patterns.PRODUTIVO['reclamacao'])
        }
    
    def _determine_subcategory(self, category_scores, structural):
        """Determina a subcategoria baseada nos scores e análise estrutural"""
        if not category_scores:
            # Usa análise estrutural se não há scores de categoria
            if structural['has_questions']:
                return 'Dúvida'
            elif structural['has_technical_terms']:
                return 'Suporte Técnico' 
            elif structural['has_complaint_tone']:
                return 'Reclamação'
            else:
                return 'Informativo'
        
        # Pega a categoria com maior score
        top_category = max(category_scores, key=category_scores.get)
        
        mapping = {
            'urgente': 'Urgente',
            'suporte_tecnico': 'Suporte Técnico',
            'solicitacao': 'Solicitação', 
            'reclamacao': 'Reclamação',
            'duvida': 'Dúvida',
            'felicitacoes': 'Felicitações'
        }
        
        return mapping.get(top_category, 'Geral')
    
    def _detect_tone(self, text_lower):
        """Detecta o tom do email"""
        pos_score = sum(1 for word in self.patterns.TOM['positivo'] if word in text_lower)
        neg_score = sum(1 for word in self.patterns.TOM['negativo'] if word in text_lower)
        
        if pos_score > neg_score:
            return 'Positivo'
        elif neg_score > pos_score:
            return 'Negativo' 
        else:
            return 'Neutro'
    
    def _detect_urgency(self, text_lower, has_structural_urgency):
        """Detecta o nível de urgência"""
        if any(word in text_lower for word in self.patterns.URGENCIA['alta']) or has_structural_urgency:
            return 'Alta'
        elif any(word in text_lower for word in self.patterns.URGENCIA['media']):
            return 'Média'
        else:
            return 'Baixa'