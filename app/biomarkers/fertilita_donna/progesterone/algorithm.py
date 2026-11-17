from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ProgesteroneAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Progesterone (Fase Luteale)",
            category="Fertilita Donna",
            default_unit="ng/mL",
            default_min=5.0,
            default_max=25.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "nmol/l" in u:
            return round(value / 3.18, 2), "ng/mL"
        return value, "ng/mL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value < 3.0:
            return "ALTO", f"Progesterone luteale insufficiente ({value} ng/mL). Ciclo presumibilmente anovulatorio o grave difetto della fase luteale."
        elif value < 10.0:
            return "MODERATO", f"Progesterone luteale subottimale ({value} ng/mL). Insufficienza del corpo luteo con ridotta ricettivita endometriale per l'impianto embrionario."
        return "OTTIMALE", f"Attivita del corpo luteo eccellente con ovulazione confermata ({value} ng/mL)."

progesterone_algorithm = ProgesteroneAlgorithm()
