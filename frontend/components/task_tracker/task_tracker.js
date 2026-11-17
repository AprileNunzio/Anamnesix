class TaskTracker {
  constructor() {
    this.jobs = {};
    this.timer = null;
    this.dock = null;
    this.titleEl = null;
    this.filenameEl = null;
    this.stepEl = null;
    this.fillEl = null;
    this.percentEl = null;
    this.actionBtn = null;
    this.closeBtn = null;
  }

  init() {
    this.dock = document.getElementById("floating-task-tracker");
    if (!this.dock) return;

    this.titleEl = document.getElementById("tracker-title");
    this.filenameEl = document.getElementById("tracker-filename");
    this.stepEl = document.getElementById("tracker-step");
    this.fillEl = document.getElementById("tracker-fill");
    this.percentEl = document.getElementById("tracker-percent");
    this.actionBtn = document.getElementById("btn-tracker-action");
    this.closeBtn = document.getElementById("btn-close-tracker");

    if (this.closeBtn) {
      this.closeBtn.onclick = () => {
        this.dock.style.display = "none";
      };
    }
  }

  track(jobId, filename, onCompleteCallback) {
    if (!this.dock) this.init();

    this.jobs[jobId] = {
      jobId: jobId,
      filename: filename,
      onComplete: onCompleteCallback,
      status: "IN_ESECUZIONE",
      progress: 5
    };

    this.renderActiveJob(jobId);
    if (!this.timer) {
      this.startPolling();
    }
  }

  renderActiveJob(jobId) {
    const job = this.jobs[jobId];
    if (!job || !this.dock) return;

    this.dock.style.display = "flex";
    this.filenameEl.textContent = job.filename || "Referto clinico";
    this.stepEl.textContent = job.current_step || "Inizializzazione elaborazione...";
    this.fillEl.style.width = `${job.progress || 5}%`;
    this.percentEl.textContent = `${job.progress || 5}%`;

    if (job.status === "COMPLETATO") {
      this.titleEl.textContent = "Elaborazione Completata";
      this.stepEl.textContent = "Analisi conclusa con successo. Dati pronti.";
      this.fillEl.style.width = "100%";
      this.percentEl.textContent = "100%";
      this.actionBtn.style.display = "inline-block";
      this.actionBtn.onclick = () => {
        if (job.onComplete) {
          job.onComplete(job.result);
        } else if (job.result && job.result.referto_id) {
          window.router.navigate("human_in_loop", { uploadResult: job.result });
        }
        this.dock.style.display = "none";
        delete this.jobs[jobId];
      };
    } else if (job.status === "ERRORE") {
      this.titleEl.textContent = "Errore Elaborazione";
      this.stepEl.textContent = job.error_message || "Errore durante l'elaborazione.";
      this.actionBtn.style.display = "none";
    } else {
      this.titleEl.textContent = "Elaborazione in Background";
      this.actionBtn.style.display = "none";
    }
  }

  startPolling() {
    this.timer = setInterval(async () => {
      const activeJobIds = Object.keys(this.jobs).filter(
        id => this.jobs[id].status === "IN_ESECUZIONE" || this.jobs[id].status === "PENDING"
      );

      if (activeJobIds.length === 0) {
        clearInterval(this.timer);
        this.timer = null;
        return;
      }

      for (const jid of activeJobIds) {
        try {
          const status = await window.api.get(`/api/jobs/status/${jid}`);
          if (status) {
            this.jobs[jid].status = status.status;
            this.jobs[jid].progress = status.progress;
            this.jobs[jid].current_step = status.current_step;
            this.jobs[jid].error_message = status.error_message;

            if (status.status === "COMPLETATO") {
              try {
                this.jobs[jid].result = status.result_json ? JSON.parse(status.result_json) : null;
              } catch (_) {
                this.jobs[jid].result = null;
              }
              window.showToast(`Referto '${this.jobs[jid].filename}' completato con successo!`, "success");
              if (window.refreshRefertiTable) {
                window.refreshRefertiTable();
              }
            } else if (status.status === "ERRORE") {
              window.showToast(`Errore elaborazione referto: ${status.error_message}`, "error");
            }
            this.renderActiveJob(jid);
          }
        } catch (_) {}
      }
    }, 1800);
  }
}

window.taskTracker = new TaskTracker();
