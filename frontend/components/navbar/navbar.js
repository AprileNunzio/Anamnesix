window.initNavbar = function() {
  document.querySelectorAll(".nav-link").forEach(btn => {
    btn.onclick = () => {
      const route = btn.dataset.route;
      if (route) {
        window.router.navigate(route);
      }
    };
  });

  const lockBtn = document.getElementById("lock-vault-btn");
  if (lockBtn) {
    lockBtn.onclick = async () => {
      await window.api.post("/api/auth/lock", {});
      window.showToast("Sessione bloccata. Chiavi azzerate in RAM.", "info");
      window.router.navigate("auth");
    };
  }

  const themeBtn = document.getElementById("theme-toggle-btn");
  const themeIcon = document.getElementById("theme-icon");
  if (themeBtn) {
    themeBtn.onclick = () => {
      const isDark = document.documentElement.getAttribute("data-theme") !== "light";
      if (isDark) {
        document.documentElement.setAttribute("data-theme", "light");
        themeIcon.textContent = "☀️";
      } else {
        document.documentElement.removeAttribute("data-theme");
        themeIcon.textContent = "🌙";
      }
    };
  }

  window.addEventListener("session-locked", () => {
    window.router.navigate("auth");
  });
};
