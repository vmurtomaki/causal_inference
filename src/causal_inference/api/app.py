import streamlit as st
from causal_inference.config import config
from causal_inference.services.data_ingestion import fetch_observational_data, partition_causal_roles

def run_dashboard() -> None:
    st.set_page_config(page_title="Price Elasticity Simulator", layout="wide")
    st.title("Causal Pricing AI: Scenario Simulator")
    st.markdown("Interact with the Double Machine Learning causal estimator.")
    
    # Placeholder for the data state and causal parameter
    st.info("System Ready. Awaiting integration of causal parameters...")

if __name__ == "__main__":
    run_dashboard()