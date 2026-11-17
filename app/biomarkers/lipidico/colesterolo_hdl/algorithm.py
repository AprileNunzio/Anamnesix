from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ColesteroloHDLAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Colesterolo HDL",
            category="Profilo Lipidico",
            default_unit="mg/dL",
            default_min=45.0,
            default_max=85.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mmol/l" in u:
            return round(value * 38.67, 1), "mg/dL"
        return value, "mg/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 40.0:
            return "ALTO", f"Colesterolo HDL deficitario ({value} mg/dL). Perdita della protezione anti-aterogena fisiologica."
        elif value < 45.0:
            return "MODERATO", f"Colesterolo HDL subottimale ({value} mg/dL)."
        return "OTTIMALE", f"Frazione antiossidante e protettiva HDL efficiente ({value} mg/dL)."

colesterolo_hdl_algorithm = ColesteroloHDLAlgorithm()
