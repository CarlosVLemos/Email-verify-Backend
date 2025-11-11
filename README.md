# 🤖 Email Intelligence API

API REST completa para classificação inteligente de emails e analytics de produtividade usando IA.

## 🎯 Características Principais

### 📧 Email Classifier
- ✅ Classificação automática por categoria (Produtivo/Social/Improdutivo)
- ✅ Detecção de subcategoria (Suporte, Dúvida, Spam, etc.)
- ✅ Análise de tom emocional (Positivo/Negativo/Neutro)
- ✅ Detecção de urgência (Alta/Média/Baixa)
- ✅ Geração automática de resposta sugerida
- ✅ Análise de anexos mencionados
- ✅ Resumo executivo para emails longos
- ✅ Processamento em lote (até 50 emails)

### 📊 Analytics Dashboard
- ✅ Métricas de produtividade em tempo real
- ✅ Tendências temporais e gráficos
- ✅ Análise de remetentes e domínios
- ✅ Insights de palavras-chave
- ✅ Métricas de performance
- ✅ Distribuição de categorias
- ✅ Lista paginada com filtros

## 🚀 Quick Start

### Pré-requisitos
- Python 3.8+
- pip
- virtualenv (recomendado)

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/CarlosVLemos/Email-verify-Backend.git
cd Email-verify-Backend
```

2. **Crie e ative ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

4. **Execute migrações**
```bash
python manage.py migrate
```

5. **Inicie o servidor**
```bash
python manage.py runserver
```

6. **Acesse a documentação**
```
http://localhost:8000/api/docs/
```

## 📖 Documentação da API

### Swagger UI (Interativo)
```
http://localhost:8000/api/docs/
```
Interface interativa para testar todos os endpoints.

### ReDoc (Detalhado)
```
http://localhost:8000/api/redoc/
```
Documentação completa e bem formatada.

### OpenAPI Schema
```
http://localhost:8000/api/schema/
```
Schema JSON para integração automática.

## 🔗 Endpoints Principais

### Email Classifier

#### Classificar Email
```bash
POST /api/classifier/classify/
Content-Type: application/json

{
  "email_text": "Olá, preciso de ajuda com o sistema..."
}
```

#### Resumo Executivo
```bash
POST /api/classifier/summary/
Content-Type: application/json

{
  "email_text": "Email muito longo...",
  "max_sentences": 3
}
```

#### Processamento em Lote
```bash
POST /api/classifier/batch/
Content-Type: application/json

{
  "emails": [
    "Email 1...",
    "Email 2...",
    "Email 3..."
  ]
}
```

### Analytics Dashboard

#### Overview do Dashboard
```bash
GET /api/analytics/dashboard/overview/?days=30
```

#### Tendências de Produtividade
```bash
GET /api/analytics/dashboard/trends/?days=30&granularity=daily
```

#### Distribuição de Categorias
```bash
GET /api/analytics/dashboard/categories/?days=30
```

## 📁 Estrutura do Projeto

```
Email-verify-Backend/
├── classifier/              # App de classificação de emails
│   ├── email_scripts/       # Lógica de IA e classificação
│   ├── serializers.py       # Serializers DRF
│   ├── views_api.py         # Views da API
│   └── urls.py              # Rotas do classifier
├── analytics/               # App de analytics e métricas
│   ├── models.py            # Models de dados
│   ├── views.py             # Views do dashboard
│   ├── serializers.py       # Serializers de analytics
│   ├── utils/               # Utilitários (helpers, queries, services)
│   └── urls.py              # Rotas de analytics
├── core/                    # Configurações do projeto
│   ├── settings.py          # Settings Django
│   └── urls.py              # URLs principais
├── manage.py                # CLI Django
└── requirements.txt         # Dependências Python
```

## 🛠️ Tecnologias Utilizadas

- **Django 5.2** - Framework web
- **Django REST Framework** - API REST
- **drf-spectacular** - Documentação OpenAPI/Swagger
- **SQLite** - Banco de dados (desenvolvimento)
- **pdfplumber** - Extração de texto de PDFs
- **python-docx** - Leitura de arquivos Word
- **NLTK** - Processamento de linguagem natural

## 📊 Analytics Automático

Todos os emails processados são automaticamente salvos no sistema de analytics, permitindo:

- 📈 Rastreamento de tendências ao longo do tempo
- 🎯 Métricas de produtividade
- 🔍 Análise de padrões de comunicação
- 📊 Dashboard em tempo real
- 💡 Insights sobre remetentes e categorias

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Testar apenas classifier
python manage.py test classifier

# Testar apenas analytics
python manage.py test analytics
```

## 🐳 Docker (Em Breve)

```bash
# Build
docker-compose build

# Run
docker-compose up

# Com Redis cache
docker-compose -f docker-compose.yml -f docker-compose.redis.yml up
```

## 🔐 Segurança

### Desenvolvimento
- CORS aberto para testes locais
- Debug mode ativado
- Sem autenticação necessária

### Produção (Recomendações)
- [ ] Implementar autenticação JWT
- [ ] Configurar CORS restritivo
- [ ] Adicionar rate limiting
- [ ] Usar HTTPS
- [ ] Configurar SECRET_KEY seguro
- [ ] Desativar DEBUG mode

## 📈 Roadmap

### Em Desenvolvimento
- [ ] Sistema de cache com Redis
- [ ] Rate limiting por IP
- [ ] Autenticação JWT

### Futuro
- [ ] Machine Learning para classificação
- [ ] Suporte a mais idiomas
- [ ] API de webhooks
- [ ] Dashboard web frontend
- [ ] Exportação de relatórios PDF/Excel

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👤 Autor

**Carlos V. Lemos**
- GitHub: [@CarlosVLemos](https://github.com/CarlosVLemos)
- Repositório: [Email-verify-Backend](https://github.com/CarlosVLemos/Email-verify-Backend)

## 🙏 Agradecimentos

- Comunidade Django
- Django REST Framework
- drf-spectacular para documentação automática

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
