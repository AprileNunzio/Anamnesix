from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class FerritinaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Ferritina",
            category="Ematologico",
            default_unit="ng/mL",
            default_min=25.0,
            default_max=300.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 15.0:
            return "ALTO", f"Deplezione totale delle riserve corporee di ferro ({value} ng/mL). Anemia sideropenica manifesta o latente."
        elif value < 30.0:
            return "MODERATO", f"Ferritina ridotta ({value} ng/mL). Depositi marziali epatici e midollari esauriti."
        elif value > 600.0:
            return "ALTO", f"Iperferritinemia severa ({value} ng/mL). Possibile emocromatosi, sovraccarico da trasfusioni o potente reattante di fase acuta infiammatoria."
        return "OTTIMALE", f"Riserva di ferro nei depositi cellulari adeguata ({value} ng/mL)."

ferritina_algorithm = FerritinaAlgorithm()
