# 🐳 Docker Setup

## Quick Start

```bash
# Build e start
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

## Comandos com Helper Script

```bash
chmod +x docker-manager.sh

./docker-manager.sh start          # Inicia serviços
./docker-manager.sh stop           # Para serviços
./docker-manager.sh restart        # Reinicia serviços
./docker-manager.sh logs-web       # Logs do Django
./docker-manager.sh logs-redis     # Logs do Redis
./docker-manager.sh logs-celery    # Logs do Celery
./docker-manager.sh shell          # Django shell
./docker-manager.sh bash           # Bash no container
./docker-manager.sh migrate        # Rodar migrations
./docker-manager.sh createsuperuser # Criar admin
./docker-manager.sh test           # Rodar testes
./docker-manager.sh redis-cli      # Redis CLI
./docker-manager.sh db-shell       # PostgreSQL shell
./docker-manager.sh clean          # Limpar tudo (cuidado!)
./docker-manager.sh help           # Ver todos comandos
```

## Serviços

- **web** (porta 8000) - Django + Gunicorn
- **db** (porta 5432) - PostgreSQL 15
- **redis** (porta 6379) - Redis 7
- **celery_worker** - Processamento assíncrono
- **celery_beat** - Tarefas agendadas

## Testar Endpoints

```bash
chmod +x test_endpoints.sh
./test_endpoints.sh
```

## Configuração

Edite o arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://postgres:password@db:5432/email_classifier_db
REDIS_URL=redis://redis:6379/0
```

## Volumes

- `postgres_data` - Dados do PostgreSQL
- `redis_data` - Dados do Redis
- `static_volume` - Arquivos estáticos
- `nltk_data` - Dados do NLTK

## Health Checks

```bash
# Status dos containers
docker-compose ps

# Health da API
curl http://localhost:8000/api/classifier/health/

# PostgreSQL
docker-compose exec db pg_isready -U postgres

# Redis
docker-compose exec redis redis-cli ping
```
