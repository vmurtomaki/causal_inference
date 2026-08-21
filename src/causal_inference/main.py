from causal_inference.config import config
from causal_inference.core.dml_engine import estimate_price_elasticity, evaluate_robustness
from causal_inference.services.artifact_manager import save_metrics
from causal_inference.services.data_ingestion import (
    fetch_observational_data,
    partition_causal_roles,
)


def main() -> None:
    """
    Primary orchestrator for the causal inference lifecycle.
    """
    print("Initiating deterministic causal inference pipeline...")

    # Extract and assign causal roles (Y, D, X)
    raw_df = fetch_observational_data(config.data_path)
    df, y_col, d_col, x_cols = partition_causal_roles(raw_df)

    # Dynamically calculate the baseline probability (mean of binary outcome)
    baseline_prob = float(df[y_col].mean())

    print(f"Data successfully parsed. Confounders detected: {len(x_cols)}")
    print(f"Baseline Purchase Probability: {baseline_prob:.4f}")
    print(
        f"Executing Double Machine Learning (PLR) cross-fitting sequence with "
        f"{config.n_folds} folds and {config.n_rep} repetitions..."
    )
    # Execute orthogonal estimation
    dml_model = estimate_price_elasticity(
        df=df,
        y_col=y_col,
        d_col=d_col,
        x_cols=x_cols,
        n_folds=config.n_folds,
        n_rep=config.n_rep,
        random_seed=config.random_seed,
    )

    # Synthesize causal findings
    marginal_effect = float(dml_model.coef[0])
    p_value = float(dml_model.pval[0])

    print("-" * 50)
    print("CAUSAL IDENTIFICATION RESULTS")
    print("-" * 50)
    print(f"Treatment Variable (D): {d_col}")
    print(f"Outcome Variable (Y)  : {y_col}")
    print(f"\nMarginal Effect (θ₀)  : {marginal_effect:.4f}")
    p_val_display = "< 0.001" if p_value < 0.001 else f"{p_value:.4f}"
    print(f"P-Value               : {p_val_display}")

    print("\nInterpretation:")
    print(
        f"A $0.10 increase in {d_col} changes the probability of purchasing "
        f"Citrus Hill by approximately {marginal_effect * 10:.2f} percentage points, "
        "holding brand loyalty and competitor pricing constant. Read as a local slope: "
        "the treatment spans $1.39-$2.09, so dollar-scale moves are out of support."
    )

    print("\nModel Statistical Summary:")
    print(dml_model.summary)

    # Execute Phase 9 Robustness Check
    evaluate_robustness(dml_model=dml_model, cf_y=0.05, cf_d=0.05)

    # Persist metrics for frontend consumption
    print(f"\nSerializing artifacts to {config.artifact_path}...")
    save_metrics(
        marginal_effect=marginal_effect,
        p_value=p_value,
        baseline_prob=baseline_prob,
        filepath=config.artifact_path,
    )
    print("Pipeline execution complete.")


if __name__ == "__main__":
    main()
