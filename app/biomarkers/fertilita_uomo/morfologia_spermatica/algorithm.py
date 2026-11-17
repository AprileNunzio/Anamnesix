from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class MorfologiaSpermaticaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Morfologia Spermatica Normale",
            category="Fertilita Uomo",
            default_unit="%",
            default_min=4.0,
            default_max=100.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value < 1.0:
            return "ALTO", f"Teratozoospermia severa ({value}% forme normali). Anomalie acrosomiali, nucleari o flagellari diffuse."
        elif value < 4.0:
            return "MODERATO", f"Teratozoospermia ({value}%, cut-off WHO: 4%). Ridotta fertilizzazione naturale, indicazione a FIVET/ICSI."
        return "OTTIMALE", f"Morfologia spermatica normale conforme ai criteri restrittivi di Tygerberg ({value}%)."

morfologia_spermatica_algorithm = MorfologiaSpermaticaAlgorithm()
