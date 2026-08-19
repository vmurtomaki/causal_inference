from pathlib import Path

import pandas as pd


def fetch_observational_data(file_path: str) -> pd.DataFrame:
    """
    Retrieves the raw observational dataset.
    Assuming the file is placed locally based on the provided configuration path.
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(
            f"Dataset not found at {file_path}. Please ensure oj_data.csv is present."
        )

    return pd.read_csv(file_path)


def partition_causal_roles(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str, list[str]]:
    """
    Translates the ISLR Orange Juice dataframe into structured causal roles.
    Isolates the target outcome, treatment variable, and high-dimensional confounders.
    """
    processed_df = df.copy()
    processed_df["Purchase_CH"] = (processed_df["Purchase"] == "CH").astype(int)

    y_col = "Purchase_CH"
    d_col = "SalePriceCH"

    # PriceCH and SpecialCH deliberately EXCLUDED: SalePriceCH = PriceCH - (promo discount
    # implied by SpecialCH), so conditioning on them induces perfect collinearity with the
    # treatment and destroys the exogenous variance the orthogonal score requires.
    # LoyalCH is an exponentially smoothed loyalty index updated from *past* purchases
    # only (L_t = λ·Purchase_{t-1} + (1-λ)·L_{t-1}), per the standard construction in
    # Guadagni & Little (1983); it does not incorporate the current-row purchase, so
    # conditioning on it here is not post-treatment.
    x_cols = [
        "LoyalCH",
        "SalePriceMM",
        "PriceMM",
        "SpecialMM",
    ]
    return processed_df, y_col, d_col, x_cols
