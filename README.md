# 🤖 Email Intelligence API

API REST completa para classificação inteligente de emails e analytics de produtividade usando IA e NLP.

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
- ✅ Suporte a arquivos (.txt, .pdf, .docx)

### 📊 Analytics Dashboard
- ✅ Métricas de produtividade em tempo real
- ✅ Tendências temporais e gráficos
- ✅ Análise de remetentes e domínios
- ✅ Insights de palavras-chave
- ✅ Métricas de performance
- ✅ Distribuição de categorias
- ✅ Lista paginada com filtros

### 🐳 Docker & Infrastructure
- ✅ Docker Compose completo
- ✅ PostgreSQL 15 como banco de dados
- ✅ Redis para cache e filas
- ✅ Celery para processamento assíncrono
- ✅ Gunicorn como servidor WSGI
- ✅ Health checks automáticos

## � Docker (Recomendado para Produção)

### Quick Start com Docker

```bash
# 1. Clone o repositório
git clone https://github.com/CarlosVLemos/Email-verify-Backend.git
cd Email-verify-Backend

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# 3. Build e start
cd docker
docker-compose up -d

# 4. Migrations
docker-compose exec web python manage.py migrate

# 5. Criar superuser
docker-compose exec web python manage.py createsuperuser

# 6. Acessar
# API: http://localhost:8000
# Swagger: http://localhost:8000/api/docs/
```

### Script Helper

```bash
cd docker
chmod +x docker-manager.sh

# Comandos disponíveis
./docker-manager.sh start          # Inicia todos os serviços
./docker-manager.sh stop           # Para todos os serviços
./docker-manager.sh logs-web       # Ver logs do Django
./docker-manager.sh shell          # Django shell
./docker-manager.sh migrate        # Rodar migrations
./docker-manager.sh help           # Ver todos os comandos
```

### Serviços Docker

- **web** - Django + Gunicorn (porta 8000)
- **db** - PostgreSQL 15 (porta 5432)
- **redis** - Redis 7 (porta 6379)
- **celery_worker** - Processamento assíncrono
- **celery_beat** - Tarefas agendadas

## 🚀 Desenvolvimento Local (Sem Docker)

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

### Backend
- **Django 5.2** - Framework web
- **Django REST Framework 3.16** - API REST
- **drf-spectacular** - Documentação OpenAPI/Swagger
- **NLTK** - Processamento de linguagem natural

### Infrastructure
- **PostgreSQL 15** - Banco de dados
- **Redis 7** - Cache e message broker
- **Celery** - Processamento assíncrono
- **Gunicorn** - WSGI server
- **Whitenoise** - Static files

### Processamento
- **pdfplumber** - Extração de texto de PDFs
- **python-docx** - Leitura de arquivos Word
- **NLTK** - NLP e stemming

## 📁 Estrutura do Projeto

```
Email-verify-Backend/
├── docker/                  # Arquivos Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-manager.sh
│   └── test_endpoints.sh
├── classifier/              # App de classificação
│   ├── email_scripts/       # Lógica de IA
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── analytics/               # App de analytics
│   ├── models.py
│   ├── views.py
│   ├── tasks.py             # Celery tasks
│   ├── cache_decorators.py  # Cache helpers
│   └── urls.py
├── core/                    # Configurações
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

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

## � Roadmap

### ✅ Concluído
- [x] Classificação inteligente de emails
- [x] Analytics dashboard completo
- [x] Docker com PostgreSQL e Redis
- [x] Cache em múltiplos níveis
- [x] Processamento assíncrono (Celery)
- [x] Documentação Swagger completa
- [x] Suporte a múltiplos formatos de arquivo

### 🚧 Em Desenvolvimento
- [ ] Autenticação JWT
- [ ] Rate limiting por IP
- [ ] Integração com APIs de IA externas

### 🔮 Futuro
- [ ] Machine Learning para classificação
- [ ] Suporte a mais idiomas
- [ ] Dashboard web frontend (React/Vue)
- [ ] Exportação de relatórios
- [ ] Webhooks para notificações

## 🔐 Segurança & Produção

### Checklist de Deploy

- [ ] Mudar `SECRET_KEY` no `.env`
- [ ] Definir `DEBUG=False`
- [ ] Configurar `ALLOWED_HOSTS` com domínios reais
- [ ] Usar senhas fortes para PostgreSQL
- [ ] Configurar CORS com origens específicas
- [ ] Habilitar HTTPS
- [ ] Implementar rate limiting
- [ ] Configurar backup do PostgreSQL
- [ ] Monitorar logs e métricas

## 🧪 Testes de Endpoints

```bash
cd docker
chmod +x test_endpoints.sh
./test_endpoints.sh
```

Este script testa:
- Health check
- Classificação de email
- Dashboard overview
- Resumo executivo
- Processamento em lote

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
