.PHONY: help install-compose up down logs migrate test clean shell bash psql

# Override manual:
# make up MAC=true
MAC ?= false

ifeq ($(MAC),true)
	COMPOSE := docker-compose
else
	COMPOSE := docker compose
endif

help:
	@echo "Finance Analysis - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install-compose    Install Docker Compose v2"
	@echo "  make build              Build Docker images"
	@echo ""
	@echo "Development:"
	@echo "  make up                 Start all services"
	@echo "  make down               Stop all services"
	@echo "  make logs               View Django logs"
	@echo "  make shell              Django shell (python manage.py shell)"
	@echo "  make bash               Bash into Django container"
	@echo ""
	@echo "Database:"
	@echo "  make migrate            Run Django migrations"
	@echo "  make psql               Access PostgreSQL"
	@echo ""
	@echo "Testing:"
	@echo "  make test               Run tests"
	@echo "  make test-coverage      Run tests with coverage"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean              Stop containers and remove volumes"
	@echo "  make clean-all          Remove all containers, volumes, images"

install-compose:
	@echo "Installing Docker Compose v2..."
	@mkdir -p ~/.docker/cli-plugins
	@curl -sSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
	@chmod +x ~/.docker/cli-plugins/docker-compose
	@echo "✓ Docker Compose v2 installed"
	@docker compose version

build:
	@echo "Building Docker images..."
	$(COMPOSE) -f docker-compose.dev.yml build

up:
	@echo "Starting services..."
	@mkdir -p ./data/seaweed-master ./data/seaweed-volume
	$(COMPOSE) -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  Django: http://localhost:$${APP_PORT:-8000}"
	@echo "  Seaweed Admin: http://localhost:$${SEAWEED_ADMIN_PORT:-18080}"
	@echo "  PostgreSQL: localhost:$${POSTGRES_PORT:-5432}"
	@echo ""
	@make logs

down:
	@echo "Stopping services..."
	$(COMPOSE) -f docker-compose.dev.yml down
	@echo "✓ Services stopped"

logs:
	$(COMPOSE) -f docker-compose.dev.yml logs -f django

migrate:
	@echo "Running migrations..."
	$(COMPOSE) -f docker-compose.dev.yml exec django python manage.py migrate
	@echo "✓ Migrations completed"

shell:
	$(COMPOSE) -f docker-compose.dev.yml exec django python manage.py shell

bash:
	$(COMPOSE) -f docker-compose.dev.yml exec django /bin/bash

psql:
	$(COMPOSE) -f docker-compose.dev.yml exec postgres psql -U postgres -d finance_analysis

test:
	@echo "Running tests..."
	$(COMPOSE) -f docker-compose.dev.yml exec django python manage.py test
	@echo "✓ Tests completed"

test-coverage:
	@echo "Running tests with coverage..."
	$(COMPOSE) -f docker-compose.dev.yml exec django coverage run --source='.' manage.py test
	$(COMPOSE) -f docker-compose.dev.yml exec django coverage report
	@echo "✓ Coverage report generated"

clean:f
	@echo "Cleaning up (stopping containers)..."
	$(COMPOSE) -f docker-compose.dev.yml down
	@echo "✓ Cleaned up"

clean-all:
	@echo "WARNING: This will remove all containers, volumes, and images"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) -f docker-compose.dev.yml down -v --rmi all; \
		echo "✓ All cleaned up"; \
	else \
		echo "Cancelled"; \
	fi

.DEFAULT_GOAL := help
