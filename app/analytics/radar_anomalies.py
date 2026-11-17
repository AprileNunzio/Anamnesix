from typing import List, Dict, Any
from app.database.connection import get_db_connection

class RadarAnomaliesEngine:
    def __init__(self):
        self.ready = True

    def get_ranked_anomalies(self, profile_id: str | None = None) -> List[Dict[str, Any]]:
        conn = get_db_connection(profile_id=profile_id)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT a.*
                FROM analiti a
                INNER JOIN (
                    SELECT nome_standardizzato, MAX(data_prelievo) as max_data
                    FROM analiti
                    GROUP BY nome_standardizzato
                ) latest ON a.nome_standardizzato = latest.nome_standardizzato AND a.data_prelievo = latest.max_data
                WHERE a.stato_flag != 'NORMALE'
                """
            )
            latest_anomalies = [dict(r) for r in cur.fetchall()]

            ranked = []
            for item in latest_anomalies:
                val = item.get("valore_numerico")
                r_min = item.get("range_min")
                r_max = item.get("range_max")
                deviation_pct = 0.0

                if val is not None:
                    if r_min is not None and val < r_min:
                        span = (r_max - r_min) if (r_max is not None and r_max > r_min) else (r_min if r_min != 0 else 1.0)
                        deviation_pct = round(((r_min - val) / span) * 100.0, 1)
                    elif r_max is not None and val > r_max:
                        span = (r_max - r_min) if (r_min is not None and r_max > r_min) else (r_max if r_max != 0 else 1.0)
                        deviation_pct = round(((val - r_max) / span) * 100.0, 1)

                name = item.get("nome_standardizzato", "")
                cur.execute(
                    """
                    SELECT stato_flag
                    FROM analiti
                    WHERE nome_standardizzato = ?
                    ORDER BY data_prelievo DESC
                    LIMIT 5
                    """,
                    (name,)
                )
                history_flags = [r["stato_flag"] for r in cur.fetchall()]
                persistence_count = sum(1 for f in history_flags if f != "NORMALE")

                item["scostamento_percentuale"] = deviation_pct
                item["persistenza_storica"] = persistence_count
                item["totale_prelievi_recenti"] = len(history_flags)

                severity_rank = 1
                if item.get("stato_flag") in ["CRITICO_ALTO", "CRITICO_BASSO"]:
                    severity_rank = 3
                elif item.get("stato_flag") in ["ALTO", "BASSO"]:
                    severity_rank = 2

                item["punteggio_priorita"] = round((severity_rank * 100.0) + deviation_pct + (persistence_count * 15.0), 1)
                ranked.append(item)

            ranked.sort(key=lambda x: x["punteggio_priorita"], reverse=True)
            return ranked
        finally:
            conn.close()

radar_anomalies_engine = RadarAnomaliesEngine()
