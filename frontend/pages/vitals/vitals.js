async function init_vitals_page() {
  const modal = document.getElementById("vitals-modal");
  const openBtn = document.getElementById("btn-open-vitals-modal");
  const closeBtn = document.getElementById("close-vitals-modal");
  const cancelBtn = document.getElementById("btn-cancel-vitals");
  const saveBtn = document.getElementById("btn-save-vitals");

  const todayStr = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("input-vital-data");
  if (dateInput) {
    dateInput.value = todayStr;
  }

  function toggleModal(show) {
    if (modal) {
      modal.style.display = show ? "flex" : "none";
    }
  }

  if (openBtn) {
    openBtn.onclick = () => toggleModal(true);
  }
  if (closeBtn) {
    closeBtn.onclick = () => toggleModal(false);
  }
  if (cancelBtn) {
    cancelBtn.onclick = () => toggleModal(false);
  }

  async function loadData() {
    try {
      const resLatest = await fetch("/api/health-metrics/latest");
      if (resLatest.ok) {
        const latest = await resLatest.json();
        updateKpis(latest);
      }

      const resHistory = await fetch("/api/health-metrics/history");
      if (resHistory.ok) {
        const history = await resHistory.json();
        renderTable(history);
      }
    } catch (err) {
      if (window.toast) {
        window.toast.error("Errore caricamento parametri vitali: " + err.message);
      }
    }
  }

  function updateKpis(data) {
    if (!data || !data.data) {
      return;
    }
    const passiEl = document.getElementById("kpi-passi");
    const passiSub = document.getElementById("kpi-passi-sub");
    if (passiEl && data.passi_giornalieri !== null && data.passi_giornalieri !== undefined) {
      passiEl.textContent = Number(data.passi_giornalieri).toLocaleString("it-IT");
      if (passiSub && data.distanza_km) {
        passiSub.textContent = `${data.distanza_km.toFixed(1)} km | ${data.calorie_attive_kcal || 0} kcal`;
      }
    }

    const bpmEl = document.getElementById("kpi-bpm");
    const bpmSub = document.getElementById("kpi-bpm-sub");
    if (bpmEl && data.bpm_riposo) {
      bpmEl.textContent = Math.round(data.bpm_riposo).toString();
      if (bpmSub) {
        bpmSub.textContent = `Min: ${data.bpm_min || '--'} | Max: ${data.bpm_max || '--'}`;
      }
    }

    const pressEl = document.getElementById("kpi-pressione");
    const pressSub = document.getElementById("kpi-pressione-sub");
    if (pressEl && data.pressione_sistolica && data.pressione_diastolica) {
      pressEl.textContent = `${Math.round(data.pressione_sistolica)}/${Math.round(data.pressione_diastolica)}`;
      if (pressSub) {
        if (data.pressione_sistolica < 120 && data.pressione_diastolica < 80) {
          pressSub.className = "kpi-badge badge-normal";
          pressSub.textContent = "Ottimale";
        } else if (data.pressione_sistolica <= 129 && data.pressione_diastolica <= 84) {
          pressSub.className = "kpi-badge badge-normal";
          pressSub.textContent = "Normale";
        } else if (data.pressione_sistolica <= 139 || data.pressione_diastolica <= 89) {
          pressSub.className = "kpi-badge badge-warning";
          pressSub.textContent = "Pre-Ipertensione";
        } else {
          pressSub.className = "kpi-badge badge-danger";
          pressSub.textContent = "Ipertensione";
        }
      }
    }

    const spo2El = document.getElementById("kpi-spo2");
    const spo2Sub = document.getElementById("kpi-spo2-sub");
    if (spo2El && data.spo2_media) {
      spo2El.textContent = data.spo2_media.toFixed(1);
      if (spo2Sub && data.spo2_min) {
        spo2Sub.textContent = `Minima notturna: ${data.spo2_min.toFixed(1)}%`;
      }
    }

    const ahiEl = document.getElementById("kpi-ahi");
    const ahiSub = document.getElementById("kpi-ahi-sub");
    if (ahiEl && data.indice_apnea_ahi !== null && data.indice_apnea_ahi !== undefined) {
      ahiEl.textContent = data.indice_apnea_ahi.toFixed(1);
      if (ahiSub) {
        if (data.indice_apnea_ahi < 5.0) {
          ahiSub.className = "kpi-badge badge-normal";
          ahiSub.textContent = "Normale (<5/h)";
        } else if (data.indice_apnea_ahi < 15.0) {
          ahiSub.className = "kpi-badge badge-warning";
          ahiSub.textContent = "Apnea Lieve (5-15/h)";
        } else if (data.indice_apnea_ahi < 30.0) {
          ahiSub.className = "kpi-badge badge-danger";
          ahiSub.textContent = "Apnea Moderata (15-30/h)";
        } else {
          ahiSub.className = "kpi-badge badge-critical";
          ahiSub.textContent = "Apnea Grave (>30/h)";
        }
      }
    }
  }

  function renderTable(list) {
    const tbody = document.getElementById("vitals-tbody");
    if (!tbody) {
      return;
    }
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="11" style="text-align:center; padding:18px; color:var(--text-muted);">Nessun parametro vitale registrato. Clicca su "Registra Parametri Vitali" per inserire la prima rilevazione.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(item => `
      <tr>
        <td style="font-weight:600;">${item.data}</td>
        <td style="font-family:var(--font-mono); font-weight:700;">${item.passi_giornalieri !== null && item.passi_giornalieri !== undefined ? Number(item.passi_giornalieri).toLocaleString('it-IT') : '--'}</td>
        <td>${item.bpm_riposo ? Math.round(item.bpm_riposo) : '--'} / ${item.bpm_max ? Math.round(item.bpm_max) : '--'}</td>
        <td>${item.pressione_sistolica && item.pressione_diastolica ? Math.round(item.pressione_sistolica) + '/' + Math.round(item.pressione_diastolica) : '--'}</td>
        <td>${item.spo2_media ? item.spo2_media.toFixed(1) + '%' : '--'}</td>
        <td style="font-weight:700;">${item.indice_apnea_ahi !== null && item.indice_apnea_ahi !== undefined ? item.indice_apnea_ahi.toFixed(1) : '--'}</td>
        <td>${item.episodi_apnea_totali !== null && item.episodi_apnea_totali !== undefined ? item.episodi_apnea_totali : '--'}</td>
        <td>${item.durata_desaturazione_minuti ? item.durata_desaturazione_minuti.toFixed(1) + ' min' : '--'}</td>
        <td>${item.ore_sonno_totali ? item.ore_sonno_totali.toFixed(1) + ' h' : '--'}</td>
        <td>${item.hrv_ms ? Math.round(item.hrv_ms) + ' ms' : '--'}</td>
        <td>
          <button class="btn btn-secondary" style="padding:2px 8px; font-size:0.7rem;" onclick="deleteVitalEntry('${item.id}')">Elimina</button>
        </td>
      </tr>
    `).join("");
  }

  window.deleteVitalEntry = async function(id) {
    if (!confirm("Confermi di voler eliminare questa rilevazione?")) {
      return;
    }
    try {
      const res = await fetch(`/api/health-metrics/${id}`, { method: "DELETE" });
      if (res.ok) {
        if (window.toast) {
          window.toast.success("Rilevazione eliminata.");
        }
        await loadData();
      }
    } catch (err) {
      if (window.toast) {
        window.toast.error("Errore: " + err.message);
      }
    }
  };

  if (saveBtn) {
    saveBtn.onclick = async () => {
      const dataVal = document.getElementById("input-vital-data").value;
      if (!dataVal) {
        if (window.toast) {
          window.toast.warning("Inserisci la data di rilevazione.");
        }
        return;
      }

      const payload = {
        data: dataVal,
        passi_giornalieri: parseInt(document.getElementById("input-vital-passi").value, 10) || null,
        distanza_km: parseFloat(document.getElementById("input-vital-distanza").value) || null,
        calorie_attive_kcal: parseFloat(document.getElementById("input-vital-calorie").value) || null,
        bpm_riposo: parseFloat(document.getElementById("input-vital-bpm-riposo").value) || null,
        bpm_max: parseFloat(document.getElementById("input-vital-bpm-max").value) || null,
        pressione_sistolica: parseFloat(document.getElementById("input-vital-sistolica").value) || null,
        pressione_diastolica: parseFloat(document.getElementById("input-vital-diastolica").value) || null,
        spo2_media: parseFloat(document.getElementById("input-vital-spo2-media").value) || null,
        spo2_min: parseFloat(document.getElementById("input-vital-spo2-min").value) || null,
        indice_apnea_ahi: parseFloat(document.getElementById("input-vital-ahi").value) || null,
        episodi_apnea_totali: parseInt(document.getElementById("input-vital-episodi-apnea").value, 10) || null,
        durata_desaturazione_minuti: parseFloat(document.getElementById("input-vital-durata-desat").value) || null,
        ore_sonno_totali: parseFloat(document.getElementById("input-vital-ore-sonno").value) || null,
        hrv_ms: parseFloat(document.getElementById("input-vital-hrv").value) || null,
        frequenza_respiratoria: parseFloat(document.getElementById("input-vital-frequenza-resp").value) || null,
        note: document.getElementById("input-vital-note").value || null
      };

      try {
        const res = await fetch("/api/health-metrics/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          if (window.toast) {
            window.toast.success("Parametri vitali salvati con successo!");
          }
          toggleModal(false);
          await loadData();
        } else {
          const err = await res.json();
          if (window.toast) {
            window.toast.error("Errore salvataggio: " + (err.detail || "Errore sconosciuto"));
          }
        }
      } catch (e) {
        if (window.toast) {
          window.toast.error("Errore di rete: " + e.message);
        }
      }
    };
  }

  await loadData();
}
