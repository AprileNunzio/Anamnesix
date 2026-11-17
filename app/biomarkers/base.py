from typing import Tuple, Optional, Dict, Any
from pydantic import BaseModel

class BiomarkerResult(BaseModel):
    categoria: str
    nome_esame_originale: str
    nome_standardizzato: str
    valore_numerico: Optional[float] = None
    valore_testuale: Optional[str] = None
    unita_misura: str
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    stato_flag: str
    rischio_clinico: str
    interpretazione: str
    data_prelievo: str
    laboratorio: str
    note_referto: Optional[str] = None

class BaseBiomarkerAlgorithm:
    def __init__(self, standard_name: str, category: str, default_unit: str, default_min: Optional[float], default_max: Optional[float]):
        self.standard_name = standard_name
        self.category = category
        self.default_unit = default_unit
        self.default_min = default_min
        self.default_max = default_max

    def convert_unit(self, value: float, current_unit: str) -> Tuple[float, str]:
        return value, self.default_unit

    def determine_flag(self, value: Optional[float], r_min: Optional[float], r_max: Optional[float]) -> str:
        if value is None:
            return "NORMALE"
        effective_min = r_min if r_min is not None else self.default_min
        effective_max = r_max if r_max is not None else self.default_max

        if effective_min is not None and effective_max is not None:
            span = effective_max - effective_min
            if span <= 0:
                span = effective_min if effective_min != 0 else 1.0
            if value < effective_min:
                dev = (effective_min - value) / span
                return "CRITICO_BASSO" if dev > 0.4 else "BASSO"
            elif value > effective_max:
                dev = (value - effective_max) / span
                return "CRITICO_ALTO" if dev > 0.4 else "ALTO"
            return "NORMALE"

        if effective_min is not None and value < effective_min:
            return "BASSO"
        if effective_max is not None and value > effective_max:
            return "ALTO"
        return "NORMALE"

    def evaluate_clinical_risk(self, flag: str, value: Optional[float]) -> Tuple[str, str]:
        if flag == "CRITICO_ALTO":
            return "ALTO", f"Valore significativamente superiore ai limiti di riferimento ({value} {self.default_unit})."
        elif flag == "CRITICO_BASSO":
            return "ALTO", f"Valore significativamente inferiore ai limiti di riferimento ({value} {self.default_unit})."
        elif flag in ["ALTO", "BASSO"]:
            return "MODERATO", f"Valore lievemente scostato dai parametri fisiologici attesi ({value} {self.default_unit})."
        return "BASSO", f"Parametro nei limiti fisiologici di normalita ({value} {self.default_unit})."

    def process(self, original_name: str, val_num: Optional[float], val_txt: Optional[str], unit: str, r_min: Optional[float], r_max: Optional[float], data_prelievo: str, laboratorio: str, note: Optional[str] = None) -> BiomarkerResult:
        processed_val = val_num
        target_unit = unit or self.default_unit

        if processed_val is not None and unit:
            processed_val, target_unit = self.convert_unit(processed_val, unit)

        final_min = r_min if r_min is not None else self.default_min
        final_max = r_max if r_max is not None else self.default_max

        flag = self.determine_flag(processed_val, final_min, final_max)
        risk, insight = self.evaluate_clinical_risk(flag, processed_val)

        return BiomarkerResult(
            categoria=self.category,
            nome_esame_originale=original_name,
            nome_standardizzato=self.standard_name,
            valore_numerico=processed_val,
            valore_testuale=val_txt,
            unita_misura=target_unit,
            range_min=final_min,
            range_max=final_max,
            stato_flag=flag,
            rischio_clinico=risk,
            interpretazione=insight,
            data_prelievo=data_prelievo,
            laboratorio=laboratorio,
            note_referto=note
        )
