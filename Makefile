# Makefile for T1 Construção Project

# Variables
POETRY := poetry
DOCKER_COMPOSE := docker compose
PYTHON := python3.12

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install build run test clean lint format check db-setup db-migrate db-reset docker-build docker-run docker-stop docker-clean ci-setup ci-test ci-build all

# Default target
help: ## Show this help message
	@echo "$(BLUE)T1 Construção - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Development Setup
install: ## Install dependencies using Poetry
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(POETRY) install
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

# Database Commands
db-setup: ## Initialize database and run migrations
	@echo "$(YELLOW)Setting up database...$(NC)"
	$(POETRY) run aerich init-db
	$(POETRY) run aerich upgrade
	@echo "$(GREEN)Database setup complete!$(NC)"

db-migrate: ## Generate and apply new migrations
	@echo "$(YELLOW)Generating migrations...$(NC)"
	$(POETRY) run aerich migrate
	$(POETRY) run aerich upgrade
	@echo "$(GREEN)Migrations applied successfully!$(NC)"

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)WARNING: This will reset the database and delete all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(POETRY) run aerich reset
	@echo "$(GREEN)Database reset complete!$(NC)"

# Code Quality
lint: ## Run linting with pylint
	@echo "$(YELLOW)Running linting...$(NC)"
	$(POETRY) run pylint src/ tests/
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	$(POETRY) run black src/ tests/
	@echo "$(GREEN)Code formatted successfully!$(NC)"

type-check: ## Run type checking with pyright
	@echo "$(YELLOW)Running type checking...$(NC)"
	$(POETRY) run pyright
	@echo "$(GREEN)Type checking complete!$(NC)"

check: format lint type-check ## Run all code quality checks

# Testing
test: ## Run tests with pytest
	@echo "$(YELLOW)Running tests...$(NC)"
	$(POETRY) run pytest
	@echo "$(GREEN)Tests completed!$(NC)"

test-verbose: ## Run tests with verbose output
	@echo "$(YELLOW)Running tests with verbose output...$(NC)"
	$(POETRY) run pytest -v
	@echo "$(GREEN)Tests completed!$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	$(POETRY) run pytest --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated!$(NC)"

# Docker Commands
docker-build: ## Build Docker images
	@echo "$(YELLOW)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Docker images built successfully!$(NC)"

docker-run: ## Run the application with Docker Compose
	@echo "$(YELLOW)Starting application with Docker Compose...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Application started! Available at http://localhost:8000$(NC)"
	@echo "$(BLUE)Adminer (DB Admin) available at http://localhost:8080$(NC)"

docker-run-logs: ## Run the application with logs
	@echo "$(YELLOW)Starting application with Docker Compose (with logs)...$(NC)"
	$(DOCKER_COMPOSE) up

docker-stop: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Containers stopped!$(NC)"

docker-clean: ## Stop and remove containers, networks, and volumes
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Docker cleanup complete!$(NC)"

docker-logs: ## Show Docker container logs
	$(DOCKER_COMPOSE) logs -f

# Development Commands
dev: ## Run the application in development mode
	@echo "$(YELLOW)Starting development server...$(NC)"
	$(POETRY) run fastapi dev src/t1_construcao/main.py --host 0.0.0.0 --port 8000

dev-reload: ## Run the application in development mode with auto-reload
	@echo "$(YELLOW)Starting development server with auto-reload...$(NC)"
	$(POETRY) run fastapi dev src/t1_construcao/main.py --host 0.0.0.0 --port 8000 --reload

# Build Commands
build: install check test docker-build ## Complete build process (install, check, test, build)
	@echo "$(GREEN)Build process completed successfully!$(NC)"

# Run Commands
run: docker-run ## Run the application (alias for docker-run)

run-dev: db-setup dev ## Setup database and run in development mode

# CI/CD Commands
ci-setup: ## Setup for CI environment
	@echo "$(YELLOW)Setting up CI environment...$(NC)"
	pip install poetry
	$(POETRY) install
	@echo "$(GREEN)CI environment setup complete!$(NC)"

ci-test: ## Run tests for CI (with coverage and JUnit output)
	@echo "$(YELLOW)Running CI tests...$(NC)"
	$(POETRY) run pytest --cov=src --cov-report=xml --cov-report=term --junitxml=test-results.xml
	@echo "$(GREEN)CI tests completed!$(NC)"

ci-build: ci-setup check ci-test docker-build ## Complete CI build pipeline
	@echo "$(GREEN)CI build completed successfully!$(NC)"

# Cleanup
clean: ## Clean up generated files and caches
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Full workflow commands
all: build ## Run complete build and setup process

fresh-start: clean install db-setup test docker-build ## Fresh start: clean, install, setup DB, test, and build

# Environment info
info: ## Show environment information
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Poetry version: $$($(POETRY) --version)"
	@echo "Docker version: $$(docker --version)"
	@echo "Docker Compose version: $$($(DOCKER_COMPOSE) --version)"
