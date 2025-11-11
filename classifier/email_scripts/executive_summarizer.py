"""
Resumidor executivo de emails
Extrai pontos-chave usando algoritmos de relevância
"""
import re
from typing import List, Dict, Tuple
from collections import Counter


class ExecutiveSummarizer:
    def __init__(self):
        self.importance_keywords = {
            'alta': [
                'urgente', 'imediato', 'crítico', 'emergência', 'agora', 'hoje', 'asap',
                'prioridade máxima', 'extremamente importante', 'não pode esperar'
            ],
            'media': [
                'importante', 'necessário', 'preciso', 'solicitação', 'pedido',
                'fundamental', 'essencial', 'significativo', 'relevante'
            ],
            'acao': [
                'solicito', 'precisa', 'favor', 'poderia', 'gostaria', 'requero',
                'ação necessária', 'providenciar', 'resolver', 'atender', 'executar'
            ],
            'tempo': [
                'prazo', 'deadline', 'até', 'antes', 'depois', 'quando', 'data',
                'cronograma', 'agenda', 'programação', 'vencimento', 'limite'
            ],
            'pessoa': [
                'reunião', 'encontro', 'conversar', 'falar', 'contato',
                'coordenação', 'alinhamento', 'discussão', 'apresentação'
            ],
            'documento': [
                'relatório', 'documento', 'arquivo', 'planilha', 'apresentação',
                'anexo', 'material', 'dados', 'informação', 'detalhes'
            ],
            'problema': [
                'erro', 'problema', 'falha', 'bug', 'defeito', 'inconsistência',
                'não funciona', 'travou', 'parou', 'dificuldade'
            ],
            'projeto': [
                'projeto', 'desenvolvimento', 'implementação', 'execução',
                'progresso', 'andamento', 'status', 'situação', 'evolução'
            ]
        }
        
        self.sentence_endings = ['.', '!', '?', ';']
        self.noise_words = {
            'artigos': ['o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas'],
            'preposicoes': ['de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'para', 'por'],
            'conectivos': ['e', 'ou', 'mas', 'porque', 'pois', 'então', 'assim'],
            'pronomes': ['eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'me', 'te', 'se']
        }

    def summarize(self, text: str, max_sentences: int = 3) -> Dict:
        text = text.strip()
        simple_result = {
            'summary': [text] if text else [],
            'key_points': [],
            'context_analysis': {},
            'relevance_score': 0.0,
            'word_reduction': 0.0
        }
        if not text or len(text) < 50:
            return simple_result
        sentences = self._split_sentences(text)
        if len(sentences) <= max_sentences:
            return {
                'summary': sentences,
                'key_points': self._extract_key_points(text),
                'context_analysis': self._analyze_email_context(text),
                'relevance_score': 0.8,
                'word_reduction': 0.0
            }
        scored_sentences = self._score_sentences(sentences, text)
        top_sentences = self._select_top_sentences(scored_sentences, max_sentences)
        key_points = self._extract_key_points(text)
        context_analysis = self._analyze_email_context(text)
        original_words, summary_words = len(text.split()), sum(len(s.split()) for s in top_sentences)
        reduction = ((original_words - summary_words) / original_words) * 100 if original_words else 0
        return {
            'summary': top_sentences,
            'key_points': key_points,
            'context_analysis': context_analysis,
            'relevance_score': self._calculate_relevance_score(scored_sentences, top_sentences),
            'word_reduction': round(reduction, 1)
        }
    def _split_sentences(self, text: str) -> List[str]:
        text = re.sub(r'\s+', ' ', text.strip())
        sentences, current = [], ""  
        for char in text:
            current += char
            # Usando operador walrus para condição mais concisa
            if char in self.sentence_endings and (stripped := current.strip()) and len(stripped) > 10:
                if not re.search(r'\b[A-Z]\.$', stripped):
                    sentences.append(stripped)
                    current = "" 
        sentences.extend([current.strip()] if current.strip() else [])
        return [s for s in sentences if 10 <= len(s.split()) <= 50]
    def _score_sentences(self, sentences: List[str], full_text: str) -> List[Tuple[str, float]]:
        total_sentences = len(sentences)
        position_scores = {0: 15, total_sentences - 1: 10}
        first_third_threshold = int(total_sentences * 0.3)
        category_multipliers = {'alta': 12, 'acao': 10}
        patterns = {
            'numbers': re.compile(r'\d+'),
            'dates': re.compile(r'\d{1,2}/\d{1,2}(/\d{2,4})?'),
            'money': re.compile(r'R\$|reais|valor|preço')
        }       
        action_starts = {'solicito', 'preciso', 'gostaria', 'peço', 'requero'}       
        scored = []
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            words = len(sentence.split())
            score = position_scores.get(i, 8 if i < first_third_threshold else 0)
            for category, keywords in self.importance_keywords.items():
                matches = sum(1 for kw in keywords if kw in sentence_lower)
                multiplier = category_multipliers.get(category, 6)
                score += matches * multiplier
            score += sum([
                8 if patterns['numbers'].search(sentence) else 0,
                10 if patterns['dates'].search(sentence) else 0,
                8 if patterns['money'].search(sentence_lower) else 0,
                7 if '?' in sentence else 0,
                12 if any(sentence_lower.startswith(action) for action in action_starts) else 0
            ])
            score += 5 if 8 <= words <= 25 else (-3 if words > 30 else 0)
            if words > 0:
                important_words = self._count_important_words(sentence_lower)
                noise_words = self._count_noise_words(sentence_lower)
                score += ((important_words - noise_words) / words) * 10
            
            scored.append((sentence, max(0, score)))
        return scored
    def _count_important_words(self, sentence: str) -> int:
        return sum(
            sum(1 for kw in keywords if kw in sentence) 
            for keywords in self.importance_keywords.values()
        )
    def _count_noise_words(self, sentence: str) -> int:
        words = sentence.split()
        word_set = set(words)
        return sum(
            len(word_set.intersection(noise_category))
            for noise_category in self.noise_words.values()
        )
    def _select_top_sentences(self, scored_sentences: List[Tuple[str, float]], max_sentences: int) -> List[str]:
        sentence_scores = {sentence: score for sentence, score in scored_sentences}       
        top_sentences = sorted(sentence_scores.keys(), key=sentence_scores.get, reverse=True)[:max_sentences]
        top_set = set(top_sentences)
        return [sentence for sentence, _ in scored_sentences if sentence in top_set][:max_sentences]

    def _extract_key_points(self, text: str) -> List[str]:
        text_lower = text.lower()
        key_points = []
        
        # Padrões melhorados e mais específicos
        patterns = {
            'prazo_deadline': [
                r'prazo\s+até\s+[\w\d/\s]+',
                r'deadline\s+[\w\d/\s]+', 
                r'vence\s+em\s+[\w\d/\s]+',
                r'data\s+limite\s+[\w\d/\s]+'
            ],
            'acao_solicitada': [
                r'(preciso|necessito|solicito|requeiro)\s+que\s+[\w\s]+',
                r'(favor|por favor)\s+[\w\s]+',
                r'(poderia|você poderia)\s+[\w\s]+',
                r'ação\s+necessária\s*:?\s*[\w\s]+'
            ],
            'problema_erro': [
                r'(erro|problema|falha)\s+[\w\s]+',
                r'não\s+(funciona|está funcionando)\s+[\w\s]+',
                r'(bug|defeito)\s+[\w\s]+'
            ],
            'documento_anexo': [
                r'(relatório|documento|planilha|arquivo)\s+[\w\s]+',
                r'(anexo|anexado|em anexo)\s+[\w\s]+',
                r'(segue|vai)\s+anexo\s+[\w\s]+'
            ],
            'projeto_status': [
                r'projeto\s+[\w\s]+',
                r'status\s+do\s+[\w\s]+',
                r'progresso\s+[\w\s]+',
                r'andamento\s+[\w\s]+'
            ],
            'reuniao_contato': [
                r'reunião\s+[\w\s]+',
                r'(falar|conversar)\s+com\s+[\w\s]+',
                r'contato\s+[\w\s]+',
                r'(agendar|marcar)\s+[\w\s]+'
            ]
        }
        
        # Extrai pontos por categoria
        for category, pattern_list in patterns.items():
            category_points = []
            for pattern in pattern_list:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches[:2]:  # Máximo 2 por categoria
                    cleaned_match = match.strip()
                    if isinstance(match, tuple):
                        cleaned_match = ' '.join(match).strip()
                    
                    if len(cleaned_match) > 8 and cleaned_match not in category_points:
                        category_points.append(cleaned_match)
            
            key_points.extend(category_points[:2])  # Máximo 2 por categoria
        
        # Remove duplicatas preservando ordem
        seen = set()
        unique_points = []
        for point in key_points:
            if point not in seen and len(point) > 8:
                seen.add(point)
                unique_points.append(point.capitalize())
        
        return unique_points[:6]  # Máximo 6 pontos totais

    def _analyze_email_context(self, text: str) -> Dict:
        """Analisa o contexto geral do email para melhor compreensão"""
        text_lower = text.lower()
        
        # Tipos de comunicação
        communication_types = {
            'solicitacao': ['solicito', 'preciso', 'gostaria', 'poderia', 'favor'],
            'informativo': ['informo', 'comunico', 'aviso', 'notificação'],
            'urgente': ['urgente', 'imediato', 'emergência', 'crítico'],
            'feedback': ['opinião', 'parecer', 'avaliação', 'feedback'],
            'coordenacao': ['coordenação', 'alinhamento', 'próximos passos']
        }
        
        # Detecta tipo principal
        detected_types = [
            comm_type for comm_type, keywords in communication_types.items()
            if any(keyword in text_lower for keyword in keywords)
        ]
        
        # Sentimento/Tom
        sentiment_indicators = {
            'positivo': ['obrigado', 'agradeço', 'excelente', 'ótimo', 'parabéns'],
            'negativo': ['problema', 'erro', 'falha', 'insatisfeito', 'reclamação'],
            'neutro': ['informação', 'dados', 'relatório', 'status']
        }
        
        detected_sentiment = 'neutro'
        for sentiment, keywords in sentiment_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_sentiment = sentiment
                break
        
        # Complexidade do email
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        complexity = 'baixa' if word_count < 50 else 'media' if word_count < 150 else 'alta'
        
        # Indicadores de ação
        action_required = any(action in text_lower for action in [
            'ação necessária', 'preciso', 'solicito', 'favor', 'poderia'
        ])
        
        return {
            'communication_types': detected_types,
            'primary_sentiment': detected_sentiment,
            'complexity_level': complexity,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'action_required': action_required,
            'has_deadline': any(deadline in text_lower for deadline in [
                'prazo', 'deadline', 'até', 'vence', 'limite'
            ]),
            'has_attachments_mentioned': any(attach in text_lower for attach in [
                'anexo', 'arquivo', 'documento', 'planilha'
            ])
        }

    def _calculate_relevance_score(self, all_scored: List[Tuple[str, float]], selected: List[str]) -> float:
        if not (all_scored and selected):
            return 0.0
        score_map = {sentence: score for sentence, score in all_scored}
        selected_set = set(selected)      
        selected_scores = [score_map[s] for s in selected_set if s in score_map]
        return (
            min(1.0, (sum(selected_scores) / len(selected_scores)) / max(score_map.values()))
            if selected_scores and max(score_map.values()) > 0 
            else 0.0
        )