from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class TSHAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Tireotropina (TSH)",
            category="Tiroide",
            default_unit="uUI/mL",
            default_min=0.35,
            default_max=4.2
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 10.0:
            return "ALTO", f"TSH notevolmente elevato ({value} uUI/mL). Quadro di ipotiroidismo conclamato, richiede dosaggio FT4/FT3 e supporto terapeutico."
        elif value > 4.2:
            return "MODERATO", f"TSH sopra la soglia ({value} uUI/mL), suggestivo di ipotiroidismo subclinico o tiroidite autoimmune."
        elif value < 0.1:
            return "ALTO", f"TSH soppresso ({value} uUI/mL). Rischio di ipertiroidismo o adenoma tossico."
        return "OTTIMALE", f"Eutirodismo: stimolazione ipofisaria tiroidea in perfetto equilibrio ({value} uUI/mL)."

tsh_algorithm = TSHAlgorithm()
