.PHONY: check format typecheck test

check:
	uv run ruff check . --fix

format:
	uv run ruff format .

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/ -v

all: format check typecheck test