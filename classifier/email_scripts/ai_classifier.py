"""
Classificador usando Google Gemini API (gratuita)
Usado apenas como fallback quando classificador de regras tem baixa confiança
"""
import os
from typing import Dict, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIClassifier:
    """Classificador usando Google Gemini API como fallback inteligente"""
    
    def __init__(self):
        self.model = None
        self.enabled = False
        
        if GEMINI_AVAILABLE:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.enabled = True
                except Exception as e:
                    print(f"Erro ao configurar Gemini: {e}")
                    self.enabled = False
    
    def classify(self, email_text: str, nlp_stats: Dict = None) -> Optional[Dict]:
        """
        Classifica email usando IA do Gemini
        Retorna None se não disponível ou erro
        """
        if not self.enabled or not self.model:
            return None
        
        try:
            prompt = self._build_prompt(email_text, nlp_stats)
            response = self.model.generate_content(prompt)
            
            return self._parse_response(response.text)
        
        except Exception as e:
            print(f"Erro ao chamar Gemini API: {e}")
            return None
    
    def _build_prompt(self, email_text: str, nlp_stats: Dict = None) -> str:
        """Constrói prompt otimizado para classificação"""
        
        stats_info = ""
        if nlp_stats:
            stats_info = f"""
Estatísticas do email:
- Palavras: {nlp_stats.get('palavras_totais', 'N/A')}
- Sentenças: {nlp_stats.get('sentencas', 'N/A')}
- Diversidade lexical: {nlp_stats.get('diversidade_lexical', 'N/A')}
"""
        
        prompt = f"""Você é um especialista em classificação de emails corporativos.

Analise o email abaixo e classifique conforme as regras:

**CATEGORIAS:**
1. **Produtivo**: Emails que requerem ação, solicitações, suporte técnico, dúvidas, reclamações, comunicação de trabalho
2. **Improdutivo**: Spam, marketing, agradecimentos simples, informativos sem ação necessária

**SUBCATEGORIAS Produtivo:**
- Urgente: Emergências, prazos críticos
- Suporte Técnico: Problemas técnicos, bugs, erros
- Solicitação: Pedidos, requisições
- Dúvida: Perguntas, esclarecimentos
- Reclamação: Insatisfações, problemas
- Comunicação de Trabalho: Coordenação, updates
- Felicitações: Parabéns genuínos

**SUBCATEGORIAS Improdutivo:**
- Spam: Conteúdo suspeito, não solicitado
- Marketing: Promoções, vendas
- Agradecimento: Apenas agradecimento sem conteúdo adicional
- Informativo: Apenas informação, sem ação necessária

**TOM:**
- Positivo
- Negativo
- Neutro

**URGÊNCIA:**
- Alta: Emergências, prazos críticos
- Média: Requer atenção em breve
- Baixa: Pode esperar

{stats_info}

**EMAIL:**
{email_text[:1000]}

**RESPONDA APENAS NO FORMATO JSON:**
{{
  "categoria": "Produtivo ou Improdutivo",
  "subcategoria": "uma das subcategorias válidas",
  "tom": "Positivo, Negativo ou Neutro",
  "urgencia": "Alta, Média ou Baixa",
  "confianca": 0.XX (entre 0 e 1),
  "reasoning": "breve explicação da classificação"
}}
"""
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse da resposta do Gemini para formato padrão"""
        import json
        import re
        
        # Tenta extrair JSON da resposta
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                result = json.loads(json_match.group())
                
                # Valida e normaliza
                return {
                    'categoria': result.get('categoria', 'Produtivo'),
                    'subcategoria': result.get('subcategoria', 'Geral'),
                    'tom': result.get('tom', 'Neutro'),
                    'urgencia': result.get('urgencia', 'Média'),
                    'confianca': float(result.get('confianca', 0.75)),
                    'reasoning': result.get('reasoning', 'Classificação via IA'),
                    'source': 'gemini-api'
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback se não conseguir parsear
        return None
