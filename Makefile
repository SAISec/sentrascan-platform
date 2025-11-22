# SentraScan Platform Makefile
# Provides targets for development, testing, Docker operations, and GCP deployment

.PHONY: help install venv dev-install server db-init db-reset auth-create
.PHONY: test test-unit test-integration test-smoke test-ui lint format type-check doctor
.PHONY: docker-build docker-build-multiarch docker-up docker-down docker-logs docker-clean docker-shell docker-test
.PHONY: test-cloud-ci test-cloud-remote test-cloud-smoke
.PHONY: gcp-auth gcp-build gcp-deploy-cloudrun gcp-deploy-gke gcp-setup
.PHONY: clean clean-all

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Configuration Variables
# ============================================================================

# Docker configuration
IMAGE_TAG ?= sentrascan/platform:dev
DOCKER_COMPOSE := docker compose

# GCP configuration
GCP_PROJECT ?= $(shell gcloud config get-value project 2>/dev/null || echo "")
GCP_REGION ?= us-central1
GCP_IMAGE_REGISTRY ?= gcr.io
GCP_SERVICE_NAME ?= sentrascan-platform

# API configuration
API_BASE ?= http://localhost:8200
API_PORT ?= 8200

# Python configuration
PYTHON ?= python3
PIP ?= pip3
VENV_DIR ?= venv

# Test configuration
PYTEST ?= pytest
TEST_DIR ?= tests

# ============================================================================
# Help Target
# ============================================================================

help: ## Display this help message
	@echo "SentraScan Platform - Available Targets:"
	@echo ""
	@echo "Local Development:"
	@echo "  make install          - Install package in editable mode"
	@echo "  make venv             - Create virtual environment"
	@echo "  make dev-install      - Install with dev dependencies"
	@echo "  make server           - Run local development server"
	@echo "  make db-init          - Initialize database"
	@echo "  make db-reset         - Reset database (drop and recreate)"
	@echo "  make auth-create      - Create API key (use NAME=... ROLE=...)"
	@echo ""
	@echo "Local Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests (requires docker-compose)"
	@echo "  make test-smoke       - Run API smoke tests"
	@echo "  make test-ui          - Run UI smoke tests"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code"
	@echo "  make type-check       - Run type checking"
	@echo "  make doctor           - Run health check"
	@echo ""
	@echo "Docker Operations:"
	@echo "  make docker-build           - Build Docker image"
	@echo "  make docker-build-multiarch - Build multi-architecture image"
	@echo "  make docker-up              - Start docker-compose services"
	@echo "  make docker-down            - Stop docker-compose services"
	@echo "  make docker-logs            - View docker-compose logs"
	@echo "  make docker-clean           - Remove containers, volumes, images"
	@echo "  make docker-shell           - Open shell in API container"
	@echo "  make docker-test            - Run tests inside Docker container"
	@echo ""
	@echo "Cloud Testing:"
	@echo "  make test-cloud-ci     - Run tests in CI/CD context"
	@echo "  make test-cloud-remote - Run tests against remote instance (use API_BASE=...)"
	@echo "  make test-cloud-smoke  - Run smoke tests against cloud instance"
	@echo ""
	@echo "GCP Deployment:"
	@echo "  make gcp-auth            - Authenticate with GCP"
	@echo "  make gcp-build           - Build and push to GCP Artifact Registry"
	@echo "  make gcp-deploy-cloudrun - Deploy to Cloud Run"
	@echo "  make gcp-deploy-gke      - Deploy to GKE"
	@echo "  make gcp-setup           - Setup GCP project resources"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      - Clean build artifacts and cache"
	@echo "  make clean-all  - Clean everything including Docker volumes"
	@echo ""
	@echo "Examples:"
	@echo "  make docker-build IMAGE_TAG=my-tag"
	@echo "  make auth-create NAME=admin ROLE=admin"
	@echo "  make test-cloud-remote API_BASE=https://api.example.com"

