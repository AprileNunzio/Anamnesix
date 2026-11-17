from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ConcentrazioneSpermaticaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Concentrazione Spermatica",
            category="Fertilita Uomo",
            default_unit="milioni/mL",
            default_min=16.0,
            default_max=200.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value == 0.0:
            return "CRITICO", "Azoospermia: assenza totale di spermatozoi nell'eiaculato. Necessaria diagnosi differenziale tra ostruttiva (CBAVD) e secretoria (biopsia testicolare/Micro-TESE)."
        elif value < 5.0:
            return "ALTO", f"Oligozoospermia severa ({value} milioni/mL). Indicazione a consulenza andrologica, cariotipo e ricerca microdelezioni cromosoma Y."
        elif value < 16.0:
            return "MODERATO", f"Oligozoospermia ({value} milioni/mL, limite WHO 2021: 16 mil/mL). Valutare ecocolordoppler per varicocele."
        return "OTTIMALE", f"Concentrazione spermatica pienamente conforme ai criteri WHO 6a edizione ({value} milioni/mL)."

concentrazione_spermatica_algorithm = ConcentrazioneSpermaticaAlgorithm()
