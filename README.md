# 🤖 Email Intelligence API

> **API REST completa para classificação inteligente de emails e analytics de produtividade usando IA e NLP.**

Sistema de análise automatizada de emails que classifica mensagens por categoria, tom, urgência e gera respostas sugeridas, além de fornecer métricas detalhadas de produtividade.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Como Rodar o Projeto

### **Pré-requisitos**
- **Python 3.11+** ou **Docker**
- **Git**

### **Opção 1: 🐧 Linux/macOS com Python venv (Recomendado para Desenvolvimento)**

```bash

git clone https://github.com/CarlosVLemos/Email-verify-Backend.git
cd Email-verify-Backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt


cp .env.example .env
nano .env 


python manage.py migrate


python manage.py createcachetable


python manage.py createsuperuser


python manage.py runserver
```

✅ **Pronto!** Acesse:
- **API:** http://localhost:8000
- **Swagger (Documentação):** http://localhost:8000/api/docs/
- **Admin:** http://localhost:8000/admin/

---

### **Opção 2: 🐳 Docker (Recomendado para Produção)**

```bash

git clone https://github.com/CarlosVLemos/Email-verify-Backend.git
cd Email-verify-Backend

cp .env.example .env
nano .env  

docker-compose up -d

docker-compose exec web python manage.py migrate

\
docker-compose exec web python manage.py createsuperuser
```

✅ **Pronto!** Acesse:
- **API:** http://localhost:8000
- **Swagger:** http://localhost:8000/api/docs/

**Comandos úteis do Docker:**
```bash
# Ver logs
docker-compose logs -f web

# Parar containers
docker-compose down

# Reconstruir
docker-compose up -d --build
```

---

### **⚙️ Configuração das Variáveis de Ambiente**

Edite o arquivo `.env` com suas configurações:

#### **🔧 Para Desenvolvimento (SQLite - Simples):**
```bash
# Segurança
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados (SQLite - padrão, sem configuração extra)
DB_ENGINE=sqlite

# Cache (Database cache - sem Redis)
USE_REDIS=False

# API Key para testes
API_KEYS=dev_test_key_123

# CORS para frontend local
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# IA (Opcional - deixe vazio se não for usar)
HF_API_KEY=
```

#### **🐳 Para Docker (PostgreSQL + Redis):**
```bash
# Segurança
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Banco de dados PostgreSQL (Docker)
DB_ENGINE=postgresql
DB_NAME=email_classifier_db
DB_USER=postgres
DB_PASSWORD=postgres_password_change_in_production
DB_HOST=db  # Nome do serviço no docker-compose
DB_PORT=5432

# Cache Redis (Docker)
USE_REDIS=True
REDIS_URL=redis://redis:6379/0

# API Key
API_KEYS=dev_test_key_123

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# IA (Opcional)
HF_API_KEY=
```

#### **🚀 Para Produção (Render, Railway, etc):**
```bash
# Segurança (GERE CHAVES NOVAS!)
SECRET_KEY=sua-chave-secreta-gerada-aqui
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com,seu-dominio.com

# Banco (SQLite para free tier ou PostgreSQL para produção)
DB_ENGINE=sqlite

# Cache
USE_REDIS=False

# API Key (GERE NOVA!)
API_KEYS=prod_sua_chave_api_gerada_aqui

# CORS (URL do seu frontend)
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app

# Logs
LOG_LEVEL=INFO

# IA (Opcional)
HF_API_KEY=
```

**📝 Gerar chaves seguras:**
```bash
# SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# API_KEY
python generate_api_key.py prod
```

---

## 🎯 Características Principais

