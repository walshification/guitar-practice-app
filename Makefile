.PHONY: build install fmt lint test ci

build:
	uv pip install -e .

install:
	uv venv
	uv pip install --group dev

fmt:
	uv run ruff format guitar/ tests/

lint:
	uv run ruff check guitar/ tests/

test:
	uv run pytest tests/ --cov=guitar --cov-report=term-missing

ci: lint test
