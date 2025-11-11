"""
Analisador de anexos mencionados em emails
Detecta, classifica e avalia riscos de segurança
"""
import re
from typing import Dict, List, Optional


class AttachmentAnalyzer:
    def __init__(self):
        
        self.mention_patterns = [
            r'anexo[s]?\b',
            r'anexado[s]?\b', 
            r'anexando\b',
            r'anexei\b',
            r'arquivo[s]?\s+anexo[s]?\b',
            r'documento[s]?\s+em\s+anexo\b',
            r'relatório\s+anexo[s]?\b',
            r'planilha\s+anexa[s]?\b',
            r'segue\s+anexo[s]?\b',
            r'em\s+anexo\b',
            r'está\s+anexo[s]?\b',
            r'estão\s+anexo[s]?\b',
            r'encontra-se\s+anexo[s]?\b',
            r'vai\s+anexo[s]?\b',
            r'follow[s]?\s+attached\b',
            r'attached\s+file[s]?\b',
            r'attachment[s]?\b',
            # Padrões para capturar contextos mais amplos
            r'\w*erro\w*\s+.*\s+anexo',
            r'detalhado\s+.*\s+anexo',
            r'relatório\s+.*\s+anexo'
        ]
        
        self.suspicious_patterns = [
            r'clique\s+no\s+anexo',
            r'abra\s+o\s+anexo',
            r'execute\s+o\s+arquivo',
            r'instale\s+o\s+programa',
            r'baixe\s+e\s+execute',
            r'arquivo\s+importante',
            r'documento\s+urgente\s+anexo'
        ]

    def analyze(self, text: str) -> Dict:
        text_lower = text.lower()
        
        # Processamento paralelo dos dados
        mentions = self._detect_mentions(text_lower)
        file_types = self._detect_file_types(text_lower)
        security_analysis = self._analyze_security(text_lower)
        context = self._analyze_context(text_lower, text)
        
        return {
            'has_attachments_mentioned': bool(mentions),
            'mention_count': len(mentions),
            'mentions': mentions,
            'security_risk_level': security_analysis['risk_level'],
            'security_flags': security_analysis['flags'],
            'context_analysis': context,
            'attachment_score': self._calculate_attachment_score(mentions, file_types, security_analysis)
        }
    
    def _detect_mentions(self, text: str) -> List[str]:
        # Limpeza do texto para melhor detecção
        text_cleaned = re.sub(r'\s+', ' ', text.strip())
        
        mentions = set()
        processed_positions = set()  # Para evitar sobreposições
        
        for pattern in self.mention_patterns:
            for match in re.finditer(pattern, text_cleaned, re.IGNORECASE):
                match_start = match.start()
                match_end = match.end()
                
                # Verifica se já processamos uma região similar
                if any(abs(pos - match_start) < 20 for pos in processed_positions):
                    continue
                
                # Procura pela sentença completa que contém a menção
                sentences = re.split(r'[.!?]+', text_cleaned)
                for sentence in sentences:
                    if sentence.strip() and match.group().lower() in sentence.lower():
                        cleaned_sentence = sentence.strip()
                        if len(cleaned_sentence) > 15:  # Filtro de tamanho mínimo
                            mentions.add(cleaned_sentence)
                            processed_positions.add(match_start)
                            break
        
        # Remove menções que são substrings de outras
        final_mentions = []
        sorted_mentions = sorted(list(mentions), key=len, reverse=True)
        
        for mention in sorted_mentions:
            is_substring = any(
                mention != existing and mention.lower() in existing.lower() 
                for existing in final_mentions
            )
            if not is_substring:
                final_mentions.append(mention)
        
        return final_mentions[:3]  # Limita a 3 menções mais relevantes
    
    def _detect_file_types(self, text: str) -> Dict[str, List[str]]:
        # Removido: não detectamos mais tipos de arquivo
        # Isso evita classificações incorretas e simplifica a análise
        return {}
    
    def _analyze_security(self, text: str) -> Dict:
        suspicious_matches = [
            pattern.replace(r'\s+', ' ').replace(r'\b', '')
            for pattern in self.suspicious_patterns
            if re.search(pattern, text, re.IGNORECASE)
        ]
        
        risk_score = len(suspicious_matches) * 15  # Aumentado para compensar remoção de tipos
        
        # Verifica apenas padrões suspeitos no texto
        executable_patterns = ['.exe', '.msi', '.bat', '.cmd', '.scr']
        has_executables = any(ext in text.lower() for ext in executable_patterns)
        
        if has_executables:
            risk_score += 25
            suspicious_matches.append('arquivo_executavel_mencionado')
        
        # Níveis de risco baseados apenas em padrões suspeitos
        risk_levels = [(40, 'alto'), (25, 'medio'), (10, 'baixo')]
        risk_level = next((level for threshold, level in risk_levels if risk_score >= threshold), 'seguro')
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'flags': suspicious_matches
        }
    
    def _analyze_context(self, text_lower: str, original_text: str) -> Dict:
        contexts = {
            'solicitacao_documento': [
                'preciso do documento', 'envie o arquivo', 'poderia anexar',
                'você poderia enviar', 'me mande o arquivo', 'solicito o documento'
            ],
            'compartilhamento': [
                'segue anexo', 'anexo solicitado', 'documento anexado',
                'está anexo', 'vai anexo', 'encontra-se anexo', 'conforme solicitado'
            ],
            'trabalho_profissional': [
                'relatório', 'planilha', 'apresentação', 'projeto', 'análise',
                'dados', 'resultado', 'estatística', 'levantamento', 'pesquisa'
            ],
            'suporte_tecnico': [
                'erro', 'bug', 'falha', 'problema', 'log', 'debug',
                'screenshot', 'print', 'evidência', 'captura'
            ],
            'administrativo': [
                'contrato', 'proposta', 'orçamento', 'fatura', 'recibo',
                'documento fiscal', 'comprovante', 'certificado'
            ],
            'comunicacao_interna': [
                'ata de reunião', 'memorando', 'circular', 'comunicado',
                'política', 'procedimento', 'manual', 'diretriz'
            ]
        }
        
        # Detecta múltiplos contextos
        detected_contexts = [
            context for context, keywords in contexts.items()
            if any(keyword in text_lower for keyword in keywords)
        ]
        
        # Análise de urgência expandida
        urgency_patterns = {
            'alta': ['urgente', 'imediato', 'emergência', 'crítico', 'hoje', 'agora'],
            'media': ['importante', 'necessário', 'prazo', 'breve', 'logo'],
            'baixa': ['quando possível', 'sem pressa', 'conveniência']
        }
        
        urgency_level = 'nenhuma'
        for level, keywords in urgency_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                urgency_level = level
                break
        
        # Análise de propósito do anexo
        purpose_indicators = {
            'evidencia': ['prova', 'evidência', 'comprovação', 'demonstração'],
            'referencia': ['consulta', 'referência', 'base', 'modelo'],
            'acao_requerida': ['revisar', 'analisar', 'verificar', 'validar', 'aprovar'],
            'informacao': ['informação', 'dados', 'detalhes', 'especificação']
        }
        
        attachment_purpose = [
            purpose for purpose, keywords in purpose_indicators.items()
            if any(keyword in text_lower for keyword in keywords)
        ]
        
        return {
            'contexts': detected_contexts,
            'has_urgency': urgency_level != 'nenhuma',
            'urgency_level': urgency_level,
            'attachment_purpose': attachment_purpose,
            'email_length': len(original_text.split()),
            'attachment_to_text_ratio': self._calculate_attachment_density(text_lower),
            'context_score': len(detected_contexts) + len(attachment_purpose)
        }
    
    def _calculate_attachment_density(self, text: str) -> float:
        word_count = len(text.split())
        # Usando operador ternário e sum() com generator
        return (
            (sum(1 for pattern in self.mention_patterns if re.search(pattern, text, re.IGNORECASE)) / word_count) * 100
            if word_count > 0 else 0.0
        )
    
    def _calculate_attachment_score(self, mentions: List[str], file_types: Dict, 
                                  security: Dict) -> float:
        # Score baseado apenas em menções e contexto
        base_score = 0
        
        # Pontuação por menções (mais peso já que não temos tipos)
        if mentions:
            base_score += len(mentions) * 20  # Aumentado para compensar
            
            # Bonus por qualidade das menções
            for mention in mentions:
                mention_words = mention.split()
                if len(mention_words) > 8:  # Menção com contexto completo
                    base_score += 15
                elif len(mention_words) > 5:  # Menção com contexto médio
                    base_score += 10
                
                # Bonus por palavras-chave profissionais
                professional_keywords = [
                    'relatório', 'documento', 'arquivo', 'log', 'dados',
                    'planilha', 'análise', 'resultado', 'evidência'
                ]
                if any(word in mention.lower() for word in professional_keywords):
                    base_score += 12
        
        # Penalidades de segurança (ajustadas)
        risk_penalties = {'alto': -20, 'medio': -10, 'baixo': -5, 'seguro': 0}
        base_score += risk_penalties.get(security['risk_level'], 0)
        
        # Bonus por contexto profissional específico
        if mentions:
            combined_text = ' '.join(mentions).lower()
            professional_contexts = [
                'projeto', 'erro', 'problema', 'status', 'progresso',
                'reunião', 'apresentação', 'resultado', 'análise'
            ]
            if any(context in combined_text for context in professional_contexts):
                base_score += 18
        
        # Score mínimo para emails com anexos mencionados
        if mentions:
            base_score = max(15, base_score)  # Mínimo 15 se tem menções
        
        return max(0, min(100, base_score))