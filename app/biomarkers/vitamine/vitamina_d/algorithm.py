from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class VitaminaDAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Vitamina D (25-OH)",
            category="Vitamine",
            default_unit="ng/mL",
            default_min=30.0,
            default_max=100.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "nmol/l" in u:
            return round(value / 2.496, 1), "ng/mL"
        return value, "ng/mL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 10.0:
            return "ALTO", f"Grave carenza di 25-OH Vitamina D ({value} ng/mL). Rischio demineralizzazione ossea, osteopenia e ipocalcemia."
        elif value < 20.0:
            return "MODERATO", f"Deficit di Vitamina D ({value} ng/mL). Necessita integrazione."
        elif value < 30.0:
            return "MODERATO", f"Livelli insufficienti di Vitamina D ({value} ng/mL)."
        return "OTTIMALE", f"Riserva di Vitamina D pienamente sufficiente e protettiva ({value} ng/mL)."

vitamina_d_algorithm = VitaminaDAlgorithm()
