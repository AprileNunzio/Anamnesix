from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class AMHAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Ormone Anti-Mulleriano (AMH)",
            category="Fertilita Donna",
            default_unit="ng/mL",
            default_min=1.2,
            default_max=4.5
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "pmol/l" in u:
            return round(value / 7.14, 2), "ng/mL"
        return value, "ng/mL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value < 0.5:
            return "ALTO", f"Riserva ovarica gravemente ridotta ({value} ng/mL). Pool follicolare primordiale critico, indicazione urgente a consulenza di procreazione medicalmente assistita."
        elif value < 1.2:
            return "MODERATO", f"Riserva ovarica diminuita ({value} ng/mL). Risposta ovarica a stimolazione attesa bassa/moderata."
        elif value > 5.0:
            return "MODERATO", f"AMH elevato ({value} ng/mL). Sospetto quadro di Ovaio Policistico (PCOS) o elevato rischio di iperstimolazione ovarica (OHSS)."
        return "OTTIMALE", f"Riserva follicolare ovarica pienamente conservata per l'eta ({value} ng/mL)."

amh_algorithm = AMHAlgorithm()
