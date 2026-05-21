import joblib
import numpy as np
from app import extract_features

# Load SVM Model
svm_model = joblib.load('models/svm/svm_model.pkl')
svm_scaler = joblib.load('models/svm/scaler.pkl')
svm_feature_names = joblib.load('models/svm/feature_names.pkl')

# Load XGBoost Model
xgb_model = joblib.load('models/xgboost/xgb_model.pkl')
xgb_scaler = joblib.load('models/xgboost/xgb_scaler.pkl')
xgb_selector = joblib.load('models/xgboost/xgb_selector.pkl')
all_features = joblib.load('models/xgboost/all_features.pkl')

urls_to_test = [
    # Safe URLs
    ("https://www.google.com/", "legitimate"),
    ("https://github.com/", "legitimate"),
    ("https://www.wikipedia.org/", "legitimate"),
    ("http://www.youtube.com/watch?v=dQw4w9WgXcQ", "legitimate"),
    # Phishing / Suspicious URLs (simulated real-world)
    ("http://login-secure-paypal.com-update.info/signin", "phishing"),
    ("https://www.netflix-account-verify.tk/login.php", "phishing"),
    ("http://192.168.1.1/admin/login.php", "phishing"), # IP instead of domain
    ("http://bit.ly/2uA9z2x", "phishing"), # Shortener
]

print(f"{'URL':<50} | {'Actual':<12} | {'SVM':<10} | {'XGBoost':<10}")
print("-" * 90)

svm_correct = 0
xgb_correct = 0

for url, actual in urls_to_test:
    # Extract features for both (app.py now extracts 87 correctly)
    feature_vector_87, features_dict = extract_features(url)
    
    # 1. SVM Prediction (uses 56 features)
    svm_vector = [features_dict.get(f, 0) for f in svm_feature_names]
    svm_input = np.array(svm_vector).reshape(1, -1)
    try:
        svm_scaled = svm_scaler.transform(svm_input)
        svm_pred = svm_model.predict(svm_scaled)[0]
        svm_label = 'phishing' if svm_pred == 1 else 'legitimate'
    except Exception as e:
        svm_label = "ERROR"

    # 2. XGBoost Prediction (uses 87 -> 43 features)
    xgb_input = np.array(feature_vector_87).reshape(1, -1)
    try:
        xgb_scaled = xgb_scaler.transform(xgb_input)
        xgb_selected = xgb_selector.transform(xgb_scaled)
        xgb_pred = xgb_model.predict(xgb_selected)[0]
        xgb_label = 'phishing' if xgb_pred == 1 else 'legitimate'
    except Exception as e:
        xgb_label = "ERROR"
        
    print(f"{url[:48]:<50} | {actual:<12} | {svm_label:<10} | {xgb_label:<10}")
    
    if svm_label == actual: svm_correct += 1
    if xgb_label == actual: xgb_correct += 1

print("-" * 90)
print(f"SVM Accuracy on Live Test: {svm_correct}/{len(urls_to_test)}")
print(f"XGBoost Accuracy on Live Test: {xgb_correct}/{len(urls_to_test)}")
