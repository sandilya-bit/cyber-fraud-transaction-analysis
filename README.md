# CYBER FRAUD DATA TRANSACTION ANALYSIS AND DETECTION SYSTEM

### **Transaction Intelligence • Fraud Detection • Risk Analysis**

A complete, production-ready, functional **Cyber Fraud Data Transaction Analysis and Detection System** designed for BTech/CSE college project presentations, seminars, demonstrations, and viva voce evaluation. 

This project integrates Data Preprocessing, Exploratory Data Analysis (EDA), Data Visualization, Machine Learning (Random Forest Classifier), Model Serialization, and a Security Operations Center (SOC) style dashboard interface with secure role-based authentication and real-time stream monitoring.

---

## 📌 1. INTRODUCTION

With the rapid expansion of electronic commerce, digital banking, and online payment gateways, cyber financial fraud has emerged as a major security challenge globally. Fraudulent transactions result in billions of dollars in losses annually. Traditional rule-based fraud detection mechanisms often fail against complex, evolving fraud tactics. 

This project implements an intelligent, data-driven cyber fraud detection engine that leverages **Random Forest Machine Learning** to analyze transaction behaviors across 100,000+ records, detect anomalies, calculate fraud probability, and assign actionable risk classifications in real time.

---

## 🎯 2. PROBLEM STATEMENT

Detecting fraud within high-volume financial transaction streams is difficult due to:
1. **Extreme Class Imbalance**: Fraudulent transactions represent a tiny fraction (typically ~1%) of overall transaction volume.
2. **Dynamic Fraud Patterns**: Fraudsters continuously change transaction locations, amounts, and timing to evade static detection rules.
3. **False Alarm Overhead**: Overly strict security triggers block genuine users (high false positives), causing operational friction and customer dissatisfaction.

A machine learning solution must achieve **high recall** (detecting nearly all fraudulent attempts) while preserving **high precision** (minimizing false alarms).

---

## 🚀 3. PROJECT OBJECTIVES & KEY FEATURES

* **Dataset Scale**: Analyzes over **100,000 transaction records** (`credit_card_fraud_dataset.csv`).
* **Authentication System**: SHA-256 encrypted multi-user role-based authentication (Admin, Fraud Analyst, Viewer).
* **Exploratory Data Analysis**: Deep descriptive and statistical summaries across transaction amounts, merchant IDs, locations, and timestamps.
* **Matplotlib Visualizations**: High-contrast, dark-mode SOC-styled visual charts (Distribution, Histograms, Heatmaps, Donut charts, Confusion Matrix).
* **Machine Learning**: Balanced **Random Forest Classifier** achieving calibrated probability outputs.
* **Transaction Risk Analyzer**: Interactive single-transaction scanner providing instant Risk Classification (**LOW**, **MEDIUM**, **HIGH**).
* **Live Transaction Stream Monitor (Unique Feature)**: Real-time radar scanning simulating live inbound transaction feeds.
* **Fraud Intelligence Report Generator (Unique Feature)**: Instant auto-generation of downloadable analytical reports (`.txt`).
* **Multi-Transaction Batch Analysis**: Filterable records table with instant prediction checks.

---

## 🔐 4. AUTHENTICATION CREDENTIALS

| Username | Password | Role | Access Level |
| :--- | :--- | :--- | :--- |
| `admin` | `admin@2024` | System Administrator | Full SOC Administrative Access |
| `analyst` | `fraud@123` | Fraud Analyst | Analytics, Scanning & Report Generation |
| `viewer` | `view@2024` | Report Viewer | Read-Only Analytical Access |

---

## 🛠️ 5. TECHNOLOGY STACK

* **Programming Language**: Python 3
* **Data Processing**: Pandas, NumPy
* **Data Visualization**: Matplotlib
* **Machine Learning Engine**: Scikit-learn (RandomForestClassifier)
* **Model Storage**: Joblib
* **Web Interfaces**: Streamlit (Cloud deployment) & Flask (Local API server)
* **Security & Auth**: SHA-256 Hashing, Session State Management

---

## 🔄 6. MACHINE LEARNING WORKFLOW

