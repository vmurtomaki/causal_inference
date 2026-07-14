import streamlit as st

# TODO: Hard coded constants. Modify so that values change when dml_engine change. Some solution to this.
# Constant derived from causal pipeline execution
ELASTICITY_THETA = -0.4699
BASELINE_PROBABILITY = 0.60  # Example baseline for the CH product


def run_dashboard() -> None:
    st.set_page_config(page_title="Causal Pricing Simulator", layout="wide")

    st.title("📈 Causal Pricing AI: Scenario Simulator")
    st.markdown(f"""
    **Model Status:** Production-Ready  
    **Estimated Price Elasticity ($\theta_0$):** `{ELASTICITY_THETA}`  
    *Interpretation: A $1.00 increase in price changes purchase probability by ~46.99 percentage points.*
    """)

    st.divider()

    # Sidebar for Scenario Inputs
    st.sidebar.header("Scenario Configuration")
    price_change = st.sidebar.slider(
        "Hypothetical Price Increase ($)", min_value=-1.0, max_value=2.0, value=0.5, step=0.1
    )

    # Calculation logic
    # Linear approximation for probability change: ΔP ≈ θ * ΔPrice
    prob_impact = ELASTICITY_THETA * price_change
    new_probability = max(0.0, min(1.0, BASELINE_PROBABILITY + prob_impact))

    # Main UI Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Impact Visualization")
        st.metric(label="Original Probability", value=f"{BASELINE_PROBABILITY * 100:.1f}%")
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
