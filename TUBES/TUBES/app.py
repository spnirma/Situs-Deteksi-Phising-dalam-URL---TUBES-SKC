"""
GUI Deteksi Phishing Website - Flask Localhost
Model  : XGBoost + Feature Selection + K-Fold CV
Jalankan: python app.py
Buka    : http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Load model XGBoost, scaler, selector, dan feature names
model         = joblib.load('models/xgboost/xgb_model.pkl')
scaler        = joblib.load('models/xgboost/xgb_scaler.pkl')
selector      = joblib.load('models/xgboost/xgb_selector.pkl')
feature_names = joblib.load('models/xgboost/xgb_features.pkl')
all_features  = joblib.load('models/xgboost/all_features.pkl')

# ================================================================
# EKSTRAKSI FITUR DARI URL
# ================================================================
def extract_features(url):
    parsed   = urlparse(url)
    hostname = parsed.hostname or ''
    path     = parsed.path or ''
    full_url = url

    features = {}

    # Panjang
    features['length_url']      = len(full_url)
    features['length_hostname'] = len(hostname)
    features['ip'] = 1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname) else 0

    # Karakter khusus
    features['nb_dots']        = full_url.count('.')
    features['nb_hyphens']     = full_url.count('-')
    features['nb_at']          = full_url.count('@')
    features['nb_qm']          = full_url.count('?')
    features['nb_and']         = full_url.count('&')
    features['nb_or']          = full_url.count('|')
    features['nb_eq']          = full_url.count('=')
    features['nb_underscore']  = full_url.count('_')
    features['nb_tilde']       = full_url.count('~')
    features['nb_percent']     = full_url.count('%')
    features['nb_slash']       = full_url.count('/')
    features['nb_star']        = full_url.count('*')
    features['nb_colon']       = full_url.count(':')
    features['nb_comma']       = full_url.count(',')
    features['nb_semicolumn']  = full_url.count(';')
    features['nb_dollar']      = full_url.count('$')
    features['nb_space']       = full_url.count(' ')
    features['nb_www']         = full_url.lower().count('www')
    features['nb_com']         = full_url.lower().count('.com')

    # Double slash tanpa protokol
    url_no_protocol            = full_url.replace('http://', '').replace('https://', '')
    features['nb_dslash']      = url_no_protocol.count('//')

    # HTTP/HTTPS
    features['http_in_path']   = 1 if 'http' in path.lower() else 0
    features['https_token']    = 1 if 'https' in hostname.lower() else 0

    # Rasio digit
    digits_url  = sum(c.isdigit() for c in full_url)
    digits_host = sum(c.isdigit() for c in hostname)
    features['ratio_digits_url']  = round(digits_url / len(full_url) if full_url else 0, 4)
    features['ratio_digits_host'] = round(digits_host / len(hostname) if hostname else 0, 4)

    # Struktur domain
    features['punycode']           = 1 if 'xn--' in hostname else 0
    features['port']               = 1 if parsed.port else 0
    features['tld_in_path']        = 1 if re.search(r'\.(com|net|org|info|biz)', path) else 0
    features['tld_in_subdomain']   = 0
    subdomain = hostname.replace('www.', '').split('.')[:-2]
    features['abnormal_subdomain'] = 1 if len(subdomain) > 1 else 0
    features['nb_subdomains']      = len(hostname.split('.')) - 2 if hostname else 0
    features['prefix_suffix']      = 1 if '-' in hostname else 0
    features['random_domain']      = 0
    features['shortening_service'] = 1 if any(s in hostname for s in ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']) else 0
    features['path_extension']     = 1 if re.search(r'\.(exe|zip|rar|php|asp|js)', path) else 0

    # Redirection
    features['nb_redirection']          = url_no_protocol.count('//')
    features['nb_external_redirection'] = 0

    # Statistik kata
    words      = [w for w in re.split(r'[\W_]+', full_url) if w]
    words_host = [w for w in re.split(r'[\W_]+', hostname) if w]
    words_path = [w for w in re.split(r'[\W_]+', path) if w]

    features['length_words_raw']   = len(words)
    features['char_repeat']        = max((full_url.count(c) for c in set(full_url)), default=0)
    features['shortest_words_raw'] = min((len(w) for w in words), default=0)
    features['shortest_word_host'] = min((len(w) for w in words_host), default=0)
    features['shortest_word_path'] = min((len(w) for w in words_path), default=0)
    features['longest_words_raw']  = max((len(w) for w in words), default=0)
    features['longest_word_host']  = max((len(w) for w in words_host), default=0)
    features['longest_word_path']  = max((len(w) for w in words_path), default=0)
    features['avg_words_raw']      = round(np.mean([len(w) for w in words]) if words else 0, 4)
    features['avg_word_host']      = round(np.mean([len(w) for w in words_host]) if words_host else 0, 4)
    features['avg_word_path']      = round(np.mean([len(w) for w in words_path]) if words_path else 0, 4)

    # Phishing hints
    phish_keywords = ['login', 'secure', 'account', 'update', 'confirm', 'verify',
                      'bank', 'paypal', 'password', 'signin', 'ebay', 'apple', 'amazon']
    features['phish_hints']        = sum(1 for kw in phish_keywords if kw in full_url.lower())
    features['domain_in_brand']    = 0
    features['brand_in_subdomain'] = 0
    features['brand_in_path']      = 0
    features['suspecious_tld']     = 1 if any(full_url.endswith(t) for t in ['.tk', '.ml', '.ga', '.cf', '.gq']) else 0
    features['statistical_report'] = 0

    # Fitur konten halaman (default 0, tidak fetch halaman)
    for key in ['nb_hyperlinks', 'ratio_intHyperlinks', 'ratio_extHyperlinks',
                'ratio_nullHyperlinks', 'nb_extCSS', 'ratio_intRedirection',
                'ratio_extRedirection', 'ratio_intErrors', 'ratio_extErrors',
                'login_form', 'external_favicon', 'links_in_tags', 'submit_email',
                'ratio_intMedia', 'ratio_extMedia', 'sfh', 'iframe', 'popup_window',
                'safe_anchor', 'onmouseover', 'right_clic', 'empty_title',
                'domain_in_title', 'domain_with_copyright', 'whois_registered_domain',
                'domain_registration_length', 'domain_age', 'web_traffic',
                'dns_record', 'google_index', 'page_rank']:
        features[key] = 0

    feature_vector = [features.get(f, 0) for f in all_features]
    return feature_vector, features


# ================================================================
# ROUTES
# ================================================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        url  = data.get('url', '').strip()

        if not url:
            return jsonify({'error': 'URL tidak boleh kosong'})
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        # Ekstrak fitur → scale → select → prediksi
        feature_vector, features = extract_features(url)
        X_input    = np.array(feature_vector).reshape(1, -1)
        X_scaled   = scaler.transform(X_input)
        X_selected = selector.transform(X_scaled)
        pred       = model.predict(X_selected)[0]
        label      = 'phishing' if pred == 1 else 'legitimate'

        feature_groups = [
            {
                "group": "Panjang URL",
                "items": [
                    {"label": "Panjang URL",     "value": features['length_url']},
                    {"label": "Panjang Hostname", "value": features['length_hostname']},
                ]
            },
            {
                "group": "Karakter Khusus",
                "items": [
                    {"label": "Jumlah Titik (.)",        "value": features['nb_dots']},
                    {"label": "Jumlah Tanda Hubung (-)", "value": features['nb_hyphens']},
                    {"label": "Jumlah Slash (/)",        "value": features['nb_slash']},
                    {"label": "Jumlah @",                "value": features['nb_at']},
                    {"label": "Jumlah Tanda Tanya (?)",  "value": features['nb_qm']},
                    {"label": "Jumlah =",                "value": features['nb_eq']},
                    {"label": "Jumlah &",                "value": features['nb_and']},
                    {"label": "Jumlah %",                "value": features['nb_percent']},
                ]
            },
            {
                "group": "Struktur Domain",
                "items": [
                    {"label": "Jumlah Subdomain",    "value": features['nb_subdomains']},
                    {"label": "IP sebagai Hostname", "value": features['ip']},
                    {"label": "Prefix/Suffix (-)",   "value": features['prefix_suffix']},
                    {"label": "Subdomain Abnormal",  "value": features['abnormal_subdomain']},
                    {"label": "Port Tidak Standar",  "value": features['port']},
                    {"label": "Punycode (xn--)",     "value": features['punycode']},
                    {"label": "TLD Mencurigakan",    "value": features['suspecious_tld']},
                    {"label": "URL Shortener",       "value": features['shortening_service']},
                ]
            },
            {
                "group": "Konten URL",
                "items": [
                    {"label": "HTTP dalam Path",         "value": features['http_in_path']},
                    {"label": "HTTPS dalam Hostname",    "value": features['https_token']},
                    {"label": "Kata Phishing Hints",     "value": features['phish_hints']},
                    {"label": "Rasio Digit dalam URL",   "value": features['ratio_digits_url']},
                    {"label": "Rasio Digit dalam Host",  "value": features['ratio_digits_host']},
                    {"label": "Ekstensi File Berbahaya", "value": features['path_extension']},
                    {"label": "Jumlah Redirection (//)", "value": features['nb_redirection']},
                ]
            },
            {
                "group": "Statistik Kata",
                "items": [
                    {"label": "Jumlah Kata dalam URL",    "value": features['length_words_raw']},
                    {"label": "Kata Terpendek URL",       "value": features['shortest_words_raw']},
                    {"label": "Kata Terpanjang URL",      "value": features['longest_words_raw']},
                    {"label": "Rata-rata Panjang Kata",   "value": features['avg_words_raw']},
                    {"label": "Kata Terpanjang Hostname", "value": features['longest_word_host']},
                    {"label": "Kata Terpanjang Path",     "value": features['longest_word_path']},
                ]
            },
        ]

        return jsonify({
            'url'           : url,
            'label'         : label,
            'feature_groups': feature_groups,
        })

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    print("=" * 50)
    print("  Deteksi Phishing Website - Flask Server")
    print("  Buka browser: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)