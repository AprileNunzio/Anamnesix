window.init_referti_page = async function() {
  const dropzone = document.getElementById("upload-dropzone");
  const fileInput = document.getElementById("file-input");
  const spinner = document.getElementById("upload-spinner");
  const tbody = document.getElementById("referti-table-body");
  const manualModal = document.getElementById("manual-modal");
  const openManualBtn = document.getElementById("btn-open-manual-modal");
  const closeManualBtn = document.getElementById("close-manual-modal");
  const cancelManualBtn = document.getElementById("btn-cancel-manual");
  const saveManualBtn = document.getElementById("btn-save-manual");

  const todayStr = new Date().toISOString().split("T")[0];
  const manualDateInput = document.getElementById("manual-data");
  if (manualDateInput) {
    manualDateInput.value = todayStr;
  }

  function toggleManualModal(show) {
    if (manualModal) {
      manualModal.style.display = show ? "flex" : "none";
    }
  }

  if (openManualBtn) {
    openManualBtn.onclick = () => toggleManualModal(true);
  }
  if (closeManualBtn) {
    closeManualBtn.onclick = () => toggleManualModal(false);
  }
  if (cancelManualBtn) {
    cancelManualBtn.onclick = () => toggleManualModal(false);
  }

  if (saveManualBtn) {
    saveManualBtn.onclick = async () => {
      const dataVal = document.getElementById("manual-data").value;
      const nomeVal = document.getElementById("manual-nome").value;
      const unitaVal = document.getElementById("manual-unita").value;
      const catVal = document.getElementById("manual-categoria").value;
      const labVal = document.getElementById("manual-laboratorio").value || "Inserimento Manuale";
      const numValStr = document.getElementById("manual-valore-num").value;
      const txtVal = document.getElementById("manual-valore-txt").value || null;
      const minValStr = document.getElementById("manual-range-min").value;
      const maxValStr = document.getElementById("manual-range-max").value;
      const noteVal = document.getElementById("manual-note").value || null;

      if (!dataVal || !nomeVal || !unitaVal) {
        window.showToast("Compila data, nome esame e unita di misura.", "warning");
        return;
      }

      const numVal = numValStr !== "" ? parseFloat(numValStr) : null;
      const minVal = minValStr !== "" ? parseFloat(minValStr) : null;
      const maxVal = maxValStr !== "" ? parseFloat(maxValStr) : null;

      const payload = {
        data_prelievo: dataVal,
        laboratorio: labVal,
        categoria: catVal,
        nome_esame_originale: nomeVal,
        nome_standardizzato: nomeVal,
        valore_numerico: numVal,
        valore_testuale: txtVal,
        unita_misura: unitaVal,
        range_min: minVal,
        range_max: maxVal,
        note_referto: noteVal
      };

      try {
        const res = await window.api.post("/api/referti/manual-entry", payload);
        window.showToast("Parametro registrato con successo (" + res.stato_flag + ")!", "success");
        toggleManualModal(false);
        document.getElementById("manual-nome").value = "";
        document.getElementById("manual-valore-num").value = "";
        document.getElementById("manual-valore-txt").value = "";
        loadReferti();
      } catch (err) {
        window.showToast("Errore inserimento: " + err.message, "error");
      }
    };
  }

  const loadReferti = async () => {
    try {
      const data = await window.api.get("/api/referti");
      if (data && data.length > 0) {
        tbody.innerHTML = "";
        data.forEach(r => {
          const tr = document.createElement("tr");
          const isConfirmed = r.stato_revisione === "CONFERMATO";
          const badgeClass = isConfirmed ? "badge-normal" : "badge-warning";

          tr.innerHTML = `
            <td><strong>${r.data_prelievo}</strong></td>
            <td>${r.laboratorio}</td>
            <td>${r.totale_analiti || 0}</td>
            <td><strong style="color: ${r.anomalie_count > 0 ? 'var(--status-danger)' : 'var(--status-normal)'};">${r.anomalie_count || 0}</strong></td>
            <td><span class="badge ${badgeClass}">${r.stato_revisione}</span></td>
            <td><span style="font-size:var(--font-xs); color:var(--text-muted);">${r.note || '-'}</span></td>
            <td>
              <div style="display:flex; gap:6px;">
                <button class="btn btn-secondary btn-sm btn-view-ref">Revisiona / Visualizza</button>
                <button class="btn btn-danger btn-sm btn-del-ref">Elimina</button>
              </div>
            </td>
          `;

          tr.querySelector(".btn-view-ref").onclick = async () => {
            const fullRef = await window.api.get(`/api/referti/${r.id}`);
            window.router.navigate("human_in_loop", { referto: fullRef });
          };

          tr.querySelector(".btn-del-ref").onclick = async () => {
            if (confirm("Eliminare definitivamente questo referto e tutti i suoi dati?")) {
              await window.api.delete(`/api/referti/${r.id}`);
              window.showToast("Referto eliminato.", "info");
              loadReferti();
            }
          };

          tbody.appendChild(tr);
        });
      } else {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px; color: var(--text-muted);">Nessun referto presente per questo profilo.</td></tr>`;
      }
    } catch (err) {
      console.error(err);
    }
  };

  window.refreshRefertiTable = loadReferti;

  const handleUpload = async (file) => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await window.api.post("/api/referti/upload", formData);
      if (res.job_id) {
        window.showToast("Referto preso in carico! L'analisi procede in background. Puoi navigare liberamente.", "info");
        if (window.taskTracker) {
          window.taskTracker.track(res.job_id, file.name, (resultData) => {
            if (resultData && resultData.referto_id) {
              window.router.navigate("human_in_loop", { uploadResult: resultData });
            }
          });
        }
      } else if (res.data) {
        window.showToast("Documento analizzato! Procedi con la revisione fianco a fianco.", "success");
        window.router.navigate("human_in_loop", { uploadResult: res.data });
      }
    } catch (err) {
      window.showToast(err.message, "error");
    }
  };

  fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
      handleUpload(fileInput.files[0]);
    }
  };

  dropzone.ondragover = (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  };

  dropzone.ondragleave = () => {
    dropzone.classList.remove("dragover");
  };

  dropzone.ondrop = (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  loadReferti();
};
