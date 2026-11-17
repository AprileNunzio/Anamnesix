window.init_correlations_page = async function() {
  const grid = document.getElementById("correlations-grid");
  const generateBtn = document.getElementById("btn-generate-second-opinion");
  const outputBox = document.getElementById("second-opinion-output");

  try {
    const list = await window.api.get("/api/analytics/correlations");
    grid.innerHTML = "";

    if (!list || list.length === 0) {
      grid.innerHTML = '<div class="clinical-card" style="grid-column: 1 / -1; text-align:center; color:var(--text-muted); padding:30px;">Nessuna correlazione patologica complessa identificata al momento.</div>';
    } else {
      list.forEach(c => {
        const card = document.createElement("div");
        const critClass = (c.criticita || "").toLowerCase();
        card.className = `clinical-card correlation-card ${critClass}`;

        const chips = (c.biomarcatori || []).map(b => `<span class="corr-chip">${b}</span>`).join("");

        card.innerHTML = `
          <div class="corr-header">
            <span class="corr-title">${c.titolo}</span>
            <span class="badge ${critClass === 'alta' ? 'badge-danger' : 'badge-warning'}">${c.criticita}</span>
          </div>
          <p class="corr-desc">${c.descrizione}</p>
          <div class="corr-chips">${chips}</div>
        `;
        grid.appendChild(card);
      });
    }
  } catch (err) {
    console.error(err);
  }

  generateBtn.onclick = async () => {
    generateBtn.disabled = true;
    generateBtn.textContent = "⏳ Analisi ed Elaborazione AI in corso...";
    outputBox.innerHTML = '<div style="text-align:center; padding:40px; color:var(--accent-cyan);">Elaborazione dello storico clinico con intelligenza artificiale...</div>';

    try {
      const res = await window.api.post("/api/analytics/second-opinion", {});
      const rawText = res.report || "";
      const htmlFormatted = rawText
        .replace(/^### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^# (.*$)/gim, "<h1>$1</h1>")
        .replace(/^\* (.*$)/gim, "<li>$1</li>")
        .replace(/^\- (.*$)/gim, "<li>$1</li>")
        .replace(/\n\n/gim, "<br><br>");

      outputBox.innerHTML = `<div style="max-height: 800px; overflow-y:auto; padding:10px;">${htmlFormatted}</div>`;
      window.showToast("Rapporto di Second Opinion generato con successo.", "success");
    } catch (err) {
      outputBox.innerHTML = `<p style="color:var(--status-danger); padding:20px;">Errore: ${err.message}</p>`;
      window.showToast(err.message, "error");
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = "⚡ Genera Rapporto Second Opinion AI";
    }
  };
};
