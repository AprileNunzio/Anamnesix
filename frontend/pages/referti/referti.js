window.init_referti_page = async function() {
  const dropzone = document.getElementById("upload-dropzone");
  const fileInput = document.getElementById("file-input");
  const spinner = document.getElementById("upload-spinner");
  const tbody = document.getElementById("referti-table-body");

  const loadReferti = async () => {
    try {
      const data = await window.api.get("/api/referti");
      if (data && data.length > 0) {
        tbody.innerHTML = "";
        data.forEach(r => {
          const tr = document.createElement("tr");
          const isConfirmed = r.stato_revisione === "CONFERMATO";
          const badgeClass = isConfirmed ? "badge-normal" : "badge-warning";

          tr.innerHTML = `
            <td><strong>${r.data_prelievo}</strong></td>
            <td>${r.laboratorio}</td>
            <td>${r.totale_analiti || 0}</td>
            <td><strong style="color: ${r.anomalie_count > 0 ? 'var(--status-danger)' : 'var(--status-normal)'};">${r.anomalie_count || 0}</strong></td>
            <td><span class="badge ${badgeClass}">${r.stato_revisione}</span></td>
            <td><span style="font-size:var(--font-xs); color:var(--text-muted);">${r.note || '-'}</span></td>
            <td>
              <div style="display:flex; gap:6px;">
                <button class="btn btn-secondary btn-sm btn-view-ref">Revisiona / Visualizza</button>
                <button class="btn btn-danger btn-sm btn-del-ref">Elimina</button>
              </div>
            </td>
          `;

          tr.querySelector(".btn-view-ref").onclick = async () => {
            const fullRef = await window.api.get(`/api/referti/${r.id}`);
            window.router.navigate("human_in_loop", { referto: fullRef });
          };

          tr.querySelector(".btn-del-ref").onclick = async () => {
            if (confirm("Eliminare definitivamente questo referto e tutti i suoi dati?")) {
              await window.api.delete(`/api/referti/${r.id}`);
              window.showToast("Referto eliminato.", "info");
              loadReferti();
            }
          };

          tbody.appendChild(tr);
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (file) => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    spinner.style.display = "flex";
    try {
      const res = await window.api.post("/api/referti/upload", formData);
      window.showToast("Documento analizzato! Procedi con la revisione fianco a fianco.", "success");
      window.router.navigate("human_in_loop", { uploadResult: res.data });
    } catch (err) {
      window.showToast(err.message, "error");
    } finally {
      spinner.style.display = "none";
    }
  };

  fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
      handleUpload(fileInput.files[0]);
    }
  };

  dropzone.ondragover = (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  };

  dropzone.ondragleave = () => {
    dropzone.classList.remove("dragover");
  };

  dropzone.ondrop = (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  loadReferti();
};
