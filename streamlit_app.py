import os
os.environ['MPLBACKEND'] = 'Agg'

import textwrap
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import time
import random
from datetime import datetime

# Helper to render clean HTML without markdown indentation bugs
def html(raw_html):
    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Fraud Analytics | SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg:       #020817;
    --card:     #0A1628;
    --card2:    #0F1F38;
    --border:   rgba(51,65,85,0.7);
    --accent:   #06B6D4;
    --fraud:    #EF4444;
    --safe:     #10B981;
    --warn:     #F59E0B;
    --purple:   #8B5CF6;
    --t1:       #F8FAFC;
    --t2:       #94A3B8;
    --t3:       #475569;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--t1) !important;
}

.block-container { padding-top: 1.2rem !important; padding-bottom: 3rem !important; }
.stMainBlockContainer { padding-left: 1.5rem !important; padding-right: 1.5rem !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #050D1A 100%) !important;
    border-right: 1px solid rgba(6,182,212,0.12) !important;
}
[data-testid="stSidebar"] * { color: var(--t2) !important; }
[data-testid="stSidebar"] strong, [data-testid="stSidebar"] h3 { color: var(--t1) !important; }

/* Radio Buttons Navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin: 2px 0 !important;
    display: flex !important;
    align-items: center !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    color: var(--t2) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(6,182,212,0.08) !important;
    color: var(--t1) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div + label,
[data-testid="stSidebar"] input[type="radio"]:checked ~ label {
    background: rgba(6,182,212,0.15) !important;
    color: var(--accent) !important;
    font-weight: 700 !important;
    border-left: 3px solid var(--accent) !important;
}

/* Input Fields */
input, select, textarea,
[data-baseweb="input"] > div,
[data-baseweb="select"] > div:first-child {
    background: rgba(15,31,56,0.8) !important;
    border: 1px solid rgba(51,65,85,0.8) !important;
    border-radius: 10px !important;
    color: var(--t1) !important;
}
input:focus, [data-baseweb="input"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,0.1) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0E9BB5, #06B6D4) !important;
    color: #020817 !important;
    font-weight: 800 !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.4rem !important;
    box-shadow: 0 4px 16px rgba(6,182,212,0.3) !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 24px rgba(6,182,212,0.45) !important;
    filter: brightness(1.08) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(10,22,40,0.9), rgba(5,13,26,0.95));
    border: 1px solid rgba(51,65,85,0.6);
    border-radius: 16px;
    padding: 18px 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
