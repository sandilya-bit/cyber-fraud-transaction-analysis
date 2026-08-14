import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from src.data_preprocessing import load_raw_data, prepare_feature_matrix

MODEL_PATH = 'models/random_forest_model.pkl'

def train_and_save_model(data_path='data/credit_card_fraud_dataset.csv', model_path=MODEL_PATH):
    """Train lightweight, high-performance Random Forest model optimized for cloud memory constraints."""
    print("[+] Loading data for training...")
    df = load_raw_data(data_path)
    
    print("[+] Preprocessing features...")
    X, y, feature_cols, _ = prepare_feature_matrix(df)
    
    print("[+] Splitting dataset (80% Train, 20% Test, Stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("[+] Training lightweight RandomForestClassifier...")
    rf_model = RandomForestClassifier(
        n_estimators=30,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    model_payload = {
        'model': rf_model,
        'feature_names': feature_cols,
        'X_test': X_test,
        'y_test': y_test
    }
    
    joblib.dump(model_payload, model_path, compress=3)
    print(f"[+] Model successfully compressed and saved to {model_path}")
    return model_payload

if __name__ == '__main__':
    train_and_save_model()
