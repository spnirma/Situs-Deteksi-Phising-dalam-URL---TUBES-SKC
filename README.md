# PhishGuard — Deteksi URL Phishing Berbasis Machine Learning

PhishGuard adalah aplikasi web berbasis Flask yang digunakan untuk mendeteksi apakah sebuah URL merupakan **Legitimate (Aman)** atau **Phishing (Berbahaya)**. Aplikasi ini memanfaatkan arsitektur *Machine Learning* untuk mengekstraksi puluhan fitur struktural dan leksikal langsung dari string URL secara *real-time*.

## Fitur Utama

- **Dual-Model ML Architecture**: Mendukung dua model deteksi sekaligus yang dapat dialihkan langsung melalui antarmuka web.
  - **SVM (RBF Kernel)**: Mengekstraksi 56 fitur leksikal. Sangat akurat, stabil, dan menghindari *False Positive* pada situs-situs populer (Cocok untuk penggunaan sehari-hari).
  - **XGBoost**: Mengekstraksi 87 fitur. Sangat agresif dan *strict* dalam memblokir potensi ancaman (Mode keamanan preventif).
- **Ekstraksi Fitur Mandiri**: Menganalisis elemen-elemen URL seperti panjang *hostname*, *subdomain*, eksistensi karakter khusus, hingga analisis sintaks teks.
- **Antarmuka Modern & Responsif**: UI/UX yang profesional, *clean*, dan memberikan *feedback* prediksi yang seketika.

---

## Teknologi yang Digunakan

- **Backend**: Python, Flask, Pandas, NumPy
- **Machine Learning**: Scikit-Learn (SVM), XGBoost
- **Frontend**: HTML5, CSS3 (Vanilla / Custom Design), JavaScript
- **Deployment & Scaling**: Standard WSGI (Flask bawaan untuk local dev)

---

## Cara Menjalankan Aplikasi Lokal

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/spnirma/Situs-Deteksi-Phising-dalam-URL---TUBES-SKC.git
   cd Situs-Deteksi-Phising-dalam-URL---TUBES-SKC/TUBES/TUBES
   ```

2. **Install dependensi yang dibutuhkan:**
   Pastikan Python 3 telah terinstall, lalu jalankan:
   ```bash
   pip install -r requirements.txt
   ```
   *(Atau install manual library utama: `flask`, `scikit-learn`, `xgboost`, `pandas`, `numpy`)*

3. **Jalankan Server:**
   ```bash
   python app.py
   ```

4. **Buka di Web Browser:**
   Akses `http://127.0.0.1:5000`

---

## Komparasi Model (SVM vs XGBoost)

Berikut adalah ringkasan singkat pengujian sampel 200 URL (100 legitimate, 100 phishing):

| Metrik | Model SVM | Model XGBoost | Catatan |
| :--- | :--- | :--- | :--- |
| **Akurasi Keseluruhan** | **84.0%** | **75.5%** | SVM jauh lebih optimal untuk dataset ini (pada limitasi fitur yang ada). |
| **False Positives** | Rendah (23/100) | Sangat Tinggi (47/100)| XGBoost sangat agresif mendeteksi situs baru sebagai bahaya. |
| **False Negatives** | Sedang (9/100) | Sangat Rendah (2/100) | XGBoost hampir tidak pernah kelewatan situs phishing. |

*Untuk penjelasan detail mengenai hasil ekstraksi fitur dan perbandingan komprehensif, silakan lihat file [`komparasi.md`](./TUBES/TUBES/komparasi.md).*

---

