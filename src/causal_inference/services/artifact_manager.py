import json
from pathlib import Path


def save_metrics(
    marginal_effect: float, p_value: float, baseline_prob: float, filepath: str
) -> None:
    """
    Serializes pipeline telemetry and causal metrics to a persistent JSON artifact.
    """
    out_path = Path(filepath)

    # Enforce directory existence prior to file generation
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "marginal_effect": marginal_effect,
        "p_value": p_value,
        "baseline_prob": baseline_prob,
    }

    # Utilizing Path.write_text to comply with Ruff PTH123 rule
    out_path.write_text(json.dumps(payload, indent=4), encoding="utf-8")


def load_metrics(filepath: str) -> dict[str, float]:
    """
    Deserializes causal inference metrics from the disk artifact.
    """
    in_path = Path(filepath)

    if not in_path.exists():
        raise FileNotFoundError(f"Artifact not found at {filepath}. Run the pipeline first.")

    data = json.loads(in_path.read_text(encoding="utf-8"))

    # Explicit type return to satisfy strict MyPy evaluation
    return {
        "marginal_effect": float(data["marginal_effect"]),
        "p_value": float(data["p_value"]),
        "baseline_prob": float(data["baseline_prob"]),
    }
