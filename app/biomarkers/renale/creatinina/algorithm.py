from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class CreatininaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Creatinina Sierica",
            category="Funzionalita Renale",
            default_unit="mg/dL",
            default_min=0.6,
            default_max=1.2
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "umol/l" in u or "µmol/l" in u:
            return round(value / 88.4, 2), "mg/dL"
        return value, "mg/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 2.5:
            return "CRITICO", f"Grave insufficienza renale ({value} mg/dL). Rischio uremico e ritenzione di scorie azotate."
        elif value > 1.2:
            return "MODERATO", f"Creatinina oltre il limite fisiologico ({value} mg/dL). Possibile declino della clearance renale."
        return "OTTIMALE", f"Filtrazione glomerulare e clearance creatininica ben conservate ({value} mg/dL)."

creatinina_algorithm = CreatininaAlgorithm()
