# 📋 Email Intelligence API - Documentação Completa

## 🎯 Visão Geral

API REST completa para classificação inteligente de emails e analytics de produtividade.

**Base URL**: `http://localhost:8000/api`

**Documentação Interativa**:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

---

## 🤖 **Email Classifier** (`/api/classifier/`)

### 1. Classificar Email
**POST** `/api/classifier/classify/`

Analisa email e retorna classificação completa com tom, urgência e sugestão de resposta.

**Request (JSON)**:
```json
{
  "email_text": "Olá, preciso de ajuda urgente com o login do sistema. Não consigo acessar há 2 horas."
}
```

**Request (File Upload)**:
```bash
curl -X POST http://localhost:8000/api/classifier/classify/ \
  -F "file=@email.txt"
```

**Response 200**:
```json
{
  "topic": "Suporte Técnico",
  "category": "Produtivo",
  "confidence": null,
  "tone": "Neutro",
  "urgency": "Alta",
  "suggested_response": "Olá! Agradecemos por entrar em contato. Compreendo a urgência da situação com o acesso ao sistema...",
  "attachment_analysis": {
    "has_attachments_mentioned": false,
    "attachment_keywords": [],
    "score": 0
  },
  "word_count": 15,
  "char_count": 95,
  "processing_time_ms": 234
}
```

**Categorias Possíveis**:
- **Produtivo**: Suporte Técnico, Dúvida, Reunião, Informação, Tarefa
- **Social**: Agradecimento, Convite, Conversa
- **Improdutivo**: Spam, Promoção, Newsletter

---

### 2. Resumo Executivo
**POST** `/api/classifier/summary/`

Gera resumo inteligente de emails longos com extração de pontos-chave.

**Request**:
```json
{
  "email_text": "Email muito longo com várias informações sobre o projeto, prazos de entrega até sexta-feira, orçamento aprovado de R$ 15.000, necessidade de revisar documentos antes da reunião...",
  "max_sentences": 3
}
```

**Response 200**:
```json
{
  "summary": [
    "O projeto precisa ser entregue até sexta-feira.",
    "O orçamento aprovado é de R$ 15.000.",
    "É necessário revisar os documentos antes da reunião."
  ],
  "key_points": [
    "Prazo: sexta-feira",
    "Orçamento: R$ 15.000",
    "Ação: revisar documentos"
  ],
  "relevance_score": 0.85,
  "word_reduction": 75.5,
  "original_word_count": 250,
  "summary_word_count": 61
}
```

**Parâmetros**:
- `max_sentences`: 1-10 (padrão: 3)

---

### 3. Processamento em Lote
**POST** `/api/classifier/batch/`

Processa até 50 emails simultaneamente.

**Request**:
```json
{
  "emails": [
    "Olá, preciso de ajuda com o sistema de login.",
    "Obrigado pela ajuda de ontem!",
    "Quando teremos a próxima reunião?"
  ]
}
```

**Response 200**:
```json
{
  "request_id": "abc12345",
  "total_emails": 3,
  "successful": 3,
  "failed": 0,
  "total_time_ms": 1250,
  "avg_time_per_email_ms": 416.67,
  "results": [
    {
      "email_id": 1,
      "status": "success",
      "classification": {
        "topic": "Suporte Técnico",
        "category": "Produtivo",
        "tone": "Neutro",
        "urgency": "Média",
        "suggested_response": "..."
      },
      "preview": "Olá, preciso de ajuda..."
    }
  ]
}
```

**Limites**:
- Máximo: 50 emails por request
- Timeout: 30 segundos

---

### 4. Health Check
**GET** `/api/classifier/health/`

Verifica saúde do sistema.

