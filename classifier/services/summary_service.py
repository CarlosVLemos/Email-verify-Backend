"""
Service para geração de resumos executivos
"""
from ..email_scripts import ExecutiveSummarizer


class SummaryService:
    """Service para resumos de emails"""
    
    def __init__(self):
        self.summarizer = ExecutiveSummarizer()
    
    def generate_summary(self, email_text, max_sentences=3):
        """
        Gera resumo executivo de email
        
        Args:
            email_text: Texto do email
            max_sentences: Número máximo de frases
            
        Returns:
            dict: Resumo completo com métricas
        """
        result = self.summarizer.summarize(email_text, max_sentences)
        original_words = len(email_text.split())
        summary_words = sum(len(sentence.split()) for sentence in result['summary'])
        
        return {
            'summary': result['summary'],
            'key_points': result['key_points'],
            'relevance_score': round(result['relevance_score'], 3),
            'word_reduction': round(result['word_reduction'], 2),
            'original_word_count': original_words,
            'summary_word_count': summary_words
        }
