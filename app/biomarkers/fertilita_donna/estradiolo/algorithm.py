from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class EstradioloAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="17-Beta Estradiolo (E2)",
            category="Fertilita Donna",
            default_unit="pg/mL",
            default_min=20.0,
            default_max=75.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "pmol/l" in u:
            return round(value / 3.67, 1), "pg/mL"
        return value, "pg/mL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value > 80.0:
            return "MODERATO", f"Estradiolo basale precocemente elevato al 3 giorno ({value} pg/mL). Possibile reclutamento follicolare anticipato che puo mascherare un aumento compensatorio dell'FSH."
        elif value < 15.0:
            return "MODERATO", f"Estradiolo soppresso ({value} pg/mL). Ipogonadismo ipogonadotropo o blocco ipotalamico."
        return "OTTIMALE", f"Livello di estradiolo follicolare perfettamente sincronizzato ({value} pg/mL)."

estradiolo_algorithm = EstradioloAlgorithm()