[data-testid="stMetricValue"] {
    color: var(--t1) !important;
    font-weight: 800 !important;
    font-size: 1.6rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--t2) !important;
    font-size: 0.74rem !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(51,65,85,0.5) !important;
    border-radius: 12px !important;
}
hr { border-color: rgba(51,65,85,0.4) !important; }
</style>
""")

# ── Helper Components ──────────────────────────────────────────────────────────
def kpi_card(label, value, color, icon, subtext=""):
    return f"""
    <div style="background:linear-gradient(145deg, rgba(10,22,40,0.95) 0%, rgba(5,13,26,0.98) 100%);
                border:1px solid rgba(51,65,85,0.5); border-radius:18px; padding:22px 22px 18px;
                border-bottom:3px solid {color};
                box-shadow:0 8px 32px rgba(0,0,0,0.35); position:relative; overflow:hidden;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;
                        letter-spacing:0.8px;">{label}</div>
            <div style="width:36px;height:36px;border-radius:10px;display:flex;align-items:center;
                        justify-content:center;font-size:1.1rem;
                        background:linear-gradient(135deg,{color}22,{color}08);
                        border:1px solid {color}35;">{icon}</div>
        </div>
        <div style="font-size:2.0rem;font-weight:900;color:{color};margin:10px 0 5px;
                    letter-spacing:-0.03em;">{value}</div>
        <div style="font-size:0.72rem;color:#64748B;font-weight:500;">{subtext}</div>
    </div>"""

def section_header(title, subtitle=""):
    sub_html = f"<div style='font-size:0.77rem;color:#64748B;margin-top:3px;'>{subtitle}</div>" if subtitle else ""
    html(f"""
    <div style="margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid rgba(51,65,85,0.35);">
        <div style="font-size:1.0rem;font-weight:800;color:#F8FAFC;letter-spacing:-0.01em;">{title}</div>
        {sub_html}
    </div>""")

def metric_pill(label, value, color="#06B6D4"):
    return f"""
    <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(51,65,85,0.5);border-radius:12px;
                padding:14px 18px;text-align:center;">
        <div style="font-size:0.67rem;color:#64748B;text-transform:uppercase;font-weight:700;letter-spacing:0.5px;">{label}</div>
        <div style="font-size:1.4rem;font-weight:900;color:{color};margin-top:5px;">{value}</div>
    </div>"""

# ── Load Data (Cached) ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_everything():
    from src.data_preprocessing import load_raw_data, get_dataset_info
    from src.exploratory_analysis import compute_eda_statistics, generate_visualizations
    from src.train_model import train_and_save_model
    from src.evaluate_model import evaluate_performance
    from src.prediction import FraudPredictor

    data_file = 'data/credit_card_fraud_dataset.csv'
    if not os.path.exists(data_file):
        data_file = 'credit_card_fraud_dataset.csv'

    df = load_raw_data(data_file)
    dataset_info = get_dataset_info(df)
    eda_stats = compute_eda_statistics(df)

    os.makedirs('outputs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    generate_visualizations(df, output_dir='outputs')

    model_path = 'models/random_forest_model.pkl'
    if os.path.exists(model_path):
        model_payload = joblib.load(model_path)
    else:
        model_payload = train_and_save_model(data_file, model_path)

    metrics = evaluate_performance(model_payload, output_dir='outputs')
    predictor = FraudPredictor(model_path=model_path)

    fraud_s   = df[df['IsFraud'] == 1].head(10)
    genuine_s = df[df['IsFraud'] == 0].head(15)
    batch_df  = pd.concat([fraud_s, genuine_s]).sample(frac=1, random_state=42)
    batch_samples = predictor.predict_batch(batch_df)

    return df, dataset_info, eda_stats, metrics, predictor, batch_samples

# ── Sidebar Content ────────────────────────────────────────────────────────────
with st.sidebar:
    html("""
    <div style="padding:4px 0 20px;border-bottom:1px solid rgba(51,65,85,0.4);margin-bottom:8px;">
        <div style="display:flex;align-items:center;gap:13px;margin-bottom:14px;">
            <div style="width:44px;height:44px;background:linear-gradient(135deg,rgba(6,182,212,0.25),rgba(6,182,212,0.06));
                        border:1px solid rgba(6,182,212,0.4);border-radius:12px;display:flex;
                        align-items:center;justify-content:center;font-size:1.35rem;
                        box-shadow:0 0 20px rgba(6,182,212,0.18);">🛡️</div>
            <div>
                <div style="font-size:0.9rem;font-weight:800;color:#F8FAFC;">CYBER FRAUD <span style="color:#06B6D4;">ANALYTICS</span></div>
                <div style="font-size:0.62rem;color:#64748B;text-transform:uppercase;letter-spacing:0.7px;">v2.0 • SOC Dashboard</div>
            </div>
        </div>
        <div style="background:linear-gradient(135deg,rgba(6,182,212,0.1),rgba(6,182,212,0.03));
                    border:1px solid rgba(6,182,212,0.25);border-radius:12px;padding:10px 14px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
                <span style="width:7px;height:7px;background:#10B981;border-radius:50%;
                             box-shadow:0 0 8px #10B981;display:inline-block;"></span>
                <span style="font-size:0.78rem;font-weight:700;color:#F8FAFC;">SOC Live Portal</span>
            </div>
            <div style="font-size:0.68rem;color:#64748B;">Dataset: 100,000 Transactions</div>
        </div>
    </div>
    """)

    page = st.radio(
        "Navigate",
        ["📊  Dashboard", "📁  Dataset Overview", "📈  Visualizations",
         "⚙️  Model Performance", "🔍  Transaction Analyzer",
         "📡  Live Monitor", "📑  Batch Analysis", "📥  Intelligence Report", "ℹ️  About & Viva"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    html("""
    <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(51,65,85,0.4);
                border-radius:12px;padding:12px 14px;margin-bottom:12px;">
        <div style="font-size:0.65rem;color:#64748B;text-transform:uppercase;font-weight:700;
                    letter-spacing:0.7px;margin-bottom:6px;">System Status</div>
        <div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;font-weight:600;color:#F8FAFC;margin-bottom:3px;">
            <span style="width:7px;height:7px;background:#10B981;border-radius:50%;
                         box-shadow:0 0 8px #10B981;display:inline-block;"></span>
            Model Online
        </div>
        <div style="font-size:0.67rem;color:#64748B;">Random Forest Classifier<br>100k records trained</div>
    </div>
    """)

# ── Load Data ───────────────────────────────────────────────────────────────────
with st.spinner("🔄  Loading SOC Engine..."):
    df, dataset_info, eda_stats, metrics, predictor, batch_samples = load_everything()

# ══════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "📊  Dashboard":
    html("""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;
                margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid rgba(51,65,85,0.35);">
        <div>
            <div style="font-size:1.45rem;font-weight:900;color:#F8FAFC;letter-spacing:-0.02em;margin-bottom:4px;">
                CYBER FRAUD DATA TRANSACTION ANALYSIS</div>
            <div style="font-size:0.82rem;color:#64748B;">
                Transaction Intelligence &nbsp;•&nbsp; Fraud Detection &nbsp;•&nbsp; Risk Analysis</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;background:rgba(10,22,40,0.9);
                    border:1px solid rgba(51,65,85,0.5);border-radius:10px;padding:8px 16px;">
            <span style="width:7px;height:7px;background:#10B981;border-radius:50%;
                         box-shadow:0 0 8px #10B981;display:inline-block;"></span>
            <span style="font-size:0.78rem;color:#94A3B8;font-weight:600;">SOC Engine Active</span>
        </div>
    </div>
    """)

    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1: html(kpi_card("Total Transactions", f"{eda_stats['total_transactions']:,}", "#06B6D4", "💳", "100% of Dataset"))
    with k2: html(kpi_card("Genuine Transactions", f"{eda_stats['genuine_transactions']:,}", "#10B981", "✓", f"{eda_stats['genuine_percentage']}% Verified Safe"))
    with k3: html(kpi_card("Fraudulent Transactions", f"{eda_stats['fraud_transactions']:,}", "#EF4444", "⚠️", f"{eda_stats['fraud_percentage']}% of Total"))
    with k4: html(kpi_card("Fraud Rate", f"{eda_stats['fraud_percentage']}%", "#F59E0B", "📊", "Low but Critical"))

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Charts row
    section_header("📊 Key Insights", "Visualizations generated directly from the 100k transaction dataset")
    c1, c2 = st.columns(2)
    with c1:
        html("<div style='font-size:0.74rem;color:#06B6D4;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;'>Fraud vs Genuine Distribution</div>")
        st.image("outputs/fraud_distribution.png", use_container_width=True)
    with c2:
        html("<div style='font-size:0.74rem;color:#06B6D4;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;'>Transaction Amount Histogram</div>")
        st.image("outputs/transaction_distribution.png", use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        html("<div style='font-size:0.74rem;color:#06B6D4;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;'>Risk Distribution (Donut)</div>")
        st.image("outputs/risk_donut.png", use_container_width=True)
    with c4:
        section_header("⚙️ Model Performance Snapshot")
        pm1, pm2 = st.columns(2)
        pm1.metric("Accuracy",  f"{metrics['accuracy']}%")
        pm2.metric("Precision", f"{metrics['precision']}%")
        pm3, pm4 = st.columns(2)
        pm3.metric("Recall",    f"{metrics['recall']}%")
        pm4.metric("F1 Score",  f"{metrics['f1_score']}%")

# ══════════════════════════════════════════════════════════════════════
# PAGE: DATASET OVERVIEW
# ══════════════════════════════════════════════════════════════════════
elif page == "📁  Dataset Overview":
    section_header("📁 Dataset Overview", "credit_card_fraud_dataset.csv — 100,000 Transaction Records")

    r1, r2, r3 = st.columns(3)
    r1.metric("Total Rows",        f"{dataset_info['total_rows']:,}")
    r2.metric("Total Columns",     dataset_info['total_cols'])
    r3.metric("Missing Values",    dataset_info['missing_values'])
    r4, r5, r6 = st.columns(3)
    r4.metric("Duplicate Records", dataset_info['duplicate_rows'])
    r5.metric("Avg Amount",        f"${eda_stats['amount_mean']:,.2f}")
    r6.metric("Max Fraud Amount",  f"${eda_stats['fraud_amount_max']:,.2f}")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    section_header("Column Schema")
    col_df = pd.DataFrame(dataset_info['columns'])
    st.dataframe(col_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section_header("Statistical Summary")
    summary = {
        "Metric": ["Mean Amount","Min Amount","Max Amount","Median Amount","Std Deviation","Fraud Mean","Genuine Mean"],
        "Value":  [f"${eda_stats['amount_mean']:,.2f}", f"${eda_stats['amount_min']:,.2f}",
                   f"${eda_stats['amount_max']:,.2f}", f"${eda_stats['amount_median']:,.2f}",
                   f"${eda_stats['amount_std']:,.2f}", f"${eda_stats['fraud_amount_mean']:,.2f}",
                   f"${eda_stats['genuine_amount_mean']:,.2f}"]
    }
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════
elif page == "📈  Visualizations":
    section_header("📈 Matplotlib SOC Visualizations", "All charts generated from live 100k transaction dataset")
    charts = [
        ("fraud_distribution.png",       "Fraud vs Genuine Distribution"),
        ("transaction_distribution.png", "Transaction Amount Histogram"),
        ("fraud_amount_distribution.png","Fraud Transaction Amount"),
        ("correlation.png",              "Feature Correlation Heatmap"),
        ("risk_donut.png",               "Transaction Risk Analysis"),
    ]
    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(charts):
                fname, title = charts[i+j]
                with col:
                    html(f"<div style='font-size:0.74rem;color:#06B6D4;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;'>{title}</div>")
                    st.image(f"outputs/{fname}", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE: MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════
elif page == "⚙️  Model Performance":
    section_header("⚙️ Machine Learning Model Evaluation", "RandomForestClassifier — n_estimators=30, class_weight='balanced'")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy",  f"{metrics['accuracy']}%")
    m2.metric("Precision", f"{metrics['precision']}%")
    m3.metric("Recall",    f"{metrics['recall']}%")
    m4.metric("F1 Score",  f"{metrics['f1_score']}%")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    section_header("Confusion Matrix & Accuracy Gauge")
    ci1, ci2 = st.columns(2)
    with ci1: st.image("outputs/confusion_matrix.png", use_container_width=True)
    with ci2: st.image("outputs/accuracy_gauge.png",   use_container_width=True)

    cm = metrics['confusion_matrix']
    section_header("Confusion Matrix Breakdown")
    cm_df = pd.DataFrame({
        "": ["Actual: Genuine", "Actual: Fraudulent"],
        "Predicted: Genuine":    [f"✅ TN = {cm['tn']:,}", f"❌ FN = {cm['fn']:,}"],
        "Predicted: Fraudulent": [f"⚠️ FP = {cm['fp']:,}", f"🎯 TP = {cm['tp']:,}"]
    })
    st.dataframe(cm_df, use_container_width=True, hide_index=True)

    html(f"""
    <div style="background:linear-gradient(135deg,rgba(6,182,212,0.07),rgba(6,182,212,0.02));
                border:1px solid rgba(6,182,212,0.2);border-radius:14px;padding:18px 22px;margin-top:16px;">
        <div style="color:#06B6D4;font-size:0.78rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:8px;">💡 Why Recall & Precision Matter</div>
        <p style="color:#94A3B8;font-size:0.83rem;line-height:1.65;margin:0;">{metrics['explanation']}</p>
    </div>
    """)

# ══════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTION ANALYZER
# ══════════════════════════════════════════════════════════════════════
elif page == "🔍  Transaction Analyzer":
    section_header("🔍 Interactive Transaction Risk Analyzer", "Real-time fraud prediction using trained Random Forest model")

    col_form, col_result = st.columns([1, 1])

    with col_form:
        html("<div style='font-size:0.74rem;color:#06B6D4;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:12px;'>Transaction Feature Input</div>")
        with st.form("predict_form"):
            amount      = st.number_input("Transaction Amount ($)", min_value=0.01, value=4189.27, step=0.01)
            merchant_id = st.number_input("Merchant ID",            min_value=1,   value=688,     step=1)
            tx_type     = st.selectbox("Transaction Type", ["purchase","refund","transfer","withdrawal"], index=1)
            location    = st.selectbox("Location / Region", [
                "India", "India (Mumbai)", "India (Delhi)", "India (Bengaluru)", "India (Hyderabad)",
                "San Antonio", "New York", "Los Angeles", "Chicago",
                "Houston", "Phoenix", "Philadelphia", "San Diego", "Dallas", "San Jose"
            ])
            hour        = st.slider("Transaction Hour (0–23)", 0, 23, 3)
            submitted   = st.form_submit_button("⚡  ANALYZE TRANSACTION", use_container_width=True)

    with col_result:
        html("<div style='font-size:0.74rem;color:#06B6D4;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:12px;'>Prediction Result</div>")
        if submitted:
            with st.spinner("Scanning transaction..."):
                result = predictor.predict_single(amount, merchant_id, tx_type, location, hour)
            is_fraud = result['prediction'] == 'FRAUDULENT'
            col   = "#EF4444" if is_fraud else "#10B981"
            icon  = "🚨" if is_fraud else "✅"
            label = "FRAUDULENT TRANSACTION" if is_fraud else "GENUINE TRANSACTION"
            msg   = "Suspicious anomaly pattern detected. Recommend blocking transaction." if is_fraud \
                    else "Transaction parameters align with normal activity. Safe to proceed."
            bg_gl = "rgba(239,68,68,0.06)" if is_fraud else "rgba(16,185,129,0.06)"

            html(f"""
            <div style="background:linear-gradient(160deg,{bg_gl},rgba(5,13,26,0.9));
                        border:1px solid {col}40;border-radius:18px;padding:24px 22px;
                        box-shadow:0 0 40px {col}12;">
                <div style="font-size:1.05rem;font-weight:800;color:{col};margin-bottom:16px;
                            display:flex;align-items:center;gap:10px;">{icon} {label}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;
                            border-top:1px solid rgba(51,65,85,0.4);padding-top:16px;">
                    <div>
                        <div style="font-size:0.64rem;color:#64748B;text-transform:uppercase;font-weight:700;">Prediction</div>
                        <div style="font-size:1.0rem;font-weight:800;color:{col};margin-top:5px;">{result['prediction']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.64rem;color:#64748B;text-transform:uppercase;font-weight:700;">Fraud Probability</div>
                        <div style="font-size:1.0rem;font-weight:800;color:{col};margin-top:5px;">{result['fraud_probability']}%</div>
                    </div>
                    <div>
                        <div style="font-size:0.64rem;color:#64748B;text-transform:uppercase;font-weight:700;">Risk Level</div>
                        <div style="font-size:1.0rem;font-weight:800;color:{col};margin-top:5px;">{result['risk_level']}</div>
                    </div>
                </div>
                <div style="margin-top:12px;height:5px;background:rgba(51,65,85,0.5);border-radius:4px;overflow:hidden;">
                    <div style="width:{result['fraud_probability']}%;height:100%;background:{col};border-radius:4px;
                                box-shadow:0 0 12px {col}80;"></div>
                </div>
                <div style="font-size:0.74rem;color:#64748B;margin-top:10px;">{msg}</div>
            </div>
            """)
        else:
            html("""
            <div style="background:rgba(10,22,40,0.7);border:1px dashed rgba(51,65,85,0.5);
                        border-radius:18px;padding:48px 20px;text-align:center;color:#475569;">
                <div style="font-size:2.2rem;margin-bottom:14px;">🔍</div>
                <div style="font-size:0.88rem;line-height:1.6;">
                    Configure transaction features and click<br>
                    <strong style="color:#06B6D4;">ANALYZE TRANSACTION</strong>
                </div>
            </div>
            """)

# ══════════════════════════════════════════════════════════════════════
# PAGE: LIVE MONITOR
# ══════════════════════════════════════════════════════════════════════
elif page == "📡  Live Monitor":
    section_header("📡 Live Transaction Stream Monitor",
                   "Simulates real-time SOC feed — auto-analyzes random transactions from the dataset")

    html("""
    <div style="background:linear-gradient(135deg,rgba(6,182,212,0.08),rgba(99,102,241,0.05));
                border:1px solid rgba(6,182,212,0.2);border-radius:14px;padding:14px 18px;margin-bottom:20px;">
        <span style="font-size:0.8rem;color:#94A3B8;">
            🔴 &nbsp;<strong style="color:#EF4444;">LIVE</strong> &nbsp;— Scanning inbound transactions in real-time.
            Each scan runs the trained Random Forest model and displays probability scores instantly.
        </span>
    </div>
    """)

    cc1, cc2, cc3 = st.columns([1, 1, 2])
    with cc1:
        n_scans = st.selectbox("Transactions to Scan", [5, 10, 20, 50], index=1)
    with cc2:
        scan_speed = st.selectbox("Scan Speed", ["Fast (0.3s)", "Normal (0.7s)", "Slow (1.5s)"], index=0)
    speed_map = {"Fast (0.3s)": 0.3, "Normal (0.7s)": 0.7, "Slow (1.5s)": 1.5}
    delay = speed_map[scan_speed]

    with cc3:
        run_scan = st.button("▶  START LIVE SCAN", use_container_width=True)

    feed_placeholder = st.empty()
    summary_placeholder = st.empty()

    if run_scan:
        sample = df.sample(n=n_scans, random_state=random.randint(0, 9999)).reset_index(drop=True)
        feed_rows = []
        fraud_count = 0

        feed_placeholder.markdown("""
        <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(51,65,85,0.5);
                    border-radius:14px;padding:20px;font-family:'Inter',monospace;">
            <div style="color:#06B6D4;font-size:0.78rem;font-weight:700;margin-bottom:14px;">
                ⣾ Initializing scan engine...</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.4)

        for idx, row in sample.iterrows():
            result = predictor.predict_single(
                float(row['Amount']),
                float(row['MerchantID']),
                str(row['TransactionType']),
                str(row['Location'])
            )
            is_fraud = result['prediction'] == 'FRAUDULENT'
            if is_fraud:
                fraud_count += 1

            color = "#EF4444" if is_fraud else "#10B981"
            icon  = "🚨" if is_fraud else "✅"
            ts    = datetime.now().strftime("%H:%M:%S.%f")[:12]

            feed_rows.append({
                "icon": icon, "color": color,
                "ts": ts,
                "tx_id": row.get('TransactionID', idx+1),
                "amount": f"${float(row['Amount']):,.2f}",
                "type": str(row['TransactionType']).title(),
                "loc": str(row['Location']),
                "pred": result['prediction'],
                "prob": result['fraud_probability'],
                "risk": result['risk_level'],
            })

            rows_html = ""
            for r in feed_rows:
                rows_html += f"""
                <div style="display:flex;align-items:center;gap:14px;padding:10px 0;
                            border-bottom:1px solid rgba(51,65,85,0.25);">
                    <span style="font-size:1.1rem;">{r['icon']}</span>
                    <span style="font-size:0.68rem;color:#475569;font-family:monospace;min-width:80px;">{r['ts']}</span>
                    <span style="font-size:0.78rem;color:#64748B;min-width:70px;">#{r['tx_id']}</span>
                    <span style="font-size:0.8rem;color:#F8FAFC;font-weight:600;min-width:80px;">{r['amount']}</span>
                    <span style="font-size:0.75rem;color:#64748B;min-width:70px;">{r['type']}</span>
                    <span style="font-size:0.75rem;color:#64748B;min-width:100px;">{r['loc']}</span>
                    <span style="font-size:0.8rem;font-weight:700;color:{r['color']};min-width:110px;">{r['pred']}</span>
                    <span style="font-size:0.78rem;color:{r['color']};min-width:60px;">{r['prob']}%</span>
                    <span style="background:{r['color']}18;border:1px solid {r['color']}35;color:{r['color']};
                                 padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;">{r['risk']}</span>
                </div>"""

            feed_placeholder.markdown(f"""
            <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(51,65,85,0.5);
                        border-radius:14px;padding:18px 20px;max-height:460px;overflow-y:auto;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:7px;height:7px;background:#EF4444;border-radius:50%;
                                     box-shadow:0 0 8px #EF4444;display:inline-block;"></span>
                        <span style="font-size:0.75rem;color:#94A3B8;font-weight:700;">LIVE SCAN FEED</span>
                    </div>
                    <span style="font-size:0.72rem;color:#475569;">{len(feed_rows)}/{n_scans} scanned</span>
                </div>
                <div style="font-size:0.65rem;color:#475569;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.5px;padding-bottom:8px;border-bottom:1px solid rgba(51,65,85,0.4);
                            display:flex;gap:14px;">
                    <span style="min-width:20px;">·</span>
                    <span style="min-width:80px;">Timestamp</span>
                    <span style="min-width:70px;">Tx ID</span>
                    <span style="min-width:80px;">Amount</span>
                    <span style="min-width:70px;">Type</span>
                    <span style="min-width:100px;">Location</span>
                    <span style="min-width:110px;">Prediction</span>
                    <span style="min-width:60px;">Prob</span>
                    <span>Risk</span>
                </div>
                {rows_html}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(delay)

        genuine_count = n_scans - fraud_count
        summary_placeholder.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;margin-top:18px;">
            {metric_pill("Scanned",   str(n_scans),       "#06B6D4")}
            {metric_pill("Genuine",   str(genuine_count), "#10B981")}
            {metric_pill("Fraud",     str(fraud_count),   "#EF4444")}
            {metric_pill("Fraud Rate",f"{round(fraud_count/n_scans*100,1)}%", "#F59E0B")}
        </div>
        """, unsafe_allow_html=True)

    else:
        html("""
        <div style="background:rgba(10,22,40,0.8);border:1px dashed rgba(51,65,85,0.5);
                    border-radius:14px;padding:64px 20px;text-align:center;color:#475569;">
            <div style="font-size:2rem;margin-bottom:14px;">📡</div>
            <div style="font-size:0.88rem;">Click <strong style='color:#06B6D4;'>START LIVE SCAN</strong>
             to begin real-time transaction monitoring</div>
        </div>
        """)

