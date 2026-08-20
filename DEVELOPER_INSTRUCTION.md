# Developer Operations & Onboarding Guide

Welcome to the standard analytical architecture. This project uses strict Git isolation, the `src/` layout, and `uv` to guarantee that your development environment is bit-for-bit identical to the production runner. 

## 1. Getting Started
Do not use `pip`, `poetry`, or `virtualenv`. Do not manually run `source .venv/bin/activate`. 

* **Initialize the environment:** Running `uv sync` or any `uv run` command automatically detects the `pyproject.toml`, fetches the pinned Python 3.12.4 runtime, resolves the `uv.lock` file, and provisions a hidden `.venv` directory.
* **Running Code:** Always prefix your execution with `uv run`. This dynamically injects the virtual environment into the sub-shell.
    * *Correct:* `uv run python src/causal_inference/main.py`
    * *Incorrect:* `python src/causal_inference/main.py`
* **Environment Variables:** Create a `.env` file at the root containing `DATA_PATH`, `ARTIFACT_PATH`, `N_FOLDS`, `N_REP`, and `RANDOM_SEED`. Load it directly via: `uv run --env-file .env python src/causal_inference/main.py`.

## 2. Developing & Updating Code
We enforce strict, declarative code standards. Unused imports, missing types, and legacy syntax will instantly fail CI builds.

* **Formatting (Ruff):** Formats to a 100-character line length and enforces double quotes.
    * *Command:* `make format` (Executes `uv run ruff format .`)
* **Linting (Ruff):** Validates against aggressive standards including flake8-bugbear, comprehensions, and implicit string concatenations. 
    * *Command:* `make check` (Executes `uv run ruff check . --fix`, which mutates the codebase to resolve standard library import sorting and legacy syntax automatically)
* **Type Checking (MyPy):** The `src/` directory is strictly typed.
    * *Command:* `make typecheck` (Executes `uv run mypy src/`)
* **Adding Dependencies:** * *Production package:* `uv add <package>` (Updates `pyproject.toml` and locks `uv.lock`).
    * *Development package:* `uv add --dev <package>` (Isolates toolchains like `pytest` from production containers).

## 3. Troubleshooting Matrix

| Symptom | Root Cause | Resolution |
| :--- | :--- | :--- |
| **`ModuleNotFoundError` during `pytest`** | You are executing tests without `uv run`, causing the test suite to miss the `src/` installation mapping. | Execute tests strictly via `make test` or `uv run pytest tests/`. |
| **Import shadowing / Local code ignored** | You placed a Python file at the repository root. The `src/` layout is mandated precisely to prevent root-level `sys.path` injection. | Move all business logic into `src/causal_inference/`. Note the root also legitimately contains `tests/`, `scripts/`, and `docs/` alongside metadata files (`.env`, `pyproject.toml`). |
| **CI build fails on Ruff `TID` or `S` rules** | You used a relative import (e.g., `from ..utils import X`) or an insecure library (e.g., `xml.etree`). | Refactor to absolute imports (`from causal_inference.utils import X`). Replace insecure libraries as dictated by the Ruff security linter. |
| **MyPy complains about missing `py.typed`** | A new library or local module isn't exposing its type hints to the daemon. | Ensure `src/causal_inference/py.typed` remains intact. If a third-party library is untyped, add `# type: ignore` locally or install its stub package. |
| **Sudden environment corruption** | Edge case caching error or cross-contamination from a manual `.venv` modification. | Because `uv` is incredibly fast, safely nuke the cache: Delete `.venv/`, then run `uv sync`. It will rebuild perfectly in milliseconds. |