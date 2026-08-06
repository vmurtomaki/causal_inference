import pandas as pd

from causal_inference.services.data_ingestion import partition_causal_roles


def test_partition_causal_roles() -> None:
    """
    Validates that the data ingestion module correctly transforms the categorical
    outcome and separates the DAG roles (Y, D, X).
    """
    # 1. Setup mock data simulating the oj_data.csv schema
    mock_data = {
        "Purchase": ["CH", "MM", "CH"],
        "SalePriceCH": [1.75, 1.69, 1.99],
        "LoyalCH": [0.5, 0.4, 0.9],
        "PriceCH": [1.75, 1.69, 1.99],
        "SpecialCH": [0, 0, 1],
        "SalePriceMM": [1.99, 1.69, 1.59],
        "PriceMM": [1.99, 1.69, 1.99],
        "SpecialMM": [0, 0, 1],
    }
    df = pd.DataFrame(mock_data)

    # 2. Execute the function
    processed_df, y_col, d_col, x_cols = partition_causal_roles(df)
    assert y_col == "Purchase_CH"
    assert d_col == "SalePriceCH"
    assert len(x_cols) == 4  # PriceCH, SpecialCH deliberately excluded (see data_ingestion.py)
    assert "PriceCH" not in x_cols
    assert "SpecialCH" not in x_cols
    assert processed_df["Purchase_CH"].tolist() == [1, 0, 1]
