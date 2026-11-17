from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class MotilitaProgressivaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Motilita Progressiva Spermatica (PR)",
            category="Fertilita Uomo",
            default_unit="%",
            default_min=30.0,
            default_max=100.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value < 10.0:
            return "ALTO", f"Astenozoospermia severa ({value}%). Capacita cinetica di risalita nel tratto riproduttivo femminile fortemente compromessa."
        elif value < 30.0:
            return "MODERATO", f"Astenozoospermia ({value}%, cut-off WHO 2021: 30%). Possibile infezione prostatica/vescicolare, varicocele o stress ossidativo."
        return "OTTIMALE", f"Cinematica e motilita progressiva spermatica ottimali ({value}%)."

motilita_progressiva_algorithm = MotilitaProgressivaAlgorithm()
