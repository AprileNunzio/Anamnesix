from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class FSHFemminileAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="FSH Basale (Fase Follicolare)",
            category="Fertilita Donna",
            default_unit="mUI/mL",
            default_min=3.0,
            default_max=10.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value >= 25.0:
            return "CRITICO", f"FSH basale fortemente elevato ({value} mUI/mL). Transizione menopausale o insufficienza ovarica precoce (POI)."
        elif value >= 12.0:
            return "ALTO", f"FSH basale al 3 giorno del ciclo alterato ({value} mUI/mL). Segno di declino della riserva ovarica e resistenza follicolare periferica."
        elif value >= 10.0:
            return "MODERATO", f"FSH basale borderline ({value} mUI/mL). Raccomandato dosaggio AMH e conta follicoli antrali (AFC)."
        return "OTTIMALE", f"Risposta follicolare ipofisaria ottimale ({value} mUI/mL)."

fsh_femminile_algorithm = FSHFemminileAlgorithm()
