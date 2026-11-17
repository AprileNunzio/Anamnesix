window.init_auth_page = async function() {
  const form = document.getElementById("auth-form");
  const passwordInput = document.getElementById("auth-password");
  const enableDpapiCheck = document.getElementById("auth-enable-dpapi");
  const submitBtn = document.getElementById("auth-submit-btn");
  const dpapiBtn = document.getElementById("auth-dpapi-btn");
  const titleLabel = document.getElementById("auth-password-label");

  let isSetup = false;

  try {
    const status = await window.api.get("/api/auth/status");
    isSetup = status.is_initial_setup;

    if (isSetup) {
      titleLabel.textContent = "Crea Nuova Master Password di Sicurezza";
      submitBtn.textContent = "Inizializza Archivio Cifrato";
      document.querySelector(".auth-subtitle").textContent = "Primo avvio: crea la tua chiave di cifratura principale";
    } else {
      titleLabel.textContent = "Master Password di Sblocco";
      submitBtn.textContent = "Sblocca Archivio Clinico";
      if (status.dpapi_available) {
        dpapiBtn.style.display = "block";
      }
    }
  } catch (err) {
    console.error(err);
  }

  dpapiBtn.onclick = async () => {
    try {
      await window.api.post("/api/auth/unlock-dpapi", {});
      window.showToast("Accesso rapido DPAPI riuscito.", "success");
      await window.initFamilySelector();
      window.router.navigate("dashboard");
    } catch (err) {
      window.showToast("Sblocco rapido non riuscito. Inserisci la password.", "error");
    }
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const password = passwordInput.value;
    const enableDpapi = enableDpapiCheck.checked;

    if (!password) return;

    submitBtn.disabled = true;
    submitBtn.textContent = "Derivazione Argon2id in corso...";

    try {
      const endpoint = isSetup ? "/api/auth/setup" : "/api/auth/unlock";
      await window.api.post(endpoint, {
        password: password,
        enable_dpapi: enableDpapi
      });

      window.showToast("Archivio crittografico sbloccato.", "success");
      await window.initFamilySelector();
      window.router.navigate("dashboard");
    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.textContent = isSetup ? "Inizializza Archivio Cifrato" : "Sblocca Archivio Clinico";
      window.showToast(err.message || "Password errata.", "error");
    }
  };
};
