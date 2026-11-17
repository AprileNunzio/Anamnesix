from typing import Dict, Any, List
from app.database.connection import get_db_connection

SYSTEM_CATEGORIES = {
    "Cardiovascolare": ["Profilo Lipidico", "Cardiovascolare"],
    "Metabolico": ["Metabolico"],
    "Epatico": ["Funzionalita Epatica"],
    "Renale": ["Funzionalita Renale"],
    "Ematologico": ["Ematologico", "Coagulazione"],
    "Ormonale": ["Tiroide", "Ormoni"],
    "Infiammatorio": ["Infiammatorio"]
}

class HealthScoreCalculator:
    def __init__(self):
        self.ready = True

    def calculate_scores(self, profile_id: str | None = None) -> Dict[str, Any]:
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
                """
            )
            rows = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        if not rows:
            return {
                "overall_score": 100,
                "stato_sintetico": "Nessun dato clinico registrato",
                "totale_biomarcatori": 0,
                "sistemi": {k: {"score": 100, "stato": "Ottimale", "anomalie": 0, "totale": 0} for k in SYSTEM_CATEGORIES}
            }

        systems_data: Dict[str, Dict[str, Any]] = {}
        total_penalties = 0.0

        for system_name, cat_list in SYSTEM_CATEGORIES.items():
            matched = [r for r in rows if r.get("categoria") in cat_list]
            if not matched:
                systems_data[system_name] = {
                    "score": 100,
                    "stato": "Nessun esame",
                    "anomalie": 0,
                    "totale": 0
                }
                continue

            score = 100.0
            anomalie = 0

            for r in matched:
                flag = r.get("stato_flag", "NORMALE")
                if flag in ["BASSO", "ALTO"]:
                    score -= 15.0
                    anomalie += 1
                elif flag in ["CRITICO_BASSO", "CRITICO_ALTO"]:
                    score -= 35.0
                    anomalie += 1

            score = max(0.0, min(100.0, score))
            total_penalties += (100.0 - score)

            stato = "Ottimale"
            if score < 50:
                stato = "Critico"
            elif score < 75:
                stato = "Attenzione"
            elif score < 90:
                stato = "Discreto"

            systems_data[system_name] = {
                "score": round(score, 1),
                "stato": stato,
                "anomalie": anomalie,
                "totale": len(matched)
            }

        avg_score = max(0.0, 100.0 - (total_penalties / max(1, len(SYSTEM_CATEGORIES))))
        global_state = "Eccellente"
        if avg_score < 50:
            global_state = "Richiede Attenzione Medica Urgente"
        elif avg_score < 75:
            global_state = "Valori Alterati da Monitorare"
        elif avg_score < 90:
            global_state = "Buono con Lievi Anomalie"

        return {
            "overall_score": round(avg_score, 1),
            "stato_sintetico": global_state,
            "totale_biomarcatori": len(rows),
            "sistemi": systems_data
        }

health_score_calculator = HealthScoreCalculator()
