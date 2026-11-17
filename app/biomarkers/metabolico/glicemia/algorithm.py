from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class GlicemiaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Glucosio Basale",
            category="Metabolico",
            default_unit="mg/dL",
            default_min=70.0,
            default_max=99.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mmol/l" in u:
            return round(value * 18.0182, 1), "mg/dL"
        return value, "mg/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 55.0:
            return "CRITICO", f"Grave ipoglicemia clinica ({value} mg/dL). Rischio neuroglicopenico immediato."
        elif value < 70.0:
            return "MODERATO", f"Ipoglicemia lieve-moderata ({value} mg/dL)."
        elif value >= 126.0:
            return "ALTO", f"Glicemia a digiuno patologica ({value} mg/dL), indicativa di diabete mellito manifesto."
        elif value >= 100.0:
            return "MODERATO", f"Alterata glicemia a digiuno IFG ({value} mg/dL), stato prediabetico."
        return "OTTIMALE", f"Euglicemia a digiuno perfettamente conservata ({value} mg/dL)."

glicemia_algorithm = GlicemiaAlgorithm()
