import re
from typing import Tuple, Optional, Dict, Any
from app.database.models import AnalitaBase

SYNONYM_MAP: Dict[str, Tuple[str, str, str]] = {
    "alt": ("Alanina Aminotransferasi (ALT)", "Funzionalita Epatica", "U/L"),
    "gpt": ("Alanina Aminotransferasi (ALT)", "Funzionalita Epatica", "U/L"),
    "alanina aminotransferasi": ("Alanina Aminotransferasi (ALT)", "Funzionalita Epatica", "U/L"),
    "transaminasi alt": ("Alanina Aminotransferasi (ALT)", "Funzionalita Epatica", "U/L"),
    "transaminasi gpt": ("Alanina Aminotransferasi (ALT)", "Funzionalita Epatica", "U/L"),
    "ast": ("Aspartato Aminotransferasi (AST)", "Funzionalita Epatica", "U/L"),
    "got": ("Aspartato Aminotransferasi (AST)", "Funzionalita Epatica", "U/L"),
    "aspartato aminotransferasi": ("Aspartato Aminotransferasi (AST)", "Funzionalita Epatica", "U/L"),
    "transaminasi ast": ("Aspartato Aminotransferasi (AST)", "Funzionalita Epatica", "U/L"),
    "transaminasi got": ("Aspartato Aminotransferasi (AST)", "Funzionalita Epatica", "U/L"),
    "gamma gt": ("Gamma Glutamil Transferasi (GGT)", "Funzionalita Epatica", "U/L"),
    "ggt": ("Gamma Glutamil Transferasi (GGT)", "Funzionalita Epatica", "U/L"),
    "gamma glutamil transferasi": ("Gamma Glutamil Transferasi (GGT)", "Funzionalita Epatica", "U/L"),
    "fosfatasi alcalina": ("Fosfatasi Alcalina (ALP)", "Funzionalita Epatica", "U/L"),
    "alp": ("Fosfatasi Alcalina (ALP)", "Funzionalita Epatica", "U/L"),
    "bilirubina totale": ("Bilirubina Totale", "Funzionalita Epatica", "mg/dL"),
    "bilirubina diretta": ("Bilirubina Diretta", "Funzionalita Epatica", "mg/dL"),
    "bilirubina frazionata": ("Bilirubina Totale", "Funzionalita Epatica", "mg/dL"),
    "glicemia": ("Glucosio Basale", "Metabolico", "mg/dL"),
    "glucosio": ("Glucosio Basale", "Metabolico", "mg/dL"),
    "glucosio basale": ("Glucosio Basale", "Metabolico", "mg/dL"),
    "glicemia a digiuno": ("Glucosio Basale", "Metabolico", "mg/dL"),
    "hba1c": ("Emoglobina Glicata (HbA1c)", "Metabolico", "%"),
    "emoglobina glicata": ("Emoglobina Glicata (HbA1c)", "Metabolico", "%"),
    "colesterolo totale": ("Colesterolo Totale", "Profilo Lipidico", "mg/dL"),
    "colesterolo": ("Colesterolo Totale", "Profilo Lipidico", "mg/dL"),
    "hdl": ("Colesterolo HDL", "Profilo Lipidico", "mg/dL"),
    "colesterolo hdl": ("Colesterolo HDL", "Profilo Lipidico", "mg/dL"),
    "ldl": ("Colesterolo LDL", "Profilo Lipidico", "mg/dL"),
    "colesterolo ldl": ("Colesterolo LDL", "Profilo Lipidico", "mg/dL"),
    "trigliceridi": ("Trigliceridi", "Profilo Lipidico", "mg/dL"),
    "creatinina": ("Creatinina Sierica", "Funzionalita Renale", "mg/dL"),
    "creatininemia": ("Creatinina Sierica", "Funzionalita Renale", "mg/dL"),
    "azotemia": ("Azotemia (Urea)", "Funzionalita Renale", "mg/dL"),
    "urea": ("Azotemia (Urea)", "Funzionalita Renale", "mg/dL"),
    "egfr": ("Velocita di Filtrazione Glomerulare (eGFR)", "Funzionalita Renale", "mL/min/1.73m2"),
    "filtrato glomerulare": ("Velocita di Filtrazione Glomerulare (eGFR)", "Funzionalita Renale", "mL/min/1.73m2"),
    "acido urico": ("Acido Urico", "Metabolico", "mg/dL"),
    "uricemia": ("Acido Urico", "Metabolico", "mg/dL"),
    "tsh": ("Tireotropina (TSH)", "Tiroide", "uUI/mL"),
    "ormone tireotropo": ("Tireotropina (TSH)", "Tiroide", "uUI/mL"),
    "ft3": ("Triiodotironina Libera (FT3)", "Tiroide", "pg/mL"),
    "triiodotironina libera": ("Triiodotironina Libera (FT3)", "Tiroide", "pg/mL"),
    "ft4": ("Tiroxina Libera (FT4)", "Tiroide", "ng/dL"),
    "tiroxina libera": ("Tiroxina Libera (FT4)", "Tiroide", "ng/dL"),
    "sideremia": ("Sideremia (Ferro)", "Ematologico", "ug/dL"),
    "ferro": ("Sideremia (Ferro)", "Ematologico", "ug/dL"),
    "ferritina": ("Ferritina", "Ematologico", "ng/mL"),
    "emoglobina": ("Emoglobina (Hb)", "Ematologico", "g/dL"),
    "hb": ("Emoglobina (Hb)", "Ematologico", "g/dL"),
    "globuli rossi": ("Globuli Rossi (RBC)", "Ematologico", "10^6/uL"),
    "rbc": ("Globuli Rossi (RBC)", "Ematologico", "10^6/uL"),
    "eritrociti": ("Globuli Rossi (RBC)", "Ematologico", "10^6/uL"),
    "globuli bianchi": ("Globuli Bianchi (WBC)", "Ematologico", "10^3/uL"),
    "wbc": ("Globuli Bianchi (WBC)", "Ematologico", "10^3/uL"),
    "leucociti": ("Globuli Bianchi (WBC)", "Ematologico", "10^3/uL"),
    "piastrine": ("Piastrine (PLT)", "Ematologico", "10^3/uL"),
    "plt": ("Piastrine (PLT)", "Ematologico", "10^3/uL"),
    "ematocrito": ("Ematocrito (HCT)", "Ematologico", "%"),
    "hct": ("Ematocrito (HCT)", "Ematologico", "%"),
    "mcv": ("Volume Corpuscolare Medio (MCV)", "Ematologico", "fL"),
    "mch": ("Contenuto Medio di Emoglobina (MCH)", "Ematologico", "pg"),
    "mchc": ("Concentrazione Media di Emoglobina (MCHC)", "Ematologico", "g/dL"),
    "rdw": ("Ampiezza Distribuzione Eritrocitaria (RDW)", "Ematologico", "%"),
    "ves": ("Velocita di Eritrosedimentazione (VES)", "Infiammatorio", "mm/h"),
    "pcr": ("Proteina C Reattiva (PCR)", "Infiammatorio", "mg/L"),
    "proteina c reattiva": ("Proteina C Reattiva (PCR)", "Infiammatorio", "mg/L"),
    "vitamina d": ("Vitamina D (25-OH)", "Vitamine", "ng/mL"),
    "25 oh vitamina d": ("Vitamina D (25-OH)", "Vitamine", "ng/mL"),
    "vitamina b12": ("Vitamina B12", "Vitamine", "pg/mL"),
    "acido folico": ("Acido Folico (Folati)", "Vitamine", "ng/mL"),
    "folati": ("Acido Folico (Folati)", "Vitamine", "ng/mL"),
    "sodio": ("Sodio (Na)", "Elettroliti", "mEq/L"),
    "potassio": ("Potassio (K)", "Elettroliti", "mEq/L"),
    "cloro": ("Cloro (Cl)", "Elettroliti", "mEq/L"),
    "calcio": ("Calcio Totale", "Elettroliti", "mg/dL"),
    "magnesio": ("Magnesio", "Elettroliti", "mg/dL"),
    "omocisteina": ("Omocisteina", "Cardiovascolare", "umol/L"),
    "d-dimero": ("D-Dimero", "Coagulazione", "ng/mL"),
    "fibrinogeno": ("Fibrinogeno", "Coagulazione", "mg/dL"),
    "inr": ("INR (Tempo di Protrombina)", "Coagulazione", "indice"),
    "pt": ("Tempo di Protrombina (PT)", "Coagulazione", "sec")
}

