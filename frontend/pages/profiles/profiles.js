window.init_profiles_page = async function() {
  const grid = document.getElementById("profiles-grid");
  const modal = document.getElementById("profile-modal");
  const openBtn = document.getElementById("btn-open-new-profile");
  const closeBtn = document.getElementById("profile-modal-close");
  const cancelBtn = document.getElementById("profile-modal-cancel");
  const form = document.getElementById("profile-form");
  const modalTitle = document.getElementById("profile-modal-title");

  const idInput = document.getElementById("p-id");
  const nomeInput = document.getElementById("p-nome");
  const cognomeInput = document.getElementById("p-cognome");
  const parentelaInput = document.getElementById("p-parentela");
  const dataNascitaInput = document.getElementById("p-data-nascita");
  const sessoInput = document.getElementById("p-sesso");
  const gruppoInput = document.getElementById("p-gruppo");
  const noteInput = document.getElementById("p-note");

  const openModal = (profile = null) => {
    if (profile) {
      modalTitle.textContent = "Modifica Membro della Famiglia";
      idInput.value = profile.id;
      nomeInput.value = profile.nome;
      cognomeInput.value = profile.cognome;
      parentelaInput.value = profile.parentela;
      dataNascitaInput.value = profile.data_nascita;
      sessoInput.value = profile.sesso;
      gruppoInput.value = profile.gruppo_sanguigno || "";
      noteInput.value = profile.note_anamnestiche || "";
    } else {
      modalTitle.textContent = "Aggiungi Membro della Famiglia";
      form.reset();
      idInput.value = "";
    }
    modal.style.display = "flex";
  };

  const closeModal = () => {
    modal.style.display = "none";
  };

  openBtn.onclick = () => openModal(null);
  closeBtn.onclick = closeModal;
  cancelBtn.onclick = closeModal;

  const loadProfiles = async () => {
    try {
      const res = await window.api.get("/api/profiles");
      grid.innerHTML = "";

      res.profiles.forEach(p => {
        const isActive = p.id === res.active_profile_id;
        const card = document.createElement("div");
        card.className = `clinical-card profile-card ${isActive ? "active-profile" : ""}`;

        const initials = `${p.nome.charAt(0)}${p.cognome.charAt(0)}`.toUpperCase();

        card.innerHTML = `
          ${isActive ? '<span class="profile-active-badge">ATTIVO</span>' : ''}
          <div style="display:flex; align-items:center; gap:16px;">
            <div class="profile-avatar">${initials}</div>
            <div class="profile-info">
              <span class="profile-name">${p.nome} ${p.cognome}</span>
              <span class="profile-relation">${p.parentela}</span>
            </div>
          </div>
          <div class="profile-meta-row">
            <span>Nascita: ${p.data_nascita}</span>
            <span>Sesso: ${p.sesso} | Gruppo: ${p.gruppo_sanguigno || 'N/D'}</span>
          </div>
          ${p.note_anamnestiche ? `<p style="font-size:var(--font-xs); color:var(--text-secondary); background:var(--bg-tertiary); padding:8px; border-radius:var(--radius-sm);">${p.note_anamnestiche}</p>` : ''}
          <div style="display:flex; gap:8px; margin-top:auto; padding-top:10px;">
            ${!isActive ? `<button class="btn btn-primary btn-sm btn-activate" style="flex:1;">Seleziona</button>` : `<button class="btn btn-secondary btn-sm" style="flex:1;" disabled>In Uso</button>`}
            <button class="btn btn-secondary btn-sm btn-edit">Modifica</button>
            ${!isActive ? `<button class="btn btn-danger btn-sm btn-del">Elimina</button>` : ''}
          </div>
        `;

        const actBtn = card.querySelector(".btn-activate");
        if (actBtn) {
          actBtn.onclick = async () => {
            await window.api.post(`/api/profiles/active/${p.id}`, {});
            window.showToast(`Profilo di ${p.nome} attivato.`, "success");
            await window.initFamilySelector();
            loadProfiles();
          };
        }

        const editBtn = card.querySelector(".btn-edit");
        if (editBtn) {
          editBtn.onclick = () => openModal(p);
        }

        const delBtn = card.querySelector(".btn-del");
        if (delBtn) {
          delBtn.onclick = async () => {
            if (confirm(`Confermi l'eliminazione del profilo di ${p.nome} ${p.cognome} e del suo database crittografato?`)) {
              await window.api.delete(`/api/profiles/${p.id}`);
              window.showToast("Profilo rimosso.", "info");
              await window.initFamilySelector();
              loadProfiles();
            }
          };
        }

        grid.appendChild(card);
      });
    } catch (err) {
      console.error(err);
    }
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const id = idInput.value;
    const payload = {
      nome: nomeInput.value,
      cognome: cognomeInput.value,
      parentela: parentelaInput.value,
      data_nascita: dataNascitaInput.value,
      sesso: sessoInput.value,
      gruppo_sanguigno: gruppoInput.value,
      note_anamnestiche: noteInput.value
    };

    try {
      if (id) {
        await window.api.put(`/api/profiles/${id}`, payload);
        window.showToast("Profilo aggiornato.", "success");
      } else {
        await window.api.post("/api/profiles", payload);
        window.showToast("Nuovo profilo clinico familiare aggiunto.", "success");
      }
      closeModal();
      await window.initFamilySelector();
      loadProfiles();
    } catch (err) {
      window.showToast(err.message, "error");
    }
  };

  loadProfiles();
};
