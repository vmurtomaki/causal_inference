# Causal Inference & Price Elasticity Optimization

## Overview
This repository implements an advanced econometrics pipeline utilizing Double Machine Learning (DML) to isolate the true causal effect of pricing interventions. By leveraging Partially Linear Regression and cross-fitting, this model resolves confounding variables (e.g., seasonality, competitor actions) inherent in high-dimensional retail data (Orange Juice dataset).

The core parameter estimated is the price elasticity of demand:
$$\theta_0 = \frac{\partial q / q}{\partial p / p}$$

## Architecture
Built on a strict, modern enterprise standard:
* **Environment & Lockfile:** Managed deterministically via `uv` (Rust-based).
* **Layout:** Enforces the `src/` layout to prevent `sys.path` shadowing and ensure test isolation.
* **Static Analysis:** Linting and formatting via `Ruff`; static type checking via `MyPy`.

## Directory Structure
```text
causal_inference/
├── .env                 # Local variables (gitignored)
├── pyproject.toml       # Declarative configuration
├── uv.lock              # Deterministic dependency graph
├── Makefile             # Orchestration commands
├── src/causal_inference/
│   ├── core/            # Pure math & DML models (dml_engine.py)
│   ├── services/        # Side-effects & ingestion (data_ingestion.py)
│   ├── main.py          # Pipeline entry point
│   └── config.py        # Environment validation
├── tests/               # Pytest suite
└── data/                # Segmented data (raw/ & processed/)

```

## Quick Start

This project requires **Python 3.12.4** and **uv**. DO NOT manually activate virtual environments.

1. **Install uv:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Clone & Sync:** ```bash
git clone <repo_url> && cd causal_inference
uv sync
```

```


3. **Execute Pipeline:**
```bash
uv run --env-file .env python src/causal_inference/main.py

```


4. **Validate Code:**
```bash
make format && make check && make typecheck

```