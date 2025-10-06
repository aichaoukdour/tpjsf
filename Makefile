.PHONY: help install clean run test lint

help:
	@echo "Secure Data Curation Pipeline - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  clean      - Clean generated files and directories"
	@echo "  run        - Run the pipeline with default config"
	@echo "  test       - Run tests (placeholder)"
	@echo "  lint       - Run linting (placeholder)"
	@echo "  setup      - Create sample test data"

install:
	@echo "Installing dependencies..."
	pip install pyyaml

clean:
	@echo "Cleaning generated files..."
	rm -rf data/raw/*
	rm -rf data/quarantine/*
	rm -rf data/curated/*
	rm -rf reports/*
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

run:
	@echo "Running pipeline with default configuration..."
	python3 -m pipeline.cli run --config configs/default.yaml

test:
	@echo "Running tests..."
	@echo "⚠️  Tests not implemented yet"

lint:
	@echo "Running linting..."
	@echo "⚠️  Linting not implemented yet"

setup:
	@echo "Creating sample test data..."
	mkdir -p data/sample_code
	@echo "✅ Sample directory created at data/sample_code"
	@echo "   Add your Python files there and run 'make run'"
