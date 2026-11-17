class PageRouter {
  constructor() {
    this.routes = {
      "auth": { path: "pages/auth/auth", title: "Sblocco Archivio" },
      "dashboard": { path: "pages/dashboard/dashboard", title: "Cockpit Clinico" },
      "profiles": { path: "pages/profiles/profiles", title: "Gestione Famiglia" },
      "referti": { path: "pages/referti/referti", title: "Esami & Inserimento Manuale" },
      "body_composition": { path: "pages/body_composition/body_composition", title: "Composizione Corporea & BIA" },
      "vitals": { path: "pages/vitals/vitals", title: "Vitals, Passi & Apnee Notturne" },
      "fertility": { path: "pages/fertility/fertility", title: "Suite Fertilita & Imaging" },
      "trends": { path: "pages/trends/trends", title: "Trend Biomarcatori" },
      "correlations": { path: "pages/correlations/correlations", title: "Correlazioni & Second Opinion" },
      "jobs": { path: "pages/jobs/jobs", title: "Deep AI Reasoning & Long-Running Jobs" },
      "human_in_loop": { path: "pages/human_in_loop/human_in_loop", title: "Revisione Clinica Assistita" },
      "chat_rag": { path: "pages/chat_rag/chat_rag", title: "Chat Clinica Intelligente" },
      "dossier": { path: "pages/dossier/dossier", title: "Esportazione Flusso Dati & Dossier" },
      "settings": { path: "pages/settings/settings", title: "Configurazione Sistema" }
    };
    this.currentRoute = null;
    this.loadedStyles = new Set();
    this.loadedScripts = new Set();
  }

  async navigate(routeKey, params = {}) {
    if (!this.routes[routeKey]) {
      routeKey = "auth";
    }

    const route = this.routes[routeKey];
    this.currentRoute = routeKey;

    const cssPath = `${route.path}.css`;
    if (!this.loadedStyles.has(cssPath)) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = `${cssPath}?v=${Date.now()}`;
      document.head.appendChild(link);
      this.loadedStyles.add(cssPath);
    }

    try {
      const res = await fetch(`${route.path}.html?v=${Date.now()}`);
      const html = await res.text();
      const contentEl = document.getElementById("content-outlet");
      if (contentEl) {
        contentEl.innerHTML = html;
      }

      const scriptPath = `${route.path}.js`;
      const oldScript = document.getElementById(`script-${routeKey}`);
      if (oldScript) {
        oldScript.remove();
      }

      const script = document.createElement("script");
      script.id = `script-${routeKey}`;
      script.src = `${scriptPath}?t=${Date.now()}`;
      script.onload = () => {
        const initFn = window[`init_${routeKey}_page`];
        if (typeof initFn === "function") {
          initFn(params);
        }
      };
      document.body.appendChild(script);

      document.querySelectorAll(".sidebar-nav .nav-link").forEach(btn => {
        if (btn.getAttribute("data-route") === routeKey) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
      });

      const titleEl = document.getElementById("header-page-title");
      if (titleEl) {
        titleEl.textContent = route.title;
      }
    } catch (err) {
      const contentEl = document.getElementById("content-outlet");
      if (contentEl) {
        contentEl.innerHTML = `<div class="clinical-card" style="margin:20px; color:var(--status-danger);">Errore caricamento vista: ${err.message}</div>`;
      }
    }
  }
}

window.router = new PageRouter();
