from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ProgesteroneAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Progesterone (Fase Luteale / Giorno 21)",
            category="Fertilita",
            default_unit="ng/mL",
            default_min=8.0,
            default_max=25.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "nmol/l" in u:
            return round(value / 3.18, 2), "ng/mL"
        return value, "ng/mL"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 3.0:
            return "ALTO", f"Ciclo anovulatorio confermato ({value} ng/mL a meta fase luteale). Assenza di corpo luteo funzionale."
        elif value < 8.0:
            return "MODERATO", f"Difetto della fase luteale ({value} ng/mL). Corpo luteo insufficiente per sostenere l'attecchimento endometriale."
        return "OTTIMALE", f"Avvenuta ovulazione con ottima attivita funzionale del corpo luteo ({value} ng/mL)."

progesterone_algorithm = ProgesteroneAlgorithm()
