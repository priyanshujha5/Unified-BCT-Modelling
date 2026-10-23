"""
===============================================================================
BCT PREDICTION & ADHESIVE GSM OPTIMIZATION WEB APPLICATION
===============================================================================
Streamlit Web Interface for Packaging Engineers, Procurement, and Sales Teams.
Runs the mathematical model behind a clean UI without revealing python code.
===============================================================================
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set Page Config
st.set_page_config(
    page_title="BCT Prediction & GSM Optimization Engine",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 15px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .savings-card {
        background-color: #ECFDF5;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #10B981;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MODEL ENGINE CORE (Proprietary Math Logic)
# =============================================================================
class BCTModelEngine:
    """
    Log-Linearized Power-Law BCT Prediction & Sealing Efficiency Engine
    Fitted Model: BCT (Kgf) = 0.030497 * (GSM)^1.423962 * phi
    """
    def __init__(self):
        self.k = 0.030497183
        self.n = 1.423962
        self.ln_k = -3.490119
        self.r2 = 0.996079
        self.rmse = 8.26
        self.mape = 1.26

        self.phi_map = {
            "Taped Standard Closure (Baseline)": 1.000,
            "Stelda Glued Closure @ 15mm Deflection (Conservative)": 1.209,
            "Stelda Glued Closure @ 7mm Deflection (Aggressive)": 1.413
        }

    def predict_bct(self, total_gsm: float, phi: float = 1.0) -> float:
        return self.k * (total_gsm ** self.n) * phi

    def invert_gsm(self, target_bct_kgf: float, phi: float = 1.0) -> float:
        base_bct = target_bct_kgf / phi
        return (base_bct / self.k) ** (1.0 / self.n)

engine = BCTModelEngine()

# =============================================================================
# SIDEBAR CONTROLS
# =============================================================================
st.sidebar.title("⚙️ Model Controls")

# Sealing Tech Selection
st.sidebar.subheader("1. Sealing Closure Technology")
closure_option = st.sidebar.selectbox(
    "Select Closure Method:",
    list(engine.phi_map.keys()),
    index=1
)
phi_val = engine.phi_map[closure_option]

st.sidebar.markdown("---")

# Navigation Mode
st.sidebar.subheader("2. Analysis Mode")
app_mode = st.sidebar.radio(
    "Choose Workflow:",
    [
        "🛠️ Custom 5-Ply Board Spec Builder",
        "🎯 Target BCT & Paper Savings Inverter",
        "📊 Customer Proposal Presets (A-E & K/R/H)",
        "🔬 Benchmark Validation & Diagnostics"
    ]
)

# =============================================================================
# APP HEADER
# =============================================================================
st.markdown('<div class="main-header">📦 BCT Prediction & Adhesive GSM Optimization Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Validated Structural Compression Science & Sealing Efficiency for 5-Ply Corrugated Shipper Cartons</div>', unsafe_allow_html=True)

# =============================================================================
# WORKFLOW 1: CUSTOM 5-PLY BOARD SPEC BUILDER
# =============================================================================
if app_mode == "🛠️ Custom 5-Ply Board Spec Builder":
    st.header("Custom 5-Ply Corrugated Board Spec Builder")
    st.markdown("Configure the individual GSM weight for all five board layers to calculate structural Box Compression Strength.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Board Layer Inputs (GSM)")
        outer_liner = st.number_input("Outer Liner (g/m²)", min_value=100, max_value=400, value=230, step=10)
        flute_1 = st.number_input("Flute Medium 1 (g/m²)", min_value=70, max_value=250, value=140, step=5)
        center_liner = st.number_input("Center Liner (g/m²)", min_value=80, max_value=300, value=140, step=10)
        flute_2 = st.number_input("Flute Medium 2 (g/m²)", min_value=70, max_value=250, value=140, step=5)
        inner_liner = st.number_input("Inner Liner (g/m²)", min_value=100, max_value=400, value=230, step=10)

        total_board_gsm = outer_liner + flute_1 + center_liner + flute_2 + inner_liner

    with col2:
        st.subheader("Predicted Structural Performance")

        predicted_bct = engine.predict_bct(total_board_gsm, phi=phi_val)
        baseline_taped_bct = engine.predict_bct(total_board_gsm, phi=1.0)
        
        equivalent_taped_gsm = engine.invert_gsm(predicted_bct, phi=1.0)
        gsm_saved = equivalent_taped_gsm - total_board_gsm
        pct_saved = (gsm_saved / equivalent_taped_gsm) * 100 if equivalent_taped_gsm > 0 else 0

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Total Board Weight", f"{total_board_gsm} gsm")
            st.metric("Predicted BCT Strength", f"{predicted_bct:.1f} Kgf", delta=f"{((phi_val-1)*100):.1f}% Sealing Uplift" if phi_val > 1 else None)
        with m2:
            st.metric("Baseline Taped BCT", f"{baseline_taped_bct:.1f} Kgf")
            st.metric("Equivalent Taped Board GSM", f"{equivalent_taped_gsm:.1f} gsm")

        if phi_val > 1.0:
            st.success(f"🌱 **Paper Optimization Benefit**: Glued sealing delivers **{predicted_bct:.1f} Kgf** BCT with **{total_board_gsm} gsm** board. Achieving this strength with tape requires **{equivalent_taped_gsm:.1f} gsm** (saving **{pct_saved:.1f}% paper weight**).")

    # Interactive Graph
    st.subheader("BCT vs. Total Board GSM Curve")
    gsm_axis = np.linspace(600, 1400, 100)
    bct_taped_curve = engine.predict_bct(gsm_axis, phi=1.0)
    bct_selected_curve = engine.predict_bct(gsm_axis, phi=phi_val)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(gsm_axis, bct_taped_curve, 'k--', label="Taped Standard Baseline (phi = 1.0)")
    if phi_val > 1.0:
        ax.plot(gsm_axis, bct_selected_curve, 'g-', label=f"Selected Sealing Method (phi = {phi_val:.3f})")
    
    ax.scatter([total_board_gsm], [predicted_bct], color='red', s=120, zorder=5, label=f"Configured Spec ({total_board_gsm} gsm, {predicted_bct:.1f} Kgf)")
    ax.set_xlabel("Total Board GSM (g/m²)")
    ax.set_ylabel("Box Compression Strength BCT (Kgf)")
    ax.set_title("Power-Law BCT Curve & Spec Operating Point")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    st.pyplot(fig)

# =============================================================================
# WORKFLOW 2: TARGET BCT & PAPER SAVINGS INVERTER
# =============================================================================
elif app_mode == "🎯 Target BCT & Paper Savings Inverter":
    st.header("Target BCT Inverse GSM Calculator & Savings Estimator")
    st.markdown("Enter your customer's target Box Compression requirement (Kgf) to calculate the required board GSM for Taped vs. Glued shippers.")

    target_bct = st.slider("Target Box Compression Strength BCT (Kgf)", min_value=300, max_value=1200, value=480, step=10)

    gsm_taped = engine.invert_gsm(target_bct, phi=1.0)
    gsm_glued_15 = engine.invert_gsm(target_bct, phi=1.209)
    gsm_glued_7 = engine.invert_gsm(target_bct, phi=1.413)

    sav_15_pct = ((gsm_taped - gsm_glued_15) / gsm_taped) * 100
    sav_7_pct = ((gsm_taped - gsm_glued_7) / gsm_taped) * 100

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(f"### Taped Baseline\n**Required Board:** {gsm_taped:.1f} GSM\n\n**Paper Savings:** 0.0%")
    with c2:
        st.success(f"### Glued @ 15mm Deflection\n**Required Board:** {gsm_glued_15:.1f} GSM\n\n**Paper Savings:** {sav_15_pct:.2f}%")
    with c3:
        st.success(f"### Glued @ 7mm Deflection\n**Required Board:** {gsm_glued_7:.1f} GSM\n\n**Paper Savings:** {sav_7_pct:.2f}%")

    st.markdown("---")
    st.subheader("💰 Commercial Annual Savings Estimator")
    col_a, col_b = st.columns(2)
    with col_a:
        annual_cartons = st.number_input("Annual Shipper Box Volume (Units)", min_value=10000, max_value=50000000, value=1000000, step=100000)
        box_area_sqm = st.number_input("Carton Blank Surface Area (m²)", min_value=0.1, max_value=5.0, value=0.85, step=0.05)
    with col_b:
        paper_cost_per_ton = st.number_input("Average Paper Cost (USD $ / Tonne)", min_value=300, max_value=2000, value=750, step=25)

    # Calculation
    annual_tonnage_taped = (annual_cartons * box_area_sqm * gsm_taped) / 1e6
    annual_tonnage_glued_15 = (annual_cartons * box_area_sqm * gsm_glued_15) / 1e6

    tonnage_saved = annual_tonnage_taped - annual_tonnage_glued_15
    cost_saved_usd = tonnage_saved * paper_cost_per_ton

    st.markdown(f"""
    <div class="savings-card">
        <h3>🎉 Estimated Annual Financial & Environmental Impact</h3>
        <p style="font-size: 18px;">
        • <b>Paper Saved:</b> {tonnage_saved:.2f} Metric Tonnes / Year<br>
        • <b>Cost Saved:</b> ${cost_saved_usd:,.2f} USD / Year<br>
        • <b>CO₂ Reduction:</b> ~{tonnage_saved * 1.3:.1f} Tonnes CO₂e Saved
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# WORKFLOW 3: CUSTOMER PROPOSAL PRESETS
# =============================================================================
elif app_mode == "📊 Customer Proposal Presets (A-E & K/R/H)":
    st.header("Preset Customer Proposals & Paper Grade Combinations")
    st.markdown("Evaluate pre-configured 5-ply board combinations across Virgin Kraft, Recycled Testliner, and Hybrid specs.")

    presets = [
        {"ID": "Henkel Baseline", "Type": "Original Spec", "Liners": "300/300", "Mediums": "180/180/180", "Total GSM": 1260},
        {"ID": "Henkel 2023", "Type": "First Phase Reduction", "Liners": "230/230", "Mediums": "180/180/180", "Total GSM": 1050},
        {"ID": "Noa Kalang Target", "Type": "Tested Spec", "Liners": "230/230", "Mediums": "140/140/140", "Total GSM": 880},
        {"ID": "A-Baseline", "Type": "775gsm Target", "Liners": "230/230", "Mediums": "105/105/105", "Total GSM": 775},
        {"ID": "B-Balanced", "Type": "775gsm Target", "Liners": "215/215", "Mediums": "115/115/115", "Total GSM": 775},
        {"ID": "C-HighLiner", "Type": "775gsm Target", "Liners": "250/250", "Mediums": "92/91/92", "Total GSM": 775},
        {"ID": "D-HardMediumCut", "Type": "698gsm Target", "Liners": "230/230", "Mediums": "79/79/79", "Total GSM": 698},
        {"ID": "E-FloorLiners", "Type": "698gsm Target", "Liners": "200/200", "Mediums": "99/99/99", "Total GSM": 698},
        {"ID": "K1-AllVirginKraft", "Type": "Virgin Export Grade", "Liners": "230/230", "Mediums": "112/112/112", "Total GSM": 796},
        {"ID": "R1-AllRecycled", "Type": "Recycled Budget Grade", "Liners": "200/200", "Mediums": "112/112/112", "Total GSM": 736},
        {"ID": "H1-HybridOuterKraft", "Type": "Hybrid Print Grade", "Liners": "230/200", "Mediums": "112/112/112", "Total GSM": 766}
    ]

    df_presets = pd.DataFrame(presets)
    df_presets["Predicted BCT Taped (Kgf)"] = df_presets["Total GSM"].apply(lambda g: round(engine.predict_bct(g, phi=1.0), 1))
    df_presets["Predicted BCT Glued @ 15mm (Kgf)"] = df_presets["Total GSM"].apply(lambda g: round(engine.predict_bct(g, phi=1.209), 1))
    df_presets["Predicted BCT Glued @ 7mm (Kgf)"] = df_presets["Total GSM"].apply(lambda g: round(engine.predict_bct(g, phi=1.413), 1))

    st.dataframe(df_presets, use_container_width=True)

    # Bar chart
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(df_presets))
    width = 0.35
    ax.bar(x - width/2, df_presets["Predicted BCT Taped (Kgf)"], width, label='Taped (phi=1.0)', color='#94A3B8')
    ax.bar(x + width/2, df_presets["Predicted BCT Glued @ 15mm (Kgf)"], width, label='Glued @ 15mm (phi=1.22)', color='#10B981')
    ax.axhline(480, color='red', linestyle='--', label='Noa Kalang Target BCT (480 Kgf)')
    ax.set_xticks(x)
    ax.set_xticklabels(df_presets["ID"], rotation=45, ha='right')
    ax.set_ylabel("BCT Strength (Kgf)")
    ax.set_title("Predicted Compression Strength Across Preset Combinations")
    ax.legend()
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    st.pyplot(fig)

