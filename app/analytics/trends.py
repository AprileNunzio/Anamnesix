from typing import Dict, Any, List
from app.database.connection import get_db_connection

class TrendsEngine:
    def __init__(self):
        self.ready = True

    def get_analyte_trend_data(self, nome_standardizzato: str, profile_id: str | None = None) -> Dict[str, Any]:
        conn = get_db_connection(profile_id=profile_id)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, referto_id, data_prelievo, laboratorio, valore_numerico,
                       valore_testuale, unita_misura, range_min, range_max, stato_flag
                FROM analiti
                WHERE nome_standardizzato = ?
                ORDER BY data_prelievo ASC
                """,
                (nome_standardizzato,)
            )
            rows = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        if not rows:
            return {
                "nome_standardizzato": nome_standardizzato,
                "unita_misura": "",
                "range_min": None,
                "range_max": None,
                "punti": [],
                "variazione_percentuale": 0.0,
                "trend_direzione": "STABILE"
            }

        unita = rows[-1].get("unita_misura", "")
        r_min = rows[-1].get("range_min")
        r_max = rows[-1].get("range_max")

        punti = []
        for r in rows:
            punti.append({
                "data": r["data_prelievo"],
                "valore": r["valore_numerico"],
                "valore_testuale": r["valore_testuale"],
                "stato_flag": r["stato_flag"],
                "laboratorio": r["laboratorio"],
                "range_min": r["range_min"],
                "range_max": r["range_max"]
            })

        numeric_values = [p["valore"] for p in punti if p["valore"] is not None]
        variazione_pct = 0.0
        direzione = "STABILE"

        if len(numeric_values) >= 2:
            first_val = numeric_values[0]
            last_val = numeric_values[-1]
            if first_val != 0.0:
                variazione_pct = round(((last_val - first_val) / abs(first_val)) * 100.0, 1)

            if variazione_pct > 5.0:
                direzione = "CRESCENTE"
            elif variazione_pct < -5.0:
                direzione = "DECRESCENTE"

        return {
            "nome_standardizzato": nome_standardizzato,
            "unita_misura": unita,
            "range_min": r_min,
            "range_max": r_max,
            "punti": punti,
            "variazione_percentuale": variazione_pct,
            "trend_direzione": direzione,
            "valore_minimo": min(numeric_values) if numeric_values else None,
            "valore_massimo": max(numeric_values) if numeric_values else None,
            "valore_medio": round(sum(numeric_values) / len(numeric_values), 2) if numeric_values else None
        }

trends_engine = TrendsEngine()
