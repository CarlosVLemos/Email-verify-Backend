"""
Classificador de emails com lógica hierárquica
Responsabilidade única: classificar emails seguindo as regras de negócio
"""
from .email_patterns import EmailPatterns


class EmailClassifier:
    def __init__(self):
        self.patterns = EmailPatterns()
        
    def classify(self, text):
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
        full_text = text_lower
        
        if self.patterns.has_suspicious_spam_patterns(full_text):
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Spam',
                'tom': 'Neutro',
                'urgencia': 'Baixa',
                'confianca': 0.98,
                'reasoning': 'Padrões altamente suspeitos de spam detectados'
            }
        
        if self.patterns.is_genuine_congratulation(full_text):
            return None
            
        spam_score = 0
        for keyword in self.patterns.IMPRODUTIVO['spam']:
            if keyword in text_lower:
                spam_score += 3
                
        if 'parabéns' in text_lower or 'felicitações' in text_lower:
            spam_score += 2
            
        if spam_score >= 8:
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
        # Verifica se tem contexto profissional genuíno primeiro
        has_work_context = any(
            keyword in text_lower 
            for keyword in self.patterns.PRODUTIVO['comunicacao_trabalho'][:15]  # Só as principais
        )
        
        # Se tem contexto de trabalho, não é marketing
        if has_work_context:
            return None
        
        marketing_score = sum(2 for keyword in self.patterns.IMPRODUTIVO['marketing'] if keyword in text_lower)
        
        # Score mais alto para evitar falsos positivos
        if marketing_score >= 6:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Marketing', 
                'tom': 'Neutro',
                'urgencia': 'Baixa',
                'confianca': 0.88,
                'reasoning': f'Conteúdo comercial/marketing (score: {marketing_score})'
            }
        return None
    
    def _check_simple_thanks(self, text_lower, full_text):
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
        category_scores = {}
        
        for categoria, keywords in self.patterns.PRODUTIVO.items():
            score = sum(2 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[categoria] = score
        
        structural = self._analyze_structure(text_lower)
        
        if 'felicitacoes' in category_scores:
            if self.patterns.is_genuine_congratulation(full_text):
                subcategoria = 'Felicitações'
                categoria = 'Produtivo'
                confianca = 0.92
                reasoning = 'Felicitação genuína detectada'
            else:
                category_scores.pop('felicitacoes', None)
        
        subcategoria = self._determine_subcategory(category_scores, structural)
        
        if category_scores:
            top_category = max(category_scores, key=category_scores.get) if category_scores else None
            if top_category:
                context_score = self.patterns.get_context_score(full_text, top_category)
                confianca = min(0.95, 0.70 + (context_score / 100))
            else:
                confianca = 0.85
        else:
            confianca = 0.75
        
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
            'confianca': confianca,
            'reasoning': f'Classificação baseada em: {list(category_scores.keys()) if category_scores else "análise estrutural"}'
        }
    
    def _analyze_structure(self, text_lower):
        """Analisa características estruturais do email"""
        return {
            'has_questions': '?' in text_lower or any(q in text_lower for q in ['como', 'quando', 'onde', 'por que', 'qual']),
            'has_urgency': (
                any(u in text_lower for u in self.patterns.URGENCIA['alta']) or
                any(u in text_lower for u in self.patterns.URGENCIA['media'])
            ),
            'has_technical_terms': any(t in text_lower for t in ['sistema', 'erro', 'bug', 'falha', 'login', 'servidor']),
            'has_complaint_tone': any(c in text_lower for c in self.patterns.PRODUTIVO['reclamacao']),
            'has_work_coordination': any(w in text_lower for w in ['ação necessária', 'próximos passos', 'coordenação', 'prazo'])
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
            'felicitacoes': 'Felicitações',
            'comunicacao_trabalho': 'Comunicação de Trabalho'
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
        """Detecta o nível de urgência com maior precisão"""
        # Urgência alta - termos explícitos de emergência
        if any(word in text_lower for word in self.patterns.URGENCIA['alta']):
            return 'Alta'
        
        # Urgência média - prazos, ações necessárias, coordenação
        elif (any(word in text_lower for word in self.patterns.URGENCIA['media']) or 
              has_structural_urgency or
              any(pattern in text_lower for pattern in ['ação necessária', 'próximos passos', 'prazo', 'deadline', 'coordenação'])):
            return 'Média'
        
        # Urgência baixa - apenas para agradecimentos simples ou informativos
        else:
            return 'Baixa'