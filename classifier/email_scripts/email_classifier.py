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
        import logging
        logger = logging.getLogger(__name__)

        nlp_data = self.nlp.preprocess(text)
        text_lower = nlp_data['cleaned_text']
        
        # 🆕 Log detalhado para debug
        logger.debug(f"[CLASSIFY] Processando email com {nlp_data['word_count']} palavras")
        logger.debug(f"[CLASSIFY] Top palavras: {nlp_data.get('most_common_words', [])[:5]}")

        spam_result = self._check_spam(text_lower, nlp_data)
        if spam_result:
            spam_result['nlp_stats'] = self.nlp.get_text_stats(text)
            logger.info(f"[CLASSIFY] Classificado como SPAM: {spam_result['reasoning']}")
            return spam_result

        entertainment_result = self._check_entertainment(text_lower, nlp_data)
        if entertainment_result:
            entertainment_result['nlp_stats'] = self.nlp.get_text_stats(text)
            logger.info(f"[CLASSIFY] Classificado como ENTRETENIMENTO: {entertainment_result['reasoning']}")
            return entertainment_result

        marketing_result = self._check_marketing(text_lower, nlp_data)  
        if marketing_result:
            marketing_result['nlp_stats'] = self.nlp.get_text_stats(text)
            logger.info(f"[CLASSIFY] Classificado como MARKETING: {marketing_result['reasoning']}")
            return marketing_result
        
  
        thanks_result = self._check_simple_thanks(text_lower, text)
        if thanks_result:
            thanks_result['nlp_stats'] = self.nlp.get_text_stats(text)
            logger.info(f"[CLASSIFY] Classificado como AGRADECIMENTO: {thanks_result['reasoning']}")
            return thanks_result

        rule_result = self._classify_productive(text_lower, text, nlp_data)
        
        logger.info(f"[CLASSIFY] Classificado como {rule_result['categoria']}/{rule_result['subcategoria']} (confiança: {rule_result['confianca']:.2f})")

        if rule_result['confianca'] < 0.70:
            nlp_stats = self.nlp.get_text_stats(text)
            hf_result = self._generate_response_with_huggingface(text, nlp_stats)
            if hf_result and hf_result['confianca'] > rule_result['confianca']:
                hf_result['nlp_stats'] = nlp_stats
                hf_result['fallback_used'] = True
                logger.info(f"[CLASSIFY] Usando fallback IA")
                return hf_result

        rule_result['nlp_stats'] = self.nlp.get_text_stats(text)
        rule_result['fallback_used'] = False
        return rule_result
    
    def _check_spam(self, text_lower, nlp_data):
        """Detecta spam com validação cruzada e regex"""
        full_text = text_lower
        
        # 🆕 Verifica padrões regex fortes de spam
        spam_regex_count, spam_patterns = self.patterns.check_regex_patterns(full_text, 'spam_strong')
        if spam_regex_count >= 2:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Spam',
                'tom': 'Neutro',
                'urgencia': 'Baixa',
                'confianca': 0.98,
                'reasoning': f'Padrões regex de spam detectados: {spam_patterns[:2]}'
            }
        
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
    
    def _check_entertainment(self, text_lower, nlp_data):
        """Detecta conteúdo de entretenimento (memes, gatinhos, vídeos, etc)"""
        # 🆕 Verifica padrões regex fortes de entretenimento
        entertain_regex_count, entertain_patterns = self.patterns.check_regex_patterns(text_lower, 'entertainment_strong')
        if entertain_regex_count >= 1:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Entretenimento',
                'tom': 'Positivo',
                'urgencia': 'Baixa',
                'confianca': 0.95,
                'reasoning': f'Padrão forte de entretenimento: {entertain_patterns[0]}'
            }
        
        # 🆕 Verifica n-grams (contexto de 2-3 palavras)
        bigrams_text = nlp_data.get('bigrams_text', '')
        entertainment_bigrams = [
            'nada a ver', 'chorei de', 'vale a', 'alegrar seu',
            'meme do', 'gatinho fofo', 'vídeo engraçado'
        ]
        
        bigram_matches = sum(1 for bg in entertainment_bigrams if bg in bigrams_text)
        
        entertainment_score = sum(
            3 for keyword in self.patterns.IMPRODUTIVO.get('entretenimento', []) 
            if keyword in text_lower
        )
        
        # Adiciona score de bigrams
        entertainment_score += bigram_matches * 4
        
        strong_indicators = [
            'nada a ver com trabalho',
            'vale a pausa',
            'alegrar seu dia',
            'chorei de rir',
            'meme',
            'gatinho',
            'fofo'
        ]
        
        has_strong_indicator = any(ind in text_lower for ind in strong_indicators)

        if entertainment_score >= 6 or has_strong_indicator:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Entretenimento',
                'tom': 'Positivo',
                'urgencia': 'Baixa',
                'confianca': 0.92,
                'reasoning': f'Conteúdo recreativo detectado (score: {entertainment_score}, bigrams: {bigram_matches})'
            }
        return None
    
    def _check_marketing(self, text_lower, nlp_data):
        """Detecta marketing/promoções comerciais com validação cruzada"""
        # 🆕 PRIMEIRO: Verifica se tem contexto de trabalho GENUÍNO
        work_regex_count, work_patterns = self.patterns.check_regex_patterns(text_lower, 'work_context')
        if work_regex_count >= 2:
            # É uma comunicação de trabalho legítima, NÃO é marketing
            return None
        
        # 🆕 Verifica padrões regex FORTES de marketing
        marketing_regex_count, marketing_patterns = self.patterns.check_regex_patterns(text_lower, 'marketing_strong')
        marketing_negative_count, _ = self.patterns.check_regex_patterns(text_lower, 'marketing_negative')
        
        # Se tem indicadores negativos (trabalho), reduz chance de ser marketing
        if marketing_negative_count >= 1:
            return None
        
        # Se tem 2+ padrões regex de marketing, É marketing
        if marketing_regex_count >= 2:
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Marketing', 
                'tom': 'Neutro',
                'urgencia': 'Baixa',
                'confianca': 0.96,
                'reasoning': f'Padrões regex fortes de marketing: {marketing_patterns[:2]}'
            }
        
        # Verifica se tem contexto profissional genuíno (método antigo)
        has_work_context = any(
            keyword in text_lower 
            for keyword in self.patterns.PRODUTIVO['comunicacao_trabalho'][:15]
        )
        
        if has_work_context:
            return None
        
        marketing_score = sum(2 for keyword in self.patterns.IMPRODUTIVO['marketing'] if keyword in text_lower)
        
        # 🆕 Verifica n-grams de marketing
        bigrams_text = nlp_data.get('bigrams_text', '')
        marketing_bigrams = [
            'mega promoção', 'super oferta', 'último dia', 
            'frete grátis', 'aproveite antes', 'desconto de'
        ]
        bigram_matches = sum(1 for bg in marketing_bigrams if bg in bigrams_text)
        marketing_score += bigram_matches * 3
        
        very_strong_marketing = [
            'mega promoção',
            'super promoção', 
            'último dia',
            'aproveite antes que acabe',
            '% desconto',
            '% off',
            'desconto de',
            'acesse agora',
            'visite nosso site',
            'www.',
            'http',
            'equipe ',  # "Equipe SuperOfertas" etc
        ]
        
        strong_marketing_count = sum(1 for indicator in very_strong_marketing if indicator in text_lower)
        

        if strong_marketing_count >= 2 or marketing_score >= 6 or (marketing_regex_count >= 1 and marketing_score >= 4):
            return {
                'categoria': 'Improdutivo',
                'subcategoria': 'Marketing', 
                'tom': 'Neutro',
                'urgencia': 'Baixa',
                'confianca': 0.93,
                'reasoning': f'Conteúdo comercial/marketing (score: {marketing_score}, strong: {strong_marketing_count}, regex: {marketing_regex_count}, bigrams: {bigram_matches})'
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
    
    def _classify_productive(self, text_lower, full_text, nlp_data):
        category_scores = {}
        
        for categoria, keywords in self.patterns.PRODUTIVO.items():
            score = sum(2 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[categoria] = score
        
        # 🆕 Boost de score se encontrar n-grams relevantes
        bigrams_text = nlp_data.get('bigrams_text', '')
        work_bigrams = [
            'problema urgente', 'preciso de', 'muito urgente',
            'poderia me', 'não funciona', 'erro no'
        ]
        for bg in work_bigrams:
            if bg in bigrams_text:
                # Aumenta score da categoria mais relevante
                if 'urgente' in category_scores:
                    category_scores['urgente'] += 3
                elif 'suporte_tecnico' in category_scores:
                    category_scores['suporte_tecnico'] += 3
        
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
            if structural['has_questions']:
                return 'Dúvida'
            elif structural['has_technical_terms']:
                return 'Suporte Técnico' 
            elif structural['has_complaint_tone']:
                return 'Reclamação'
            else:
                return 'Informativo'
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
        if any(word in text_lower for word in self.patterns.URGENCIA['alta']):
            return 'Alta'
        elif (any(word in text_lower for word in self.patterns.URGENCIA['media']) or 
              has_structural_urgency or
              any(pattern in text_lower for pattern in ['ação necessária', 'próximos passos', 'prazo', 'deadline', 'coordenação'])):
            return 'Média'
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