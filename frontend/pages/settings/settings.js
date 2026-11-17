window.init_settings_page = async function() {
  const providerSelect = document.getElementById("set-provider");
  const ollamaSection = document.getElementById("ollama-config-section");
  const geminiSection = document.getElementById("gemini-config-section");
  const ollamaUrlInput = document.getElementById("set-ollama-url");
  const ollamaModelSelect = document.getElementById("set-ollama-model");
  const ollamaVisionSelect = document.getElementById("set-ollama-vision-model");
  const detectOllamaBtn = document.getElementById("btn-detect-ollama");
  const geminiKeyInput = document.getElementById("set-gemini-key");
  const geminiModelSelect = document.getElementById("set-gemini-model");
  const piiCheck = document.getElementById("set-pii-scrubbing");
  const autoLockInput = document.getElementById("set-auto-lock");
  const saveBtn = document.getElementById("btn-save-settings");
  const hotReloadBtn = document.getElementById("btn-hot-reload");

  const currentShaEl = document.getElementById("update-current-sha");
  const resultMsgEl = document.getElementById("update-result-msg");
  const checkUpdateBtn = document.getElementById("btn-check-update");
  const applyUpdateBtn = document.getElementById("btn-apply-update");

  providerSelect.onchange = () => {
    const isGemini = providerSelect.value === "gemini";
    ollamaSection.style.display = isGemini ? "none" : "flex";
    geminiSection.style.display = isGemini ? "flex" : "none";
  };

  const loadOllamaModels = async () => {
    try {
      const data = await window.api.get("/api/settings/ollama-models");
      if (ollamaModelSelect) {
        ollamaModelSelect.innerHTML = "";
      }
      if (ollamaVisionSelect) {
        ollamaVisionSelect.innerHTML = "";
      }
      if (data.models && data.models.length > 0) {
        data.models.forEach(m => {
          const optText = document.createElement("option");
          optText.value = m.name;
          optText.textContent = `${m.name} ${m.is_vision ? '(Vision)' : ''} [${m.parameter_size || ''}]`;
          if (ollamaModelSelect) {
            ollamaModelSelect.appendChild(optText);
          }

          if (m.is_vision || m.name.toLowerCase().includes("vision") || m.name.toLowerCase().includes("llava")) {
            const optVision = document.createElement("option");
            optVision.value = m.name;
            optVision.textContent = `${m.name} [Vision Nativa]`;
            if (ollamaVisionSelect) {
              ollamaVisionSelect.appendChild(optVision);
            }
          }
        });
        if (ollamaVisionSelect && ollamaVisionSelect.children.length === 0) {
          data.models.forEach(m => {
            const optFallback = document.createElement("option");
            optFallback.value = m.name;
            optFallback.textContent = `${m.name} (Adattivo)`;
            ollamaVisionSelect.appendChild(optFallback);
          });
        }
      } else {
        if (ollamaModelSelect) {
          ollamaModelSelect.innerHTML = '<option value="llama3.1:latest">llama3.1:latest (Nessun modello trovato)</option>';
        }
        if (ollamaVisionSelect) {
          ollamaVisionSelect.innerHTML = '<option value="llama3.2-vision:latest">llama3.2-vision:latest (Scarica con: ollama pull llama3.2-vision)</option>';
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (detectOllamaBtn) {
    detectOllamaBtn.onclick = async () => {
      detectOllamaBtn.disabled = true;
      detectOllamaBtn.textContent = "Rilevamento in corso...";
      await loadOllamaModels();
      detectOllamaBtn.disabled = false;
      detectOllamaBtn.textContent = "🔄 Rileva Modelli Installati in Ollama";
      window.showToast("Elenco modelli Ollama sincronizzato con successo.", "info");
    };
  }

  if (hotReloadBtn) {
    hotReloadBtn.onclick = async () => {
      hotReloadBtn.disabled = true;
      hotReloadBtn.textContent = "Ricaricamento a caldo...";
      try {
        const res = await window.api.post("/api/settings/reload-system", {});
        window.showToast(`Ricaricamento completato! ${res.biomarker_scan ? res.biomarker_scan.total_algorithms_registered + ' algoritmi sincronizzati.' : ''}`, "success");
        setTimeout(() => {
          window.location.reload(true);
        }, 800);
      } catch (e) {
        window.showToast("Errore ricaricamento: " + e.message, "error");
      } finally {
        hotReloadBtn.disabled = false;
        hotReloadBtn.textContent = "⚡ Ricarica Sistema & Rescan Algoritmi";
      }
    };
  }

  try {
    const s = await window.api.get("/api/settings");
    providerSelect.value = s.ai_provider || "ollama";
    providerSelect.dispatchEvent(new Event("change"));

    ollamaUrlInput.value = s.ollama_url || "http://127.0.0.1:11434";
    await loadOllamaModels();
    if (s.ollama_model && ollamaModelSelect) {
      ollamaModelSelect.value = s.ollama_model;
    }
    if (s.ollama_vision_model && ollamaVisionSelect) {
      ollamaVisionSelect.value = s.ollama_vision_model;
    }

    if (s.gemini_api_key) {
      geminiKeyInput.value = s.gemini_api_key;
    }
    if (s.gemini_model) {
      geminiModelSelect.value = s.gemini_model;
    }
    piiCheck.checked = s.pii_scrubbing !== false;
    autoLockInput.value = s.auto_lock_minutes || 15;
  } catch (err) {
    console.error(err);
  }

  saveBtn.onclick = async () => {
    const payload = {
      ai_provider: providerSelect.value,
      ollama_model: ollamaModelSelect ? ollamaModelSelect.value : "llama3.1:latest",
      ollama_vision_model: ollamaVisionSelect ? ollamaVisionSelect.value : "llama3.2-vision:latest",
      ollama_url: ollamaUrlInput.value,
      gemini_api_key: geminiKeyInput.value,
      gemini_model: geminiModelSelect.value,
      pii_scrubbing: piiCheck.checked,
      auto_lock_minutes: parseInt(autoLockInput.value, 10) || 15
    };

    try {
      await window.api.post("/api/settings", payload);
      window.showToast("Impostazioni e modelli salvati con crittografia nel vault.", "success");
    } catch (err) {
      window.showToast(err.message, "error");
    }
  };

  checkUpdateBtn.onclick = async () => {
    checkUpdateBtn.disabled = true;
    checkUpdateBtn.textContent = "Verifica in corso...";
    resultMsgEl.textContent = "";

    try {
      const data = await window.api.get("/api/updater/check");
      currentShaEl.textContent = data.current_sha || "Iniziale";

      if (data.has_update) {
        resultMsgEl.innerHTML = `<span style="color:var(--status-normal);">Nuovo aggiornamento disponibile: <strong>${data.remote_sha.substring(0, 7)}</strong> (${data.message || 'Miglioramenti'})</span>`;
        applyUpdateBtn.style.display = "inline-flex";
      } else {
        resultMsgEl.innerHTML = `<span style="color:var(--text-muted);">Il software e aggiornato all'ultimo commit.</span>`;
        applyUpdateBtn.style.display = "none";
      }
    } catch (err) {
      resultMsgEl.innerHTML = `<span style="color:var(--status-danger);">Errore verifica: ${err.message}</span>`;
    } finally {
      checkUpdateBtn.disabled = false;
      checkUpdateBtn.textContent = "🔍 Verifica Nuovi Commit";
    }
  };

  applyUpdateBtn.onclick = async () => {
    applyUpdateBtn.disabled = true;
    applyUpdateBtn.textContent = "Applicazione e ricompilazione in corso...";

    try {
      await window.api.post("/api/updater/apply", {});
      window.showToast("Aggiornamento applicato con successo! Ricaricamento interfaccia in corso...", "success");
      resultMsgEl.innerHTML = `<span style="color:var(--status-normal);">Aggiornato all'ultimo commit. Riavvio immediato...</span>`;
      setTimeout(() => {
        window.location.reload(true);
      }, 1200);
    } catch (err) {
      window.showToast(err.message, "error");
      applyUpdateBtn.disabled = false;
      applyUpdateBtn.textContent = "⬇ Applica Aggiornamento & Ricarica";
    }
  };
};
