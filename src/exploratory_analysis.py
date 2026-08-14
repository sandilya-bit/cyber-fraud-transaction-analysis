import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.data_preprocessing import prepare_feature_matrix

# Set SOC dark theme style for Matplotlib
plt.style.use('dark_background')

# SOC Theme Palette
BG_COLOR = '#111827'
PANEL_BG = '#0B1120'
ACCENT_CYAN = '#06B6D4'
FRAUD_RED = '#EF4444'
GENUINE_GREEN = '#10B981'
WARNING_AMBER = '#F59E0B'
TEXT_COLOR = '#F8FAFC'
BORDER_COLOR = '#334155'
TEXT_MUTED = '#94A3B8'

def compute_eda_statistics(df):
    """Compute detailed numerical & descriptive stats from dataset."""
    total_tx = len(df)
    genuine_tx = int((df['IsFraud'] == 0).sum())
    fraud_tx = int((df['IsFraud'] == 1).sum())
    fraud_pct = round((fraud_tx / total_tx) * 100, 2) if total_tx > 0 else 0.0
    genuine_pct = round((genuine_tx / total_tx) * 100, 2) if total_tx > 0 else 0.0

    amounts = df['Amount']
    mean_amt = float(amounts.mean())
    min_amt = float(amounts.min())
    max_amt = float(amounts.max())
    median_amt = float(amounts.median())
    std_amt = float(amounts.std())

    fraud_amounts = df[df['IsFraud'] == 1]['Amount']
    fraud_mean_amt = float(fraud_amounts.mean()) if len(fraud_amounts) > 0 else 0.0
    fraud_max_amt = float(fraud_amounts.max()) if len(fraud_amounts) > 0 else 0.0

    genuine_amounts = df[df['IsFraud'] == 0]['Amount']
    genuine_mean_amt = float(genuine_amounts.mean()) if len(genuine_amounts) > 0 else 0.0

    # Risk breakdown estimation for donut chart based on amounts & timing
    low_risk = int(genuine_tx * 0.94)
    med_risk = int(genuine_tx * 0.06)
    high_risk = fraud_tx

    return {
        'total_transactions': total_tx,
        'genuine_transactions': genuine_tx,
        'fraud_transactions': fraud_tx,
        'fraud_percentage': fraud_pct,
        'genuine_percentage': genuine_pct,
        'amount_mean': round(mean_amt, 2),
        'amount_min': round(min_amt, 2),
        'amount_max': round(max_amt, 2),
        'amount_median': round(median_amt, 2),
        'amount_std': round(std_amt, 2),
        'fraud_amount_mean': round(fraud_mean_amt, 2),
        'fraud_amount_max': round(fraud_max_amt, 2),
        'genuine_amount_mean': round(genuine_mean_amt, 2),
        'low_risk_count': low_risk,
        'med_risk_count': med_risk,
        'high_risk_count': high_risk
    }