# ============================================================================
# Local Development
# ============================================================================

venv: ## Create virtual environment
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtual environment created at $(VENV_DIR)"; \
		echo "Activate with: source $(VENV_DIR)/bin/activate"; \
	else \
		echo "Virtual environment already exists at $(VENV_DIR)"; \
	fi

install: ## Install package in editable mode with dependencies
	$(PIP) install -e .

dev-install: ## Install with dev dependencies (if any)
	$(PIP) install -e .
	@echo "Note: Add dev dependencies to pyproject.toml if needed"

server: ## Run local development server
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "Warning: DATABASE_URL not set. Using default."; \
	fi
	sentrascan server --host 0.0.0.0 --port $(API_PORT)

db-init: ## Initialize database (local)
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "Error: DATABASE_URL environment variable not set"; \
		echo "For local: export DATABASE_URL=postgresql+psycopg2://sentrascan:changeme@localhost:5432/sentrascan"; \
		exit 1; \
	fi
	sentrascan db init

db-reset: ## Reset database (drop and recreate) - WARNING: Destructive
	@echo "WARNING: This will drop and recreate the database"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Dropping database..."; \
		$(DOCKER_COMPOSE) exec -T db psql -U sentrascan -d postgres -c "DROP DATABASE IF EXISTS sentrascan;" || true; \
		$(DOCKER_COMPOSE) exec -T db psql -U sentrascan -d postgres -c "CREATE DATABASE sentrascan;" || true; \
		$(DOCKER_COMPOSE) exec api sentrascan db init; \
		echo "Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

auth-create: ## Create API key (use NAME=... ROLE=admin|viewer)
	@if [ -z "$(NAME)" ] || [ -z "$(ROLE)" ]; then \
		echo "Error: NAME and ROLE required"; \
		echo "Usage: make auth-create NAME=mykey ROLE=admin"; \
		exit 1; \
	fi
	@if [ "$(ROLE)" != "admin" ] && [ "$(ROLE)" != "viewer" ]; then \
		echo "Error: ROLE must be 'admin' or 'viewer'"; \
		exit 1; \
	fi
	@if command -v docker >/dev/null 2>&1 && $(DOCKER_COMPOSE) ps api >/dev/null 2>&1; then \
		$(DOCKER_COMPOSE) exec api sentrascan auth create --name "$(NAME)" --role "$(ROLE)"; \
	else \
		sentrascan auth create --name "$(NAME)" --role "$(ROLE)"; \
	fi

# ============================================================================
# Local Testing
# ============================================================================

test: ## Run all tests (unit + integration)
	@echo "Running all tests..."
	$(PYTEST) $(TEST_DIR)

test-unit: ## Run unit tests only (exclude integration)
	@echo "Running unit tests (excluding integration tests)..."
	$(PYTEST) $(TEST_DIR) -m "not integration"

test-integration: ## Run integration tests (requires docker-compose)
	@echo "Checking if docker-compose services are running..."
	@if ! $(DOCKER_COMPOSE) ps api >/dev/null 2>&1; then \
		echo "Error: docker-compose services not running. Run 'make docker-up' first."; \
		exit 1; \
	fi
	@echo "Running integration tests..."
	@SENTRASCAN_API_BASE=$(API_BASE) bash scripts/test.sh

test-smoke: ## Run API smoke tests
	@echo "Checking if docker-compose services are running..."
	@if ! $(DOCKER_COMPOSE) ps api >/dev/null 2>&1; then \
		echo "Error: docker-compose services not running. Run 'make docker-up' first."; \
		exit 1; \
	fi
	@echo "Running API smoke tests..."
	bash scripts/api-smoketest.sh

test-ui: ## Run UI smoke tests
	@echo "Running UI smoke tests..."
	$(PYTEST) $(TEST_DIR)/test_ui_smoke.py -v

