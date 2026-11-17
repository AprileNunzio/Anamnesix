from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class EmoglobinaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Emoglobina (Hb)",
            category="Ematologico",
            default_unit="g/dL",
            default_min=12.5,
            default_max=17.5
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "g/l" in u:
            return round(value / 10.0, 1), "g/dL"
        return value, "g/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 8.0:
            return "CRITICO", f"Anemia severa acuta o cronica ({value} g/dL). Rischio di ipossia tissutale e instabilita emodinamica."
        elif value < 12.0:
            return "ALTO", f"Quadro anemico conclamato ({value} g/dL)."
        elif value > 18.5:
            return "ALTO", f"Policitemia / poliglobulia ({value} g/dL). Aumentata viscosita ematica e rischio trombotico."
        return "OTTIMALE", f"Capacita di trasporto di ossigeno eritrocitario fisiologica ({value} g/dL)."

emoglobina_algorithm = EmoglobinaAlgorithm()
