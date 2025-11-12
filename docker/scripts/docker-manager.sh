

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

show_help() {
    cat << EOF
🐳 Email Classifier - Docker Management

Usage: ./docker-manager.sh [command]

Commands:
    start           Start all services
    stop            Stop all services
    restart         Restart all services
    build           Build/rebuild Docker images
    logs            Show logs (all services)
    logs-web        Show web service logs
    logs-redis      Show Redis logs
    logs-celery     Show Celery worker logs
    shell           Open Django shell
    bash            Open bash in web container
    migrate         Run database migrations
    makemigrations  Create new migrations
    createsuperuser Create Django superuser
    collectstatic   Collect static files
    test            Run tests
    clean           Stop and remove all containers and volumes
    status          Show status of all services
    redis-cli       Open Redis CLI
    db-shell        Open PostgreSQL shell
    help            Show this help message

Examples:
    ./docker-manager.sh start
    ./docker-manager.sh logs-web
    ./docker-manager.sh shell

EOF
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Please install docker-compose first."
        exit 1
    fi
}

case "$1" in
    start)
        print_info "Starting all services..."
        docker-compose up -d
        print_success "Services started!"
        print_info "Access the API at http://localhost:8000"
        print_info "Access Swagger at http://localhost:8000/api/docs/"
        ;;
    
    stop)
        print_info "Stopping all services..."
        docker-compose down
        print_success "Services stopped!"
        ;;
    
    restart)
        print_info "Restarting all services..."
        docker-compose restart
        print_success "Services restarted!"
        ;;
    
    build)
        print_info "Building Docker images..."
        docker-compose build --no-cache
        print_success "Build complete!"
        ;;
    
    logs)
        docker-compose logs -f
        ;;
    
    logs-web)
        docker-compose logs -f web
        ;;
    
    logs-redis)
        docker-compose logs -f redis
        ;;
    
    logs-celery)
        docker-compose logs -f celery_worker
        ;;
    
    shell)
        print_info "Opening Django shell..."
        docker-compose exec web python manage.py shell
        ;;
    
    bash)
        print_info "Opening bash in web container..."
        docker-compose exec web bash
        ;;
    
    migrate)
        print_info "Running migrations..."
        docker-compose exec web python manage.py migrate
        print_success "Migrations complete!"
        ;;
    
    makemigrations)
        print_info "Creating migrations..."
        docker-compose exec web python manage.py makemigrations
        print_success "Migrations created!"
        ;;
    
    createsuperuser)
        print_info "Creating superuser..."
        docker-compose exec web python manage.py createsuperuser
        ;;
    
    collectstatic)
        print_info "Collecting static files..."
        docker-compose exec web python manage.py collectstatic --noinput
        print_success "Static files collected!"
        ;;
    
    test)
        print_info "Running tests..."
        docker-compose exec web python manage.py test
        ;;
    
    clean)
        print_info "⚠️  This will remove all containers and volumes!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            print_success "Cleanup complete!"
        else
            print_info "Cancelled."
        fi
        ;;
    
    status)
        print_info "Services status:"
        docker-compose ps
        ;;
    
    redis-cli)
        print_info "Opening Redis CLI..."
        docker-compose exec redis redis-cli
        ;;
    
    db-shell)
        print_info "Opening PostgreSQL shell..."
        docker-compose exec db psql -U postgres -d email_classifier_db
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
