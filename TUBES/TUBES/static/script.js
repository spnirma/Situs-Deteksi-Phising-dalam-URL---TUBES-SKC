async function checkURL() {
  const url = document.getElementById('urlInput').value.trim();
  if (!url) { alert('Masukkan URL terlebih dahulu'); return; }

  document.getElementById('checkBtn').disabled = true;
  document.getElementById('loading').classList.remove('d-none');
  document.getElementById('resultCard').classList.add('d-none');

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    if (data.error) { alert('Error: ' + data.error); return; }

    const isPhishing = data.label === 'phishing';

    const verdictCard = document.getElementById('verdictCard');
    verdictCard.className = 'verdict-card ' + data.label;

    document.getElementById('verdictIcon').textContent  = isPhishing ? '!' : '';
    document.getElementById('verdictLabel').textContent = isPhishing ? 'PHISHING' : 'LEGITIMATE';
    document.getElementById('urlDisplay').textContent   = data.url;
    document.getElementById('resultSub').textContent    = isPhishing
      ? 'Model XGBoost mendeteksi pola mencurigakan pada URL ini. Hindari memasukkan data pribadi.'
      : 'Model XGBoost tidak mendeteksi pola phishing. URL ini terlihat aman.';

    document.getElementById('resultCard').classList.remove('d-none');

  } catch (e) {
    alert('Gagal menghubungi server: ' + e.message);
  } finally {
    document.getElementById('loading').classList.add('d-none');
    document.getElementById('checkBtn').disabled = false;
  }
}

document.getElementById('urlInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') checkURL();
});