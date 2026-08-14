# CYBER FRAUD DATA TRANSACTION ANALYSIS AND DETECTION SYSTEM

### **Transaction Intelligence • Fraud Detection • Risk Analysis**

A complete, production-ready, functional **Cyber Fraud Data Transaction Analysis and Detection System** designed for BTech/CSE college project presentations, seminars, demonstrations, and viva voce evaluation. 

This project integrates Data Preprocessing, Exploratory Data Analysis (EDA), Data Visualization, Machine Learning (Random Forest Classifier), Model Serialization, and a Security Operations Center (SOC) style dashboard interface.

---

## 📌 1. INTRODUCTION

With the rapid expansion of electronic commerce, digital banking, and online payment gateways, cyber financial fraud has emerged as a major security challenge globally. Fraudulent transactions result in billions of dollars in losses annually. Traditional rule-based fraud detection mechanisms often fail against complex, evolving fraud tactics. 

This project implements an intelligent, data-driven cyber fraud detection engine that leverages **Random Forest Machine Learning** to analyze transaction behaviors, detect anomalies, calculate fraud probability, and assign actionable risk classifications in real time.

---

## 🎯 2. PROBLEM STATEMENT

Detecting fraud within high-volume financial transaction streams is difficult due to:
1. **Extreme Class Imbalance**: Fraudulent transactions represent a tiny fraction (typically ~1%) of overall transaction volume.
2. **Dynamic Fraud Patterns**: Fraudsters continuously change transaction locations, amounts, and timing to evade static detection rules.
3. **False Alarm Overhead**: Overly strict security triggers block genuine users (high false positives), causing operational friction and customer dissatisfaction.

A machine learning solution must achieve **high recall** (detecting nearly all fraudulent attempts) while preserving **high precision** (minimizing false alarms).

---

## 🚀 3. PROJECT OBJECTIVES

* Load and preprocess the actual dataset (`credit_card_fraud_dataset.csv`).
* Detect and handle missing values, duplicates, and feature data types.
* Perform detailed exploratory analysis (amounts, timing, frequencies, merchant patterns).
* Generate dark-mode SOC-styled visualizations using **Matplotlib**.
* Train a **Random Forest Classifier** with balanced class weights.
* Evaluate performance metrics (Accuracy, Precision, Recall, F1-score, Confusion Matrix).
* Provide a web-based **Transaction Risk Analyzer** interface.
* Calculate exact **Fraud Probability** (0.0% – 100.0%).
* Categorize transaction risk into **LOW (0-30%)**, **MEDIUM (30-70%)**, and **HIGH (70-100%)**.
* Enable multi-transaction batch analysis with interactive filtering.

---

## 🛠️ 4. TECHNOLOGY STACK

* **Programming Language**: Python 3
* **Data Processing**: Pandas, NumPy
* **Data Visualization**: Matplotlib
* **Machine Learning Engine**: Scikit-learn (RandomForestClassifier)
* **Model Storage**: Joblib
* **Web Framework & API**: Flask
* **Frontend Dashboard**: HTML5, Vanilla CSS3 (Custom SOC Dark Theme), JavaScript (Fetch API)

---

## 🔄 5. MACHINE LEARNING WORKFLOW

```text
               CREDIT CARD TRANSACTION DATASET
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
           (100 estimators, balanced class weights)
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

## 🎨 6. DESIGN SYSTEM & COLOR PALETTE

The dashboard uses a Security Operations Center (SOC) dark cybersecurity theme:

* **Primary Background**: `#0B1120` (Deep Navy)
* **Card Surface**: `#111827` (Dark Slate)
* **Secondary Surface**: `#1E293B`
* **Analytics Accent**: `#06B6D4` (Cyan)
* **Fraudulent Alert**: `#EF4444` (Red)
* **Genuine / Safe**: `#10B981` (Emerald Green)
* **Warning / Medium**: `#F59E0B` (Amber)
* **Text Primary**: `#F8FAFC`
* **Text Secondary**: `#94A3B8`
* **Borders**: `#334155`

---

## 📁 7. PROJECT STRUCTURE

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
│   ├── correlation.png
│   └── confusion_matrix.png
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
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
├── main.py
├── requirements.txt
└── README.md
```

---

## 🎓 8. VIVA VOCE QUESTIONS & ANSWERS

### Q1: What is the Cyber Fraud Transaction Analysis System?
**Answer**: It is an end-to-end cybersecurity analytics platform that processes financial transaction data and applies machine learning (Random Forest) to detect fraudulent activity, calculate risk probability, and present actionable insights via an interactive dashboard.

### Q2: Why is Random Forest preferred over simple algorithms like Logistic Regression?
**Answer**: Financial transaction data contains complex non-linear feature interactions (e.g., combinations of unusual late-night hours, high refund amounts, and specific merchant IDs). Random Forest combines decision trees into an ensemble, capturing these non-linearities while reducing variance and preventing overfitting.

### Q3: Why is class weighting (`class_weight="balanced"`) necessary?
**Answer**: Fraud datasets are severely imbalanced (usually ~1% fraud, 99% genuine). Without balanced class weighting, standard classifiers tend to predict everything as genuine to maximize accuracy while failing to detect actual fraud.

### Q4: What is the difference between Precision and Recall?
**Answer**: 
* **Recall**: Measures the percentage of actual fraud cases caught by the model (\(\frac{TP}{TP + FN}\)). Missing a fraud leads to monetary loss.
* **Precision**: Measures the accuracy of positive fraud flags (\(\frac{TP}{TP + FP}\)). High precision prevents false alarms for legitimate customers.

### Q5: How is Risk Level determined?
**Answer**: Risk level is derived directly from the model's output class probability:
* **0.0% – 30.0%**: LOW RISK (`#10B981` Green - Safe Transaction)
* **30.0% – 70.0%**: MEDIUM RISK (`#F59E0B` Amber - Warning / Secondary Verification Required)
* **70.0% – 100.0%**: HIGH RISK (`#EF4444` Red - Immediate Fraud Alert)

---

## 🏃 9. HOW TO RUN THE APPLICATION

### Prerequisites
Make sure Python 3.9+ is installed on your system.

### Step 1: Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### Step 2: Launch Flask SOC Engine
```bash
py main.py
```

### Step 3: Open Dashboard in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```
