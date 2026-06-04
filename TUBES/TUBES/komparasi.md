# Komparasi Model: XGBoost vs SVM

Dokumen ini berisi hasil pengujian dan komparasi performa antara model **XGBoost** dan **SVM** pada sistem *Situs Deteksi Phishing*. Pengujian dilakukan dengan mengambil sampel 200 URL (100 legitimate, 100 phishing) langsung dari dataset.

## 1. Hasil Evaluasi Performa (Dataset Sampling 200 URL)

| Metrik | Model XGBoost | Model SVM (RBF) | Keterangan |
| :--- | :--- | :--- | :--- |
| **Akurasi Keseluruhan** | **75.5%** (151/200) | **84.0%** (168/200) | SVM memprediksi jauh lebih akurat pada pipeline yang tersedia saat ini. |
| **False Positives (Situs Legit dianggap Phishing)** | **47** (dari 100 situs legit) | **23** (dari 100 situs legit) | XGBoost sangat sensitif, hampir setengah situs aman diblokir. SVM memiliki tingkat kesalahan yang lebih dapat diterima. |
| **False Negatives (Phishing dianggap Legit)** | **2** (dari 100 situs phishing) | **9** (dari 100 situs phishing) | XGBoost unggul mendeteksi situs berbahaya (Recall tinggi), tapi mengorbankan akurasi situs aman (Precision rendah). |

---

## 2. Analisis Arsitektur Model

### Fitur yang Digunakan
1. **SVM (Support Vector Machine):**
   - **Fitur Ekstraksi:** Hanya menggunakan **56 fitur leksikal** (didasarkan semata-mata pada teks dan struktur URL itu sendiri seperti panjang teks, keberadaan `@`, tanda hubung `-`, dll).
   - **Kelebihan:** Sangat cepat secara komputasi dan tidak bergantung pada respon server tujuan atau API pihak ketiga.
   - **Kekurangan:** Terkadang salah memprediksi URL aman yang strukturnya rumit atau terlalu panjang (contoh: *stackoverflow.com/questions*).

2. **XGBoost (Extreme Gradient Boosting):**
   - **Fitur Ekstraksi:** Memanfaatkan hingga **87 fitur awal** dan diperkecil menjadi **43 fitur terpilih** menggunakan `SelectKBest`. Fitur yang diperlukan di antaranya mencakup hasil "Web Scraping" / API eksternal (seperti `page_rank`, `google_index`, jumlah *hyperlinks* HTML, dll).
   - **Kelebihan:** Sangat kuat jika **semua datanya** di-*scrape* dan dieksekusi dengan sempurna secara real-time. Deteksi phishing hampir absolut.
   - **Masalah Utama:** Karena aplikasi ini hanya fokus mendeteksi berdasarkan pola URL, fitur *web scraping* dan DNS di-*hardcode* menjadi `0`. Mengirim parameter `0` ke XGBoost pada fitur seperti `page_rank` membuatnya percaya bahwa semua situs adalah situs baru yang mencurigakan. Inilah alasan utama tingginya **False Positive**.

---

## 3. Kesimpulan

- **Gunakan SVM** apabila menginginkan hasil yang stabil, cepat, dan lebih ramah pengguna untuk keseharian tanpa koneksi server eksternal tambahan. Cocok sebagai *Default Mode*.
- **Gunakan XGBoost** jika menginginkan keamanan absolut tanpa toleransi, dengan catatan banyak situs legitimate populer akan terdeteksi sebagai bahaya akibat keterbatasan skrip sistem. Sangat bersifat preventif agresif.
