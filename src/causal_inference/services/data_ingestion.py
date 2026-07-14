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
    # Create a clean working copy to avoid SettingWithCopy warnings
    processed_df = df.copy()

    # Transform categorical outcome into a binary numerical indicator (1 = CH, 0 = MM)
    processed_df["Purchase_CH"] = (processed_df["Purchase"] == "CH").astype(int)

    # Define the Causal Graph nodes
    y_col = "Purchase_CH"  # Outcome (Y): Probability of purchasing Citrus Hill
    d_col = "SalePriceCH"  # Treatment (D): The actual price paid for Citrus Hill

    # Define the Confounding Adjustment Set (X)
    # We must control for loyalty, baseline prices, competitor final prices, and promotions.
    x_cols = [
        "LoyalCH",  # Customer's historical loyalty to CH
        "PriceCH",  # Baseline list price of CH
        "SpecialCH",  # Indicator of a CH promotion
        "SalePriceMM",  # Actual sale price of competitor (Minute Maid)
        "PriceMM",  # Baseline list price of MM
        "SpecialMM",  # Indicator of a MM promotion
    ]

    return processed_df, y_col, d_col, x_cols