### 📧 **Email Classifier - Análise Inteligente**
- ✅ **Classificação automática** por categoria (Produtivo/Social/Improdutivo)
- ✅ **Detecção de subcategoria** (Suporte, Dúvida, Spam, Promoção, etc.)
- ✅ **Análise de tom emocional** (Positivo/Negativo/Neutro)
- ✅ **Detecção de urgência** (Alta/Média/Baixa)
- ✅ **Geração automática de resposta** sugerida com IA
- ✅ **Análise de anexos** mencionados no texto
- ✅ **Resumo executivo** para emails longos
- ✅ **Processamento em lote** (até 50 emails de uma vez)
- ✅ **Suporte a arquivos** (.txt, .pdf, .docx)

### 📊 **Analytics Dashboard - Métricas em Tempo Real**
- ✅ **Métricas de produtividade** em tempo real
- ✅ **Tendências temporais** com gráficos (diário/horário)
- ✅ **Análise de remetentes** e domínios mais produtivos/improdutivos
- ✅ **Insights de palavras-chave** por categoria
- ✅ **Métricas de performance** do sistema
- ✅ **Distribuição de categorias** para visualização
- ✅ **Lista paginada** de emails processados com filtros

### 🔐 **Segurança & Autenticação**
- ✅ **API Key Authentication** via header `X-API-Key`
- ✅ **Rate limiting** diferenciado por tipo de usuário
- ✅ **Throttling configurável** (burst/anon/authenticated)
- ✅ **CORS** configurável para múltiplas origens
- ✅ **Debug mode protection** para produção

**📊 Rate Limits:**
- 🚀 **Burst:** 10 requisições/minuto (todos)
- 👤 **Sem API Key:** 50 requisições/hora
- 🔑 **Com API Key:** 1000 requisições/hora

## 📖 Documentação da API

A API possui documentação interativa completa e sempre atualizada.

### **Swagger UI (Recomendado)**
Interface interativa para testar todos os endpoints diretamente no navegador.

```
http://localhost:8000/api/docs/
```

**Features:**
- ✅ Teste de endpoints em tempo real
- ✅ Exemplos de requisições e respostas
- ✅ Validação de schemas
- ✅ Suporte a autenticação com API Key

### **ReDoc**
Documentação detalhada e bem formatada.

```
http://localhost:8000/api/redoc/
```

### **OpenAPI Schema**
Schema JSON para integração automática.

```
http://localhost:8000/api/schema/
```

---

## 🔗 Principais Endpoints

### **📧 Email Classifier**

#### **Classificar Email Único**
```bash
POST /api/classifier/classify/
Content-Type: application/json
X-API-Key: sua_api_key_aqui

{
  "email_text": "Olá, preciso de ajuda com o sistema de login. É urgente!"
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "topic": "Suporte Técnico",
    "category": "Produtivo",
    "tone": "Neutro",
    "urgency": "Alta",
    "suggested_response": "Olá! Agradecemos por entrar em contato...",
    "word_count": 12,
    "processing_time_ms": 234
  }
}
```

#### **Resumo Executivo**
```bash
POST /api/classifier/summary/
Content-Type: application/json
X-API-Key: sua_api_key_aqui

{
  "email_text": "Email muito longo com várias informações...",
  "max_sentences": 3
}
```

#### **Processamento em Lote**
```bash
POST /api/classifier/batch/
Content-Type: application/json
X-API-Key: sua_api_key_aqui

{
  "emails": [
    "Email 1...",
    "Email 2...",
    "Email 3..."
  ]
}
```

### **📊 Analytics Dashboard**

#### **Overview Geral**
```bash
GET /api/analytics/dashboard/overview/?days=30
X-API-Key: sua_api_key_aqui
```

#### **Tendências de Produtividade**
```bash
GET /api/analytics/dashboard/trends/?days=30&granularity=daily
X-API-Key: sua_api_key_aqui
```

#### **Distribuição de Categorias**
```bash
GET /api/analytics/dashboard/categories/?days=30
X-API-Key: sua_api_key_aqui
```

#### **Análise de Remetentes**
```bash
GET /api/analytics/dashboard/senders/?limit=20&min_emails=3
X-API-Key: sua_api_key_aqui
```

