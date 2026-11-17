async function init_body_composition_page() {
  const modal = document.getElementById("body-modal");
  const openBtn = document.getElementById("btn-open-body-modal");
  const closeBtn = document.getElementById("close-body-modal");
  const cancelBtn = document.getElementById("btn-cancel-body");
  const saveBtn = document.getElementById("btn-save-body");

  const todayStr = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("input-body-data");
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
      const resLatest = await fetch("/api/body-composition/latest");
      if (resLatest.ok) {
        const latest = await resLatest.json();
        updateKpis(latest);
      }

      const resHistory = await fetch("/api/body-composition/history");
      if (resHistory.ok) {
        const history = await resHistory.json();
        renderTable(history);
      }
    } catch (err) {
      if (window.toast) {
        window.toast.error("Errore caricamento dati corporei: " + err.message);
      }
    }
  }

  function updateKpis(data) {
    if (!data || !data.peso_kg) {
      return;
    }
    const pesoEl = document.getElementById("kpi-peso");
    const pesoSub = document.getElementById("kpi-peso-sub");
    if (pesoEl) {
      pesoEl.textContent = data.peso_kg.toFixed(1);
    }
    if (pesoSub) {
      pesoSub.textContent = "Data: " + data.data_misurazione;
    }

    const bmiEl = document.getElementById("kpi-bmi");
    const bmiSub = document.getElementById("kpi-bmi-sub");
    if (bmiEl && data.bmi) {
      bmiEl.textContent = data.bmi.toFixed(1);
      if (bmiSub) {
        if (data.bmi < 18.5) {
          bmiSub.className = "kpi-badge badge-warning";
          bmiSub.textContent = "Sottopeso";
        } else if (data.bmi <= 24.9) {
          bmiSub.className = "kpi-badge badge-normal";
          bmiSub.textContent = "Normopeso";
        } else if (data.bmi <= 29.9) {
          bmiSub.className = "kpi-badge badge-warning";
          bmiSub.textContent = "Sovrappeso";
        } else {
          bmiSub.className = "kpi-badge badge-danger";
          bmiSub.textContent = "Obesita";
        }
      }
    }

    const acquaEl = document.getElementById("kpi-acqua");
    if (acquaEl && data.acqua_totale_pct) {
      acquaEl.textContent = data.acqua_totale_pct.toFixed(1);
    }

    const ossaEl = document.getElementById("kpi-ossa-muscolo");
    if (ossaEl) {
      const ossaTxt = data.massa_ossea_kg ? data.massa_ossea_kg.toFixed(1) : "--";
      const muscTxt = data.massa_muscolare_kg ? data.massa_muscolare_kg.toFixed(1) : "--";
      ossaEl.textContent = `${ossaTxt} / ${muscTxt}`;
    }

    const viscEl = document.getElementById("kpi-viscerale");
    if (viscEl) {
      const viscTxt = data.grasso_viscerale !== null && data.grasso_viscerale !== undefined ? data.grasso_viscerale.toString() : "--";
      const bmrTxt = data.metabolismo_basale_kcal ? data.metabolismo_basale_kcal.toString() : "--";
      viscEl.textContent = `${viscTxt} / ${bmrTxt}`;
    }
  }

  function renderTable(list) {
    const tbody = document.getElementById("body-comp-tbody");
    if (!tbody) {
      return;
    }
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:18px; color:var(--text-muted);">Nessuna rilevazione corporea registrata. Clicca su "Nuova Rilevazione Bilancia" per iniziare.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(item => `
      <tr>
        <td style="font-weight:600;">${item.data_misurazione}</td>
        <td style="font-family:var(--font-mono); font-weight:700;">${item.peso_kg ? item.peso_kg.toFixed(1) : '--'}</td>
        <td>${item.bmi ? item.bmi.toFixed(1) : '--'}</td>
        <td>${item.massa_grassa_pct ? item.massa_grassa_pct.toFixed(1) + '%' : '--'}</td>
        <td>${item.acqua_totale_pct ? item.acqua_totale_pct.toFixed(1) + '%' : '--'}</td>
        <td>${item.massa_muscolare_kg ? item.massa_muscolare_kg.toFixed(1) : '--'}</td>
        <td>${item.massa_ossea_kg ? item.massa_ossea_kg.toFixed(1) : '--'}</td>
        <td>${item.grasso_viscerale !== null && item.grasso_viscerale !== undefined ? item.grasso_viscerale : '--'}</td>
        <td>${item.metabolismo_basale_kcal ? item.metabolismo_basale_kcal + ' kcal' : '--'}</td>
        <td>
          <button class="btn btn-secondary" style="padding:2px 8px; font-size:0.7rem;" onclick="deleteBodyEntry('${item.id}')">Elimina</button>
        </td>
      </tr>
    `).join("");
  }

  window.deleteBodyEntry = async function(id) {
    if (!confirm("Confermi di voler eliminare questa misurazione?")) {
      return;
    }
    try {
      const res = await fetch(`/api/body-composition/${id}`, { method: "DELETE" });
      if (res.ok) {
        if (window.toast) {
          window.toast.success("Misurazione eliminata.");
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
      const dataVal = document.getElementById("input-body-data").value;
      const pesoVal = parseFloat(document.getElementById("input-body-peso").value);
      if (!dataVal || isNaN(pesoVal)) {
        if (window.toast) {
          window.toast.warning("Inserisci almeno la data e il peso corporeo.");
        }
        return;
      }

      const altVal = parseFloat(document.getElementById("input-body-altezza").value) || null;
      const grassoVal = parseFloat(document.getElementById("input-body-grasso").value) || null;
      const acquaVal = parseFloat(document.getElementById("input-body-acqua").value) || null;
      const muscoloVal = parseFloat(document.getElementById("input-body-muscolo").value) || null;
      const ossaVal = parseFloat(document.getElementById("input-body-ossa").value) || null;
      const visceraleVal = parseFloat(document.getElementById("input-body-viscerale").value) || null;
      const bmrVal = parseFloat(document.getElementById("input-body-bmr").value) || null;
      const etaMetabVal = parseFloat(document.getElementById("input-body-eta-metabolica").value) || null;
      const noteVal = document.getElementById("input-body-note").value || null;

      const payload = {
        data_misurazione: dataVal,
        peso_kg: pesoVal,
        altezza_cm: altVal,
        massa_grassa_pct: grassoVal,
        acqua_totale_pct: acquaVal,
        massa_muscolare_kg: muscoloVal,
        massa_ossea_kg: ossaVal,
        grasso_viscerale: visceraleVal,
        metabolismo_basale_kcal: bmrVal,
        eta_metabolica: etaMetabVal,
        note: noteVal
      };

      try {
        const res = await fetch("/api/body-composition/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          if (window.toast) {
            window.toast.success("Misurazione corporea salvata!");
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
