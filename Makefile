.PHONY: help build up down logs clean test dev start stop restart

DOCKER_COMPOSE := docker-compose
PYTHON := python3

help:
	@echo "Shoulder-to-Shoulder Microservices Management"
	@echo ""
	@echo "Usage:"
	@echo "  make build              Build all service containers"
	@echo "  make up                 Start all services (detached)"
	@echo "  make down               Stop all services"
	@echo "  make logs               Show logs for all services"
	@echo "  make logs-follow        Follow logs for all services"
	@echo "  make stop               Stop all services"
	@echo "  make restart            Restart all services"
	@echo "  make clean              Remove containers, volumes and images"
	@echo "  make dev                Start services with volume mounts for development"
	@echo "  make status             Show status of all services"
	@echo "  make bash-USER          Enter bash shell in user_service"
	@echo "  make bash-NOTIF         Enter bash shell in notification_service"
	@echo "  make bash-EVENT         Enter bash shell in event_service"
	@echo "  make bash-ADMIN         Enter bash shell in admin_service"
	@echo "  make bash-MAPS          Enter bash shell in maps_service"
	@echo "  make migrate-user       Run database migrations for user service"
	@echo "  make migrate-event      Run database migrations for event service"
	@echo "  make migrate-notif      Run database migrations for notification service"
	@echo ""

# Build services
build:
	$(DOCKER_COMPOSE) build

# Start services in background
up:
	$(DOCKER_COMPOSE) up -d
	@echo "Services are starting. Use 'make logs-follow' to see logs"

# Development mode with volume mounts
dev:
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

# Stop services
down:
	$(DOCKER_COMPOSE) down

# Stop without removing volumes
stop:
	$(DOCKER_COMPOSE) stop

# Restart services
restart: stop up

# View logs
logs:
	$(DOCKER_COMPOSE) logs

logs-follow:
	$(DOCKER_COMPOSE) logs -f

# Check service status
status:
	@echo "Docker Compose Status:"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "Service Health:"
	@$(DOCKER_COMPOSE) exec -T postgres pg_isready -U postgres 2>/dev/null && echo "✓ PostgreSQL is healthy" || echo "✗ PostgreSQL is unavailable"
	@curl -s http://localhost:4222/ping > /dev/null 2>&1 && echo "✓ NATS is healthy" || echo "✗ NATS is unavailable"
	@curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "✓ User Service is healthy" || echo "✗ User Service is unavailable"
	@curl -s http://localhost:8001/health > /dev/null 2>&1 && echo "✓ Notification Service is healthy" || echo "✗ Notification Service is unavailable"
	@curl -s http://localhost:8002/health > /dev/null 2>&1 && echo "✓ Event Service is healthy" || echo "✗ Event Service is unavailable"
	@curl -s http://localhost:8003/health > /dev/null 2>&1 && echo "✓ Admin Service is healthy" || echo "✗ Admin Service is unavailable"

# Database migrations
migrate-user:
	$(DOCKER_COMPOSE) exec -T user_service alembic upgrade head

migrate-event:
	$(DOCKER_COMPOSE) exec -T event_service alembic upgrade head

migrate-notif:
	$(DOCKER_COMPOSE) exec -T notification_service alembic upgrade head

# Access service shells
bash-user:
	$(DOCKER_COMPOSE) exec user_service bash

bash-notif:
	$(DOCKER_COMPOSE) exec notification_service bash

bash-event:
	$(DOCKER_COMPOSE) exec event_service bash

bash-admin:
	$(DOCKER_COMPOSE) exec admin_service bash

bash-maps:
	$(DOCKER_COMPOSE) exec maps_service bash

# Clean up
clean:
	$(DOCKER_COMPOSE) down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove containers and images
clean-all: clean
	$(DOCKER_COMPOSE) down -v --rmi all

# Format code
format:
	@echo "Formatting Python code with black and ruff..."
	$(PYTHON) -m black . --exclude="\.venv|build|dist" 2>/dev/null || echo "black not available"
	$(PYTHON) -m ruff check . --fix 2>/dev/null || echo "ruff not available"

# Lint code
lint:
	@echo "Linting Python code..."
	$(PYTHON) -m ruff check . 2>/dev/null || echo "ruff not available"
	$(PYTHON) -m black . --check --exclude="\.venv|build|dist" 2>/dev/null || echo "black not available"

# Database reset (WARNING: destructive)
db-reset:
	@echo "Resetting database..."
	$(DOCKER_COMPOSE) exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS shoulder_to_shoulder_db;"
	$(DOCKER_COMPOSE) exec -T postgres psql -U postgres -c "CREATE DATABASE shoulder_to_shoulder_db;"
	@echo "Database reset complete. Re-run migrations with 'make migrate-*'"

.DEFAULT_GOAL := help
