window.init_dossier_page = async function() {
  const patientInput = document.getElementById("dossier-patient-name");
  const passwordInput = document.getElementById("dossier-pdf-password");
  const exportBtn = document.getElementById("btn-export-pdf");

  try {
    const profData = await window.api.get("/api/profiles");
    const active = (profData.profiles || []).find(p => p.id === profData.active_profile_id);
    if (active) {
      patientInput.value = `${active.nome} ${active.cognome} (${active.parentela})`;
    } else {
      patientInput.value = "Profilo Principale";
    }
  } catch (err) {
    console.error(err);
  }

  exportBtn.onclick = async () => {
    exportBtn.disabled = true;
    exportBtn.textContent = "Generazione Dossier PDF in corso...";

    try {
      const payload = {
        password: passwordInput.value || null
      };

      const blob = await window.api.post("/api/export/pdf", payload);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Anamnesix_Dossier_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      window.showToast("Dossier clinico PDF scaricato con successo!", "success");
    } catch (err) {
      window.showToast(err.message, "error");
    } finally {
      exportBtn.disabled = false;
      exportBtn.textContent = "📥 Genera e Scarica Dossier Clinico PDF";
    }
  };
};
