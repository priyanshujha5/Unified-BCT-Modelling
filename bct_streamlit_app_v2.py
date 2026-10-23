"""
===============================================================================
BCT PREDICTION & Packaging GSM OPTIMIZATION DASHBOARD (STREAMLIT V2)
===============================================================================
Features:
  - Dual-Engine Toggle: Empirical Power-Law vs First-Principles McKee Model
  - Interactive 5-Ply Board Specification Sliders
  - Sealing Method Selector (Taped vs Glued @ 15mm / 7mm Deflection)
  - Target BCT Inverter & Financial Savings Simulator
  - Preset Customer Combination Comparison
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bct_unified_model import UnifiedBCTModelEngine, SEALING_FACTORS, BENCHMARKS

# Streamlit Page Config
st.set_page_config(
    page_title="📦 BCT Prediction & GSM Optimizer Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Unified Engine
@st.cache_resource
def get_engine():
    return UnifiedBCTModelEngine()

engine = get_engine()

# Sidebar: Global Settings & Engine Toggle
st.sidebar.title("⚙️ Model Settings")
selected_engine = st.sidebar.radio(
    "Select Prediction Engine:",
    ["Empirical Power-Law Model (Fitted Data)", "First-Principles McKee Model (Zero-Fit Physics)"]
)

sealing_method = st.sidebar.selectbox(
    "Box Sealing Method:",
    list(SEALING_FACTORS.keys()),
    index=1
)
phi = SEALING_FACTORS[sealing_method]

st.sidebar.markdown("---")
st.sidebar.info(
    "**Note:** Code and proprietary mathematical formulas are executed securely on the backend engine without exposing source code to end users."
)

# Header
st.title("📦 Shipping Box Compression (BCT) & GSM Optimizer")
st.markdown(
    "Predict Box Compression Test (BCT) strength, evaluate glued vs. taped sealing uplift, and calculate paper weight and financial savings."
)

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🧮 Interactive BCT Calculator", 
    "🌱 Target GSM & Financial Savings", 
    "📋 Preset Board Structures", 
    "📊 Model Validation Benchmarks"
])

# -----------------------------------------------------------------------------
# TAB 1: INTERACTIVE CALCULATOR
# -----------------------------------------------------------------------------
with tab1:
    st.header("1. Custom 5-Ply Board Specifications")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Board Layer GSM Inputs")
        outer_liner = st.slider("Outer Liner (g/m²)", 150, 350, 230, step=10)
        medium_1 = st.slider("Flute Medium 1 (g/m²)", 80, 200, 140, step=5)
        center_liner = st.slider("Center Liner (g/m²)", 100, 300, 140, step=10)
        medium_2 = st.slider("Flute Medium 2 (g/m²)", 80, 200, 140, step=5)
        inner_liner = st.slider("Inner Liner (g/m²)", 150, 350, 230, step=10)
        
        total_gsm = outer_liner + medium_1 + center_liner + medium_2 + inner_liner
        st.metric("Total Board Grammage", f"{total_gsm} gsm")

    with col2:
        st.subheader("Box Dimensions & Paper Quality (For McKee Model)")
        length_mm = st.number_input("Box Length (mm)", value=470, step=10)
        width_mm = st.number_input("Box Width (mm)", value=280, step=10)
        height_mm = st.number_input("Box Height (mm)", value=238, step=10)
        
        liner_bf = st.slider("Liner Burst Factor (BF)", 18, 35, 25)
        medium_bf = st.slider("Medium Burst Factor (BF)", 14, 25, 20)

        st.markdown("---")
        st.subheader("2. Predicted Box Performance")
        
        if "Empirical" in selected_engine:
            pred_bct = engine.predict_empirical(total_gsm, phi=phi)
            st.metric("Predicted BCT Strength", f"{pred_bct:.1f} Kgf", delta=f"Sealing Uplift: {phi}x")
            st.caption(f"Calculated via Empirical Power-Law Formula: BCT = {phi:.3f} × 0.0305 × (GSM)^1.424")
        else:
            fp_res = engine.predict_first_principles(
                length_mm=length_mm, width_mm=width_mm, height_mm=height_mm,
                liners_gsm=[outer_liner, center_liner, inner_liner],
                liners_bf=[liner_bf, medium_bf, liner_bf],
                mediums_gsm=[medium_1, medium_2],
                mediums_bf=[medium_bf, medium_bf],
                phi=phi
            )
            st.metric("Predicted BCT Strength", f"{fp_res['predicted_bct_kgf']:.1f} Kgf", delta=f"Board ECT: {fp_res['ect_kn_m']} kN/m")
            st.caption(f"Calculated via Zero-Fit McKee Mechanics Formula: BCT = 5.876 × ECT × √(Perimeter × Caliper)")

# -----------------------------------------------------------------------------
# TAB 2: TARGET GSM & SAVINGS
# -----------------------------------------------------------------------------
with tab2:
    st.header("🌱 Target BCT Inversion & Financial Savings Simulator")
    
    sc1, sc2 = st.columns(2)
    with sc1:
        target_bct = st.number_input("Target BCT Requirement (Kgf)", value=480.0, step=10.0)
        baseline_gsm_input = st.number_input("Baseline Taped Board GSM (g/m²)", value=880.0, step=10.0)
        box_blank_sqm = st.number_input("Box Surface Blank Area (m²)", value=0.52, step=0.01)
    
    with sc2:
        annual_volume = st.number_input("Annual Box Shipment Volume (Units)", value=1000000, step=100000)
        paper_cost_usd = st.number_input("Paper Cost per Metric Ton (USD)", value=650.0, step=25.0)

    st.markdown("---")
    
    savings = engine.calculate_paper_financial_savings(
        baseline_gsm=baseline_gsm_input,
        target_bct_kgf=target_bct,
        phi=phi,
        annual_box_volume=int(annual_volume),
        box_blank_area_sqm=box_blank_sqm,
        paper_cost_per_ton_usd=paper_cost_usd
    )
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Required Board GSM", f"{savings['optimized_gsm']:.1f} gsm", delta=f"-{savings['gsm_saved']:.1f} gsm")
    m2.metric("Paper Weight Savings", f"{savings['savings_pct']:.1f} %")
    m3.metric("Annual Saved Paper", f"{savings['annual_saved_tonnes']:.1f} Tonnes")
    m4.metric("Annual Cost Savings", f"${savings['annual_savings_usd']:,.2f}")

# -----------------------------------------------------------------------------
# TAB 3: PRESET STRUCTURES
# -----------------------------------------------------------------------------
with tab3:
    st.header("📋 Preset Customer Combinations")
    st.markdown("Comparison of standard paper grade structures for target 480 Kgf BCT:")
    
    preset_data = [
        {"ID": "A-Baseline", "Target": "775gsm", "Liners": "230/230", "Mediums": "105/105/105", "Total GSM": 775, "Taped BCT": 396.7, "Glued 15mm BCT": 479.6, "Glued 7mm BCT": 560.5},
        {"ID": "B-Balanced", "Target": "775gsm", "Liners": "215/215", "Mediums": "115/115/115", "Total GSM": 775, "Taped BCT": 396.7, "Glued 15mm BCT": 479.6, "Glued 7mm BCT": 560.5},
        {"ID": "C-HighLiner", "Target": "775gsm", "Liners": "250/250", "Mediums": "92/91/92", "Total GSM": 775, "Taped BCT": 396.7, "Glued 15mm BCT": 479.6, "Glued 7mm BCT": 560.5},
        {"ID": "D-HardMediumCut", "Target": "698gsm", "Liners": "230/230", "Mediums": "79/79/79", "Total GSM": 698, "Taped BCT": 341.8, "Glued 15mm BCT": 413.2, "Glued 7mm BCT": 482.9},
        {"ID": "K1-AllVirginKraft", "Target": "Commercial", "Liners": "230/230", "Mediums": "112/112/112", "Total GSM": 796, "Taped BCT": 412.1, "Glued 15mm BCT": 498.2, "Glued 7mm BCT": 582.2},
        {"ID": "H1-HybridOuterKraft", "Target": "Commercial", "Liners": "230/230", "Mediums": "112/112/112", "Total GSM": 796, "Taped BCT": 412.1, "Glued 15mm BCT": 498.2, "Glued 7mm BCT": 582.2}
    ]
    st.dataframe(pd.DataFrame(preset_data), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: BENCHMARK VALIDATION
# -----------------------------------------------------------------------------
with tab4:
    st.header("📊 Model Validation Against Henkel Industrial Data")
    df_val = engine.run_benchmark_validation()
    st.table(df_val)
