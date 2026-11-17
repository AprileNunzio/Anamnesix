from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class TrigliceridiAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Trigliceridi",
            category="Profilo Lipidico",
            default_unit="mg/dL",
            default_min=50.0,
            default_max=150.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mmol/l" in u:
            return round(value * 88.57, 1), "mg/dL"
        return value, "mg/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 500.0:
            return "CRITICO", f"Ipertrigliceridemia severa ({value} mg/dL). Rischio elevato di pancreatite acuta d'urgenza."
        elif value >= 200.0:
            return "ALTO", f"Trigliceridi marcatamente elevati ({value} mg/dL). Componente attiva di sindrome metabolica."
        elif value > 150.0:
            return "MODERATO", f"Trigliceridi borderline alti ({value} mg/dL)."
        return "OTTIMALE", f"Livello di trigliceridi perfettamente controllato ({value} mg/dL)."

trigliceridi_algorithm = TrigliceridiAlgorithm()
