# Causal Pricing Intelligence Pipeline

A production-minded analytical pipeline that isolates the true causal effect of price on purchase behavior — separating genuine demand response from confounding noise like brand loyalty and competitor pricing — to support data-driven pricing decisions.

> [!NOTE]
> **Screenshot placeholder:** add a screenshot of the Streamlit scenario simulator here, e.g. `![Scenario Simulator Dashboard](docs/images/dashboard.png)`

## Overview & Impact

- **Causal, not just correlational, insight:** Uses Double Machine Learning (DML) with a Partially Linear Regression (PLR) specification to estimate the unbiased marginal effect of price on purchase probability, controlling for high-dimensional confounders.
- **Deconfounding at scale:** K-fold cross-fitting with gradient-boosted nuisance models strips out the influence of variables like customer loyalty and competitor pricing that would otherwise bias a naive regression.
- **Decision-ready output:** Estimates feed a live scenario simulator so stakeholders can test hypothetical price changes and see projected impact on purchase probability and churn risk in real time.
- **Built-in model scrutiny:** Includes an omitted-variable-bias sensitivity analysis to quantify how robust the causal estimate is to unobserved confounding — not just a point estimate taken at face value.

## Tech Stack

`Python 3.12`, `DoubleML`, `LightGBM`, `pandas`, `scikit-learn`, `Streamlit`, `python-dotenv`, `uv`, `Ruff`, `MyPy`, `Pytest`

## Engineering Rigor

- **Deterministic environments:** Dependency resolution and virtual environments are fully locked and reproducible via `uv` and `uv.lock` — no ambient `pip`/`virtualenv` drift between machines.
- **Strict static analysis:** Aggressive `Ruff` linting (bugbear, security, import hygiene) and `MyPy --strict` type checking enforced across the `src/` layout, backed by a `py.typed` marker for downstream type consumers.
- **Isolated automated testing:** A `Pytest` suite with fixture-based isolation (`tmp_path`) covers core services, orchestrated via a single `make test` / `make all` entry point suitable for CI.

## Quick Start

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and sync the locked environment
git clone <repo_url> && cd causal_inference
uv sync

# 3. Run the pipeline, then launch the dashboard
uv run --env-file .env python src/causal_inference/main.py
uv run streamlit run src/causal_inference/api/app.py
```

## Project Architecture

**Ingestion → Causal Modeling → Artifact Persistence → UI**

```
src/causal_inference/
├── services/    # Data ingestion & causal-role partitioning (Y / D / X)
├── core/        # DML/PLR estimation engine + sensitivity analysis
├── services/    # Artifact (metrics) serialization to JSON
├── api/         # Streamlit scenario-simulator dashboard
├── config.py    # Environment-driven configuration
└── main.py      # Pipeline orchestrator
```

Raw observational data is ingested and split into causal roles, passed through the DML engine for orthogonal effect estimation and robustness checks, and the resulting metrics are persisted as an artifact that the Streamlit UI reads to power interactive scenario analysis.

## Trade-offs & Roadmap

- **Linear probability approximation:** The binary purchase outcome is currently modeled via a continuous PLR (effectively an additive LPM), requiring manual `[0, 1]` clipping in the UI. **Planned:** migrate to `DoubleMLIRM` or a logistic PLR for natively bounded outputs.
- **Fixed nuisance-model hyperparameters:** `LGBMRegressor` settings are currently static rather than tuned. **Planned:** introduce cross-validated hyperparameter search to reduce overfitting risk on small samples.
- **Sensitivity bounds are illustrative:** Omitted-variable-bias bounds are hardcoded at 5%. **Planned:** benchmark bounds dynamically against the explanatory power of the strongest observed covariate (e.g., `LoyalCH`), and evaluate incorporating additional fixed effects (e.g., store/week) to reduce residual confounding risk.