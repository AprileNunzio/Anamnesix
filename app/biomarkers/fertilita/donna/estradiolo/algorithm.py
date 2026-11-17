from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class EstradioloAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="17-Beta Estradiolo (E2)",
            category="Fertilita",
            default_unit="pg/mL",
            default_min=20.0,
            default_max=60.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "pmol/l" in u:
            return round(value / 3.67, 1), "pg/mL"
        return value, "pg/mL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value > 80.0:
            return "MODERATO", f"Estradiolo basale precocemente elevato ({value} pg/mL al 3° giorno). Possibile reclutamento follicolare anticipato che maschera valori elevati di FSH."
        elif value < 15.0:
            return "MODERATO", f"Ipoestrogenismo marcato ({value} pg/mL). Insufficiente attivita ormonale della granulosa ovarica."
        return "OTTIMALE", f"Livello di estradiolo ideale per la fase follicolare iniziale ({value} pg/mL)."

estradiolo_algorithm = EstradioloAlgorithm()