```text
               CREDIT CARD TRANSACTION DATASET (100,000 Rows)
                                     ↓
                             DATA PREPROCESSING
                       (Missing handling, Date features)
                                     ↓
                         EXPLORATORY DATA ANALYSIS (EDA)
                                     ↓
                         DATA VISUALIZATION GENERATION
                   (Fraud dist, Amount hist, Correlation matrix)
                                     ↓
                             TRAIN/TEST SPLIT
                        (80% Train, 20% Test, Stratified)
                                     ↓
                          RANDOM FOREST CLASSIFIER
                     (30 estimators, balanced class weights)
                                     ↓
                             MODEL EVALUATION
                   (Accuracy, Precision, Recall, Confusion Matrix)
                                     ↓
                        TRANSACTION RISK ANALYZER
                                     ↓
                             FRAUD PREDICTION
                                     ↓
                            FRAUD PROBABILITY %
                                     ↓
                       RISK CLASSIFICATION (LOW/MED/HIGH)
                                     ↓
                            SOC ALERT RESULT CARD
```

---

## 🎨 7. DESIGN SYSTEM & COLOR PALETTE

The dashboard uses a modern Security Operations Center (SOC) dark cybersecurity theme:

* **Primary Background**: `#020817` (Deep Midnight)
* **Card Surface**: `#0A1628` (Dark Slate Glass)
* **Secondary Surface**: `#0F1F38`
* **Analytics Accent**: `#06B6D4` (Cyan)
* **Fraudulent Alert**: `#EF4444` (Red)
* **Genuine / Safe**: `#10B981` (Emerald Green)
* **Warning / Medium**: `#F59E0B` (Amber)
* **Text Primary**: `#F8FAFC`
* **Text Secondary**: `#94A3B8`
* **Borders**: `rgba(51, 65, 85, 0.7)`

---

## 📁 8. PROJECT STRUCTURE

```text
cyber_fraud_detection/
│
├── data/
│   └── credit_card_fraud_dataset.csv
│
├── models/
│   └── random_forest_model.pkl
│
├── outputs/
│   ├── fraud_distribution.png
│   ├── transaction_distribution.png
│   ├── fraud_amount_distribution.png
│   ├── correlation.png
│   ├── risk_donut.png
│   ├── accuracy_gauge.png
│   └── confusion_matrix.png
│
├── static/
│   ├── css/style.css
│   └── js/script.js
│
├── templates/
│   └── index.html
│
├── src/
│   ├── data_preprocessing.py
│   ├── exploratory_analysis.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── prediction.py
│
├── streamlit_app.py        # Premium Streamlit Cloud App with Auth & Live Monitor
├── main.py                 # Flask server & REST API endpoints
├── Procfile                # Gunicorn cloud process configuration
├── requirements.txt        # Python dependency specifications
└── README.md
```

---

## 🏃 9. HOW TO RUN LOCALLY

### Prerequisites
Make sure Python 3.9+ is installed on your system.

### Step 1: Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### Step 2: Launch Streamlit SOC Dashboard
```bash
py -m streamlit run streamlit_app.py
```

### Step 3: Or Launch Flask Web Server
```bash
py main.py
```

---

## ☁️ 10. DEPLOYING TO STREAMLIT CLOUD

1. Go to [https://share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**.
3. Select repository: `sandilya-bit/cyber-fraud-transaction-analysis`
4. Set **Main file path**: `streamlit_app.py`
5. Click **Deploy!**

---

## 🎓 11. VIVA VOCE QUESTIONS & ANSWERS

### Q1: What is the Cyber Fraud Transaction Analysis System?
**Answer**: An end-to-end cybersecurity analytics platform that processes 100,000+ financial transaction records using a Random Forest ML model to detect fraud in real-time, calculate fraud probability, and categorize risk levels.

### Q2: Why is Random Forest preferred over simple algorithms like Logistic Regression?
**Answer**: Financial transactions contain complex non-linear relationships across transaction amounts, night-time hours, and merchant IDs. Random Forest uses an ensemble of decision trees, capturing these interactions while resisting overfitting.

### Q3: Why is class weighting (`class_weight="balanced"`) necessary?
**Answer**: Fraud datasets are severely imbalanced (~1% fraud). Without balanced weighting, classifiers predict everything as genuine to maximize accuracy while missing all actual frauds.

### Q4: What is the difference between Precision and Recall?
**Answer**: 
* **Recall**: Measures the fraction of actual fraud caught by the model (\(\frac{TP}{TP + FN}\)). Missing fraud results in financial loss.
* **Precision**: Measures how many transactions flagged as fraud were genuine threats (\(\frac{TP}{TP + FP}\)), minimizing friction for legitimate customers.

### Q5: How is Risk Level determined?
**Answer**:
* **0.0% – 30.0%**: **LOW RISK** (Green - Safe Transaction)
* **30.0% – 70.0%**: **MEDIUM RISK** (Amber - Secondary Verification Required)
* **70.0% – 100.0%**: **HIGH RISK** (Red - Immediate Fraud Alert)
