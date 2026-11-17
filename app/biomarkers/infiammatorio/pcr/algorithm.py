from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class PCRAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Proteina C Reattiva (PCR)",
            category="Infiammatorio",
            default_unit="mg/L",
            default_min=0.0,
            default_max=5.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mg/dl" in u:
            return round(value * 10.0, 1), "mg/L"
        return value, "mg/L"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 50.0:
            return "CRITICO", f"Infiammazione sistemica acuta o batterica severa ({value} mg/L)."
        elif value > 10.0:
            return "ALTO", f"Stato flogistico sistemico attivo ({value} mg/L)."
        elif value > 5.0:
            return "MODERATO", f"Lieve reattivita flogistica aspecifica ({value} mg/L)."
        return "OTTIMALE", f"Assenza di flogosi sistemica attiva ({value} mg/L)."

pcr_algorithm = PCRAlgorithm()
