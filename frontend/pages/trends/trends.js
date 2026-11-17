window.init_trends_page = async function(params = {}) {
  const select = document.getElementById("trend-analyte-select");
  const titleEl = document.getElementById("chart-analyte-title");
  const canvas = document.getElementById("trend-canvas");
  const lastValEl = document.getElementById("kpi-last-val");
  const varPctEl = document.getElementById("kpi-var-pct");
  const avgValEl = document.getElementById("kpi-avg-val");
  const dirEl = document.getElementById("kpi-direction");
  const tbody = document.getElementById("trend-history-tbody");

  let initialAnalyte = params.analyte ? decodeURIComponent(params.analyte) : null;

  try {
    const list = await window.api.get("/api/analytics/biomarkers");
    select.innerHTML = "";

    if (!list || list.length === 0) {
      select.innerHTML = '<option value="">Nessun biomarcatore registrato</option>';
      return;
    }

    list.forEach(b => {
      const opt = document.createElement("option");
      opt.value = b.nome_standardizzato;
      opt.textContent = `${b.nome_standardizzato} (${b.categoria})`;
      if (initialAnalyte && b.nome_standardizzato === initialAnalyte) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });

    const loadData = async (analyteName) => {
      titleEl.textContent = `${analyteName} - Andamento Storico`;
      const data = await window.api.get(`/api/analytics/trend/${encodeURIComponent(analyteName)}`);

      const punti = data.punti || [];
      const lastPoint = punti.length > 0 ? punti[punti.length - 1] : null;

      lastValEl.textContent = lastPoint ? `${lastPoint.valore} ${data.unita_misura}` : "--";
      varPctEl.textContent = `${data.variazione_percentuale > 0 ? '+' : ''}${data.variazione_percentuale}%`;
      avgValEl.textContent = data.valore_medio !== null ? `${data.valore_medio} ${data.unita_misura}` : "--";
      dirEl.textContent = data.trend_direzione;

      tbody.innerHTML = "";
      punti.slice().reverse().forEach(p => {
        const tr = document.createElement("tr");
        const rangeStr = (p.range_min !== null && p.range_max !== null) ? `${p.range_min} - ${p.range_max}` : "-";
        const badgeClass = p.stato_flag.includes("CRITICO") ? "badge-critical" : (p.stato_flag !== "NORMALE" ? "badge-warning" : "badge-normal");
        tr.innerHTML = `
          <td><strong>${p.data}</strong></td>
          <td><strong style="font-size:var(--font-base);">${p.valore}</strong></td>
          <td>${data.unita_misura}</td>
          <td>${rangeStr}</td>
          <td><span class="badge ${badgeClass}">${p.stato_flag}</span></td>
          <td>${p.laboratorio}</td>
        `;
        tbody.appendChild(tr);
      });

      drawTrendChart(canvas, data);
    };

    select.onchange = () => {
      loadData(select.value);
    };

    loadData(select.value);
  } catch (err) {
    console.error(err);
  }
};

function drawTrendChart(canvas, data) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();

  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;

  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);

  const w = rect.width;
  const h = rect.height;
  const padLeft = 60;
  const padRight = 30;
  const padTop = 30;
  const padBottom = 40;

  ctx.clearRect(0, 0, w, h);

  const punti = data.punti || [];
  if (punti.length === 0) {
    ctx.fillStyle = "#94a3b8";
    ctx.font = "14px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Nessun dato disponibile per il grafico", w / 2, h / 2);
    return;
  }

  let minVal = data.valore_minimo !== null ? data.valore_minimo : 0;
  let maxVal = data.valore_massimo !== null ? data.valore_massimo : 100;

  if (data.range_min !== null) minVal = Math.min(minVal, data.range_min);
  if (data.range_max !== null) maxVal = Math.max(maxVal, data.range_max);

  const span = (maxVal - minVal) || 1;
  minVal -= span * 0.15;
  maxVal += span * 0.15;

  const getY = (val) => {
    return h - padBottom - ((val - minVal) / (maxVal - minVal)) * (h - padTop - padBottom);
  };

  const getX = (idx) => {
    if (punti.length === 1) return w / 2;
    return padLeft + (idx / (punti.length - 1)) * (w - padLeft - padRight);
  };

  if (data.range_min !== null && data.range_max !== null) {
    const yTop = getY(data.range_max);
    const yBottom = getY(data.range_min);
    ctx.fillStyle = "rgba(16, 185, 129, 0.12)";
    ctx.fillRect(padLeft, yTop, w - padLeft - padRight, yBottom - yTop);
    ctx.strokeStyle = "rgba(16, 185, 129, 0.35)";
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padLeft, yTop);
    ctx.lineTo(w - padRight, yTop);
    ctx.moveTo(padLeft, yBottom);
    ctx.lineTo(w - padRight, yBottom);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
  ctx.lineWidth = 1;
  const gridSteps = 5;
  ctx.fillStyle = "#64748b";
  ctx.font = "11px monospace";
  ctx.textAlign = "right";

  for (let i = 0; i <= gridSteps; i++) {
    const val = minVal + (i / gridSteps) * (maxVal - minVal);
    const y = getY(val);
    ctx.beginPath();
    ctx.moveTo(padLeft, y);
    ctx.lineTo(w - padRight, y);
    ctx.stroke();
    ctx.fillText(val.toFixed(1), padLeft - 8, y + 4);
  }

  if (punti.length > 1) {
    ctx.strokeStyle = "#0284c7";
    ctx.lineWidth = 3;
    ctx.beginPath();
    punti.forEach((p, idx) => {
      const x = getX(idx);
      const y = getY(p.valore);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  punti.forEach((p, idx) => {
    const x = getX(idx);
    const y = getY(p.valore);
    const isAnomalous = p.stato_flag !== "NORMALE";

    ctx.fillStyle = isAnomalous ? "#ef4444" : "#0284c7";
    ctx.beginPath();
    ctx.arc(x, y, isAnomalous ? 7 : 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = "#94a3b8";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(p.data.substring(2), x, h - padBottom + 18);
  });
}
