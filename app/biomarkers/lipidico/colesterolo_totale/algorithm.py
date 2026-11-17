from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ColesteroloTotaleAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Colesterolo Totale",
            category="Profilo Lipidico",
            default_unit="mg/dL",
            default_min=120.0,
            default_max=199.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mmol/l" in u:
            return round(value * 38.67, 1), "mg/dL"
        return value, "mg/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 240.0:
            return "ALTO", f"Ipercolesterolemia marcata ({value} mg/dL). Rischio aterogeno coronarico significativo."
        elif value >= 200.0:
            return "MODERATO", f"Colesterolo totale borderline ({value} mg/dL)."
        return "OTTIMALE", f"Colesterolemia totale nei limiti protettivi desiderabili ({value} mg/dL)."

colesterolo_totale_algorithm = ColesteroloTotaleAlgorithm()
