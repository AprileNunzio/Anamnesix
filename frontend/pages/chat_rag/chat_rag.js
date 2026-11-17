window.init_chat_rag_page = function() {
  const container = document.getElementById("chat-messages-container");
  const form = document.getElementById("chat-input-form");
  const input = document.getElementById("chat-user-input");
  const sendBtn = document.getElementById("chat-send-btn");

  window.sendPresetPrompt = (text) => {
    input.value = text;
    form.dispatchEvent(new Event("submit"));
  };

  const appendUserMessage = (msg) => {
    const div = document.createElement("div");
    div.className = "chat-msg user-msg";
    div.innerHTML = `<div class="msg-bubble">${msg}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  };

  const appendBotMessage = (text, citations = []) => {
    const div = document.createElement("div");
    div.className = "chat-msg bot-msg";

    let citationsHtml = "";
    if (citations && citations.length > 0) {
      const chips = citations.map(c => `
        <span class="citation-chip">
          📅 ${c.data} | ${c.esame}: <strong>${c.valore} ${c.unita}</strong> (${c.laboratorio})
        </span>
      `).join("");
      citationsHtml = `<div class="msg-citations">${chips}</div>`;
    }

    const htmlFormatted = text
      .replace(/^### (.*$)/gim, "<strong>$1</strong><br>")
      .replace(/\n/g, "<br>");

    div.innerHTML = `
      <div class="msg-bubble">${htmlFormatted}</div>
      ${citationsHtml}
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    appendUserMessage(query);
    input.value = "";
    sendBtn.disabled = true;

    const loadingDiv = document.createElement("div");
    loadingDiv.className = "chat-msg bot-msg";
    loadingDiv.innerHTML = `<div class="msg-bubble" style="color:var(--accent-cyan);">Sto consultando il tuo archivio clinico cifrato...</div>`;
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;

    try {
      const res = await window.api.post("/api/chat/query", { query: query });
      loadingDiv.remove();
      appendBotMessage(res.risposta || "", res.citazioni || []);
    } catch (err) {
      loadingDiv.remove();
      appendBotMessage(`Errore: ${err.message}`);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  };
};
