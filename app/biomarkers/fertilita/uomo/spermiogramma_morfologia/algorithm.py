from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class SpermiogrammaMorfologiaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Morfologia Tipica Spermatozoi (Kruger %)",
            category="Fertilita",
            default_unit="%",
            default_min=4.0,
            default_max=40.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 1.0:
            return "ALTO", f"Teratozoospermia severa ({value}% forme tipiche). Anomalie prevalenti di testa/acrosoma, indicazione diretta per microiniezione intracitoplasmatica ICSI."
        elif value < 4.0:
            return "MODERATO", f"Teratozoospermia ({value}%, cut-off Kruger WHO 4%). Alterata spermiogenesi."
        return "OTTIMALE", f"Morfologia spermatozoaria conforme ai criteri restrittivi di Kruger ({value}%)."

spermiogramma_morfologia_algorithm = SpermiogrammaMorfologiaAlgorithm()
