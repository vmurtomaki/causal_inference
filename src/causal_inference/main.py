from causal_inference.config import config
from causal_inference.core.dml_engine import estimate_price_elasticity
from causal_inference.services.data_ingestion import (
    fetch_observational_data,
    partition_causal_roles,
)


def main() -> None:
    """
    Primary orchestrator for the causal inference lifecycle.
    """
    print("Initiating deterministic causal inference pipeline...")

    # Extract and format the unconfounded matrix
    raw_df = fetch_observational_data(config.data_path)
    df, y_col, d_col, x_cols = partition_causal_roles(raw_df)

    print(f"Data successfully parsed. Confounders detected: {len(x_cols)}")
    print("Executing Double Machine Learning (PLR) cross-fitting sequence...")

    # Execute orthogonal estimation (Logic remains unchanged)
    dml_model = estimate_price_elasticity(
        df=df,
        y_col=y_col,
        d_col=d_col,
        x_cols=x_cols,
        n_folds=config.n_folds,
        random_seed=config.random_seed,
    )

    # Synthesize causal findings
    marginal_effect = dml_model.coef[0]
    p_value = dml_model.pval[0]

    print("-" * 50)
    print("CAUSAL IDENTIFICATION RESULTS")
    print("-" * 50)
    print(f"Treatment Variable (D): {d_col}")
    print(f"Outcome Variable (Y)  : {y_col}")
    print(f"\nMarginal Effect (θ₀)  : {marginal_effect:.4f}")
    print(f"P-Value               : {p_value:.4e}")

    print("\nInterpretation:")
    print(
        f"A $1.00 increase in {d_col} changes the probability of purchasing "
        f"Citrus Hill by approximately {marginal_effect * 100:.2f} percentage points, "
        "holding brand loyalty and competitor pricing constant."
    )

    print("\nModel Statistical Summary:")
    print(dml_model.summary)


if __name__ == "__main__":
    main()
