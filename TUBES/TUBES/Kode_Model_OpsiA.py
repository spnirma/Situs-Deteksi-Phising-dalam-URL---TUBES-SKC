"""
DETEKSI PHISHING WEBSITE - OPSI A
Hanya menggunakan fitur URL (56 fitur)
Tanpa fitur konten halaman web
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, classification_report,
                             confusion_matrix)

# ==============================================================
# 1. LOAD DATASET
# ==============================================================
print("=" * 60)
print("OPSI A - SVM HANYA FITUR URL (56 Fitur)")
print("=" * 60)

df = pd.read_csv('dataset_phishing.csv')

# Fitur URL saja (tidak termasuk fitur konten halaman)
URL_FEATURES = [
    'length_url', 'length_hostname', 'ip', 'nb_dots', 'nb_hyphens',
    'nb_at', 'nb_qm', 'nb_and', 'nb_or', 'nb_eq', 'nb_underscore',
    'nb_tilde', 'nb_percent', 'nb_slash', 'nb_star', 'nb_colon',
    'nb_comma', 'nb_semicolumn', 'nb_dollar', 'nb_space', 'nb_www',
    'nb_com', 'nb_dslash', 'http_in_path', 'https_token',
    'ratio_digits_url', 'ratio_digits_host', 'punycode', 'port',
    'tld_in_path', 'tld_in_subdomain', 'abnormal_subdomain',
    'nb_subdomains', 'prefix_suffix', 'random_domain',
    'shortening_service', 'path_extension', 'nb_redirection',
    'nb_external_redirection', 'length_words_raw', 'char_repeat',
    'shortest_words_raw', 'shortest_word_host', 'shortest_word_path',
    'longest_words_raw', 'longest_word_host', 'longest_word_path',
    'avg_words_raw', 'avg_word_host', 'avg_word_path', 'phish_hints',
    'domain_in_brand', 'brand_in_subdomain', 'brand_in_path',
    'suspecious_tld', 'statistical_report'
]

X = df[URL_FEATURES]
y = df['status']

print(f"[INFO] Jumlah fitur digunakan : {X.shape[1]} (URL only)")
print(f"[INFO] Jumlah data            : {X.shape[0]}")

# ==============================================================
# 2. PREPROCESSING
# ==============================================================
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"[INFO] Label encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")

scaler = StandardScaler()

# ==============================================================
# 3. SPLIT DATA 70/15/15
# ==============================================================
print("\n" + "=" * 60)
print("SPLIT DATA (70% Train | 15% Validasi | 15% Test)")
print("=" * 60)

X_trainval, X_test, y_trainval, y_test = train_test_split(
    X, y_encoded, test_size=0.15, random_state=42, stratify=y_encoded)

X_train, X_val, y_train, y_val = train_test_split(
    X_trainval, y_trainval, test_size=0.1765, random_state=42, stratify=y_trainval)

print(f"[INFO] Train : {X_train.shape[0]} | Val : {X_val.shape[0]} | Test : {X_test.shape[0]}")

X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled   = scaler.transform(X_val)
X_test_scaled  = scaler.transform(X_test)

# ==============================================================
# 4. K-FOLD CROSS VALIDATION (k=10)
# ==============================================================
print("\n" + "=" * 60)
print("K-FOLD CROSS VALIDATION (k=10)")
print("=" * 60)

skf   = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)

cv_results = cross_validate(
    model, X_train_scaled, y_train, cv=skf,
    scoring=['accuracy', 'precision', 'recall', 'f1'],
    n_jobs=-1
)

print(f"\n{'Fold':<6} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
print("-" * 50)
for i in range(10):
    print(f"  {i+1:<4} "
          f"{cv_results['test_accuracy'][i]:>10.4f} "
          f"{cv_results['test_precision'][i]:>10.4f} "
          f"{cv_results['test_recall'][i]:>10.4f} "
          f"{cv_results['test_f1'][i]:>10.4f}")
print("-" * 50)
print(f"{'Mean':<6} "
      f"{cv_results['test_accuracy'].mean():>10.4f} "
      f"{cv_results['test_precision'].mean():>10.4f} "
      f"{cv_results['test_recall'].mean():>10.4f} "
      f"{cv_results['test_f1'].mean():>10.4f}")

# ==============================================================
# 5. TRAINING FINAL & EVALUASI
# ==============================================================
print("\n" + "=" * 60)
print("TRAINING MODEL FINAL")
print("=" * 60)

svm_final = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
svm_final.fit(X_train_scaled, y_train)

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
    print(f"    TP={cm[1][1]}  FP={cm[0][1]}")
    print(f"    FN={cm[1][0]}  TN={cm[0][0]}")
    return acc, prec, rec, f1

evaluate("DATA VALIDASI", y_val, svm_final.predict(X_val_scaled))
evaluate("DATA TEST",     y_test, svm_final.predict(X_test_scaled))

# ==============================================================
# 6. SIMPAN MODEL
# ==============================================================
joblib.dump(svm_final,    'svm_model.pkl')
joblib.dump(scaler,       'scaler.pkl')
joblib.dump(URL_FEATURES, 'feature_names.pkl')

print("\n[INFO] Model disimpan: svm_model.pkl, scaler.pkl, feature_names.pkl")
print("[INFO] Fitur yang digunakan: URL only (56 fitur)")
