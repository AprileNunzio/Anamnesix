class PageRouter {
  constructor() {
    this.routes = {
      "auth": { path: "pages/auth/auth", title: "Sblocco Archivio" },
      "dashboard": { path: "pages/dashboard/dashboard", title: "Panoramica Clinica" },
      "profiles": { path: "pages/profiles/profiles", title: "Gestione Famiglia" },
      "referti": { path: "pages/referti/referti", title: "Referti e Documenti" },
      "human_in_loop": { path: "pages/human_in_loop/human_in_loop", title: "Revisione Clinica Assistita" },
      "trends": { path: "pages/trends/trends", title: "Trend Biomarcatori" },
      "correlations": { path: "pages/correlations/correlations", title: "Correlazioni & Second Opinion" },
      "fertility": { path: "pages/fertility/fertility", title: "Suite Fertilità & Imaging" },
      "chat_rag": { path: "pages/chat_rag/chat_rag", title: "Chat Clinica Intelligente" },
      "dossier": { path: "pages/dossier/dossier", title: "Esportazione Dossier Medico" },
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
      link.href = cssPath;
      document.head.appendChild(link);
      this.loadedStyles.add(cssPath);
    }

    try {
      const res = await fetch(`${route.path}.html`);
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

      const titleEl = document.getElementById("header-page-title");
      if (titleEl) {
        titleEl.textContent = route.title;
      }

      document.querySelectorAll(".nav-link").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.route === routeKey);
      });

      const sidebarEl = document.getElementById("sidebar");
      const headerEl = document.getElementById("top-header");
      if (sidebarEl && headerEl) {
        if (routeKey === "auth") {
          sidebarEl.style.display = "none";
          headerEl.style.display = "none";
        } else {
          sidebarEl.style.display = "flex";
          headerEl.style.display = "flex";
        }
      }
    } catch (err) {
      console.error(err);
    }
  }
}

window.router = new PageRouter();
