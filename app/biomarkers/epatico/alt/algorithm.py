from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ALTAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Alanina Aminotransferasi (ALT)",
            category="Funzionalita Epatica",
            default_unit="U/L",
            default_min=7.0,
            default_max=45.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 200.0:
            return "CRITICO", f"Citolisi epatica acuta marcata ({value} U/L). Possibile epatite acuta o danno tossico/ischemico epatico."
        elif value > 45.0:
            return "MODERATO", f"Ipertransaminasemia ALT ({value} U/L). Sofferenza epatocitaria da steatosi, farmaci o flogosi."
        return "OTTIMALE", f"Attivita enzimatica epatica ALT nei limiti della norma ({value} U/L)."

alt_algorithm = ALTAlgorithm()
