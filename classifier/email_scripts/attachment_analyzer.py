"""
Analisador de anexos mencionados em emails.
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
            r'attachment[s]?\b'
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
        mentions = self._detect_mentions(text_lower)
        security_analysis = self._analyze_security(text_lower)
        return {
            'has_attachments_mentioned': bool(mentions),
            'mention_count': len(mentions),
            'mentions': mentions,
            'security_risk_level': security_analysis['risk_level'],
            'security_flags': security_analysis['flags']
        }
    def _detect_mentions(self, text: str) -> List[str]:
        mentions = set()
        for pattern in self.mention_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                mentions.add(match.group())
        return list(mentions)
    def _analyze_security(self, text: str) -> Dict:
        suspicious_matches = [
            pattern.replace(r'\s+', ' ').replace(r'\b', '')
            for pattern in self.suspicious_patterns
            if re.search(pattern, text, re.IGNORECASE)
        ]
        risk_score = len(suspicious_matches) * 15
        risk_levels = [(40, 'alto'), (25, 'medio'), (10, 'baixo')]
        risk_level = next((level for threshold, level in risk_levels if risk_score >= threshold), 'seguro')
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'flags': suspicious_matches
        }