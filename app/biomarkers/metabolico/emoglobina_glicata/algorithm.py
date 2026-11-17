from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class EmoglobinaGlicataAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Emoglobina Glicata (HbA1c)",
            category="Metabolico",
            default_unit="%",
            default_min=4.0,
            default_max=5.6
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "mmol/mol" in u:
            percent_val = round((0.09148 * value) + 2.152, 1)
            return percent_val, "%"
        return value, "%"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 6.5:
            return "ALTO", f"HbA1c diagnostica per diabete mellito ({value}%). Controllo glicemico trimestrale insufficiente."
        elif value >= 5.7:
            return "MODERATO", f"HbA1c compresa in fascia di prediabete / intolleranza glucidica ({value}%)."
        return "OTTIMALE", f"Compensazione metabolica a lungo termine eccellente ({value}%)."

emoglobina_glicata_algorithm = EmoglobinaGlicataAlgorithm()
