# Situs Deteksi Phishing dalam URL - TUBES SKC

Proyek ini adalah implementasi sistem deteksi *phishing* berbasis URL menggunakan Machine Learning.

## Struktur Direktori
Proyek ini telah direstrukturisasi agar lebih rapi dan profesional:

```
├── TUBES/TUBES/
│   ├── app.py                      # File utama untuk menjalankan Flask GUI
│   ├── dataset/                    # Direktori dataset latih
│   ├── dataset_phishing.csv        # File CSV dataset (87 fitur)
│   ├── live_test_models.py         # Skrip untuk menguji URL real-live (TDD)
│   ├── models/
│   │   ├── svm/                    # Model dan skrip training untuk algoritma SVM
│   │   │   ├── Kode_Model_OpsiA.py
│   │   │   ├── Kode_Model_OpsiB.py
│   │   │   ├── svm_model.pkl, scaler.pkl, feature_names.pkl
│   │   └── xgboost/                # Model dan skrip training untuk algoritma XGBoost
│   │       ├── Kode_Model_Dosen.py
│   │       ├── xgb_model.pkl, xgb_scaler.pkl, xgb_selector.pkl, dll.
│   ├── static/                     # Aset web (CSS/JS/Gambar)
│   ├── templates/                  # Template HTML untuk antarmuka pengguna
│   └── README.md                   # File informasi proyek
```

## Update & Perbaikan (Mark: awanmh)

Saya (**awanmh**) telah membenahi dan menambahkan beberapa poin kritikal dalam kode base ini, di antaranya:

1. **Bug Ekstraksi URL Diperbaiki (`app.py`)**
   - **Fix `nb_dslash`**: Sebelumnya protokol (`https://`) ikut terhitung dalam skor `//`, membuat URL legal seperti Google mendadak punya anomali deviasi raksasa dan ditebak sebagai *phishing*. Saya telah membersihkan logika agar mengabaikan string HTTP/HTTPS.
   - **Fix `NaN` di Path Kosong**: URL yang hanya bersandar di *root* (e.g. `google.com/`) menghasilkan *error* kalkulasi komputasi stat (perata-rataan me-return `NaN`). Hal ini sudah diperbaiki.
   
2. **Implementasi XGBoost (Sesuai Rekomendasi Dosen)**
   - Saya membuat modul kecerdasan buatan baru di `models/xgboost/Kode_Model_Dosen.py`.
   - Menghapus metode iterasi lambat (*K-Fold*) menjadi *train_test_split* 50:50.
   - Memasukkan filter fitur cerdas (*Chi-Square Selection*) untuk membuang metrik tidak berguna dan mengambil tepat **43 fitur unggulan**.
   - Menghasilkan akurasi evaluasi sebesar **95.64%** (Tercatat lebih tajam mengalahkan SVM yang hanya 89%).

3. **Injeksi Live Testing Script (TDD)**
   - Saya membuat `live_test_models.py` untuk mengukur daya tahan kedua arsitektur model (SVM vs XGBoost) menggunakan tautan internet asli yang disedot langsung (*out-of-box*), untuk menyoroti keunggulan parameter masing-masing.

4. **Kerapihan Arsitektur Proyek**
   - File model yang berceceran (`.pkl`) dan file training python telah dipilah secara struktural ke dalam folder `models/svm` dan `models/xgboost` masing-masing agar terlihat lebih profesional.

## Cara Menjalankan

1. Pastikan library terinstall (`flask`, `scikit-learn`, `xgboost`, `pandas`, `numpy`, `joblib`).
2. Masuk ke direktori `TUBES/TUBES/`.
3. Jalankan aplikasi via terminal:
   ```bash
   python app.py
   ```
4. Buka alamat `http://127.0.0.1:5000` di peramban web.
