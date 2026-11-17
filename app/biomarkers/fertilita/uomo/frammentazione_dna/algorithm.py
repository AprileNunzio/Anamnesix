from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class FrammentazioneDNASpermaticoAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Indice di Frammentazione DNA Spermatico (DFI %)",
            category="Fertilita",
            default_unit="%",
            default_min=0.0,
            default_max=20.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 30.0:
            return "ALTO", f"Frammentazione del DNA spermatico critica ({value}%). Significativo rischio di fallimento della fecondazione, mancato sviluppo blastocistico e abortivita precoce ricorrente."
        elif value >= 20.0:
            return "MODERATO", f"Frammentazione del DNA spermatico elevata ({value}%). Suggerito trattamento antiossidante e valutazione varicocele o flogosi delle vie seminali."
        return "OTTIMALE", f"Integrita genomica della cromatina spermatica ottimale ({value}%)."

frammentazione_dna_algorithm = FrammentazioneDNASpermaticoAlgorithm()
