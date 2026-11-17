window.init_dashboard_page = async function() {
  const scoreEl = document.getElementById("dash-health-score");
  const statusEl = document.getElementById("dash-health-status");
  const systemsGrid = document.getElementById("systems-grid");
  const anomaliesTbody = document.getElementById("anomalies-table-body");
  const visualizerMount = document.getElementById("visualizer-3d-mount");

  try {
    if (visualizerMount) {
      const vRes = await fetch("components/visualizer_3d/visualizer_3d.html");
      if (vRes.ok) {
        visualizerMount.innerHTML = await vRes.text();
        if (window.Clinical3DVisualizer) {
          window.dashboardVisualizer = new window.Clinical3DVisualizer("canvas-3d-viewport", "hud-organ-tooltip");
        }
      }
    }

    const scores = await window.api.get("/api/analytics/health-score");
    scoreEl.textContent = scores.overall_score;
    statusEl.textContent = scores.stato_sintetico;

    systemsGrid.innerHTML = "";
    for (const [sysName, data] of Object.entries(scores.sistemi || {})) {
      const card = document.createElement("div");
      card.className = "clinical-card system-card";
      card.innerHTML = `
        <div class="system-card-header">
          <span class="system-name">${sysName}</span>
          <span class="system-score">${data.score}</span>
        </div>
        <div class="system-bar-bg">
          <div class="system-bar-fill" style="width: ${data.score}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:var(--font-xs); color:var(--text-muted);">
          <span>Stato: <strong>${data.stato}</strong></span>
          <span>Anomalie: <strong>${data.anomalie}/${data.totale}</strong></span>
        </div>
      `;
      systemsGrid.appendChild(card);
    }

    const anomalies = await window.api.get("/api/analytics/radar-anomalies");
    if (window.dashboardVisualizer && anomalies) {
      window.dashboardVisualizer.setAnomalies(anomalies);
    }

    if (anomalies && anomalies.length > 0) {
      anomaliesTbody.innerHTML = "";
      anomalies.forEach((a, idx) => {
        const tr = document.createElement("tr");
        const valStr = a.valore_numerico !== null ? a.valore_numerico : a.valore_testuale;
        const rangeStr = (a.range_min !== null && a.range_max !== null) ? `${a.range_min} - ${a.range_max}` : "-";
        const badgeClass = a.stato_flag.includes("CRITICO") ? "badge-critical" : "badge-warning";

        tr.innerHTML = `
          <td><span style="font-weight:bold; color:var(--accent-cyan);">#${idx + 1}</span></td>
          <td><strong>${a.nome_standardizzato}</strong><br><span style="font-size:var(--font-xs); color:var(--text-muted);">${a.categoria}</span></td>
          <td><strong style="color:var(--text-primary); font-size:var(--font-base);">${valStr}</strong> ${a.unita_misura}</td>
          <td>${rangeStr} ${a.unita_misura}</td>
          <td><span style="color:var(--status-danger); font-weight:700;">+${a.scostamento_percentuale}%</span></td>
          <td>${a.persistenza_storica} su ${a.totale_prelievi_recenti} prelievi</td>
          <td>${a.data_prelievo}</td>
          <td><span class="badge ${badgeClass}">${a.stato_flag}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="window.router.navigate('trends', {analyte: '${encodeURIComponent(a.nome_standardizzato)}'})">
              Trend
            </button>
          </td>
        `;
        anomaliesTbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error(err);
  }
};
