"""
Email Scripts - Módulo de classificação e processamento de emails

Este módulo contém todas as classes e utilitários para:
- Classificação hierárquica de emails
- Geração de respostas automáticas
- Padrões de palavras-chave
"""

from .email_classifier import EmailClassifier
from .email_response_generator import EmailResponseGenerator
from .email_patterns import EmailPatterns

__all__ = ['EmailClassifier', 'EmailResponseGenerator', 'EmailPatterns']