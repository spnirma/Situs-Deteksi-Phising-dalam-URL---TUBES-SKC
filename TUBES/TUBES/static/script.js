async function checkURL() {
  const url = document.getElementById('urlInput').value.trim();
  if (!url) { alert('Masukkan URL terlebih dahulu'); return; }

  document.getElementById('checkBtn').disabled = true;
  document.getElementById('loading').style.display = 'block';
  document.getElementById('resultCard').style.display = 'none';

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (data.error) { alert('Error: ' + data.error); return; }

    const isPhishing = data.label === 'phishing';

    // Hasil prediksi SVM
    document.getElementById('resultHeader').className  = 'result-header ' + data.label;
    document.getElementById('resultIcon').textContent  = isPhishing ? 'WARNING' : 'NO';
    document.getElementById('resultLabel').textContent = isPhishing ? 'PHISHING' : 'LEGITIMATE';
    document.getElementById('resultLabel').className   = 'result-label ' + data.label;
    document.getElementById('resultSub').textContent   = isPhishing
      ? 'Model SVM mendeteksi URL ini sebagai situs phishing.'
      : 'Model SVM mendeteksi URL ini sebagai situs legitimate.';

    document.getElementById('urlDisplay').textContent = data.url;

    // Tampilkan fitur mentah hasil ekstraksi
    const container = document.getElementById('featureGroups');
    container.innerHTML = '';

    data.feature_groups.forEach(group => {
      const groupEl = document.createElement('div');
      groupEl.className = 'feature-group';

      let rows = '';
      group.items.forEach(item => {
        rows += `
          <tr>
            <td class="col-label">${item.label}</td>
            <td class="col-value">${item.value}</td>
          </tr>`;
      });

      groupEl.innerHTML = `
        <div class="group-title">${group.group}</div>
        <table class="feature-table"><tbody>${rows}</tbody></table>`;

      container.appendChild(groupEl);
    });

    document.getElementById('resultCard').style.display = 'block';

  } catch (e) {
    alert('Gagal menghubungi server: ' + e.message);
  } finally {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('checkBtn').disabled = false;
  }
}

document.getElementById('urlInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') checkURL();
});