# =============================================================================
# WORKFLOW 4: BENCHMARK VALIDATION & DIAGNOSTICS
# =============================================================================
elif app_mode == "🔬 Benchmark Validation & Diagnostics":
    st.header("Mathematical Model Diagnostics & Research Validation")
    st.markdown("""
    **Power-Law Formulation:**
    $$\\text{BCT (Kgf)} = 0.0305 \\times (\\text{GSM})^{1.424} \\times \\phi$$
    
    Derived via log-linear least squares regression: $\\ln(\\text{BCT}) = \\ln(k) + n \\cdot \\ln(\\text{GSM})$
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Coefficient of Determination (R²)", f"{engine.r2:.4f}")
    col2.metric("Root Mean Squared Error (RMSE)", f"{engine.rmse:.2f} Kgf")
    col3.metric("Mean Absolute Pct Error (MAPE)", f"{engine.mape:.2f}%")

    st.subheader("Validation Against Experimental Henkel Test Data")
    benchmarks = [
        {"IDH / Spec": "1714527 / Baseline", "Total GSM": 1260, "Measured BCT (Kgf)": 800.0, "Predicted BCT (Kgf)": round(engine.predict_bct(1260, 1.0), 2), "Error (%)": "-0.92%"},
        {"IDH / Spec": "2879212 / 2023 Reduction", "Total GSM": 1050, "Measured BCT (Kgf)": 600.0, "Predicted BCT (Kgf)": round(engine.predict_bct(1050, 1.0), 2), "Error (%)": "+1.90%"},
        {"IDH / Spec": "3147790 / Noa Kalang Spec", "Total GSM": 880, "Measured BCT (Kgf)": 480.0, "Predicted BCT (Kgf)": round(engine.predict_bct(880, 1.0), 2), "Error (%)": "-0.95%"}
    ]
    st.table(pd.DataFrame(benchmarks))

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("© BCT Prediction & Adhesive GSM Optimization System | Powered by Streamlit & Python Science")
