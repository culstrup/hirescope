.PHONY: help install install-dev test test-unit test-integration test-all lint format type-check security clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: install ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

test: test-unit ## Run unit tests (default)

test-unit: ## Run unit tests with coverage
	pytest tests/unit/ -v --cov=hirescope --cov-report=term-missing --cov-report=html

test-integration: ## Run integration tests
	pytest tests/integration/ -v -m integration

test-all: ## Run all tests
	pytest tests/ -v --cov=hirescope --cov-report=term-missing --cov-report=html

lint: ## Run linters (ruff)
	ruff check .

format: ## Format code with black
	black .
	ruff check . --fix

type-check: ## Run type checking with mypy
	mypy hirescope/ --ignore-missing-imports

security: ## Run security scan with bandit
	bandit -r hirescope/ -f screen

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf analysis_results/
	rm -f REPORT_*.md
	rm -f TOP_CANDIDATES_*.csv
	rm -f RESULTS_*.json
	rm -f progress_*.json

run: ## Run HireScope
	python hirescope.py

setup-test-env: install-dev ## Set up complete test environment
	@echo "Test environment ready!"
	@echo "Run 'make test' to run unit tests"
	@echo "Run 'make test-all' to run all tests"
	@echo "Run 'make pre-commit' to run all code quality checks"