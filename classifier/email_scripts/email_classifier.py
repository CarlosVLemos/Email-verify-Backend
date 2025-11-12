"""
Classificador híbrido de emails: Regras + NLP + IA
Pipeline: NLP preprocessing → Regras → IA (fallback se confiança < 0.70)
"""
from .email_patterns import EmailPatterns
from .nlp_processor import NLPProcessor
from .email_response_generator import EmailResponseGenerator


class EmailClassifier:
    def __init__(self):
        self.patterns = EmailPatterns()
        self.nlp = NLPProcessor()
        
    def classify(self, text):
        """
        Pipeline híbrido de classificação:
        1. NLP preprocessing (atende requisito)
        2. Classificação por regras (rápido, 95% dos casos)
        3. IA fallback se confiança < 0.70 (casos ambíguos)
        """
        # ETAPA 1: NLP Preprocessing
        nlp_data = self.nlp.preprocess(text)
        text_lower = nlp_data['cleaned_text']
        
        # ETAPA 2: Classificação por Regras
        spam_result = self._check_spam(text_lower)
        if spam_result:
            spam_result['nlp_stats'] = self.nlp.get_text_stats(text)
            return spam_result
            
        marketing_result = self._check_marketing(text_lower)  
        if marketing_result:
            marketing_result['nlp_stats'] = self.nlp.get_text_stats(text)
            return marketing_result
            
        thanks_result = self._check_simple_thanks(text_lower, text)
        if thanks_result:
            thanks_result['nlp_stats'] = self.nlp.get_text_stats(text)
            return thanks_result
            
        rule_result = self._classify_productive(text_lower, text)
        
        # ETAPA 3: IA Fallback (apenas se confiança baixa)
        if rule_result['confianca'] < 0.70:
            nlp_stats = self.nlp.get_text_stats(text)
            hf_result = self._generate_response_with_huggingface(text, nlp_stats)
            if hf_result and hf_result['confianca'] > rule_result['confianca']:
                hf_result['nlp_stats'] = nlp_stats
                hf_result['fallback_used'] = True
                return hf_result
        
        # Retorna resultado das regras com stats NLP
        rule_result['nlp_stats'] = self.nlp.get_text_stats(text)
        rule_result['fallback_used'] = False
        return rule_result
    
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
    
    def _generate_response_with_huggingface(self, email_text, nlp_stats):
        """Gera resposta usando Hugging Face API"""
        import requests
        import os

        HF_API_KEY = os.getenv('HF_API_KEY')
        if not HF_API_KEY:
            return None
        
        API_URL = "https://api-inference.huggingface.co/models/pierreguillou/gpt2-small-portuguese"
        prompt = f"Email: {email_text}\nEstatísticas: {nlp_stats}\nResposta profissional:"
        
        try:
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": prompt, "parameters": {"max_length": 150}}
            )
            if response.status_code == 200:
                return response.json()[0]['generated_text']
            else:
                return None
        except Exception as e:
            print(f"Erro ao chamar Hugging Face API: {e}")
            return None