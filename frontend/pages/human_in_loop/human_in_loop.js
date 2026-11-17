window.init_human_in_loop_page = function(params = {}) {
  const previewBox = document.getElementById("original-preview-box");
  const dataInput = document.getElementById("rev-data-prelievo");
  const labInput = document.getElementById("rev-laboratorio");
  const tbody = document.getElementById("rev-analiti-tbody");
  const addRowBtn = document.getElementById("btn-add-analyte-row");
  const saveBtn = document.getElementById("btn-save-confirmed");

  let refertoId = "";
  let items = [];

  if (params.uploadResult) {
    const res = params.uploadResult;
    refertoId = res.referto_id;
    dataInput.value = res.data_prelievo || "";
    labInput.value = res.laboratorio || "";
    items = res.analiti || [];

    if (res.preview_image_base64) {
      previewBox.innerHTML = `<img src="data:image/png;base64,${res.preview_image_base64}" alt="Documento">`;
    } else if (res.extracted_text) {
      previewBox.innerHTML = `<div class="preview-text-box">${res.extracted_text}</div>`;
    }
  } else if (params.referto) {
    const ref = params.referto;
    refertoId = ref.id;
    dataInput.value = ref.data_prelievo || "";
    labInput.value = ref.laboratorio || "";
    items = ref.analiti || [];
    previewBox.innerHTML = `<p style="color:var(--text-muted); padding:30px;">File salvato e protetto in archivio cifrato.</p>`;
  }

  const renderRows = () => {
    tbody.innerHTML = "";
    items.forEach((item, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><input type="text" class="table-input item-name" value="${item.nome_standardizzato || ''}"></td>
        <td><input type="text" class="table-input item-val" value="${item.valore_numerico !== null && item.valore_numerico !== undefined ? item.valore_numerico : (item.valore_testuale || '')}"></td>
        <td><input type="text" class="table-input item-unit" value="${item.unita_misura || ''}"></td>
        <td><input type="number" step="any" class="table-input item-min" value="${item.range_min !== null && item.range_min !== undefined ? item.range_min : ''}"></td>
        <td><input type="number" step="any" class="table-input item-max" value="${item.range_max !== null && item.range_max !== undefined ? item.range_max : ''}"></td>
        <td>
          <select class="table-input item-flag">
            <option value="NORMALE" ${item.stato_flag === 'NORMALE' ? 'selected' : ''}>NORMALE</option>
            <option value="BASSO" ${item.stato_flag === 'BASSO' ? 'selected' : ''}>BASSO</option>
            <option value="ALTO" ${item.stato_flag === 'ALTO' ? 'selected' : ''}>ALTO</option>
            <option value="CRITICO_BASSO" ${item.stato_flag === 'CRITICO_BASSO' ? 'selected' : ''}>CRITICO BASSO</option>
            <option value="CRITICO_ALTO" ${item.stato_flag === 'CRITICO_ALTO' ? 'selected' : ''}>CRITICO ALTO</option>
          </select>
        </td>
        <td><button class="btn btn-danger btn-sm btn-remove-row">✕</button></td>
      `;

      tr.querySelector(".btn-remove-row").onclick = () => {
        items.splice(idx, 1);
        renderRows();
      };

      tbody.appendChild(tr);
    });
  };

  addRowBtn.onclick = () => {
    items.push({
      categoria: "Altro",
      nome_esame_originale: "Nuovo Esame",
      nome_standardizzato: "Nuovo Esame",
      valore_numerico: null,
      valore_testuale: "",
      unita_misura: "",
      range_min: null,
      range_max: null,
      stato_flag: "NORMALE"
    });
    renderRows();
  };

  renderRows();

  saveBtn.onclick = async () => {
    if (!refertoId) {
      window.showToast("Nessun referto da confermare.", "error");
      return;
    }

    const rows = tbody.querySelectorAll("tr");
    const updatedAnaliti = [];

    rows.forEach(tr => {
      const name = tr.querySelector(".item-name").value.trim();
      const valRaw = tr.querySelector(".item-val").value.trim();
      const unit = tr.querySelector(".item-unit").value.trim();
      const minRaw = tr.querySelector(".item-min").value.trim();
      const maxRaw = tr.querySelector(".item-max").value.trim();
      const flag = tr.querySelector(".item-flag").value;

      if (name) {
        const numVal = !isNaN(parseFloat(valRaw)) ? parseFloat(valRaw) : null;
        const txtVal = numVal === null ? valRaw : null;
        const minVal = minRaw !== "" && !isNaN(parseFloat(minRaw)) ? parseFloat(minRaw) : null;
        const maxVal = maxRaw !== "" && !isNaN(parseFloat(maxRaw)) ? parseFloat(maxRaw) : null;

        updatedAnaliti.append || updatedAnaliti.push({
          categoria: "Esami Revisionati",
          nome_esame_originale: name,
          nome_standardizzato: name,
          valore_numerico: numVal,
          valore_testuale: txtVal,
          unita_misura: unit,
          range_min: minVal,
          range_max: maxVal,
          stato_flag: flag,
          data_prelievo: dataInput.value,
          laboratorio: labInput.value,
          note_referto: null
        });
      }
    });

    const payload = {
      referto_id: refertoId,
      data_prelievo: dataInput.value,
      laboratorio: labInput.value,
      note: "Revisionato e confermato dall'utente.",
      analiti: updatedAnaliti
    };

    saveBtn.disabled = true;
    saveBtn.textContent = "Salvataggio in corso...";

    try {
      await window.api.post("/api/referti/confirm-revision", payload);
      window.showToast("Referto confermato e salvato nell'archivio protetto!", "success");
      window.router.navigate("dashboard");
    } catch (err) {
      saveBtn.disabled = false;
      saveBtn.textContent = "✓ Conferma e Salva nel Database";
      window.showToast(err.message, "error");
    }
  };
};
