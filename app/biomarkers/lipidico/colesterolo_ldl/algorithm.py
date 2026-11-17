from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ColesteroloLDLAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Colesterolo LDL",
            category="Profilo Lipidico",
            default_unit="mg/dL",
            default_min=50.0,
            default_max=115.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mmol/l" in u:
            return round(value * 38.67, 1), "mg/dL"
        return value, "mg/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 160.0:
            return "ALTO", f"Colesterolo LDL spiccatamente elevato ({value} mg/dL). Alto potenziale di formazione di placche ateromasiche."
        elif value >= 116.0:
            return "MODERATO", f"Colesterolo LDL sopra il target preventivo standard ({value} mg/dL)."
        return "OTTIMALE", f"Frazione LDL circolante in range protettivo ottimale ({value} mg/dL)."

colesterolo_ldl_algorithm = ColesteroloLDLAlgorithm()