class BiomarkerNormalizer:
    def __init__(self):
        self.ready = True

    def clean_name(self, name: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", name.lower())
        return " ".join(cleaned.split())

    def match_synonym(self, original_name: str) -> Optional[Tuple[str, str, str]]:
        c_name = self.clean_name(original_name)
        if c_name in SYNONYM_MAP:
            return SYNONYM_MAP[c_name]
        for key, val in SYNONYM_MAP.items():
            if key in c_name:
                return val
        return None

    def convert_units(
        self,
        value: float,
        unit: str,
        target_unit: str,
        biomarker_name: str
    ) -> Tuple[float, str]:
        u_clean = unit.lower().replace(" ", "")
        t_clean = target_unit.lower().replace(" ", "")

        if u_clean == t_clean:
            return value, target_unit

        if "glucosio" in biomarker_name.lower():
            if "mmol/l" in u_clean and "mg/dl" in t_clean:
                return round(value * 18.0182, 2), target_unit
            if "mg/dl" in u_clean and "mmol/l" in t_clean:
                return round(value / 18.0182, 2), target_unit

        if "colesterolo" in biomarker_name.lower():
            if "mmol/l" in u_clean and "mg/dl" in t_clean:
                return round(value * 38.67, 2), target_unit
            if "mg/dl" in u_clean and "mmol/l" in t_clean:
                return round(value / 38.67, 2), target_unit

        if "trigliceridi" in biomarker_name.lower():
            if "mmol/l" in u_clean and "mg/dl" in t_clean:
                return round(value * 88.57, 2), target_unit
            if "mg/dl" in u_clean and "mmol/l" in t_clean:
                return round(value / 88.57, 2), target_unit

        if "g/l" in u_clean and "g/dl" in t_clean:
            return round(value / 10.0, 2), target_unit
        if "g/dl" in u_clean and "g/l" in t_clean:
            return round(value * 10.0, 2), target_unit

        return value, unit

    def determine_flag(
        self,
        val: Optional[float],
        r_min: Optional[float],
        r_max: Optional[float]
    ) -> str:
        if val is None:
            return "NORMALE"

        if r_min is not None and r_max is not None:
            if val < r_min:
                deviation = (r_min - val) / (r_max - r_min if r_max != r_min else 1.0)
                return "CRITICO_BASSO" if deviation > 0.5 else "BASSO"
            elif val > r_max:
                deviation = (val - r_max) / (r_max - r_min if r_max != r_min else 1.0)
                return "CRITICO_ALTO" if deviation > 0.5 else "ALTO"
            else:
                return "NORMALE"

        if r_min is not None and val < r_min:
            return "BASSO"
        if r_max is not None and val > r_max:
            return "ALTO"

        return "NORMALE"

    def normalize_item(
        self,
        item: Dict[str, Any],
        default_data: str,
        default_lab: str
    ) -> AnalitaBase:
        orig_name = item.get("nome_esame_originale", "").strip()
        match = self.match_synonym(orig_name)

        if match:
            standard_name, category, default_unit = match
        else:
            standard_name = item.get("nome_standardizzato", orig_name).strip()
            category = item.get("categoria", "Altro").strip()
            default_unit = item.get("unita_misura", "").strip()

        unita = item.get("unita_misura", default_unit).strip()
        val_num = item.get("valore_numerico")
        val_str = item.get("valore_testuale")
        r_min = item.get("range_min")
        r_max = item.get("range_max")

        if val_num is not None:
            val_num, unita = self.convert_units(val_num, unita, default_unit, standard_name)

        flag = item.get("stato_flag")
        if not flag or flag not in ["NORMALE", "BASSO", "ALTO", "CRITICO_BASSO", "CRITICO_ALTO"]:
            flag = self.determine_flag(val_num, r_min, r_max)

        return AnalitaBase(
            categoria=category,
            nome_esame_originale=orig_name,
            nome_standardizzato=standard_name,
            valore_numerico=val_num,
            valore_testuale=val_str,
            unita_misura=unita,
            range_min=r_min,
            range_max=r_max,
            stato_flag=flag,
            data_prelievo=item.get("data_prelievo", default_data),
            laboratorio=item.get("laboratorio", default_lab),
            note_referto=item.get("note_referto")
        )

biomarker_normalizer = BiomarkerNormalizer()
