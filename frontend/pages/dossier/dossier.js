window.init_dossier_page = async function() {
  const patientInput = document.getElementById("dossier-patient-name");
  const passwordInput = document.getElementById("dossier-pdf-password");
  const exportBtn = document.getElementById("btn-export-pdf");
  const exportCsvBtn = document.getElementById("btn-export-csv");
  const exportJsonBtn = document.getElementById("btn-export-json");
  const streamTbody = document.getElementById("stream-preview-tbody");

  try {
    const profData = await window.api.get("/api/profiles");
    const active = (profData.profiles || []).find(p => p.id === profData.active_profile_id);
    if (active) {
      patientInput.value = `${active.nome} ${active.cognome} (${active.parentela})`;
    } else {
      patientInput.value = "Profilo Principale";
    }
  } catch (err) {
    console.error(err);
  }

  async function loadStreamPreview() {
    try {
      const res = await fetch("/api/export/clinical-stream?format=json");
      if (res.ok) {
        const data = await res.json();
        if (streamTbody) {
          if (!data || data.length === 0) {
            streamTbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:12px; color:var(--text-muted);">Nessun dato registrato nel flusso clinico.</td></tr>`;
            return;
          }
          streamTbody.innerHTML = data.slice(0, 15).map(r => `
            <tr>
              <td><strong>${r.data_evento || '--'}</strong></td>
              <td>${r.tipo_flusso || '--'}</td>
              <td>${r.nome_parametro || '--'}</td>
              <td>${r.valore_numerico !== null && r.valore_numerico !== undefined ? r.valore_numerico + ' ' + (r.unita_misura || '') : (r.valore_testuale || '--')}</td>
              <td><span class="kpi-badge ${r.stato_flag === 'NORMALE' ? 'badge-normal' : 'badge-warning'}">${r.stato_flag || '--'}</span></td>
            </tr>
          `).join("");
        }
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function downloadStream(format) {
    try {
      const res = await fetch(`/api/export/clinical-stream?format=${format}`);
      if (!res.ok) {
        throw new Error("Errore durante il download del flusso");
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Anamnesix_Flusso_Clinico_${Date.now()}.${format === 'csv' ? 'csv' : 'json'}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      if (window.showToast) {
        window.showToast(`Flusso dati clinici in formato ${format.toUpperCase()} esportato!`, "success");
      }
    } catch (err) {
      if (window.showToast) {
        window.showToast(err.message, "error");
      }
    }
  }

  if (exportCsvBtn) {
    exportCsvBtn.onclick = () => downloadStream("csv");
  }
  if (exportJsonBtn) {
    exportJsonBtn.onclick = () => downloadStream("json");
  }

  exportBtn.onclick = async () => {
    exportBtn.disabled = true;
    exportBtn.textContent = "Generazione Dossier PDF in corso...";

    try {
      const payload = {
        password: passwordInput.value || null
      };

      const res = await fetch("/api/export/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        throw new Error("Errore generazione PDF");
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Anamnesix_Dossier_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      window.showToast("Dossier clinico PDF scaricato con successo!", "success");
    } catch (err) {
      window.showToast(err.message, "error");
    } finally {
      exportBtn.disabled = false;
      exportBtn.textContent = "📥 Genera e Scarica Dossier Clinico PDF";
    }
  };

  await loadStreamPreview();
};
