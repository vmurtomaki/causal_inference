import pandas as pd
from doubleml import DoubleMLData, DoubleMLPLR
from lightgbm import LGBMRegressor


def estimate_price_elasticity(
    df: pd.DataFrame,
    y_col: str,
    d_col: str,
    x_cols: list[str],
    n_folds: int,
    n_rep: int,
    random_seed: int,
) -> DoubleMLPLR:
    dml_data = DoubleMLData(df, y_col=y_col, d_cols=d_col, x_cols=x_cols)

    # n_estimators raised from 3 -> 300 (with shrinkage) so the nuisance learners can
    # actually approach the true conditional expectations rather than underfitting.
    ml_l = LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=random_seed)
    ml_m = LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=random_seed)

    dml_plr = DoubleMLPLR(
        obj_dml_data=dml_data,
        ml_l=ml_l,
        ml_m=ml_m,
        n_folds=n_folds,
        n_rep=n_rep,
        score="partialling out",
    )
    dml_plr.fit()
    return dml_plr


def evaluate_robustness(dml_model: DoubleMLPLR, cf_y: float = 0.05, cf_d: float = 0.05) -> None:
    """
    Executes Phase 9: Robustness and Sensitivity Analysis.
    Calculates bounds by simulating an unobserved confounder that explains a
    certain percentage of residual variance in both the outcome (cf_y) and treatment (cf_d).
    """
    # Execute the sensitivity analysis using Omitted Variable Bias (OVB) bounds
    dml_model.sensitivity_analysis(cf_y=cf_y, cf_d=cf_d, rho=1.0)

    print("-" * 50)
    print("SENSITIVITY ANALYSIS (OMITTED VARIABLE BIAS)")
    print("-" * 50)
    print(
        f"Hypothetical unobserved confounder explaining {cf_y * 100}% variance in Y and {cf_d * 100}% in D."
    )
    print(dml_model.sensitivity_summary)