lint: ## Run linting checks
	@echo "Running linting checks..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src/ tests/; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ tests/; \
	else \
		echo "No linter found. Install ruff or flake8."; \
		exit 1; \
	fi

format: ## Format code
	@echo "Formatting code..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format src/ tests/; \
	elif command -v black >/dev/null 2>&1; then \
		black src/ tests/; \
	else \
		echo "No formatter found. Install ruff or black."; \
		exit 1; \
	fi

type-check: ## Run type checking
	@echo "Running type checking..."
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src/ || true; \
	else \
		echo "mypy not found. Install with: pip install mypy"; \
		exit 1; \
	fi

doctor: ## Run health check command
	@if command -v docker >/dev/null 2>&1 && $(DOCKER_COMPOSE) ps api >/dev/null 2>&1; then \
		$(DOCKER_COMPOSE) exec api sentrascan doctor; \
	else \
		sentrascan doctor; \
	fi

# ============================================================================
# Docker Operations
# ============================================================================

docker-build: ## Build Docker image
	@echo "Building Docker image: $(IMAGE_TAG)"
	docker build -t $(IMAGE_TAG) .

docker-build-multiarch: ## Build multi-architecture image
	@echo "Building multi-architecture image: $(IMAGE_TAG)"
	@if [ -z "$(PUSH)" ]; then \
		bash scripts/buildx-multiarch.sh $(IMAGE_TAG); \
	else \
		bash scripts/buildx-multiarch.sh $(IMAGE_TAG) --push; \
	fi

docker-up: ## Start docker-compose services
	@echo "Starting docker-compose services..."
	$(DOCKER_COMPOSE) up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services started. API available at $(API_BASE)"
	@echo "Run 'make db-init' to initialize the database (if not already done)"

docker-down: ## Stop docker-compose services
	@echo "Stopping docker-compose services..."
	$(DOCKER_COMPOSE) down

docker-logs: ## View docker-compose logs (use SERVICE=api to filter)
	@if [ -n "$(SERVICE)" ]; then \
		$(DOCKER_COMPOSE) logs -f $(SERVICE); \
	else \
		$(DOCKER_COMPOSE) logs -f; \
	fi

docker-clean: ## Remove containers, volumes, and images
	@echo "WARNING: This will remove all containers, volumes, and images"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v --rmi local; \
		docker system prune -f; \
		echo "Docker cleanup complete"; \
	else \
		echo "Cancelled"; \
	fi

docker-shell: ## Open shell in API container
	$(DOCKER_COMPOSE) exec api /bin/bash

docker-test: ## Run tests inside Docker container
	@echo "Running tests inside Docker container..."
	$(DOCKER_COMPOSE) exec api $(PYTEST) /app/$(TEST_DIR)

# ============================================================================
# Cloud Testing
# ============================================================================

test-cloud-ci: ## Run tests in CI/CD context (set CI=true)
	@echo "Running tests in CI/CD context..."
	@export CI=true; \
	export SENTRASCAN_API_BASE=$(API_BASE); \
	$(PYTEST) $(TEST_DIR) -v

test-cloud-remote: ## Run tests against remote cloud instance (use API_BASE=...)
	@if [ "$(API_BASE)" = "http://localhost:8200" ]; then \
		echo "Warning: API_BASE is still set to localhost"; \
		echo "Usage: make test-cloud-remote API_BASE=https://api.example.com"; \
	fi
	@echo "Running tests against remote instance: $(API_BASE)"
	@export SENTRASCAN_API_BASE=$(API_BASE); \
	$(PYTEST) $(TEST_DIR) -v

test-cloud-smoke: ## Run smoke tests against cloud instance (use API_BASE=...)
	@if [ "$(API_BASE)" = "http://localhost:8200" ]; then \
		echo "Warning: API_BASE is still set to localhost"; \
		echo "Usage: make test-cloud-smoke API_BASE=https://api.example.com"; \
	fi
	@echo "Running smoke tests against: $(API_BASE)"
	@export SENTRASCAN_API_BASE=$(API_BASE); \
	bash scripts/api-smoketest.sh

