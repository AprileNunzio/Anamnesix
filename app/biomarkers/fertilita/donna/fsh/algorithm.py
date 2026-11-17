from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class FSHDonnaAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Ormone Follicolo-Stimolante (FSH Basale)",
            category="Fertilita",
            default_unit="mUI/mL",
            default_min=3.0,
            default_max=9.5
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value > 15.0:
            return "ALTO", f"FSH basale (giorni 2-4 del ciclo) gravemente elevato ({value} mUI/mL). Indica esaurimento ovarico precoce o insufficienza ovarica incipiente."
        elif value >= 10.0:
            return "MODERATO", f"FSH basale borderline ({value} mUI/mL). Segnale di ridotta risposta ovarica alla stimolazione ormonale."
        elif value < 2.5:
            return "MODERATO", f"FSH basale soppresso ({value} mUI/mL). Valutare asse ipotalamo-ipofisi per amenorrea centrale o iperestrogenismo."
        return "OTTIMALE", f"Livello basale di FSH perfettamente bilanciato per la follicologenesi ({value} mUI/mL)."

fsh_donna_algorithm = FSHDonnaAlgorithm()
