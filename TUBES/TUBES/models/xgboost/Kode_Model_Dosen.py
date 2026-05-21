"""
DETEKSI PHISHING WEBSITE - REKOMENDASI DOSEN
- XGBoost
- Train/Test Split (dibagi 2)
- Feature Selection (Chi-Square) diambil 43 fitur dari 87 (separuhnya)
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, chi2
from xgboost import XGBClassifier
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, confusion_matrix)

# ==============================================================
# 1. LOAD DATASET
# ==============================================================
print("=" * 60)
print("MODEL DOSEN - XGBoost + Chi-Square (43 Fitur) + Train/Test Split")
print("=" * 60)

df = pd.read_csv('dataset_phishing.csv')

# Semua fitur kecuali url dan status
X = df.drop(columns=['url', 'status'])
y = df['status']
all_feature_names = X.columns.tolist()

print(f"[INFO] Jumlah fitur awal : {X.shape[1]}")
print(f"[INFO] Jumlah data       : {X.shape[0]}")

# ==============================================================
# 2. PREPROCESSING
# ==============================================================
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"[INFO] Label encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# ==============================================================
# 3. SPLIT DATA (Langsung dibagi 2 / 50% Train, 50% Test)
# ==============================================================
print("\n" + "=" * 60)
print("SPLIT DATA (50% Train | 50% Test)")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.5, random_state=42, stratify=y_encoded)

print(f"[INFO] Train : {X_train.shape[0]} | Test : {X_test.shape[0]}")

# Menggunakan MinMaxScaler agar tidak ada nilai negatif untuk Chi-Square
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ==============================================================
# 4. FEATURE SELECTION (Chi-Square, k=43)
# ==============================================================
print("\n" + "=" * 60)
print("FEATURE SELECTION (Chi-Square K=43)")
print("=" * 60)

selector = SelectKBest(score_func=chi2, k=43)
X_train_selected = selector.fit_transform(X_train_scaled, y_train)
X_test_selected  = selector.transform(X_test_scaled)

selected_indices = selector.get_support(indices=True)
selected_features = [all_feature_names[i] for i in selected_indices]

print(f"[INFO] Jumlah fitur setelah seleksi : {X_train_selected.shape[1]}")
print(f"[INFO] Fitur terpilih: \n{selected_features}")

# ==============================================================
# 5. TRAINING XGBOOST
# ==============================================================
print("\n" + "=" * 60)
print("TRAINING MODEL XGBOOST")
print("=" * 60)

# Inisialisasi model XGBoost
xgb_model = XGBClassifier(
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=5, 
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

xgb_model.fit(X_train_selected, y_train)

# ==============================================================
# 6. EVALUASI MODEL
# ==============================================================
def evaluate(name, y_true, y_pred):
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec  = recall_score(y_true, y_pred)
    f1   = f1_score(y_true, y_pred)
    cm   = confusion_matrix(y_true, y_pred)
    print(f"\n--- {name} ---")
    print(f"  Accuracy  : {acc:.4f} ({acc*100:.2f}%)")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(f"  F1-Score  : {f1:.4f}")
    print(f"  Confusion Matrix:")
    print(f"    TP={cm[1][1]:<4}  FP={cm[0][1]}")
    print(f"    FN={cm[1][0]:<4}  TN={cm[0][0]}")
    return acc, prec, rec, f1

evaluate("DATA TRAIN", y_train, xgb_model.predict(X_train_selected))
evaluate("DATA TEST",  y_test,  xgb_model.predict(X_test_selected))

# ==============================================================
# 7. SIMPAN MODEL
# ==============================================================
joblib.dump(xgb_model, 'xgb_model.pkl')
joblib.dump(scaler,    'xgb_scaler.pkl')
joblib.dump(selector,  'xgb_selector.pkl')
joblib.dump(selected_features, 'xgb_features.pkl')
joblib.dump(all_feature_names, 'all_features.pkl')

print("\n[INFO] Model disimpan: xgb_model.pkl, xgb_scaler.pkl, xgb_selector.pkl, xgb_features.pkl, all_features.pkl")
