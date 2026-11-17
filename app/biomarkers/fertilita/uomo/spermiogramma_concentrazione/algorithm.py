from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class SpermiogrammaConcentrazioneAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Concentrazione Spermatozoi (Spermiogramma WHO 6th)",
            category="Fertilita",
            default_unit="milioni/mL",
            default_min=15.0,
            default_max=250.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value == 0.0:
            return "CRITICO", "Azoospermia conclamata: assenza totale di spermatozoi nel sedimento seminale centrifugato. Richiede consulenza andrologica per differenziare azoospermia ostruttiva o secretoria."
        elif value < 5.0:
            return "ALTO", f"Oligozoospermia severa ({value} milioni/mL). Concentrazione critica al di sotto del 5° percentile WHO, indicazione a tecniche di PMA (ICSI) e screening genetico (cariotipo, microdelezioni Y)."
        elif value < 15.0:
            return "MODERATO", f"Oligozoospermia ({value} milioni/mL, soglia minima WHO 15 milioni/mL). Consigliabile valutazione ormonale ed ecocolordoppler scrotale per varicocele."
        return "OTTIMALE", f"Normozoospermia per concentrazione ({value} milioni/mL)."

spermiogramma_concentrazione_algorithm = SpermiogrammaConcentrazioneAlgorithm()
