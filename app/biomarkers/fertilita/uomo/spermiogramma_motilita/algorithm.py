from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class SpermiogrammaMotilitaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Motilita Progressiva Spermatozoi (PR %)",
            category="Fertilita",
            default_unit="%",
            default_min=30.0,
            default_max=85.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value < 10.0:
            return "ALTO", f"Astenozoospermia severa ({value}%). Mobilita progressiva marcatamente compromessa, ridotte possibilita di fecondazione spontanea."
        elif value < 30.0:
            return "MODERATO", f"Astenozoospermia ({value}%, cut-off WHO 30%). Possibile causa flogistica, varicocele o stress ossidativo seminale."
        return "OTTIMALE", f"Capacita cinetica progressiva dei gameti conservata ({value}%)."

spermiogramma_motilita_algorithm = SpermiogrammaMotilitaAlgorithm()
