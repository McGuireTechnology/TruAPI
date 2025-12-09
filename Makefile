.PHONY: help install dev test format lint clean docker-build docker-up docker-down

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := poetry run python
UVICORN := poetry run uvicorn
PYTEST := poetry run pytest
BLACK := poetry run black
RUFF := poetry run ruff
MYPY := poetry run mypy
MKDOCS := poetry run mkdocs

help: ## Show this help message
	@echo "TruAPI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

install-prod: ## Install only production dependencies
	poetry install --only main

dev: ## Run the FastAPI application in development mode
	$(UVICORN) truapi.drivers.rest.main:app --reload --host 0.0.0.0 --port 8000

dev-docs: ## Serve documentation locally with MkDocs
	$(MKDOCS) serve

run: ## Run the FastAPI application in production mode
	$(UVICORN) truapi.drivers.rest.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Run tests with pytest
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage report
	$(PYTEST) tests/ -v --cov=truapi --cov-report=html --cov-report=term

format: ## Format code with Black
	$(BLACK) truapi/ tests/

format-check: ## Check code formatting without making changes
	$(BLACK) truapi/ tests/ --check

lint: ## Lint code with Ruff
	$(RUFF) check truapi/ tests/

lint-fix: ## Lint and auto-fix issues with Ruff
	$(RUFF) check truapi/ tests/ --fix

type-check: ## Type check with mypy
	$(MYPY) truapi/

check: format-check lint type-check ## Run all checks (format, lint, type)

fix: format lint-fix ## Format and auto-fix linting issues

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage dist/ build/

shell: ## Start a Poetry shell
	poetry shell

add: ## Add a new dependency (usage: make add pkg=package-name)
	poetry add $(pkg)

add-dev: ## Add a new dev dependency (usage: make add-dev pkg=package-name)
	poetry add --group dev $(pkg)

update: ## Update all dependencies
	poetry update

lock: ## Update poetry.lock file
	poetry lock --no-update

docker-build: ## Build Docker image
	docker build -t truapi:latest .

docker-up: ## Start services with docker-compose
	docker-compose up -d

docker-down: ## Stop services with docker-compose
	docker-compose down

docker-logs: ## View docker-compose logs
	docker-compose logs -f api

db-migrate: ## Run database migrations
	$(PYTHON) -m alembic upgrade head

db-revision: ## Create a new migration (usage: make db-revision msg="message")
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

db-downgrade: ## Rollback last migration
	$(PYTHON) -m alembic downgrade -1

info: ## Show project information
	@echo "Project: TruAPI"
	@echo "Python version:"
	@poetry run python --version
	@echo ""
	@echo "Installed packages:"
	@poetry show --tree

# Deployment commands
deploy-droplet: ## Deploy to Digital Ocean Droplet
	@echo "🚀 Deploying to Digital Ocean Droplet..."
	@bash deploy/deploy.sh

setup-droplet: ## Initial setup of Digital Ocean Droplet (run on server)
	@echo "🔧 Setting up droplet..."
	@bash deploy/setup.sh

restart-service: ## Restart the systemd service (run on server)
	sudo systemctl restart truapi

logs-service: ## View application logs (run on server)
	sudo journalctl -u truapi -f

logs-nginx: ## View Nginx logs (run on server)
	sudo tail -f /var/log/nginx/truapi.mcguire.technology.access.log

status: ## Check service status (run on server)
	sudo systemctl status truapi

deploy-production: ## Pull latest code and restart (run on server)
	git pull origin main
	poetry install --only main --no-interaction
	sudo systemctl restart truapi
	@echo "✅ Deployment completed"
