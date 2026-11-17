from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class FrammentazioneDNASpermaticoAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Indice di Frammentazione DNA Spermatico (DFI)",
            category="Fertilita Uomo",
            default_unit="%",
            default_min=0.0,
            default_max=15.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non pervenuto."
        if value > 30.0:
            return "ALTO", f"Frammentazione del DNA spermatico elevata ({value}%). Significativo rischio di arresto dello sviluppo blastocitario e abortivita precoce ripetuta. Indicata terapia antiossidante, correzione varicocele e selezione PICSI/MACS."
        elif value > 15.0:
            return "MODERATO", f"Frammentazione del DNA borderline ({value}%). Integrita genomica spermatica parzialmente compromessa da stress ossidativo."
        return "OTTIMALE", f"Integrita del patrimonio genetico e cromatinico dello spermatozoo intatta ({value}%)."

frammentazione_dna_algorithm = FrammentazioneDNASpermaticoAlgorithm()
