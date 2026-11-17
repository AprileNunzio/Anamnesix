from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class ASTAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Aspartato Aminotransferasi (AST)",
            category="Funzionalita Epatica",
            default_unit="U/L",
            default_min=8.0,
            default_max=40.0
        )

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value >= 200.0:
            return "CRITICO", f"Innalzamento severo di AST ({value} U/L). Rischio di necrosi epatocitaria o danno muscolare/miocardico acuto."
        elif value > 40.0:
            return "MODERATO", f"Transaminasi AST moderatamente elevata ({value} U/L)."
        return "OTTIMALE", f"Livello di AST nei limiti attesi ({value} U/L)."

ast_algorithm = ASTAlgorithm()
