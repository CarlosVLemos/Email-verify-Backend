# Email Scripts - Documentação

Esta pasta contém todos os módulos responsáveis pela classificação e processamento de emails.

## Estrutura

```
email_scripts/
├── __init__.py                    # Exporta classes principais
├── email_patterns.py              # Padrões de palavras-chave organizados
├── email_classifier.py            # Lógica de classificação hierárquica  
└── email_response_generator.py    # Geração de respostas automáticas
```

## Classes Principais

### 🔍 EmailClassifier
**Responsabilidade:** Classificação hierárquica de emails
- **Entrada:** Texto do email
- **Saída:** Categoria, subcategoria, tom, urgência

**Hierarquia de Classificação:**
1. **SPAM** (prioridade máxima)
2. **Marketing** 
3. **Agradecimento simples**
4. **Classificação produtiva**

### 📧 EmailResponseGenerator  
**Responsabilidade:** Gerar respostas automáticas personalizadas
- **Entrada:** Resultado da classificação
- **Saída:** Resposta automática adequada

### 📋 EmailPatterns
**Responsabilidade:** Centralizar padrões de palavras-chave
- Organizado por categorias (Produtivo/Improdutivo)
- Facilita manutenção e expansão

## Como Usar

```python
from classifier.email_scripts import EmailClassifier, EmailResponseGenerator

# Inicializar
classifier = EmailClassifier()
response_generator = EmailResponseGenerator()

# Classificar email
result = classifier.classify(email_text)

# Gerar resposta
response = response_generator.generate_response(
    result['categoria'],
    result['subcategoria'], 
    result['tom'],
    result['urgencia']
)
```

## Regras de Negócio

### Categorias Produtivas (requerem ação/resposta)
- ⚡ **Urgente** - Questões críticas
- 🔧 **Suporte Técnico** - Problemas técnicos
- 📝 **Solicitação** - Pedidos específicos  
- 😠 **Reclamação** - Questões a resolver
- ❓ **Dúvida** - Necessitam esclarecimento
- 🎉 **Felicitações** - Podem precisar de agradecimento

### Categorias Improdutivas (não requerem ação imediata)
- 🚫 **Spam** - Não responder
- 📈 **Marketing** - Conteúdo comercial
- 🙏 **Agradecimento** - Apenas agradecimento

## Vantagens da Nova Arquitetura

✅ **Separação de Responsabilidades** - Cada classe tem um propósito específico  
✅ **Fácil Manutenção** - Padrões organizados em arquivo separado  
✅ **Reutilização** - Classes podem ser usadas independentemente  
✅ **Testabilidade** - Cada componente pode ser testado isoladamente  
✅ **Extensibilidade** - Fácil adicionar novos padrões ou categorias