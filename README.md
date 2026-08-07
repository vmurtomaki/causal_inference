# Causal Inference & Price Optimization Pipeline

## Overview

This repository implements an econometrics pipeline utilizing Double Machine Learning (DML) to isolate the true causal effect of pricing interventions. By leveraging a Partially Linear Regression (PLR) model and K-fold cross-fitting, the pipeline strips away high-dimensional confounding variables (e.g., competitor pricing, brand loyalty) to uncover unbiased causal estimates from observational retail data.

The core parameter estimated is the **Marginal Effect** of price on demand:

$$\theta_0 = \frac{\partial \mathbb{P}(\text{Purchase}=1)}{\partial \text{Price}}$$

## Architecture

Built on a strict, modern Python enterprise standard:

- **Environment & Lockfile:** Managed deterministically via `uv` (Rust-based).
- **Layout:** Enforces the `src/` layout to prevent `sys.path` shadowing and ensure strict testing boundaries.
- **Static Analysis:** Aggressive linting and formatting via `Ruff`; strict static type checking via `MyPy`.

## Directory Structure

```text
causal_inference/
├── .env                 # Local variables (gitignored)
├── pyproject.toml       # Declarative configuration
├── uv.lock              # Deterministic dependency graph
├── Makefile              # Orchestration commands
├── src/causal_inference/
│   ├── core/            # Pure math & DML models (dml_engine.py)
│   ├── services/        # Side-effects & ingestion (data_ingestion.py)
│   ├── main.py          # Pipeline entry point
│   └── config.py        # Environment validation
├── tests/               # Pytest suite
└── data/                # Segmented data (raw/ & processed/)
```

## Quick Start

This project requires **Python 3.12+** and **uv**. The virtual environment is provisioned and managed automatically; do not manually activate virtual environments.

1. **Install uv:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone & Sync:**

   ```bash
   git clone <repo_url> && cd causal_inference
   uv sync
   ```

3. **Execute Pipeline:**

   ```bash
   uv run --env-file .env python src/causal_inference/main.py

   # Launch the interactive scenario simulator
   uv run streamlit run src/causal_inference/api/app.py
   ```

4. **Validate Code:**

   ```bash
   make all
   ```

## Technical Roadmap & Known Limitations

To maintain prototyping velocity, specific technical and econometric trade-offs were made. These establish the roadmap for productionization:

- **Linear Probability Model (LPM) on Binary Targets:** The outcome (`Purchase_CH`) is binary, but the pipeline utilizes a PLR model with a continuous LightGBM regressor. This functions mathematically as an additive LPM, which is why the Streamlit dashboard manually clips projected probabilities to a `[0, 1]` range. Production deployments will migrate to an Interactive Regression Model (`DoubleMLIRM`) or a Logistic PLR to natively bound outputs.

- **Unconstrained Nuisance Models:** The `LGBMRegressor` parameters are currently fixed (`n_estimators=300`) without depth constraints. Because DML relies on rapid nuisance convergence rates for Neyman orthogonality, the production pipeline will introduce cross-validated hyperparameter tuning to prevent out-of-sample overfitting on small datasets.

- **Competitor Collinearity:** The competitor pricing features (`SalePriceMM`, `PriceMM`, `SpecialMM`) contain deterministic collinearity (`SalePrice = Price - Discount`). While gradient-boosted trees route around this rank deficiency mathematically, deterministic features will be pruned in subsequent iterations to stabilize feature importance scores and reduce variance.

- **Illustrative Sensitivity Bounds:** The omitted variable bias (OVB) sensitivity bounds are currently hardcoded to an arbitrary 5%. In a rigorous deployment, these bounds will be dynamically benchmarked against the explanatory power of the strongest observed covariate (e.g., `LoyalCH`).

- **Unobserved Confounders:** The Directed Acyclic Graph (DAG) assumes selection on observables. High-dimensional fixed effects (e.g., `StoreID` or `Week`) are currently omitted, potentially leaving residual confounding bias.