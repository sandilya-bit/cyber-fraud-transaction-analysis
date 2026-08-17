import os
import sys
import traceback

# CRITICAL: Set matplotlib to non-interactive Agg backend BEFORE any other imports
# This must be the very first matplotlib-related line in the entire process
os.environ['MPLBACKEND'] = 'Agg'

import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

# Global cached variables
df_raw = None
dataset_info = None
eda_stats = None
model_payload = None
metrics = None
predictor = None
batch_samples = []
init_error = None

def initialize_system():
    global df_raw, dataset_info, eda_stats, model_payload, metrics, predictor, batch_samples, init_error
    if df_raw is not None:
        return

    print("[+] Initializing Cyber Fraud Detection Engine...", flush=True)
    try:
        from src.data_preprocessing import load_raw_data, get_dataset_info
        from src.exploratory_analysis import compute_eda_statistics, generate_visualizations
        from src.train_model import train_and_save_model, MODEL_PATH
        from src.evaluate_model import evaluate_performance
        from src.prediction import FraudPredictor
        import joblib

        # 1. Find and load dataset
        data_file = 'data/credit_card_fraud_dataset.csv'
        if not os.path.exists(data_file):
            if os.path.exists('credit_card_fraud_dataset.csv'):
                data_file = 'credit_card_fraud_dataset.csv'
            else:
                raise FileNotFoundError(
                    f"Dataset not found. Searched: 'data/credit_card_fraud_dataset.csv' and 'credit_card_fraud_dataset.csv'. "
                    f"CWD={os.getcwd()} Contents={os.listdir('.')}"
                )

        print(f"[+] Loading dataset from: {data_file}", flush=True)
        df_raw = load_raw_data(data_file)
        dataset_info = get_dataset_info(df_raw)
        eda_stats = compute_eda_statistics(df_raw)
        print(f"[+] Dataset loaded: {len(df_raw)} rows.", flush=True)

        # 2. Generate Matplotlib visualizations
        print("[+] Generating visualizations...", flush=True)
        os.makedirs('outputs', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        generate_visualizations(df_raw, output_dir='outputs')
        print("[+] Visualizations generated.", flush=True)

        # 3. Load or train model
        MODEL_PKL = 'models/random_forest_model.pkl'
        if os.path.exists(MODEL_PKL):
            print("[+] Loading existing model...", flush=True)
            model_payload = joblib.load(MODEL_PKL)
        else:
            print("[+] No model found — training now...", flush=True)
            model_payload = train_and_save_model(data_file, MODEL_PKL)

        # 4. Evaluate
        print("[+] Evaluating model metrics...", flush=True)
        metrics = evaluate_performance(model_payload, output_dir='outputs')
        print(f"[+] Metrics: Accuracy={metrics['accuracy']}%", flush=True)

        # 5. Predictor
        predictor = FraudPredictor(model_path=MODEL_PKL)

        # 6. Batch samples
        fraud_samples = df_raw[df_raw['IsFraud'] == 1].head(10)
        genuine_samples = df_raw[df_raw['IsFraud'] == 0].head(15)
        sample_df = pd.concat([fraud_samples, genuine_samples]).sample(frac=1, random_state=42)
        batch_samples = predictor.predict_batch(sample_df)

        print("[+] Initialization Complete! SOC Engine ready.", flush=True)

    except Exception as e:
        init_error = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
        print(f"[!] INITIALIZATION FAILED:\n{init_error}", file=sys.stderr, flush=True)


# Initialize at module import (required for Gunicorn / Render)
initialize_system()


@app.route('/')
def index():
    if init_error:
        # Show the actual error for debugging — NOT a 500 so Render shows it
        return (
            f"<html><head><title>Initialization Error</title></head><body style='background:#0B1120;color:#F8FAFC;font-family:monospace;padding:30px;'>"
            f"<h2 style='color:#EF4444;'>System Initialization Error</h2>"
            f"<p style='color:#94A3B8;'>The application failed to start. Check the Render logs for details.</p>"
            f"<pre style='background:#111827;border:1px solid #334155;padding:20px;color:#F8FAFC;overflow:auto;'>{init_error}</pre>"
            f"</body></html>"
        ), 200  # Return 200 so the error HTML actually renders

    if eda_stats is None or metrics is None:
        return (
            "<html><body style='background:#0B1120;color:#F8FAFC;font-family:monospace;padding:30px;'>"
            "<h2 style='color:#F59E0B;'>System still initializing... Please refresh in a few seconds.</h2>"
            "</body></html>"
        ), 200

    return render_template(
        'index.html',
        stats=eda_stats,
        dataset_info=dataset_info,
        metrics=metrics,
        batch_samples=batch_samples
    )


@app.route('/outputs/<path:filename>')
def serve_outputs(filename):
    return send_from_directory('outputs', filename)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json()
        result = predictor.predict_single(
            float(data.get('amount', 0)),
            float(data.get('merchant_id', 0)),
            str(data.get('transaction_type', 'purchase')),
            str(data.get('location', 'New York')),
            int(data.get('hour', 14))
        )
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/batch_predict', methods=['GET'])
def api_batch_predict():
    return jsonify({'status': 'success', 'batch': batch_samples})


@app.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify({'status': 'success', 'stats': eda_stats, 'dataset_info': dataset_info})


@app.route('/api/metrics', methods=['GET'])
def api_metrics():
    return jsonify({'status': 'success', 'metrics': metrics})


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok' if init_error is None else 'error',
        'initialized': df_raw is not None,
        'error': init_error
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
