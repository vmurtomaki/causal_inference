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

# For streamlit
uv run streamlit run src/causal_inference/api/app.py
```


4. **Validate Code:**
```bash
make format && make check && make typecheck

```

## Known Limitations

- **Linear Probability Model on a binary outcome.** The outcome (`Purchase_CH`) is binary,
  but this pipeline fits a Partially Linear Regression, which is additive and unconstrained
  to [0, 1]. This is why the dashboard (`app.py`) must manually clip projected probabilities
  to a valid range. A production version should use a Logistic PLR or an Interactive
  Regression Model designed for binary treatment/outcome effects.
- **Sensitivity analysis bounds are illustrative, not benchmarked.** `evaluate_robustness`
  uses fixed `cf_y=0.05, cf_d=0.05` values. These are not derived from the explanatory power
  of observed covariates (e.g. `LoyalCH`) and should not be read as a rigorous bound on
  omitted variable bias.
- **No hyperparameter tuning.** `LGBMRegressor` settings (`n_estimators`, `learning_rate`)
  are fixed, not cross-validated. Residual confounding bias may remain if the nuisance
  models' out-of-sample fit is suboptimal.
- no naive (OLS/logistic) baseline
- no out-of-sample nuisance-model diagnostic