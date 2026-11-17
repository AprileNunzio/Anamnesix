async function init_jobs_page() {
  const launchBtn = document.getElementById("btn-launch-deep-job");
  const cancelBtn = document.getElementById("btn-cancel-current-job");
  const activeSection = document.getElementById("active-jobs-container");
  const progressFill = document.getElementById("job-progress-fill");
  const stepText = document.getElementById("job-step-text");
  const percentageText = document.getElementById("job-percentage-text");
  const resultCard = document.getElementById("job-result-card");
  const resultContent = document.getElementById("job-result-content");
  const closeResultBtn = document.getElementById("btn-close-result");

  let currentRunningJobId = null;
  let pollingInterval = null;

  async function loadJobsList() {
    try {
      const res = await fetch("/api/jobs/list");
      if (res.ok) {
        const jobs = await res.json();
        renderTable(jobs);
        const running = jobs.find(j => j.status === "IN_ESECUZIONE" || j.status === "IN_CODA");
        if (running) {
          trackRunningJob(running.id);
        } else if (currentRunningJobId) {
          stopTracking();
        }
      }
    } catch (err) {
      if (window.toast) {
        window.toast.error("Errore caricamento lista job: " + err.message);
      }
    }
  }

  function trackRunningJob(jobId) {
    currentRunningJobId = jobId;
    if (activeSection) {
      activeSection.style.display = "block";
    }
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    pollingInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/jobs/status/${jobId}`);
        if (res.ok) {
          const job = await res.json();
          if (progressFill) {
            progressFill.style.width = `${job.progress}%`;
          }
          if (stepText) {
            stepText.textContent = job.current_step || "Elaborazione in corso...";
          }
          if (percentageText) {
            percentageText.textContent = `${job.progress}%`;
          }

          if (job.status === "COMPLETATO" || job.status === "FALLITO" || job.status === "ANNULLATO") {
            stopTracking();
            if (window.toast) {
              if (job.status === "COMPLETATO") {
                window.toast.success("Analisi clinica deep reasoning completata!");
                showJobResult(job);
              } else {
                window.toast.warning("Job terminato con stato: " + job.status);
              }
            }
            await loadJobsList();
          }
        }
      } catch (e) {
        stopTracking();
      }
    }, 2000);
  }

  function stopTracking() {
    currentRunningJobId = null;
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
    if (activeSection) {
      activeSection.style.display = "none";
    }
  }

  function showJobResult(job) {
    if (!resultCard || !resultContent) {
      return;
    }
    let parsed = {};
    try {
      parsed = JSON.parse(job.result_json);
    } catch (e) {
      parsed = { relazione_clinica: job.result_json };
    }
    resultContent.textContent = parsed.relazione_clinica || "Nessun testo refertato.";
    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth" });
  }

  if (closeResultBtn) {
    closeResultBtn.onclick = () => {
      if (resultCard) {
        resultCard.style.display = "none";
      }
    };
  }

  function renderTable(list) {
    const tbody = document.getElementById("jobs-tbody");
    if (!tbody) {
      return;
    }
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:18px; color:var(--text-muted);">Nessun job di calcolo eseguito. Clicca sul pulsante in alto per avviare una perizia deep reasoning.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(item => `
      <tr>
        <td style="font-weight:600;">${item.created_at.replace("T", " ").substring(0, 19)}</td>
        <td>${item.job_type}</td>
        <td>
          <span class="kpi-badge ${item.status === 'COMPLETATO' ? 'badge-normal' : (item.status === 'IN_ESECUZIONE' ? 'badge-warning' : 'badge-danger')}">
            ${item.status}
          </span>
        </td>
        <td style="font-family:var(--font-mono); font-weight:700;">${item.progress}%</td>
        <td style="max-width:280px; overflow:hidden; text-overflow:ellipsis;">${item.current_step || '--'}</td>
        <td>
          ${item.status === 'COMPLETATO' ? `<button class="btn btn-primary" style="padding:2px 8px; font-size:0.7rem;" onclick="viewSavedJobResult('${item.id}')">Leggi Relazione</button>` : ''}
          ${item.status === 'IN_ESECUZIONE' || item.status === 'IN_CODA' ? `<button class="btn btn-secondary" style="padding:2px 8px; font-size:0.7rem; color:var(--status-danger);" onclick="cancelRunningJob('${item.id}')">Annulla</button>` : ''}
        </td>
      </tr>
    `).join("");
  }

  window.viewSavedJobResult = async function(id) {
    try {
      const res = await fetch(`/api/jobs/status/${id}`);
      if (res.ok) {
        const job = await res.json();
        showJobResult(job);
      }
    } catch (err) {
      if (window.toast) {
        window.toast.error("Errore recupero dettagli: " + err.message);
      }
    }
  };

  window.cancelRunningJob = async function(id) {
    if (!confirm("Sei sicuro di voler interrompere questo job?")) {
      return;
    }
    try {
      const res = await fetch(`/api/jobs/cancel/${id}`, { method: "POST" });
      if (res.ok) {
        if (window.toast) {
          window.toast.success("Job annullato.");
        }
        stopTracking();
        await loadJobsList();
      }
    } catch (err) {
      if (window.toast) {
        window.toast.error("Errore annullamento: " + err.message);
      }
    }
  };

  if (cancelBtn) {
    cancelBtn.onclick = () => {
      if (currentRunningJobId) {
        window.cancelRunningJob(currentRunningJobId);
      }
    };
  }

  if (launchBtn) {
    launchBtn.onclick = async () => {
      try {
        const res = await fetch("/api/jobs/launch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_type: "LONGITUDINAL_DEEP_ANALYSIS",
            parameters: { modalita: "deep_multi_system_synthesis" }
          })
        });
        if (res.ok) {
          const data = await res.json();
          if (window.toast) {
            window.toast.success("Job di Deep AI Reasoning avviato in background!");
          }
          trackRunningJob(data.job_id);
          await loadJobsList();
        } else {
          const err = await res.json();
          if (window.toast) {
            window.toast.error("Errore avvio: " + (err.detail || "Errore"));
          }
        }
      } catch (e) {
        if (window.toast) {
          window.toast.error("Errore di rete: " + e.message);
        }
      }
    };
  }

  await loadJobsList();
}