**Response 200**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-11T10:30:00Z",
  "services": {
    "database": "healthy",
    "analytics": "healthy",
    "classifier": "healthy"
  }
}
```

---

## 📊 **Analytics Dashboard** (`/api/analytics/`)

### 1. Dashboard Overview
**GET** `/api/analytics/dashboard/overview/`

Visão geral com métricas principais de produtividade.

**Parâmetros**:
- `days` (opcional): Período em dias (padrão: 30)

**Response 200**:
```json
{
  "overview": {
    "total_emails": 150,
    "productive_emails": 120,
    "unproductive_emails": 30,
    "productivity_rate": 80.0,
    "avg_confidence": 0.875,
    "avg_processing_time": 245.5,
    "attachment_rate": 35.2,
    "period_days": 30,
    "last_updated": "2025-11-11T10:30:00Z"
  },
  "top_categories": [
    {
      "category": "Produtivo",
      "subcategory": "Suporte Técnico",
      "total_count": 45,
      "last_30_days": 45,
      "avg_confidence": 0.88
    }
  ],
  "top_senders": [
    {
      "sender_identifier": "exemplo.com",
      "sender_type": "domain",
      "productivity_rate": 85.5,
      "total_count": 50
    }
  ]
}
```

---

### 2. Tendências de Produtividade
**GET** `/api/analytics/dashboard/trends/`

Dados de série temporal para gráficos.

**Parâmetros**:
- `days` (opcional): Período em dias (padrão: 30)
- `granularity` (opcional): `daily` ou `hourly` (padrão: daily)

**Response 200**:
```json
{
  "timeline": [
    {
      "date": "2025-11-10",
      "hour": 0,
      "total_emails": 25,
      "productive_emails": 20,
      "unproductive_emails": 5,
      "productivity_rate": 80.0,
      "avg_confidence": 0.85,
      "label": "10/11/2025"
    }
  ],
  "period": "30 days",
  "granularity": "daily",
  "trend_analysis": {
    "total_change": 5.2,
    "trend_direction": "increasing",
    "best_period": {...},
    "worst_period": {...}
  }
}
```

---

### 3. Distribuição de Categorias
**GET** `/api/analytics/dashboard/categories/`

Distribuição percentual para gráfico de pizza.

**Response 200**:
```json
{
  "categories": [
    {
      "category": "Produtivo",
      "subcategory": "Suporte Técnico",
      "count": 45,
      "percentage": 30.0,
      "avg_confidence": 0.88,
      "trend_direction": "increasing",
      "trend_percentage": 12.5
    }
  ],
  "total_emails": 150,
  "period": "30 days"
}
```

---

### 4. Análise de Remetentes
**GET** `/api/analytics/dashboard/senders/`

Remetentes mais produtivos e improdutivos.

**Parâmetros**:
- `limit` (opcional): Limite de resultados (padrão: 20, máx: 100)
- `min_emails` (opcional): Mínimo de emails (padrão: 3)

**Response 200**:
```json
{
  "top_productive": [
    {
      "sender_identifier": "suporte@empresa.com",
      "sender_type": "email",
      "productivity_rate": 95.5,
      "total_count": 100,
      "productive_count": 95,
      "unproductive_count": 5
    }
  ],
  "top_unproductive": [...],
  "domains_summary": [
    {
      "sender_identifier": "empresa.com",
      "total_emails": 150,
      "avg_productivity": 80.5
    }
  ]
}
```

---

### 5. Insights de Palavras-chave
**GET** `/api/analytics/dashboard/keywords/`

Palavras-chave mais frequentes e trending.

**Response 200**:
```json
{
  "productive_keywords": [
    {
      "keyword": "suporte",
      "frequency": 45,
      "last_7_days_freq": 12,
      "last_30_days_freq": 45,
      "avg_confidence_when_present": 0.88
    }
  ],
  "unproductive_keywords": [...],
  "trending_keywords": [
    {
      "keyword": "urgente",
      "category": "Produtivo",
      "frequency": 25,
      "trend_ratio": 2.5
    }
  ]
}
```

---

### 6. Métricas de Performance
**GET** `/api/analytics/dashboard/performance/`

Performance do sistema e saúde.

**Response 200**:
```json
{
  "avg_processing_time": 245.5,
  "total_processed": 150,
  "avg_confidence": 0.875,
  "processing_distribution": [
    {
      "range": "< 100ms",
      "count": 50,
      "percentage": 33.33
    }
  ],
  "confidence_distribution": [...],
  "system_health": {
    "status": "healthy",
    "avg_processing_time": 245.5,
    "confidence_above_70": 140,
    "total_processed_today": 25
  }
}
```

---

### 7. Lista de Emails
**GET** `/api/analytics/emails/`

Lista paginada de emails processados.

**Parâmetros**:
- `category` (opcional): Filtrar por categoria
- `days` (opcional): Período em dias (padrão: 30)
- `page` (opcional): Número da página (padrão: 1)
- `per_page` (opcional): Itens por página (padrão: 50, máx: 100)

**Response 200**:
```json
{
  "emails": [
    {
      "id": "uuid-123",
      "sender_email": "usuario@exemplo.com",
      "sender_domain": "exemplo.com",
      "category": "Produtivo",
      "subcategory": "Suporte Técnico",
      "tone": "Neutro",
      "urgency": "Média",
      "confidence_score": 0.88,
      "processed_at": "2025-11-10T15:30:00Z",
      "keywords_detected": ["suporte", "login", "problema"],
      "has_attachments": false
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_count": 150,
    "per_page": 50,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## 🔧 **Códigos de Status HTTP**

| Código | Significado |
|--------|------------|
| 200 | Sucesso |
| 400 | Erro de validação (dados inválidos) |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## 📝 **Formato de Erros**

Todos os erros seguem o formato:

```json
{
  "error": "Mensagem de erro principal",
  "field_errors": {
    "email_text": ["Este campo é obrigatório"]
  },
  "details": "Detalhes técnicos (apenas em modo debug)"
}
```

---

## 🚀 **Exemplos de Uso**

### Python (requests)
```python
import requests

# Classificar email
response = requests.post(
    'http://localhost:8000/api/classifier/classify/',
    json={'email_text': 'Olá, preciso de ajuda...'}
)
result = response.json()
print(f"Categoria: {result['category']}")
print(f"Urgência: {result['urgency']}")
```

### JavaScript (fetch)
```javascript
// Classificar email
fetch('http://localhost:8000/api/classifier/classify/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email_text: 'Olá, preciso de ajuda...'
  })
})
.then(res => res.json())
.then(data => {
  console.log('Categoria:', data.category);
  console.log('Urgência:', data.urgency);
});
```

### cURL
```bash
# Classificar email
curl -X POST http://localhost:8000/api/classifier/classify/ \
  -H "Content-Type: application/json" \
  -d '{"email_text": "Olá, preciso de ajuda..."}'

# Dashboard overview
curl http://localhost:8000/api/analytics/dashboard/overview/?days=30

# Health check
curl http://localhost:8000/api/classifier/health/
```

---

## 🔐 **Autenticação**

Atualmente a API não requer autenticação (desenvolvimento).  
**Em produção, será implementado**:
- Token-based authentication (JWT)
- API Keys
- Rate limiting

---

## 📊 **Analytics Automático**

Todos os emails processados via `/api/classifier/classify/` e `/api/classifier/batch/` são **automaticamente salvos** no sistema de analytics.

Isso permite:
- Rastreamento de tendências
- Métricas de produtividade
- Análise de padrões
- Dashboard em tempo real

---

## 🎯 **Boas Práticas**

1. **Use batch para múltiplos emails** em vez de múltiplas chamadas individuais
2. **Implemente retry logic** para requests que falharem
3. **Cache responses** de analytics quando possível
4. **Monitore o health check** para garantir disponibilidade
5. **Valide dados** antes de enviar para evitar erros 400

---

## 📚 **Recursos Adicionais**

- **Swagger UI Interativo**: Teste todos endpoints em `http://localhost:8000/api/docs/`
- **ReDoc**: Documentação detalhada em `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: Download do schema em `http://localhost:8000/api/schema/`

---

## ⚡ **Performance**

| Endpoint | Tempo Médio |
|----------|-------------|
| `/classify/` | 200-500ms |
| `/summary/` | 300-800ms |
| `/batch/` (10 emails) | 2-3s |
| `/analytics/*` | 50-200ms (com cache futuro: <50ms) |

---

## 🔄 **Versionamento**

Versão atual: **v1.0.0**

Mudanças futuras serão versionadas via URL:
- `/api/v1/classifier/`
- `/api/v2/classifier/` (quando houver breaking changes)

## 🎯 Visão Geral

Esta API fornece endpoints para classificação de emails e analytics de produtividade.

---

## 📊 **Analytics Dashboard** (`/analytics/`)

### 1. Dashboard Overview
**GET** `/analytics/dashboard/overview/`
- **Descrição:** Visão geral do dashboard com métricas principais
- **Parâmetros:**
  - `days` (opcional): Período em dias (padrão: 30)
- **Response:**
  ```json
  {
    "overview": {
      "total_emails": 150,
      "productive_emails": 120,
      "unproductive_emails": 30,
      "productivity_rate": 80.0,
      "avg_confidence": 0.875,
      "avg_processing_time": 245.5,
      "attachment_rate": 35.2,
      "period_days": 30
    },
    "top_categories": [...],
    "top_senders": [...]
  }
  ```

### 2. Tendências de Produtividade
**GET** `/analytics/dashboard/trends/`
- **Descrição:** Dados de série temporal para gráficos
- **Parâmetros:**
  - `days` (opcional): Período em dias
  - `granularity` (opcional): `daily` ou `hourly`
- **Response:**
  ```json
  {
    "timeline": [
      {
        "date": "2025-11-10",
        "total_emails": 25,
        "productive_emails": 20,
        "productivity_rate": 80.0
      }
    ],
    "trend_analysis": {...}
  }
  ```

### 3. Distribuição de Categorias
**GET** `/analytics/dashboard/categories/`
- **Descrição:** Distribuição percentual de categorias (gráfico de pizza)
- **Parâmetros:**
  - `days` (opcional): Período em dias
- **Response:**
  ```json
  {
    "categories": [
      {
        "category": "Produtivo",
        "subcategory": "Suporte Técnico",
        "count": 45,
        "percentage": 30.0
      }
    ],
    "total_emails": 150
  }
  ```

### 4. Análise de Remetentes
**GET** `/analytics/dashboard/senders/`
- **Descrição:** Remetentes mais produtivos e improdutivos
- **Parâmetros:**
  - `limit` (opcional): Limite de resultados (padrão: 20)
  - `min_emails` (opcional): Mínimo de emails (padrão: 3)
- **Response:**
  ```json
  {
    "top_productive": [...],
    "top_unproductive": [...],
    "domains_summary": [...]
  }
  ```

### 5. Insights de Palavras-chave
**GET** `/analytics/dashboard/keywords/`
- **Descrição:** Palavras-chave mais frequentes e trending
- **Parâmetros:**
  - `limit` (opcional): Limite de resultados
  - `days` (opcional): Período em dias
- **Response:**
  ```json
  {
    "productive_keywords": [...],
    "unproductive_keywords": [...],
    "trending_keywords": [...]
  }
  ```

### 6. Métricas de Performance
**GET** `/analytics/dashboard/performance/`
- **Descrição:** Performance do sistema e saúde
- **Parâmetros:**
  - `days` (opcional): Período em dias
- **Response:**
  ```json
  {
    "avg_processing_time": 245.5,
    "total_processed": 150,
    "processing_distribution": [...],
    "confidence_distribution": [...],
    "system_health": {
      "status": "healthy"
    }
  }
  ```

### 7. Lista de Emails
**GET** `/analytics/emails/`
- **Descrição:** Lista paginada de emails processados
- **Parâmetros:**
  - `category` (opcional): Filtrar por categoria
  - `days` (opcional): Período em dias
  - `page` (opcional): Número da página
  - `per_page` (opcional): Itens por página (máx: 100)
- **Response:**
  ```json
  {
    "emails": [...],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_count": 150
    }
  }
  ```

---

## 🤖 **Email Classifier** (`/classifier/`)

### 1. Classificar Email (API)
**POST** `/classifier/api/classify/`
- **Descrição:** Classifica email e retorna análise completa
- **Request (JSON):**
  ```json
  {
    "email_text": "Olá, preciso de ajuda com..."
  }
  ```
- **Request (File):**
  - `file`: Upload de `.txt`, `.pdf` ou `.docx`
- **Response:**
  ```json
  {
    "topic": "Suporte Técnico",
    "category": "Produtivo",
    "confidence": null,
    "tone": "Neutro",
    "urgency": "Média",
    "suggested_response": "Olá! Agradecemos...",
    "attachment_analysis": {...},
    "word_count": 45,
    "processing_time_ms": 234
  }
  ```

### 2. Resumo Executivo (API)
**POST** `/classifier/api/summary/`
- **Descrição:** Gera resumo executivo de email longo
- **Request:**
  ```json
  {
    "email_text": "Email muito longo...",
    "max_sentences": 3
  }
  ```
- **Response:**
  ```json
  {
    "summary": ["Frase 1", "Frase 2", "Frase 3"],
    "key_points": ["Ponto importante 1", "Ponto 2"],
    "relevance_score": 0.85,
    "word_reduction": 75.5,
    "original_word_count": 200,
    "summary_word_count": 50
  }
  ```

### 3. Processamento em Lote (API)
**POST** `/classifier/api/batch/`
- **Descrição:** Processa múltiplos emails em lote
- **Request (JSON):**
  ```json
  {
    "emails": [
      "Email 1 texto...",
      "Email 2 texto...",
      "Email 3 texto..."
    ]
  }
  ```
- **Request (File):**
  - `file`: Upload de `.txt`, `.csv` ou `.json`
- **Response:**
  ```json
  {
    "request_id": "abc123",
    "total_emails": 3,
    "results": [
      {
        "email_id": 1,
        "classification": {...}
      }
    ]
  }
  ```

---

## 🌐 **Endpoints Web** (Renderizam HTML)

### Classifier Interface
- **GET** `/` - Interface web de classificação
- **POST** `/` - Processa formulário web

### Batch Processing Interface
- **GET** `/batch/` - Interface web de processamento em lote
- **POST** `/batch/` - Processa batch via formulário

### Batch Results
- **GET** `/batch/results/` - Visualiza resultados de batch

---

## 📖 **Documentação da API**

### Swagger UI
**Acesse:** `/api/swagger/`
- Interface interativa para testar todos os endpoints
- Documentação completa com exemplos

### ReDoc
**Acesse:** `/api/redoc/`
- Documentação alternativa em formato ReDoc

### Schema OpenAPI
**Acesse:** `/api/schema/`
- Schema OpenAPI 3.0 em formato JSON

---

## 🔑 **Autenticação**

Atualmente a API não requer autenticação (desenvolvimento).

---

## 📝 **Notas Importantes**

1. **Analytics:**
   - Dados são salvos automaticamente após cada classificação
   - Estatísticas agregadas são atualizadas em tempo real
   - Cache pode ser implementado para endpoints pesados

2. **Classifier:**
   - Suporta múltiplos formatos de arquivo (txt, pdf, docx)
   - Processamento em lote limitado a 50 emails
   - Analytics são salvos automaticamente

3. **Rate Limiting:**
   - Não implementado ainda (planejado para produção)

4. **CORS:**
   - Configurado em `settings.py`
   - Adicione domínios do frontend em `CORS_ALLOWED_ORIGINS`

---

## 🚀 **Como Testar**

1. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Acesse Swagger:**
   ```
   http://localhost:8000/api/swagger/
   ```

3. **Teste um endpoint:**
   - No Swagger, expanda um endpoint
   - Clique em "Try it out"
   - Preencha os parâmetros
   - Clique em "Execute"

---

## 📊 **Status de Implementação**

- ✅ Analytics Dashboard (7 endpoints)
- ✅ Email Classifier API (3 endpoints)
- ✅ Web Interface (3 páginas)
- ✅ Documentação Swagger
- ⏳ Redis Cache (planejado)
- ⏳ Rate Limiting (planejado)
- ⏳ Autenticação (planejado)
