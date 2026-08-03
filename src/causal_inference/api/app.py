import streamlit as st

from causal_inference.config import config
from causal_inference.services.artifact_manager import load_metrics


@st.cache_data
def fetch_pipeline_artifacts() -> dict[str, float]:
    """
    Retrieves the serialized metrics from disk.
    Decorated with cache_data to prevent repetitive disk I/O on widget interaction.
    """
    try:
        return load_metrics(config.artifact_path)
    except FileNotFoundError:
        st.error(
            "⚠️ Artifact payload not found. "
            "Please execute the causal inference pipeline before launching the dashboard."
        )
        st.stop()


def run_dashboard() -> None:
    st.set_page_config(page_title="Causal Pricing Simulator", layout="wide")

    # Ingest dynamic metrics
    metrics = fetch_pipeline_artifacts()
    elasticity_theta = metrics["marginal_effect"]
    baseline_probability = metrics["baseline_prob"]

    st.title("📈 Causal Pricing AI: Scenario Simulator")
    st.markdown(
        "**Model Status:** Production-Ready\n\n"
        f"**Estimated Price Elasticity ($\\theta_0$):** `{elasticity_theta:.4f}`\n\n"
        f"*Interpretation: A $1.00 increase in price changes purchase probability by ~{elasticity_theta * 100:.2f} percentage points.*"
    )

    st.divider()

    # Sidebar for Scenario Inputs
    st.sidebar.header("Scenario Configuration")
    price_change = st.sidebar.slider(
        "Hypothetical Price Increase ($)", min_value=-1.0, max_value=2.0, value=0.5, step=0.1
    )

    # Calculation logic
    # Linear approximation for probability change: ΔP ≈ θ * ΔPrice
    prob_impact = elasticity_theta * price_change
    new_probability = max(0.0, min(1.0, baseline_probability + prob_impact))

    # Main UI Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Impact Visualization")
        st.metric(label="Original Probability", value=f"{baseline_probability * 100:.1f}%")
        st.metric(
            label="Projected Probability",
            value=f"{new_probability * 100:.1f}%",
            delta=f"{prob_impact * 100:.2f} pp",
        )

    with col2:
        st.subheader("Business Insight")
        if prob_impact < -0.20:
            st.error("⚠️ Significant risk of customer churn for Citrus Hill.")
        elif prob_impact > 0.05:
            st.success("✅ Price increase likely to improve margins without drastic volume loss.")
        else:
            st.warning("⚠️ Neutral impact; monitor competitive response.")


if __name__ == "__main__":
    run_dashboard()
