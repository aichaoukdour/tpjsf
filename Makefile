.PHONY: run test lint fmt clean install help

# Default target
help:
	@echo "Available targets:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run pipeline with default config"
	@echo "  make run-tiny   - Run pipeline with tiny config (for testing)"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make fmt        - Format code"
	@echo "  make clean      - Clean generated files"

# Install dependencies
install:
	pip install -r requirements.txt

# Run pipeline
run:
	python -m pipeline.cli run --config configs/default.yaml

# Run with tiny config for quick testing
run-tiny:
	python -m pipeline.cli run --config configs/tiny.yaml

# Run tests
test:
	pytest tests/ -v

# Run linters
lint:
	flake8 pipeline/ --max-line-length=120
	pylint pipeline/ --max-line-length=120 || true

# Format code
fmt:
	black pipeline/ tests/
	isort pipeline/ tests/

# Clean generated files
clean:
	rm -rf data/raw/*
	rm -rf data/quarantine/*
	rm -rf data/curated/*
	rm -rf reports/*
	rm -rf __pycache__
	rm -rf pipeline/__pycache__
	rm -rf tests/__pycache__
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