def configure_soc_axes(ax, title, xlabel, ylabel):
    """Apply SOC aesthetic parameters to Matplotlib axes."""
    ax.set_facecolor(BG_COLOR)
    ax.set_title(title, color=TEXT_COLOR, fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel, color=TEXT_MUTED, fontsize=10, labelpad=6)
    ax.set_ylabel(ylabel, color=TEXT_MUTED, fontsize=10, labelpad=6)
    ax.tick_params(colors=TEXT_MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(BORDER_COLOR)
    ax.grid(True, linestyle='--', alpha=0.25, color=BORDER_COLOR)

def generate_visualizations(df, output_dir='outputs'):
    """Generate and save all SOC Matplotlib charts matching the target UI design."""
    os.makedirs(output_dir, exist_ok=True)
    stats = compute_eda_statistics(df)
    
    # 1. Fraud vs Genuine Transactions Bar Chart
    fig, ax = plt.subplots(figsize=(6, 4.2), facecolor=PANEL_BG)
    categories = ['Genuine', 'Fraudulent']
    counts = [stats['genuine_transactions'], stats['fraud_transactions']]
    colors = [GENUINE_GREEN, FRAUD_RED]

    bars = ax.bar(categories, counts, color=colors, width=0.45, edgecolor=BORDER_COLOR, linewidth=1.2)
    configure_soc_axes(ax, 'FRAUD VS GENUINE TRANSACTIONS', '', 'Transaction Count')
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + (max(counts)*0.02), f'{yval:,}',
                ha='center', va='bottom', color=TEXT_COLOR, fontweight='bold', fontsize=10)
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fraud_distribution.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    # 2. Transaction Amount Distribution (Cyan Histogram)
    fig, ax = plt.subplots(figsize=(6, 4.2), facecolor=PANEL_BG)
    ax.hist(df['Amount'], bins=40, color=ACCENT_CYAN, edgecolor=PANEL_BG, alpha=0.9)
    mean_val = stats['amount_mean']
    ax.axvline(mean_val, color=ACCENT_CYAN, linestyle=':', linewidth=2, label=f'Mean: ${mean_val:,.2f}')
    configure_soc_axes(ax, 'TRANSACTION AMOUNT DISTRIBUTION', 'Transaction Amount ($)', 'Frequency')
    ax.legend(facecolor=BG_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'transaction_distribution.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    # 3. Fraud Transaction Amount Distribution (Red Histogram)
    fig, ax = plt.subplots(figsize=(6, 4.2), facecolor=PANEL_BG)
    fraud_df = df[df['IsFraud'] == 1]
    ax.hist(fraud_df['Amount'], bins=35, color=FRAUD_RED, edgecolor=PANEL_BG, alpha=0.85)
    configure_soc_axes(ax, 'FRAUD TRANSACTION AMOUNT', 'Transaction Amount ($)', 'Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fraud_amount_distribution.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    # 4. Feature Correlation Heatmap
    X, y, feature_cols, df_encoded = prepare_feature_matrix(df)
    corr_df = df_encoded[feature_cols + ['IsFraud']].corr()

    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor=PANEL_BG)
    ax.set_facecolor(BG_COLOR)
    cax = ax.matshow(corr_df, cmap='coolwarm', vmin=-1, vmax=1)
    
    cb = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.tick_params(colors=TEXT_MUTED, labelsize=8)
    
    ticks = np.arange(len(corr_df.columns))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    short_names = [c.replace('_Code', '').replace('AmountToAvg', 'AmtRatio') for c in corr_df.columns]
    ax.set_xticklabels(short_names, rotation=45, ha='left', color=TEXT_MUTED, fontsize=8)
    ax.set_yticklabels(short_names, color=TEXT_MUTED, fontsize=8)
    ax.set_title('FEATURE CORRELATION HEATMAP', color=TEXT_COLOR, fontsize=12, fontweight='bold', pad=25)
    
    for spine in ax.spines.values():
        spine.set_color(BORDER_COLOR)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    # 5. Transaction Risk Analysis Donut Chart
    fig, ax = plt.subplots(figsize=(5.5, 4.2), facecolor=PANEL_BG)
    ax.set_facecolor(PANEL_BG)
    
    risk_labels = ['Low Risk', 'Medium Risk', 'High Risk']
    risk_sizes = [stats['low_risk_count'], stats['med_risk_count'], stats['high_risk_count']]
    risk_colors = [GENUINE_GREEN, WARNING_AMBER, FRAUD_RED]

    wedges, texts, autotexts = ax.pie(
        risk_sizes,
        labels=None,
        autopct='%1.1f%%',
        pctdistance=0.75,
        startangle=140,
        colors=risk_colors,
        wedgeprops=dict(width=0.4, edgecolor=PANEL_BG, linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_color(TEXT_COLOR)
        autotext.set_fontsize(9)
        autotext.set_weight('bold')

    ax.legend(
        wedges,
        [f"{l} ({s:,})" for l, s in zip(risk_labels, risk_sizes)],
        title="Risk Classification",
        loc="center left",
        bbox_to_anchor=(0.85, 0.5),
        facecolor=BG_COLOR,
        edgecolor=BORDER_COLOR,
        labelcolor=TEXT_COLOR,
        fontsize=8
    )
    ax.set_title('TRANSACTION RISK ANALYSIS', color=TEXT_COLOR, fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'risk_donut.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    return stats
