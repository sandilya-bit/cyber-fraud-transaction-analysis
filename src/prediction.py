import os
import joblib
import pandas as pd
import numpy as np
from src.data_preprocessing import TRANSACTION_TYPES, LOCATIONS

MODEL_PATH = 'models/random_forest_model.pkl'

def get_risk_level(probability_pct):
    """
    Risk Classification Thresholds:
    0% – 30%: LOW RISK (#10B981)
    30% – 70%: MEDIUM RISK (#F59E0B)
    70% – 100%: HIGH RISK (#EF4444)
    """
    if probability_pct < 30.0:
        return 'LOW', '#10B981'
    elif probability_pct < 70.0:
        return 'MEDIUM', '#F59E0B'
    else:
        return 'HIGH', '#EF4444'

class FraudPredictor:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.model_payload = None
        self.model = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model_payload = joblib.load(self.model_path)
            self.model = self.model_payload['model']
            self.feature_names = self.model_payload['feature_names']
        else:
            self.model_payload = None
            self.model = None
            self.feature_names = [
                'Amount', 'MerchantID', 'TransactionType_Code', 'Location_Code',
                'Hour', 'DayOfWeek', 'IsNight', 'AmountToAvgRatio', 'HighAmountFlag'
            ]

    def _calibrate_probability(self, raw_prob):
        """
        Calibrate raw model probability (base rate ~1%) to a 0-100% Risk Probability score.
        This provides intuitive risk scaling for security analysts.
        """
        # Linear scaling up to max model probability (~0.50) to span 0-100%
        calibrated = min(1.0, raw_prob / 0.45)
        return float(calibrated)

    def predict_single(self, amount, merchant_id, transaction_type, location, hour=14, day_of_week=2):
        """Predict fraud probability and risk level for a single transaction input."""
        if self.model is None:
            self.load_model()
            if self.model is None:
                raise RuntimeError("Model is not trained yet. Please run training first.")

        type_map = {t: i for i, t in enumerate(TRANSACTION_TYPES)}
        loc_map = {l: i for i, l in enumerate(LOCATIONS)}

        type_code = type_map.get(str(transaction_type).lower(), 0)
        loc_code = loc_map.get(str(location), 0)
        is_night = 1 if (hour >= 22 or hour < 6) else 0

        amt = float(amount)
        input_dict = {
            'Amount': amt,
            'MerchantID': float(merchant_id),
            'TransactionType_Code': int(type_code),
            'Location_Code': int(loc_code),
            'Hour': int(hour),
            'DayOfWeek': int(day_of_week),
            'IsNight': int(is_night),
            'AmountToAvgRatio': amt / 1500.0,
            'HighAmountFlag': 1 if amt > 3000.0 else 0
        }

        input_df = pd.DataFrame([input_dict])[self.feature_names]
        
        probabilities = self.model.predict_proba(input_df)[0]
        raw_fraud_prob = float(probabilities[1])
        
        calibrated_prob = self._calibrate_probability(raw_fraud_prob)
        prob_percent = round(calibrated_prob * 100.0, 2)
        
        prediction_label = "FRAUDULENT" if prob_percent >= 50.0 else "GENUINE"
        risk_level, color_code = get_risk_level(prob_percent)

        return {
            'prediction': prediction_label,
            'fraud_probability': prob_percent,
            'genuine_probability': round(100.0 - prob_percent, 2),
            'risk_level': risk_level,
            'color_code': color_code,
            'input_data': {
                'amount': amount,
                'merchant_id': merchant_id,
                'transaction_type': transaction_type,
                'location': location,
                'hour': hour
            }
        }

    def predict_batch(self, df_sample):
        """Perform predictions on a pandas DataFrame of transactions."""
        if self.model is None:
            self.load_model()

        type_map = {t: i for i, t in enumerate(TRANSACTION_TYPES)}
        loc_map = {l: i for i, l in enumerate(LOCATIONS)}

        results = []
        for idx, row in df_sample.iterrows():
            tx_id = row.get('TransactionID', str(idx + 1))
            amt = float(row.get('Amount', 0.0))
            m_id = float(row.get('MerchantID', 0))
            tx_type = str(row.get('TransactionType', 'purchase'))
            loc = str(row.get('Location', 'New York'))
            
            tx_date = row.get('TransactionDate', '')
            hour = 14
            day_of_week = 2
            if tx_date:
                try:
                    dt = pd.to_datetime(tx_date)
                    hour = dt.hour
                    day_of_week = dt.dayofweek
                except Exception:
                    pass

            type_code = type_map.get(tx_type.lower(), 0)
            loc_code = loc_map.get(loc, 0)
            is_night = 1 if (hour >= 22 or hour < 6) else 0

            input_dict = {
                'Amount': amt,
                'MerchantID': m_id,
                'TransactionType_Code': type_code,
                'Location_Code': loc_code,
                'Hour': hour,
                'DayOfWeek': day_of_week,
                'IsNight': is_night,
                'AmountToAvgRatio': amt / 1500.0,
                'HighAmountFlag': 1 if amt > 3000.0 else 0
            }
            
            input_df = pd.DataFrame([input_dict])[self.feature_names]
            probabilities = self.model.predict_proba(input_df)[0]
            raw_fraud_prob = float(probabilities[1])
            
            calibrated_prob = self._calibrate_probability(raw_fraud_prob)
            prob_percent = round(calibrated_prob * 100.0, 2)
            
            prediction_label = "FRAUDULENT" if prob_percent >= 50.0 else "GENUINE"
            risk_level, color_code = get_risk_level(prob_percent)

            results.append({
                'transaction_id': tx_id,
                'amount': f"${amt:,.2f}",
                'merchant_id': int(m_id),
                'transaction_type': tx_type,
                'location': loc,
                'actual_status': 'FRAUD' if int(row.get('IsFraud', 0)) == 1 else 'GENUINE',
                'prediction': prediction_label,
                'fraud_probability': prob_percent,
                'risk_level': risk_level,
                'color_code': color_code
            })

        return results
