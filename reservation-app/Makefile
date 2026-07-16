.PHONY: help create_virtual_env install install-prod lint lint-fix format type-check check test clean

DIRS ?= src tests

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

create_virtual_env: ## Create virtual environment
	scripts/create_virtual_env.sh

update_virtual_env: ## Update lock virtual environment
	scripts/update_virtual_env.sh

install: ## Install dependencies
	uv sync

install-prod: ## Install production dependencies
	uv sync --no-dev

lint: ## Run linting with ruff
	uv run ruff check ${DIRS}

lint-fix: ## Run linting with ruff and fix auto-fixable issues
	uv run ruff check --fix ${DIRS}

format: ## Format code with ruff
	uv run ruff format ${DIRS}

type-check: ## Run type checking with mypy
	uv run mypy --config-file mypy.toml -n 4

check: ## Run all checks (lint + format check + type check)
	@make lint
	@make format
	@make type-check

test: ## Run tests
	scripts/pytest.sh

test-cov: ## Run tests with coverage
	scripts/pytest.sh -c

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# Database migration commands
migration: ## Create a new migration file
	uv run alembic revision --autogenerate -m "$(msg)"

migrate: ## Apply all pending migrations
	uv run alembic upgrade head

migrate-downgrade: ## Downgrade to previous migration
	uv run alembic downgrade -1

migrate-history: ## Show migration history
	uv run alembic history

migrate-current: ## Show current migration
	uv run alembic current

migrate-stamp: ## Stamp database with current migration (without applying)
	uv run alembic stamp head
