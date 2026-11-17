from typing import Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm

class AMHAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self):
        super().__init__(
            standard_name="Ormone Anti-Mulleriano (AMH)",
            category="Fertilita",
            default_unit="ng/mL",
            default_min=1.2,
            default_max=4.0
        )

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        u = current_unit.lower().replace(" ", "")
        if "pmol/l" in u:
            return round(value / 7.14, 2), "ng/mL"
        return value, "ng/mL"

    def evaluate_by_age(self, value: float, age: int) -> Tuple[str, str]:
        if age < 30:
            expected_min = 2.0
            expected_max = 5.5
        elif age < 35:
            expected_min = 1.5
            expected_max = 4.0
        elif age < 40:
            expected_min = 0.8
            expected_max = 2.5
        else:
            expected_min = 0.3
            expected_max = 1.2

        if value > 6.0:
            return "ATTENZIONE", f"AMH elevato ({value} ng/mL). Suggestivo di quadro PCOS (ovaio policistico) ed elevato rischio di iperstimolazione ovarica (OHSS)."
        elif value < 0.5:
            return "CRITICO_BASSO", f"Riserva ovarica gravemente ridotta ({value} ng/mL) per la fascia di eta {age} anni. Consigliata consulenza riproduttiva tempestiva per PMA."
        elif value < expected_min:
            return "BASSO", f"Riserva ovarica inferiore ai valori attesi per l'eta di {age} anni ({value} ng/mL vs range tipico {expected_min}-{expected_max} ng/mL)."
        return "OTTIMALE", f"Riserva ovarica perfettamente congrua con l'eta cronologica ({value} ng/mL)."

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if value is None:
            return "BASSO", "Valore non quantificabile."
        if value > 6.0:
            return "MODERATO", f"AMH marcatamente elevato ({value} ng/mL). Quadro PCOS da correlare con ecografia AFC."
        elif value < 0.7:
            return "ALTO", f"Bassa riserva ovarica ({value} ng/mL). Ridotta risposta stimolatoria follicolare."
        elif value < 1.2:
            return "MODERATO", f"Riserva ovarica in fase di iniziale declino ({value} ng/mL)."
        return "OTTIMALE", f"Patrimonio follicolare residuo ottimale ({value} ng/mL)."

amh_algorithm = AMHAlgorithm()