# ══════════════════════════════════════════════════════════════════════
# PAGE: BATCH ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "📑  Batch Analysis":
    section_header("📑 Recent Transaction Batch Analysis", "Pre-analyzed sample from fraud + genuine transactions")

    f1, f2 = st.columns([1, 3])
    with f1:
        filter_opt = st.selectbox("Filter", ["All", "FRAUDULENT Only", "GENUINE Only"])

    rows = [{"Tx ID":f"#{tx['transaction_id']}","Amount":tx['amount'],"Type":tx['transaction_type'].title(),
             "Location":tx['location'],"Actual":tx['actual_status'],"Prediction":tx['prediction'],
             "Fraud Probability":f"{tx['fraud_probability']}%","Risk Level":tx['risk_level']} for tx in batch_samples]
    bdf = pd.DataFrame(rows)
    if filter_opt == "FRAUDULENT Only": bdf = bdf[bdf["Prediction"] == "FRAUDULENT"]
    elif filter_opt == "GENUINE Only":  bdf = bdf[bdf["Prediction"] == "GENUINE"]

    st.dataframe(bdf, use_container_width=True, hide_index=True)

    total  = len(bdf)
    frauds = len(bdf[bdf["Prediction"] == "FRAUDULENT"])
    html(f"""
    <div style="display:flex;gap:14px;margin-top:14px;">
        {metric_pill("Showing", str(total), "#06B6D4")}
        {metric_pill("Flagged Fraud", str(frauds), "#EF4444")}
        {metric_pill("Confirmed Safe", str(total-frauds), "#10B981")}
    </div>
    """)

