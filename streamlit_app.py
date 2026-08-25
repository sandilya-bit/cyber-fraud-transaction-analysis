import os
os.environ['MPLBACKEND'] = 'Agg'

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS Theme ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Global background */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #070C18 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Remove default streamlit padding */
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B !important;
}
[data-testid="stSidebar"] * { color: #94A3B8 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] strong {
    color: #F8FAFC !important;
}

/* All text */
p, li, label, div { color: #F8FAFC; }
h1, h2, h3, h4 { color: #F8FAFC !important; font-weight: 800; }

/* Input / select fields */
input, select, textarea,
[data-baseweb="input"] input,
[data-baseweb="select"] div {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Buttons */
.stButton > button {
    background-color: #06B6D4 !important;
    color: #070C18 !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    width: 100% !important;
}
.stButton > button:hover { filter: brightness(1.1); }

/* Metric cards */
[data-testid="stMetric"] {
    background: #0F172A;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"] { color: #F8FAFC !important; font-weight: 800; font-size: 1.7rem !important; }
[data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 0.78rem !important; text-transform: uppercase; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #334155 !important; border-radius: 10px !important; }
iframe { background-color: #0F172A !important; }

/* Dividers */
hr { border-color: #1E293B !important; }

/* Tabs */
[data-baseweb="tab-list"] { background-color: #0F172A !important; gap: 8px; }
[data-baseweb="tab"] { background-color: #1E293B !important; border-radius: 8px !important; color: #94A3B8 !important; font-weight: 600; }
[aria-selected="true"] { background-color: #06B6D4 !important; color: #070C18 !important; }

/* Spinner */
.stSpinner { color: #06B6D4 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helper: KPI Card HTML ───────────────────────────────────────────────────────
def kpi_card(label, value, color, icon, subtext=""):
    return f"""
    <div style="background:#0F172A; border:1px solid #334155; border-radius:14px;
                padding:18px 20px; border-bottom:3px solid {color}; height:100%;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="font-size:0.7rem; font-weight:700; color:#94A3B8;
                        text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
            <div style="width:34px; height:34px; border-radius:50%; display:flex;
                        align-items:center; justify-content:center; font-size:1rem;
                        background:rgba(255,255,255,0.07); border:1px solid #334155;">{icon}</div>
        </div>
        <div style="font-size:1.75rem; font-weight:800; color:{color}; margin-top:10px;">{value}</div>
        <div style="font-size:0.74rem; color:#94A3B8; margin-top:4px;">{subtext}</div>
    </div>"""


def section_title(title):
    st.markdown(f"""
    <div style="font-size:0.85rem; font-weight:700; color:#06B6D4; text-transform:uppercase;
                letter-spacing:0.8px; padding:4px 0 12px 0; border-bottom:1px solid #1E293B;
                margin-bottom:16px;">{title}</div>
    """, unsafe_allow_html=True)


def soc_card(content_html):
    st.markdown(f"""
    <div style="background:#0F172A; border:1px solid #334155; border-radius:14px;
                padding:20px 22px; margin-bottom:4px;">{content_html}</div>
    """, unsafe_allow_html=True)


# ── Data & Model Loading (cached) ───────────────────────────────────────────────
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

    fraud_s  = df[df['IsFraud'] == 1].head(10)
    genuine_s = df[df['IsFraud'] == 0].head(15)
    batch_df  = pd.concat([fraud_s, genuine_s]).sample(frac=1, random_state=42)
    batch_samples = predictor.predict_batch(batch_df)

    return df, dataset_info, eda_stats, metrics, predictor, batch_samples


# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; padding:4px 0 20px 0;
                border-bottom:1px solid #1E293B; margin-bottom:8px;">
        <div style="width:40px; height:40px; background:rgba(6,182,212,0.15);
                    border:1px solid #06B6D4; border-radius:10px; display:flex;
                    align-items:center; justify-content:center; font-size:1.3rem;">🛡️</div>
        <div>
            <div style="font-size:0.95rem; font-weight:800; color:#F8FAFC;">
                CYBER FRAUD <span style="color:#06B6D4;">ANALYTICS</span></div>
            <div style="font-size:0.68rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.5px;">Transaction Security SOC</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "📁 Dataset Overview", "📈 Visualizations",
         "⚙️ Model Performance", "🔍 Transaction Analyzer", "📑 Batch Analysis", "ℹ️ About Project"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="background:#1E293B; border-radius:8px; padding:12px 14px;">
        <div style="font-size:0.7rem; color:#94A3B8; text-transform:uppercase;
                    font-weight:700; margin-bottom:6px;">System Status</div>
        <div style="display:flex; align-items:center; gap:8px; font-size:0.82rem;
                    font-weight:600; color:#F8FAFC;">
            <span style="width:8px;height:8px;background:#10B981;border-radius:50%;
                         box-shadow:0 0 8px #10B981;display:inline-block;"></span>
            Model Online
        </div>
        <div style="font-size:0.7rem; color:#94A3B8; margin-top:4px;">Random Forest Classifier</div>
    </div>
    """, unsafe_allow_html=True)


# ── Load Data ───────────────────────────────────────────────────────────────────
with st.spinner("🔄 Loading Cyber Fraud Detection Engine..."):
    df, dataset_info, eda_stats, metrics, predictor, batch_samples = load_everything()


# ══════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <h1 style="font-size:1.4rem; font-weight:800; color:#F8FAFC; margin-bottom:2px;">
        CYBER FRAUD DATA TRANSACTION ANALYSIS AND DETECTION SYSTEM</h1>
    <p style="color:#94A3B8; font-size:0.82rem; margin-bottom:20px;">
        Transaction Intelligence • Fraud Detection • Risk Analysis</p>
    """, unsafe_allow_html=True)

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Transactions", f"{eda_stats['total_transactions']:,}",
                             "#06B6D4", "💳", "100% of Dataset"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Genuine Transactions", f"{eda_stats['genuine_transactions']:,}",
                             "#10B981", "✓", f"{eda_stats['genuine_percentage']}% of Total"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Fraudulent Transactions", f"{eda_stats['fraud_transactions']:,}",
                             "#EF4444", "⚠️", f"{eda_stats['fraud_percentage']}% of Total"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Fraud Percentage", f"{eda_stats['fraud_percentage']}%",
                             "#F59E0B", "📊", "Low but Critical"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick charts row
    section_title("📊 Key Insights — Visualizations")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div style='color:#94A3B8;font-size:0.78rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;'>Fraud vs Genuine Distribution</div>", unsafe_allow_html=True)
        st.image("outputs/fraud_distribution.png", use_container_width=True)
    with col_r:
        st.markdown("<div style='color:#94A3B8;font-size:0.78rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;'>Transaction Amount Distribution</div>", unsafe_allow_html=True)
        st.image("outputs/transaction_distribution.png", use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div style='color:#94A3B8;font-size:0.78rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;'>Transaction Risk Analysis</div>", unsafe_allow_html=True)
        st.image("outputs/risk_donut.png", use_container_width=True)
    with col4:
        st.markdown("<div style='color:#94A3B8;font-size:0.78rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;'>Model Performance</div>", unsafe_allow_html=True)
        pm1, pm2, pm3, pm4 = st.columns(4)
        pm1.metric("Accuracy",  f"{metrics['accuracy']}%")
        pm2.metric("Precision", f"{metrics['precision']}%")
        pm3.metric("Recall",    f"{metrics['recall']}%")
        pm4.metric("F1 Score",  f"{metrics['f1_score']}%")
        st.image("outputs/confusion_matrix.png", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE: DATASET OVERVIEW
# ══════════════════════════════════════════════════════════════════════
elif page == "📁 Dataset Overview":
    st.markdown("<h2>📁 Dataset Overview</h2>", unsafe_allow_html=True)

    section_title("Dataset Metadata — credit_card_fraud_dataset.csv")

    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.metric("Total Rows",       f"{dataset_info['total_rows']:,}")
    r1c2.metric("Total Columns",    f"{dataset_info['total_cols']}")
    r1c3.metric("Missing Values",   f"{dataset_info['missing_values']}")

    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.metric("Duplicate Records", f"{dataset_info['duplicate_rows']}")
    r2c2.metric("Avg Transaction",   f"${eda_stats['amount_mean']:,.2f}")
    r2c3.metric("Max Fraud Amount",  f"${eda_stats['fraud_amount_max']:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Column Schema")
    col_df = pd.DataFrame(dataset_info['columns'])
    st.dataframe(col_df.style.set_properties(**{
        'background-color': '#0F172A', 'color': '#F8FAFC', 'border': '1px solid #334155'
    }), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Statistical Summary")
    stats_data = {
        "Metric": ["Mean Amount", "Min Amount", "Max Amount", "Median Amount", "Std Deviation",
                   "Fraud Avg Amount", "Genuine Avg Amount"],
        "Value": [f"${eda_stats['amount_mean']:,.2f}", f"${eda_stats['amount_min']:,.2f}",
                  f"${eda_stats['amount_max']:,.2f}", f"${eda_stats['amount_median']:,.2f}",
                  f"${eda_stats['amount_std']:,.2f}", f"${eda_stats['fraud_amount_mean']:,.2f}",
                  f"${eda_stats['genuine_amount_mean']:,.2f}"]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE: VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════
elif page == "📈 Visualizations":
    st.markdown("<h2>📈 Matplotlib SOC Visualizations</h2>", unsafe_allow_html=True)

    charts = [
        ("fraud_distribution.png",        "Viz 1 — Fraud vs Genuine Transactions"),
        ("transaction_distribution.png",  "Viz 2 — Transaction Amount Distribution"),
        ("fraud_amount_distribution.png", "Viz 3 — Fraud Transaction Amount"),
        ("correlation.png",               "Viz 4 — Feature Correlation Heatmap"),
        ("risk_donut.png",                "Viz 5 — Transaction Risk Analysis"),
    ]

    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(charts):
                fname, title = charts[i + j]
                with col:
                    st.markdown(f"<div style='color:#06B6D4;font-size:0.8rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;'>{title}</div>", unsafe_allow_html=True)
                    st.image(f"outputs/{fname}", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE: MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════
elif page == "⚙️ Model Performance":
    st.markdown("<h2>⚙️ Machine Learning Model Evaluation</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>RandomForestClassifier(n_estimators=30, max_depth=12, class_weight='balanced')</p>", unsafe_allow_html=True)

    section_title("Performance Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy",  f"{metrics['accuracy']}%",  delta=None)
    m2.metric("Precision", f"{metrics['precision']}%", delta=None)
    m3.metric("Recall",    f"{metrics['recall']}%",    delta=None)
    m4.metric("F1 Score",  f"{metrics['f1_score']}%",  delta=None)

    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Confusion Matrix & Accuracy Gauge")
    ci1, ci2 = st.columns(2)
    with ci1:
        st.image("outputs/confusion_matrix.png", use_container_width=True)
    with ci2:
        st.image("outputs/accuracy_gauge.png",  use_container_width=True)

    cm = metrics['confusion_matrix']
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Confusion Matrix Breakdown")
    cm_df = pd.DataFrame({
        "": ["Actual: Genuine", "Actual: Fraudulent"],
        "Predicted: Genuine":    [f"TN = {cm['tn']:,}", f"FN = {cm['fn']:,}"],
        "Predicted: Fraudulent": [f"FP = {cm['fp']:,}", f"TP = {cm['tp']:,}"]
    })
    st.dataframe(cm_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#0F172A; border:1px solid #334155; border-radius:12px; padding:16px 20px;">
        <div style="color:#06B6D4; font-size:0.82rem; font-weight:700; margin-bottom:6px;">
            💡 Why Recall & Precision Matter in Cyber Fraud Detection</div>
        <p style="color:#94A3B8; font-size:0.84rem; line-height:1.6;">{metrics['explanation']}</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTION ANALYZER
# ══════════════════════════════════════════════════════════════════════
elif page == "🔍 Transaction Analyzer":
    st.markdown("<h2>🔍 Interactive Transaction Risk Analyzer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>Enter transaction details below and click Analyze to get an instant fraud prediction.</p>", unsafe_allow_html=True)

    col_form, col_result = st.columns([1, 1])

    with col_form:
        section_title("Enter Transaction Features")
        with st.form("predict_form"):
            amount       = st.number_input("Transaction Amount ($)", min_value=0.01, value=4189.27, step=0.01)
            merchant_id  = st.number_input("Merchant ID",            min_value=1,   value=688,     step=1)
            tx_type      = st.selectbox("Transaction Type",   ["purchase", "refund", "transfer", "withdrawal"], index=1)
            location     = st.selectbox("Location", ["San Antonio","New York","Los Angeles","Chicago",
                                                     "Houston","Phoenix","Philadelphia","San Diego","Dallas","San Jose"])
            hour         = st.slider("Transaction Hour (0–23)", 0, 23, 3)

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                submitted = st.form_submit_button("⚡ ANALYZE TRANSACTION")
            with col_b2:
                demo_btn = st.form_submit_button("🔄 Load Demo Values")

    with col_result:
        section_title("Prediction Result")

        if submitted:
            with st.spinner("Analyzing transaction..."):
                result = predictor.predict_single(amount, merchant_id, tx_type, location, hour)

            is_fraud = result['prediction'] == 'FRAUDULENT'
            border_color = "#EF4444" if is_fraud else "#10B981"
            bg_grad      = "rgba(239,68,68,0.1)" if is_fraud else "rgba(16,185,129,0.1)"
            icon         = "🚨" if is_fraud else "✓"
            header_text  = "FRAUDULENT TRANSACTION" if is_fraud else "GENUINE TRANSACTION"
            alert_msg    = "Warning: Suspicious anomaly detected. Recommend flagging this transaction." if is_fraud \
                           else "Transaction verified safe. Characteristics match normal behavior."

            st.markdown(f"""
            <div style="background:linear-gradient(180deg,{bg_grad} 0%,#0F172A 100%);
                        border:1px solid {border_color}; border-radius:14px; padding:20px;">
                <div style="font-size:1.1rem; font-weight:800; color:{border_color}; margin-bottom:12px;">
                    {icon} {header_text}</div>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px;
                            border-top:1px solid #334155; padding-top:14px; margin-top:4px;">
                    <div>
                        <div style="font-size:0.68rem; color:#94A3B8; text-transform:uppercase;">Prediction</div>
                        <div style="font-size:1.05rem; font-weight:800; color:{border_color}; margin-top:4px;">
                            {result['prediction']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.68rem; color:#94A3B8; text-transform:uppercase;">Fraud Probability</div>
                        <div style="font-size:1.05rem; font-weight:800; color:{border_color}; margin-top:4px;">
                            {result['fraud_probability']}%</div>
                    </div>
                    <div>
                        <div style="font-size:0.68rem; color:#94A3B8; text-transform:uppercase;">Risk Level</div>
                        <div style="font-size:1.05rem; font-weight:800; color:{border_color}; margin-top:4px;">
                            {result['risk_level']}</div>
                    </div>
                </div>
                <div style="font-size:0.74rem; color:#94A3B8; margin-top:12px;">{alert_msg}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#0F172A; border:1px dashed #334155; border-radius:14px;
                        padding:40px 20px; text-align:center; color:#94A3B8;">
                <div style="font-size:2rem; margin-bottom:12px;">🔍</div>
                <div style="font-size:0.9rem;">Enter transaction details and click<br>
                    <strong style="color:#06B6D4;">ANALYZE TRANSACTION</strong> to see the result here.</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE: BATCH ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "📑 Batch Analysis":
    st.markdown("<h2>📑 Recent Transaction Batch Analysis</h2>", unsafe_allow_html=True)

    filter_opt = st.selectbox("Filter Transactions", ["All", "FRAUDULENT Only", "GENUINE Only"])

    rows = []
    for tx in batch_samples:
        rows.append({
            "Tx ID": f"#{tx['transaction_id']}",
            "Amount": tx['amount'],
            "Type": tx['transaction_type'].title(),
            "Location": tx['location'],
            "Actual Status": tx['actual_status'],
            "Prediction": tx['prediction'],
            "Fraud Probability": f"{tx['fraud_probability']}%",
            "Risk Level": tx['risk_level'],
        })

    batch_df_display = pd.DataFrame(rows)
    if filter_opt == "FRAUDULENT Only":
        batch_df_display = batch_df_display[batch_df_display["Prediction"] == "FRAUDULENT"]
    elif filter_opt == "GENUINE Only":
        batch_df_display = batch_df_display[batch_df_display["Prediction"] == "GENUINE"]

    st.dataframe(
        batch_df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prediction": st.column_config.TextColumn("Prediction"),
            "Risk Level": st.column_config.TextColumn("Risk Level"),
        }
    )

    total  = len(batch_df_display)
    frauds = len(batch_df_display[batch_df_display["Prediction"] == "FRAUDULENT"])
    genuine = total - frauds
    st.markdown(f"""
    <div style="display:flex; gap:16px; margin-top:12px;">
        <div style="background:#0F172A; border:1px solid #334155; border-radius:10px;
                    padding:12px 18px; flex:1; text-align:center;">
            <div style="color:#94A3B8; font-size:0.72rem;">Showing</div>
            <div style="color:#06B6D4; font-size:1.2rem; font-weight:800;">{total}</div>
        </div>
        <div style="background:#0F172A; border:1px solid #334155; border-radius:10px;
                    padding:12px 18px; flex:1; text-align:center;">
            <div style="color:#94A3B8; font-size:0.72rem;">Flagged Fraud</div>
            <div style="color:#EF4444; font-size:1.2rem; font-weight:800;">{frauds}</div>
        </div>
        <div style="background:#0F172A; border:1px solid #334155; border-radius:10px;
                    padding:12px 18px; flex:1; text-align:center;">
            <div style="color:#94A3B8; font-size:0.72rem;">Confirmed Genuine</div>
            <div style="color:#10B981; font-size:1.2rem; font-weight:800;">{genuine}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE: ABOUT PROJECT
# ══════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About Project":
    st.markdown("<h2>ℹ️ About Project & Viva Voce Q&A</h2>", unsafe_allow_html=True)

    viva = [
        ("Q1: What is this project?",
         "A system that analyzes 100,000 financial transactions using Random Forest ML to detect fraud, "
         "calculate fraud probability (0–100%), and classify risk into LOW, MEDIUM, and HIGH categories."),
        ("Q2: Why Random Forest?",
         "Random Forest combines multiple decision trees into an ensemble, handling non-linear feature interactions "
         "(e.g., unusual late-night hours + high refund amounts + specific merchant IDs). It resists overfitting "
         "and produces calibrated fraud probabilities."),
        ("Q3: Why is class_weight='balanced' used?",
         "Fraud datasets are severely imbalanced (~1% fraud, 99% genuine). Without balanced class weights, "
         "classifiers predict everything as genuine to maximize accuracy while missing all actual fraud cases."),
        ("Q4: What are Precision and Recall?",
         "Recall = TP / (TP + FN): What fraction of actual frauds did the model catch? Missing fraud = financial loss. "
         "Precision = TP / (TP + FP): Of all transactions flagged as fraud, how many were real frauds? "
         "False alarms inconvenience genuine customers."),
        ("Q5: How is Risk Level determined?",
         "0–30% fraud probability → LOW RISK (Green), 30–70% → MEDIUM RISK (Amber), 70–100% → HIGH RISK (Red). "
         "These thresholds are directly derived from the Random Forest's predict_proba() output."),
        ("Q6: What features are used for prediction?",
         "Amount, MerchantID, TransactionType (encoded), Location (encoded), Hour, DayOfWeek, IsNight (binary), "
         "AmountToAvgRatio, HighAmountFlag — all derived from the raw dataset columns."),
        ("Q7: Why Pandas and NumPy?",
         "Pandas handles loading, cleaning (missing values, duplicates) and transforming the 100k-row CSV dataset. "
         "NumPy provides fast numerical processing for feature matrices."),
        ("Q8: Why Matplotlib?",
         "Matplotlib creates server-side visualizations (bar charts, histograms, correlation heatmap, donut charts, "
         "confusion matrix) saved as PNG images and served directly in the dashboard."),
    ]

    for q, a in viva:
        st.markdown(f"""
        <div style="background:#0F172A; border:1px solid #334155; border-radius:10px;
                    padding:14px 18px; margin-bottom:10px;">
            <div style="color:#06B6D4; font-weight:700; font-size:0.88rem; margin-bottom:6px;">{q}</div>
            <div style="color:#94A3B8; font-size:0.84rem; line-height:1.6;">{a}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0F172A; border:1px solid #06B6D4; border-radius:12px;
                padding:16px 20px; margin-top:16px;">
        <div style="color:#06B6D4; font-weight:700; font-size:0.85rem; margin-bottom:8px;">
            Technology Stack</div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">
    """ + "".join([
        f'<span style="background:#1E293B; border:1px solid #334155; color:#F8FAFC; '
        f'padding:4px 12px; border-radius:20px; font-size:0.76rem; font-weight:600;">{t}</span>'
        for t in ["Python 3", "Pandas", "NumPy", "Matplotlib", "Scikit-learn",
                  "Random Forest", "Joblib", "Streamlit"]
    ]) + "</div></div>", unsafe_allow_html=True)
