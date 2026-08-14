import os
import sys
import json
import traceback
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory

import matplotlib
matplotlib.use('Agg')

from src.data_preprocessing import load_raw_data, get_dataset_info
from src.exploratory_analysis import compute_eda_statistics, generate_visualizations
from src.train_model import train_and_save_model, MODEL_PATH
from src.evaluate_model import evaluate_performance
from src.prediction import FraudPredictor

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
        # 1. Load dataset
        data_file = 'data/credit_card_fraud_dataset.csv'
        if not os.path.exists(data_file) and os.path.exists('credit_card_fraud_dataset.csv'):
            data_file = 'credit_card_fraud_dataset.csv'

        print(f"[+] Loading dataset from {data_file}...", flush=True)
        df_raw = load_raw_data(data_file)
        dataset_info = get_dataset_info(df_raw)
        eda_stats = compute_eda_statistics(df_raw)
        print(f"[+] Dataset loaded successfully: {len(df_raw)} records.", flush=True)

        # 2. Generate Matplotlib SOC Visualizations
        print("[+] Generating Matplotlib Visualizations...", flush=True)
        os.makedirs('outputs', exist_ok=True)
        generate_visualizations(df_raw, output_dir='outputs')

        # 3. Train or load machine learning model
        if not os.path.exists(MODEL_PATH):
            print("[+] Model file missing. Training Random Forest model...", flush=True)
            model_payload = train_and_save_model(data_file, MODEL_PATH)
        else:
            print("[+] Loading existing Random Forest model artifact...", flush=True)
            import joblib
            model_payload = joblib.load(MODEL_PATH)

        # 4. Evaluate performance metrics
        print("[+] Evaluating model metrics...", flush=True)
        metrics = evaluate_performance(model_payload, output_dir='outputs')

        # 5. Initialize Predictor Engine
        print("[+] Initializing FraudPredictor engine...", flush=True)
        predictor = FraudPredictor(model_path=MODEL_PATH)

        # 6. Generate batch samples
        fraud_samples = df_raw[df_raw['IsFraud'] == 1].head(10)
        genuine_samples = df_raw[df_raw['IsFraud'] == 0].head(15)
        sample_df = pd.concat([fraud_samples, genuine_samples]).sample(frac=1, random_state=42)
        batch_samples = predictor.predict_batch(sample_df)

        print("[+] Initialization Complete! SOC Engine ready.", flush=True)
    except Exception as e:
        init_error = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[!] CRITICAL INITIALIZATION ERROR:\n{init_error}", file=sys.stderr, flush=True)

# Run initialization at module import time
initialize_system()

@app.route('/')
def index():
    if init_error and (eda_stats is None or metrics is None):
        return f"<h2>System Initialization Error</h2><pre>{init_error}</pre>", 500
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
        amount = float(data.get('amount', 0))
        merchant_id = float(data.get('merchant_id', 0))
        transaction_type = str(data.get('transaction_type', 'purchase'))
        location = str(data.get('location', 'New York'))
        hour = int(data.get('hour', 14))

        result = predictor.predict_single(amount, merchant_id, transaction_type, location, hour)
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
