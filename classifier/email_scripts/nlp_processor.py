"""
Processador NLP para pré-processamento de emails
Usa NLTK para tokenização, remoção de stopwords e lemmatização
"""
import re
import unicodedata
from typing import List, Dict

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import RSLPStemmer
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class NLPProcessor:
    """Processador de linguagem natural para emails em português"""
    
    def __init__(self):
        self.tokenizer = nltk.tokenize.word_tokenize
        self.stemmer = nltk.stem.RSLPStemmer()
        self.stopwords = set(nltk.corpus.stopwords.words('portuguese'))

        # Certifique-se de que o recurso RSLP está disponível
        try:
            nltk.data.find('stemmers/rslp')
        except LookupError:
            nltk.download('rslp')

    def preprocess(self, text: str) -> Dict[str, any]:
        """
        Pré-processa o texto do email aplicando técnicas de NLP
        
        Returns:
            Dict contendo:
            - cleaned_text: Texto limpo
            - tokens: Lista de tokens
            - filtered_tokens: Tokens sem stopwords
            - stems: Tokens stemizados
            - word_count: Contagem de palavras
            - sentence_count: Contagem de sentenças
        """
        # Normalização básica
        cleaned = self._normalize_text(text)
        
        # Tokenização
        tokens = self.tokenizer(cleaned, language='portuguese')
        
        # Remoção de stopwords
        filtered_tokens = [
            token for token in tokens 
            if token.lower() not in self.stopwords and len(token) > 2
        ]
        
        # Stemming (redução à raiz)
        stems = [self.stemmer.stem(token) for token in filtered_tokens]
        
        # Métricas
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        return {
            'cleaned_text': cleaned,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens,
            'stems': stems,
            'word_count': len(tokens),
            'sentence_count': sentence_count,
            'avg_word_length': sum(len(t) for t in tokens) / len(tokens) if tokens else 0,
            'unique_words': len(set(tokens)),
            'lexical_diversity': len(set(tokens)) / len(tokens) if tokens else 0
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto removendo acentos, caracteres especiais etc"""
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        text = text.lower()
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^\w\s.!?]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extrai palavras-chave mais relevantes do texto"""
        processed = self.preprocess(text)
        from collections import Counter
        stem_freq = Counter(processed['stems'])
        return [word for word, _ in stem_freq.most_common(top_n)]
    
    def get_text_stats(self, text: str) -> Dict[str, any]:
        """Retorna estatísticas detalhadas do texto"""
        processed = self.preprocess(text)
        
        return {
            'caracteres_totais': len(text),
            'palavras_totais': processed['word_count'],
            'palavras_unicas': processed['unique_words'],
            'sentencas': processed['sentence_count'],
            'diversidade_lexical': round(processed['lexical_diversity'], 2),
            'tamanho_medio_palavra': round(processed['avg_word_length'], 2),
            'densidade_informacao': len(processed['filtered_tokens']) / processed['word_count'] if processed['word_count'] > 0 else 0
        }
