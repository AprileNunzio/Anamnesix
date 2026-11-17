window.showToast = function(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:none;border:none;color:white;cursor:pointer;font-weight:bold;margin-left:12px;">✕</button>
  `;

  toast.querySelector("button").onclick = () => toast.remove();

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
};

window.addEventListener("api-error", (e) => {
  window.showToast(e.detail || "Errore di comunicazione", "error");
});
