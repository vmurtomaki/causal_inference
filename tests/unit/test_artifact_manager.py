from pathlib import Path

import pytest

from causal_inference.services.artifact_manager import load_metrics, save_metrics


def test_save_and_load_metrics(tmp_path: Path) -> None:
    """
    Validates the JSON serialization and deserialization lifecycle.
    Utilizes tmp_path to ensure strict environment isolation.
    """
    # 1. Setup mock environment
    target_file = tmp_path / "mock_dir" / "metrics.json"

    mock_marginal = -0.450
    mock_p_value = 0.001
    mock_baseline = 0.650

    # 2. Execute save function (Should automatically resolve missing parent directories)
    save_metrics(
        marginal_effect=mock_marginal,
        p_value=mock_p_value,
        baseline_prob=mock_baseline,
        filepath=str(target_file),
    )

    # 3. Assert file generation
    assert target_file.exists()

    # 4. Execute load function
    loaded_data = load_metrics(str(target_file))

    # 5. Assert data parity
    assert loaded_data["marginal_effect"] == mock_marginal
    assert loaded_data["p_value"] == mock_p_value
    assert loaded_data["baseline_prob"] == mock_baseline


def test_load_metrics_file_not_found(tmp_path: Path) -> None:
    """
    Validates that attempting to load a non-existent artifact triggers the expected exception.
    """
    missing_file = tmp_path / "does_not_exist.json"

    with pytest.raises(FileNotFoundError):
        load_metrics(str(missing_file))