### **🏥 Health Check**
```bash
GET /api/classifier/health/
```

**Resposta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "analytics": "healthy",
    "classifier": "healthy"
  }
}
```

---

## 🔑 Autenticação com API Key

### **Como Usar**

Todas as requisições devem incluir o header `X-API-Key`:

```bash
curl -X POST https://sua-api.com/api/classifier/classify/ \
  -H "X-API-Key: sua_chave_api_aqui" \
  -H "Content-Type: application/json" \
  -d '{"email_text": "Seu email aqui"}'
```

### **Exemplo com JavaScript/Fetch**
```javascript
const response = await fetch('https://sua-api.com/api/classifier/classify/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'sua_chave_api_aqui'
  },
  body: JSON.stringify({
    email_text: 'Seu email aqui'
  })
});

const data = await response.json();
console.log(data);
```

### **Exemplo com Python/Requests**
```python
import requests

url = 'https://sua-api.com/api/classifier/classify/'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'sua_chave_api_aqui'
}
payload = {
    'email_text': 'Seu email aqui'
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
print(data)
```

---

## �️ Tecnologias Utilizadas

### **Backend & Framework**
- **Python 3.11+** - Linguagem de programação
- **Django 5.2** - Framework web robusto e escalável
- **Django REST Framework 3.16** - API REST toolkit
- **drf-spectacular** - Documentação OpenAPI/Swagger automática

### **Processamento & IA**
- **NLTK** - Natural Language Processing
- **Hugging Face** (opcional) - Modelos de IA para geração de respostas
- **pdfplumber** - Extração de texto de PDFs
- **python-docx** - Leitura de arquivos Word

### **Banco de Dados & Cache**
- **SQLite** - Banco padrão para desenvolvimento
- **PostgreSQL 15** - Banco recomendado para produção
- **Redis 7** (opcional) - Cache e message broker

### **Servidor & Deploy**
- **Gunicorn** - WSGI HTTP Server para produção
- **Whitenoise** - Servir arquivos estáticos
- **Docker & Docker Compose** - Containerização

### **Segurança & Autenticação**
- **API Key Authentication** - Sistema de autenticação via chave
- **CORS Headers** - Controle de origem de requisições
- **Django Security Middleware** - Proteções de segurança

---

## 📁 Estrutura do Projeto

```
Email-verify-Backend/
├── 📁 classifier/              # App de classificação de emails
│   ├── 📁 email_scripts/       # Lógica de IA e classificação
│   │   ├── ai_classifier.py
│   │   ├── email_classifier.py
│   │   ├── nlp_processor.py
│   │   └── ...
│   ├── 📁 services/            # Camada de serviços
│   ├── 📁 utils/               # Utilitários
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📁 analytics/               # App de analytics e métricas
│   ├── 📁 utils/               # Helpers e queries
│   │   ├── query_helpers.py
│   │   ├── request_helpers.py
│   │   └── services.py
│   ├── models.py               # Models de dados
│   ├── views.py                # Views do dashboard
│   ├── serializers.py
│   └── urls.py
│
├── 📁 core/                    # Configurações do projeto
│   ├── 📁 middleware/          # Middlewares customizados
│   │   ├── authentication.py   # Autenticação API Key
│   │   └── throttling.py       # Rate limiting
│   ├── settings.py             # Configurações Django
│   ├── urls.py                 # URLs principais
│   ├── apps.py                 # Config de apps
│   └── wsgi.py
│
├── � docker/                  # Arquivos Docker
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   └── README.md
│
├── 📁 tests/                   # Testes automatizados
│
├── 📄 manage.py                # CLI do Django
├── � requirements.txt         # Dependências Python
├── 📄 .env.example             # Exemplo de variáveis de ambiente
├── � docker-compose.yml       # Compose para desenvolvimento
├── � docker-compose.prod.yml  # Compose para produção
├── � render.yaml              # Config para deploy no Render
├── 📄 build.sh                 # Script de build
└── 📄 README.md                # Este arquivo
```

---

## 🧪 Testes

### **Executar Todos os Testes**
```bash
python manage.py test
```

### **Testar App Específico**
```bash
# Testar apenas classifier
python manage.py test classifier

# Testar apenas analytics
python manage.py test analytics
```

### **Com Coverage**
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera relatório HTML
```

---

## 🚢 Deploy em Produção

### **Deploy no Render (Recomendado)**

1. **Faça fork/clone do repositório**

2. **Crie um Web Service no Render**
   - Conecte seu repositório GitHub
   - O Render detectará automaticamente o `render.yaml`

3. **Configure as variáveis de ambiente:**
   ```bash
   SECRET_KEY=sua-chave-secreta-gerada
   DEBUG=False
   ALLOWED_HOSTS=seu-app.onrender.com
   DB_ENGINE=sqlite
   USE_REDIS=False
   API_KEYS=prod_sua_chave_api_gerada
   CORS_ALLOWED_ORIGINS=https://seu-frontend.com
   LOG_LEVEL=INFO
   ```

4. **Deploy automático!** 🎉

**URLs de exemplo:**
- API: `https://seu-app.onrender.com`
- Swagger: `https://seu-app.onrender.com/api/docs/`

### **Deploy em Outros Serviços**

O projeto é compatível com:
- ✅ **Railway**
- ✅ **Heroku**
- ✅ **Google Cloud Run**
- ✅ **AWS Elastic Beanstalk**
- ✅ **Azure App Service**

**Requisitos mínimos:**
- Python 3.11+
- 512 MB RAM
- Suporte a SQLite ou PostgreSQL

---

## � Segurança em Produção

### **Checklist de Deploy:**

- [ ] Gerar nova `SECRET_KEY` forte
- [ ] Definir `DEBUG=False`
- [ ] Configurar `ALLOWED_HOSTS` com domínios reais
- [ ] Usar senhas fortes para banco de dados
- [ ] Configurar `CORS_ALLOWED_ORIGINS` com origens específicas
- [ ] Habilitar HTTPS (certificado SSL)
- [ ] Implementar rate limiting adequado
- [ ] Configurar backup do banco de dados
- [ ] Monitorar logs e métricas
- [ ] Manter dependências atualizadas

### **Gerar Chaves Seguras:**

```bash
# SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# API_KEY
python generate_api_key.py prod
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. **Fork o projeto**
2. **Crie uma branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Commit suas mudanças** (`git commit -m 'Add: Nova feature incrível'`)
4. **Push para a branch** (`git push origin feature/MinhaFeature`)
5. **Abra um Pull Request**

### **Diretrizes:**
- Escreva testes para novas features
- Mantenha o código limpo e documentado
- Siga o estilo de código PEP 8
- Atualize a documentação quando necessário

---

## 📝 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Carlos V. Lemos**

- 🔗 GitHub: [@CarlosVLemos](https://github.com/CarlosVLemos)
- 📧 Email: contato@carlosvlemos.dev
- 🌐 Repositório: [Email-verify-Backend](https://github.com/CarlosVLemos/Email-verify-Backend)

---

## 🙏 Agradecimentos

- Comunidade **Django** e **Django REST Framework**
- **drf-spectacular** pela documentação automática
- Todos os contribuidores do projeto

---

## 📚 Recursos Adicionais

### **Documentação Oficial:**
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)

### **Tutoriais e Guias:**
- [Deploy no Render](https://render.com/docs/deploy-django)
- [PostgreSQL com Django](https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes)
- [Docker com Django](https://docs.docker.com/samples/django/)

---

<div align="center">

### ⭐ **Se este projeto foi útil, considere dar uma estrela no GitHub!** ⭐

**Desenvolvido com ❤️ por [Carlos V. Lemos](https://github.com/CarlosVLemos)**

</div>
