from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class GGTAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Gamma Glutamil Transferasi (GGT)",
            category="Funzionalita Epatica",
            default_unit="U/L",
            default_min=8.0,
            default_max=55.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 150.0:
            return "ALTO", f"GGT marcatamente elevata ({value} U/L). Sospetto quadro di colestasi intra/extraepatica o induzione microsomiale severa."
        elif value > 55.0:
            return "MODERATO", f"GGT lievemente/moderatamente aumentata ({value} U/L)."
        return "OTTIMALE", f"Livello di GGT biliare nella norma ({value} U/L)."

ggt_algorithm = GGTAlgorithm()
