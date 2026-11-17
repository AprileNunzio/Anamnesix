from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class TestosteroneTotaleAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Testosterone Totale",
            category="Fertilita",
            default_unit="ng/dL",
            default_min=300.0,
            default_max=1000.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "nmol/l" in u:
            return round(value * 28.84, 1), "ng/dL"
        return value, "ng/dL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 250.0:
            return "ALTO", f"Ipogonadismo maschile conclamato ({value} ng/dL). Compromissione della stimolazione della spermatogenesi intratesticolare e della funzione delle cellule di Leydig."
        elif value < 300.0:
            return "MODERATO", f"Testosterone borderline basso ({value} ng/dL)."
        return "OTTIMALE", f"Livello androgenico sierico ideale per la funzione riproduttiva ({value} ng/dL)."

testosterone_totale_algorithm = TestosteroneTotaleAlgorithm()
