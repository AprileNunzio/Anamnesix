window.initFamilySelector = async function() {
  const select = document.getElementById("family-profile-select");
  const addBtn = document.getElementById("btn-add-family-member");
  if (!select) return;

  if (addBtn) {
    addBtn.onclick = () => window.router.navigate("profiles");
  }

  try {
    const data = await window.api.get("/api/profiles");
    select.innerHTML = "";

    if (!data.profiles || data.profiles.length === 0) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "Nessun profilo";
      select.appendChild(opt);
      return;
    }

    data.profiles.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = `${p.nome} ${p.cognome} (${p.parentela})`;
      if (p.id === data.active_profile_id) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });

    select.onchange = async () => {
      const selectedId = select.value;
      if (selectedId) {
        await window.api.post(`/api/profiles/active/${selectedId}`, {});
        window.showToast("Profilo clinico selezionato aggiornato.", "success");
        window.dispatchEvent(new CustomEvent("profile-changed", { detail: selectedId }));
        if (window.router.currentRoute) {
          window.router.navigate(window.router.currentRoute);
        }
      }
    };
  } catch (err) {
    console.error(err);
  }
};
