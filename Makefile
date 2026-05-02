.PHONY: build install fmt lint test ci

build:
	uv pip install -e .

install:
	uv pip install --group dev

fmt:
	uv run ruff format guitar/ tests/

lint:
	uv run ruff check guitar/ tests/
	uv run mypy guitar/

test:
	uv run pytest tests/ --cov=guitar --cov-report=term-missing

ci: lint test