# ══════════════════════════════════════════════════════════════════════
# PAGE: INTELLIGENCE REPORT
# ══════════════════════════════════════════════════════════════════════
elif page == "📥  Intelligence Report":
    section_header("📥 Fraud Intelligence Report Generator",
                   "Auto-generates a downloadable analytical report of the current session")

    html("""
    <div style="background:linear-gradient(135deg,rgba(139,92,246,0.08),rgba(139,92,246,0.02));
                border:1px solid rgba(139,92,246,0.25);border-radius:14px;padding:14px 18px;margin-bottom:24px;">
        <span style="font-size:0.82rem;color:#94A3B8;">
            📊 Click below to generate a complete Fraud Intelligence Report summarizing dataset statistics,
            model performance, risk distribution, and key findings — ready to download and present.
        </span>
    </div>
    """)

    if st.button("📊  GENERATE INTELLIGENCE REPORT", use_container_width=True):
        with st.spinner("Compiling intelligence report..."):
            time.sleep(1.2)

        cm = metrics['confusion_matrix']
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          CYBER FRAUD DATA TRANSACTION ANALYSIS & DETECTION SYSTEM          ║
║                    FRAUD INTELLIGENCE REPORT — v2.0                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Report Date    : {now_str}
Dataset        : credit_card_fraud_dataset.csv
Model          : RandomForestClassifier (n_estimators=30, balanced)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. DATASET SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Transactions   : {eda_stats['total_transactions']:>12,}
  Genuine Transactions : {eda_stats['genuine_transactions']:>12,}  ({eda_stats['genuine_percentage']}%)
  Fraudulent Trans.    : {eda_stats['fraud_transactions']:>12,}  ({eda_stats['fraud_percentage']}%)
  Missing Values       : {dataset_info['missing_values']:>12}
  Duplicate Records    : {dataset_info['duplicate_rows']:>12}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. TRANSACTION AMOUNT STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Mean Amount          : ${eda_stats['amount_mean']:>12,.2f}
  Min Amount           : ${eda_stats['amount_min']:>12,.2f}
  Max Amount           : ${eda_stats['amount_max']:>12,.2f}
  Median Amount        : ${eda_stats['amount_median']:>12,.2f}
  Std Deviation        : ${eda_stats['amount_std']:>12,.2f}
  Fraud Mean Amount    : ${eda_stats['fraud_amount_mean']:>12,.2f}
  Genuine Mean Amount  : ${eda_stats['genuine_amount_mean']:>12,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. MODEL PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Accuracy             : {metrics['accuracy']:>12}%
  Precision            : {metrics['precision']:>12}%
  Recall               : {metrics['recall']:>12}%
  F1 Score             : {metrics['f1_score']:>12}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. CONFUSION MATRIX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Predicted Genuine    Predicted Fraud
  Actual Genuine  :  TN = {cm['tn']:>10,}    FP = {cm['fp']:>8,}
  Actual Fraud    :  FN = {cm['fn']:>10,}    TP = {cm['tp']:>8,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. RISK DISTRIBUTION CLASSIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  LOW RISK    (0–30%  prob) : {eda_stats['low_risk_count']:>10,}  transactions (Green)
  MEDIUM RISK (30–70% prob) : {eda_stats['med_risk_count']:>10,}  transactions (Amber)
  HIGH RISK   (70–100% prob): {eda_stats['high_risk_count']:>10,}  transactions (Red)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. KEY FINDINGS & RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Fraud rate is {eda_stats['fraud_percentage']}% — low volume but each incident is high-value
  • Fraudulent transactions average ${eda_stats['fraud_amount_mean']:,.2f} vs ${eda_stats['genuine_amount_mean']:,.2f} genuine
  • Model achieves {metrics['accuracy']}% accuracy with class-balanced training
  • High-risk transactions above $3,000 at late night hours (22:00–06:00) require
    mandatory secondary verification
  • Recommend implementing real-time API scoring for all transactions > $2,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. TECHNOLOGY STACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Python 3 | Pandas | NumPy | Matplotlib | Scikit-learn | Joblib | Streamlit

══════════════════════════════════════════════════════════════════════════════
  END OF REPORT — Cyber Fraud Analytics v2.0 | Confidential
══════════════════════════════════════════════════════════════════════════════
"""
        st.download_button(
            label="⬇️  DOWNLOAD FRAUD INTELLIGENCE REPORT (.txt)",
            data=report,
            file_name=f"fraud_intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.success("✅ Report generated successfully! Click the download button above.")

        with st.expander("📄 Preview Report", expanded=True):
            st.code(report, language=None)

# ══════════════════════════════════════════════════════════════════════
# PAGE: ABOUT & VIVA
# ══════════════════════════════════════════════════════════════════════
elif page == "ℹ️  About & Viva":
    section_header("ℹ️ About Project & Viva Voce Q&A", "Prepared for BTech/CSE college project presentation")

    viva = [
        ("Q1: What is this project?", "An end-to-end Cyber Fraud Detection System that processes 100,000 financial transactions using a Random Forest ML model. It detects fraud in real-time, calculates fraud probability (0–100%), and classifies transaction risk into LOW, MEDIUM, and HIGH levels."),
        ("Q2: Why Random Forest?",    "Random Forest combines multiple decision trees (ensemble learning) to handle complex, non-linear patterns — e.g. unusual night-time hours + high refund amounts + specific merchant IDs together. It resists overfitting and outputs calibrated probability scores."),
        ("Q3: Why class_weight='balanced'?", "The dataset is severely imbalanced (~1% fraud, 99% genuine). Without balancing, classifiers learn to predict everything as genuine (99% accuracy, 0% fraud detection). Balanced weights force the model to treat each fraud sample as more important."),
        ("Q4: Precision vs Recall?",  "Recall = TP/(TP+FN) — fraction of actual frauds caught. Missing fraud costs money. Precision = TP/(TP+FP) — accuracy of fraud flags. Too many false positives frustrate genuine customers. A good system optimizes both."),
        ("Q5: How is Risk Level computed?", "The Random Forest outputs predict_proba() — a probability between 0 and 1. This is scaled to 0–100% and classified: 0–30% = LOW (Green), 30–70% = MEDIUM (Amber), 70–100% = HIGH (Red)."),
        ("Q6: What is the Live Monitor feature?", "A real-time SOC simulation that randomly samples transactions from the dataset, runs each through the trained model, and displays fraud probability scores in a live scrolling feed — mimicking a Security Operations Center environment."),
        ("Q7: What is the Intelligence Report?", "A feature that auto-generates a comprehensive analytical summary of the session — including dataset statistics, model metrics, confusion matrix, risk distribution, and recommendations — downloadable as a .txt file."),
        ("Q8: What features are used for ML?", "Amount, MerchantID, TransactionType_Code, Location_Code, Hour, DayOfWeek, IsNight, AmountToAvgRatio, HighAmountFlag — all derived from raw CSV columns through feature engineering."),
    ]

    for q, a in viva:
        html(f"""
        <div style="background:linear-gradient(135deg,rgba(10,22,40,0.95),rgba(5,13,26,0.98));
                    border:1px solid rgba(51,65,85,0.5);border-radius:14px;
                    padding:16px 20px;margin-bottom:10px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.2);">
            <div style="color:#06B6D4;font-weight:700;font-size:0.84rem;margin-bottom:7px;">{q}</div>
            <div style="color:#94A3B8;font-size:0.81rem;line-height:1.65;">{a}</div>
        </div>
        """)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    tech = ["Python 3","Pandas","NumPy","Matplotlib","Scikit-learn","Random Forest","Joblib","Streamlit"]
    badges = " ".join([f'<span style="background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.25);color:#06B6D4;padding:4px 12px;border-radius:20px;font-size:0.73rem;font-weight:700;">{t}</span>' for t in tech])
    html(f"""
    <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(51,65,85,0.4);
                border-radius:14px;padding:18px 22px;">
        <div style="color:#94A3B8;font-size:0.72rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:12px;">Technology Stack</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;">{badges}</div>
    </div>
    """)
