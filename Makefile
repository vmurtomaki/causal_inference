.PHONY: check format typecheck test run-pipeline run-app run-all

check:
	uv run ruff check . --fix

format:
	uv run ruff format .

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/ -v

run-pipeline:
	uv run python src/causal_inference/main.py

run-app:
	uv run streamlit run src/causal_inference/api/app.py

run-all: run-pipeline run-app

all: format check typecheck test