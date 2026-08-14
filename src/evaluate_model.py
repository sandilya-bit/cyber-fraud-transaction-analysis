import os
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

BG_COLOR = '#111827'
PANEL_BG = '#0B1120'
BORDER_COLOR = '#334155'
TEXT_COLOR = '#F8FAFC'
TEXT_MUTED = '#94A3B8'
CYAN = '#06B6D4'
FRAUD_RED = '#EF4444'
GENUINE_GREEN = '#10B981'

def evaluate_performance(model_payload, output_dir='outputs'):
    """Compute sklearn metrics and draw confusion matrix & accuracy gauge visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    
    rf_model = model_payload['model']
    X_test = model_payload['X_test']
    y_test = model_payload['y_test']

    y_pred = rf_model.predict(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred)

    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # 1. Confusion Matrix Plot
    fig, ax = plt.subplots(figsize=(5.5, 4.2), facecolor=PANEL_BG)
    ax.set_facecolor(BG_COLOR)
    
    cax = ax.matshow(cm, cmap='Blues', alpha=0.85)
    
    labels = [
        [f"TN: {tn:,}", f"FP: {fp:,}"],
        [f"FN: {fn:,}", f"TP: {tp:,}"]
    ]

    for i in range(2):
        for j in range(2):
            color = FRAUD_RED if (i == 1 and j == 0) else (GENUINE_GREEN if (i == 1 and j == 1) else TEXT_COLOR)
            ax.text(j, i, labels[i][j], ha='center', va='center',
                    color=color, fontsize=11, fontweight='bold')

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Pred: Genuine', 'Pred: Fraud'], color=TEXT_MUTED, fontsize=9)
    ax.set_yticklabels(['Actual: Genuine', 'Actual: Fraud'], color=TEXT_MUTED, fontsize=9)
    ax.tick_params(colors=TEXT_MUTED)
    ax.set_title('CONFUSION MATRIX', color=TEXT_COLOR, fontsize=12, fontweight='bold', pad=20)

    for spine in ax.spines.values():
        spine.set_color(BORDER_COLOR)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    # 2. Model Accuracy Ring Gauge Plot
    fig, ax = plt.subplots(figsize=(4.5, 4.2), facecolor=PANEL_BG)
    ax.set_facecolor(PANEL_BG)
    
    acc_pct = round(acc * 100, 2)
    sizes = [acc_pct, 100.0 - acc_pct]
    colors = [GENUINE_GREEN, BG_COLOR]
    
    wedges, _ = ax.pie(
        sizes,
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.3, edgecolor=BORDER_COLOR, linewidth=1.5)
    )
    
    ax.text(0, 0, f"{acc_pct}%\nAccuracy", ha='center', va='center',
            color=TEXT_COLOR, fontsize=13, fontweight='bold')
            
    ax.set_title('MODEL ACCURACY', color=TEXT_COLOR, fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'accuracy_gauge.png'), dpi=160, facecolor=PANEL_BG)
    plt.close()

    explanation = (
        "In financial cyber fraud detection, Recall is paramount because missing a fraudulent transaction "
        "(False Negative) direct incurs financial loss and security breach. Precision measures out of all transactions "
        "flagged as fraud, how many were genuine threats, minimizing false alarms and friction for benign cardholders."
    )

    metrics_result = {
        'accuracy': round(acc * 100, 2),
        'precision': round(prec * 100, 2),
        'recall': round(rec * 100, 2),
        'f1_score': round(f1 * 100, 2),
        'confusion_matrix': {
            'tn': tn,
            'fp': fp,
            'fn': fn,
            'tp': tp
        },
        'explanation': explanation
    }

    return metrics_result
