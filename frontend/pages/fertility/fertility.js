window.init_fertility_page = async function() {
  const genderEl = document.getElementById("fert-gender");
  const ageEl = document.getElementById("fert-age");
  const pctEl = document.getElementById("fert-pct");
  const statusEl = document.getElementById("fert-status");

  const fattiTbody = document.getElementById("fatti-tbody");
  const daFareTbody = document.getElementById("da-fare-tbody");
  const countFatti = document.getElementById("count-fatti");
  const countDaFare = document.getElementById("count-da-fare");

  const tabBtns = document.querySelectorAll(".fert-tab-btn");
  const tabContents = document.querySelectorAll(".fert-tab-content");

  tabBtns.forEach(btn => {
    btn.onclick = () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add("active");
    };
  });

  const loadCheckups = async () => {
    try {
      const data = await window.api.get("/api/fertility/checkups");
      genderEl.textContent = data.paziente_sesso || "--";
      ageEl.textContent = `${data.paziente_eta || '--'} anni`;
      pctEl.textContent = `${data.completamento_percentuale}%`;
      statusEl.textContent = data.stato_sintetico || "--";

      const fatti = data.controlli_fatti || [];
      const daFare = data.controlli_da_fare || [];

      countFatti.textContent = fatti.length;
      countDaFare.textContent = daFare.length;

      fattiTbody.innerHTML = "";
      if (fatti.length === 0) {
        fattiTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:20px; color:var(--text-muted);">Nessun controllo del protocollo registrato finora.</td></tr>';
      } else {
        fatti.forEach(f => {
          const tr = document.createElement("tr");
          const isNormal = f.stato === "NORMALE";
          tr.innerHTML = `
            <td><strong>${f.nome}</strong><br><span style="font-size:var(--font-xs); color:var(--text-muted);">${f.categoria}</span></td>
            <td>${f.data_esecuzione}</td>
            <td><strong style="color:var(--text-primary); font-size:var(--font-base);">${f.valore}</strong> ${f.unita}</td>
            <td><span class="badge ${isNormal ? 'badge-normal' : 'badge-warning'}">${f.stato}</span></td>
          `;
          fattiTbody.appendChild(tr);
        });
      }

      daFareTbody.innerHTML = "";
      if (daFare.length === 0) {
        daFareTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:20px; color:var(--status-normal); font-weight:bold;">Tutti i controlli raccomandati per la tua fascia di eta sono stati eseguiti!</td></tr>';
      } else {
        daFare.forEach(d => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><strong>${d.nome}</strong><br><span style="font-size:var(--font-xs); color:var(--text-muted);">${d.descrizione}</span></td>
            <td><span style="color:var(--accent-cyan); font-weight:600;">${d.tempistica}</span></td>
            <td><span class="badge ${d.priorita === 'ALTA' ? 'badge-danger' : 'badge-warning'}">${d.priorita}</span></td>
            <td><button class="btn btn-secondary btn-sm" onclick="window.router.navigate('referti')">Carica Esame</button></td>
          `;
          daFareTbody.appendChild(tr);
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const scanDropzone = document.getElementById("scan-dropzone");
  const scanFileInput = document.getElementById("scan-file-input");
  const scanFileName = document.getElementById("scan-file-name");
  const scanReportText = document.getElementById("scan-report-text");
  const scanContextInput = document.getElementById("scan-context-input");
  const btnAnalyzeScan = document.getElementById("btn-analyze-scan");
  const scanOutputBox = document.getElementById("scan-output-box");

  let selectedScanFile = null;

  scanFileInput.onchange = () => {
    if (scanFileInput.files.length > 0) {
      selectedScanFile = scanFileInput.files[0];
      scanFileName.textContent = `File selezionato: ${selectedScanFile.name}`;
    }
  };

  scanDropzone.ondragover = (e) => {
    e.preventDefault();
    scanDropzone.classList.add("dragover");
  };

  scanDropzone.ondragleave = () => {
    scanDropzone.classList.remove("dragover");
  };

  scanDropzone.ondrop = (e) => {
    e.preventDefault();
    scanDropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      selectedScanFile = e.dataTransfer.files[0];
      scanFileName.textContent = `File selezionato: ${selectedScanFile.name}`;
    }
  };

  btnAnalyzeScan.onclick = async () => {
    if (!selectedScanFile && !scanReportText.value.trim()) {
      window.showToast("Seleziona un'immagine TAC/scansione oppure inserisci il testo del referto.", "warning");
      return;
    }

    btnAnalyzeScan.disabled = true;
    btnAnalyzeScan.textContent = "⏳ Analisi radiologica e morfologica AI in corso...";
    scanOutputBox.innerHTML = '<div style="text-align:center; padding:40px; color:var(--accent-cyan);">Analisi specialistica per immagini con AI Vision in corso...</div>';

    const formData = new FormData();
    if (selectedScanFile) {
      formData.append("file", selectedScanFile);
    }
    if (scanReportText.value.trim()) {
      formData.append("report_text", scanReportText.value.trim());
    }
    if (scanContextInput.value.trim()) {
      formData.append("clinical_context", scanContextInput.value.trim());
    }

    try {
      const res = await window.api.post("/api/fertility/scan-analyze", formData);
      const formatted = (res.analysis || "")
        .replace(/^### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^# (.*$)/gim, "<h1>$1</h1>")
        .replace(/^\* (.*$)/gim, "<li>$1</li>")
        .replace(/^\- (.*$)/gim, "<li>$1</li>")
        .replace(/\n\n/gim, "<br><br>");

      scanOutputBox.innerHTML = formatted;
      window.showToast("Referto diagnostico specialistico generato con successo!", "success");
    } catch (err) {
      scanOutputBox.innerHTML = `<p style="color:var(--status-danger); padding:20px;">Errore: ${err.message}</p>`;
      window.showToast(err.message, "error");
    } finally {
      btnAnalyzeScan.disabled = false;
      btnAnalyzeScan.textContent = "🔍 Analizza Scansione con Vision AI & Genera Referto";
    }
  };

  const btnGenFertReport = document.getElementById("btn-generate-fert-report");
  const fertReportOutput = document.getElementById("fert-report-output");

  btnGenFertReport.onclick = async () => {
    btnGenFertReport.disabled = true;
    btnGenFertReport.textContent = "⏳ Sintesi Specialistica AI in corso...";
    fertReportOutput.innerHTML = '<div style="text-align:center; padding:40px; color:var(--accent-cyan);">Elaborazione della relazione riproduttiva di coppia ed individuale in corso...</div>';

    try {
      const res = await window.api.post("/api/fertility/report", {
        scan_notes: scanReportText.value.trim() || null
      });
      const formatted = (res.report || "")
        .replace(/^### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^# (.*$)/gim, "<h1>$1</h1>")
        .replace(/^\* (.*$)/gim, "<li>$1</li>")
        .replace(/^\- (.*$)/gim, "<li>$1</li>")
        .replace(/\n\n/gim, "<br><br>");

      fertReportOutput.innerHTML = formatted;
      window.showToast("Relazione clinica di fertilita elaborata!", "success");
    } catch (err) {
      fertReportOutput.innerHTML = `<p style="color:var(--status-danger); padding:20px;">Errore: ${err.message}</p>`;
      window.showToast(err.message, "error");
    } finally {
      btnGenFertReport.disabled = false;
      btnGenFertReport.textContent = "✨ Genera Relazione Clinica di Fertilita";
    }
  };

  loadCheckups();
};
