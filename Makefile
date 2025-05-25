.PHONY: help build up down logs shell test clean

help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker images (CPU)"
	@echo "  make build-gpu   - Build Docker images (GPU)"
	@echo "  make up          - Start all services (CPU)"
	@echo "  make up-gpu      - Start all services (GPU)"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - Show logs"
	@echo "  make shell       - Enter backend container"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up containers and volumes"

# Build Docker images (CPU)
build:
	docker-compose -f docker-compose.cpu.yml build

# Build Docker images (GPU)
build-gpu:
	docker-compose build

# Start services (CPU)
up:
	docker-compose -f docker-compose.cpu.yml up -d

# Start services with logs (CPU)
up-logs:
	docker-compose -f docker-compose.cpu.yml up

# Start services (GPU)
up-gpu:
	docker-compose up -d

# Start services with logs (GPU)
up-gpu-logs:
	docker-compose up

# Stop services
down:
	docker-compose -f docker-compose.cpu.yml down
	docker-compose down

# View logs
logs:
	docker-compose -f docker-compose.cpu.yml logs -f

logs-gpu:
	docker-compose logs -f

# Enter backend shell
shell:
	docker-compose -f docker-compose.cpu.yml exec backend bash

shell-gpu:
	docker-compose exec backend bash

# Run tests
test:
	docker-compose -f docker-compose.cpu.yml exec backend poetry run pytest

test-gpu:
	docker-compose exec backend poetry run pytest

# Clean everything
clean:
	docker-compose -f docker-compose.cpu.yml down -v
	docker-compose down -v
	docker system prune -f

# Database shell
db-shell:
	docker-compose -f docker-compose.cpu.yml exec postgres psql -U whereuser -d whereisthisplace

# Check health
health:
	curl http://localhost:8000/health