import os
import pandas as pd
import numpy as np

# Feature encoding mappings for deterministic transformation
TRANSACTION_TYPES = ['purchase', 'refund', 'transfer', 'withdrawal']
LOCATIONS = [
    'San Antonio', 'New York', 'Los Angeles', 'Chicago', 'Houston',
    'Phoenix', 'Philadelphia', 'San Diego', 'Dallas', 'San Jose'
]

def load_raw_data(data_path='data/credit_card_fraud_dataset.csv'):
    """Load the credit card fraud dataset from CSV."""
    if not os.path.exists(data_path):
        if os.path.exists('credit_card_fraud_dataset.csv'):
            data_path = 'credit_card_fraud_dataset.csv'
        else:
            raise FileNotFoundError(f"Dataset file not found at path: {data_path}")
    df = pd.read_csv(data_path)
    return df

def get_dataset_info(df):
    """Calculate key statistics about the raw dataset."""
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_values = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    
    target_counts = df['IsFraud'].value_counts().to_dict()
    genuine_count = int(target_counts.get(0, 0))
    fraud_count = int(target_counts.get(1, 0))
    fraud_percentage = round((fraud_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

    col_info = []
    for col in df.columns:
        col_info.append({
            'name': col,
            'dtype': str(df[col].dtype),
            'missing': int(df[col].isnull().sum())
        })

    return {
        'total_rows': total_rows,
        'total_cols': total_cols,
        'missing_values': missing_values,
        'duplicate_rows': duplicate_rows,
        'genuine_count': genuine_count,
        'fraud_count': fraud_count,
        'fraud_percentage': fraud_percentage,
        'target_variable': 'IsFraud',
        'columns': col_info
    }

def encode_categorical_features(df):
    """Encode TransactionType and Location into numerical features."""
    df_encoded = df.copy()

    # Convert TransactionDate to datetime if exists
    if 'TransactionDate' in df_encoded.columns:
        df_encoded['TransactionDate'] = pd.to_datetime(df_encoded['TransactionDate'], errors='coerce')
        df_encoded['Hour'] = df_encoded['TransactionDate'].dt.hour.fillna(12).astype(int)
        df_encoded['DayOfWeek'] = df_encoded['TransactionDate'].dt.dayofweek.fillna(0).astype(int)
        df_encoded['IsNight'] = df_encoded['Hour'].apply(lambda h: 1 if (h >= 22 or h < 6) else 0)
    else:
        df_encoded['Hour'] = 12
        df_encoded['DayOfWeek'] = 0
        df_encoded['IsNight'] = 0

    # Categorical encodings
    if 'TransactionType' in df_encoded.columns:
        type_mapping = {t: i for i, t in enumerate(TRANSACTION_TYPES)}
        df_encoded['TransactionType_Code'] = df_encoded['TransactionType'].str.lower().map(type_mapping).fillna(0).astype(int)

    if 'Location' in df_encoded.columns:
        loc_mapping = {l: i for i, l in enumerate(LOCATIONS)}
        df_encoded['Location_Code'] = df_encoded['Location'].map(loc_mapping).fillna(0).astype(int)

    # Derived Domain Features
    amount_mean = df_encoded['Amount'].mean() if len(df_encoded) > 0 else 1.0
    df_encoded['AmountToAvgRatio'] = df_encoded['Amount'] / (amount_mean + 1e-5)
    df_encoded['HighAmountFlag'] = (df_encoded['Amount'] > 3000.0).astype(int)

    return df_encoded

def prepare_feature_matrix(df):
    """
    Clean dataset and extract feature matrix X and target y.
    Returns X, y, and the processed DataFrame.
    """
    df_clean = df.drop_duplicates().copy()

    # Fill missing values if any
    if df_clean['Amount'].isnull().sum() > 0:
        df_clean['Amount'] = df_clean['Amount'].fillna(df_clean['Amount'].median())
    if df_clean['MerchantID'].isnull().sum() > 0:
        df_clean['MerchantID'] = df_clean['MerchantID'].fillna(-1)

    df_encoded = encode_categorical_features(df_clean)

    feature_cols = [
        'Amount', 'MerchantID', 'TransactionType_Code', 'Location_Code',
        'Hour', 'DayOfWeek', 'IsNight', 'AmountToAvgRatio', 'HighAmountFlag'
    ]
    
    # Ensure all feature columns exist
    for col in feature_cols:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    X = df_encoded[feature_cols].copy()
    y = df_encoded['IsFraud'].astype(int).copy()

    return X, y, feature_cols, df_encoded