# ============================================================================
# GCP Deployment
# ============================================================================

gcp-auth: ## Authenticate with GCP
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT not set. Set it or run: gcloud config set project YOUR_PROJECT_ID"; \
		exit 1; \
	fi
	@echo "Authenticating with GCP..."
	gcloud auth login
	gcloud auth configure-docker $(GCP_IMAGE_REGISTRY)
	@echo "GCP authentication complete"

gcp-build: ## Build and push to GCP Artifact Registry
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT not set"; \
		exit 1; \
	fi
	@echo "Building and pushing to GCP Artifact Registry..."
	@GCP_IMAGE=$(GCP_IMAGE_REGISTRY)/$(GCP_PROJECT)/$(GCP_SERVICE_NAME):latest; \
	echo "Image: $$GCP_IMAGE"; \
	docker build -t $$GCP_IMAGE .; \
	docker push $$GCP_IMAGE; \
	echo "Image pushed: $$GCP_IMAGE"

gcp-deploy-cloudrun: ## Deploy to Cloud Run
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT not set"; \
		exit 1; \
	fi
	@echo "Deploying to Cloud Run..."
	@GCP_IMAGE=$(GCP_IMAGE_REGISTRY)/$(GCP_PROJECT)/$(GCP_SERVICE_NAME):latest; \
	gcloud run deploy $(GCP_SERVICE_NAME) \
		--image $$GCP_IMAGE \
		--platform managed \
		--region $(GCP_REGION) \
		--allow-unauthenticated \
		--port 8200 \
		--set-env-vars "MODELAUDIT_CACHE_DIR=/cache" \
		--memory 2Gi \
		--cpu 2 \
		--timeout 300
	@echo "Deployment complete. Get URL with: gcloud run services describe $(GCP_SERVICE_NAME) --region $(GCP_REGION) --format 'value(status.url)'"

gcp-deploy-gke: ## Deploy to GKE (requires kubectl and GKE cluster)
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT not set"; \
		exit 1; \
	fi
	@if ! command -v kubectl >/dev/null 2>&1; then \
		echo "Error: kubectl not found. Install kubectl first."; \
		exit 1; \
	fi
	@echo "Deploying to GKE..."
	@echo "Note: This is a placeholder. Create Kubernetes manifests for full GKE deployment."
	@echo "Example: kubectl apply -f k8s/"

gcp-setup: ## Setup GCP project resources
	@if [ -z "$(GCP_PROJECT)" ]; then \
		echo "Error: GCP_PROJECT not set"; \
		exit 1; \
	fi
	@echo "Setting up GCP project resources..."
	@echo "1. Enabling required APIs..."
	gcloud services enable artifactregistry.googleapis.com --project $(GCP_PROJECT)
	gcloud services enable run.googleapis.com --project $(GCP_PROJECT)
	gcloud services enable container.googleapis.com --project $(GCP_PROJECT)
	@echo "2. Creating Artifact Registry repository (if not exists)..."
	@gcloud artifacts repositories create sentrascan-repo \
		--repository-format=docker \
		--location=$(GCP_REGION) \
		--project=$(GCP_PROJECT) 2>/dev/null || echo "Repository may already exist"
	@echo "GCP setup complete"

# ============================================================================
# Utilities
# ============================================================================

clean: ## Clean build artifacts, cache, and temporary files
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf dist/ build/ .coverage htmlcov/ 2>/dev/null || true
	@echo "Clean complete"

clean-all: clean ## Clean everything including Docker volumes
	@echo "Cleaning Docker resources..."
	$(DOCKER_COMPOSE) down -v 2>/dev/null || true
	docker system prune -af --volumes 2>/dev/null || true
	@echo "Full cleanup complete"
