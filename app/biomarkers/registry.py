from typing import Dict, Optional, Tuple
from app.biomarkers.base import BaseBiomarkerAlgorithm, BiomarkerResult
from app.biomarkers.metabolico.glicemia.algorithm import glicemia_algorithm
from app.biomarkers.metabolico.emoglobina_glicata.algorithm import emoglobina_glicata_algorithm
from app.biomarkers.lipidico.colesterolo_totale.algorithm import colesterolo_totale_algorithm
from app.biomarkers.lipidico.colesterolo_ldl.algorithm import colesterolo_ldl_algorithm
from app.biomarkers.lipidico.colesterolo_hdl.algorithm import colesterolo_hdl_algorithm
from app.biomarkers.lipidico.trigliceridi.algorithm import trigliceridi_algorithm
from app.biomarkers.epatico.alt.algorithm import alt_algorithm
from app.biomarkers.epatico.ast.algorithm import ast_algorithm
from app.biomarkers.epatico.ggt.algorithm import ggt_algorithm
from app.biomarkers.renale.creatinina.algorithm import creatinina_algorithm
from app.biomarkers.tiroide.tsh.algorithm import tsh_algorithm
from app.biomarkers.marziale.ferritina.algorithm import ferritina_algorithm
from app.biomarkers.emocromo.emoglobina.algorithm import emoglobina_algorithm
from app.biomarkers.infiammatorio.pcr.algorithm import pcr_algorithm
from app.biomarkers.vitamine.vitamina_d.algorithm import vitamina_d_algorithm

ALGORITHM_REGISTRY: Dict[str, BaseBiomarkerAlgorithm] = {
    "Glucosio Basale": glicemia_algorithm,
    "Emoglobina Glicata (HbA1c)": emoglobina_glicata_algorithm,
    "Colesterolo Totale": colesterolo_totale_algorithm,
    "Colesterolo LDL": colesterolo_ldl_algorithm,
    "Colesterolo HDL": colesterolo_hdl_algorithm,
    "Trigliceridi": trigliceridi_algorithm,
    "Alanina Aminotransferasi (ALT)": alt_algorithm,
    "Aspartato Aminotransferasi (AST)": ast_algorithm,
    "Gamma Glutamil Transferasi (GGT)": ggt_algorithm,
    "Creatinina Sierica": creatinina_algorithm,
    "Tireotropina (TSH)": tsh_algorithm,
    "Ferritina": ferritina_algorithm,
    "Emoglobina (Hb)": emoglobina_algorithm,
    "Proteina C Reattiva (PCR)": pcr_algorithm,
    "Vitamina D (25-OH)": vitamina_d_algorithm
}

SYNONYMS_TO_STANDARD: Dict[str, str] = {
    "glicemia": "Glucosio Basale",
    "glucosio": "Glucosio Basale",
    "glucosio basale": "Glucosio Basale",
    "glicemia a digiuno": "Glucosio Basale",
    "hba1c": "Emoglobina Glicata (HbA1c)",
    "emoglobina glicata": "Emoglobina Glicata (HbA1c)",
    "colesterolo": "Colesterolo Totale",
    "colesterolo totale": "Colesterolo Totale",
    "colesterolo ldl": "Colesterolo LDL",
    "ldl": "Colesterolo LDL",
    "colesterolo hdl": "Colesterolo HDL",
    "hdl": "Colesterolo HDL",
    "trigliceridi": "Trigliceridi",
    "alt": "Alanina Aminotransferasi (ALT)",
    "gpt": "Alanina Aminotransferasi (ALT)",
    "alanina aminotransferasi": "Alanina Aminotransferasi (ALT)",
    "transaminasi alt": "Alanina Aminotransferasi (ALT)",
    "transaminasi gpt": "Alanina Aminotransferasi (ALT)",
    "ast": "Aspartato Aminotransferasi (AST)",
    "got": "Aspartato Aminotransferasi (AST)",
    "aspartato aminotransferasi": "Aspartato Aminotransferasi (AST)",
    "transaminasi ast": "Aspartato Aminotransferasi (AST)",
    "transaminasi got": "Aspartato Aminotransferasi (AST)",
    "gamma gt": "Gamma Glutamil Transferasi (GGT)",
    "ggt": "Gamma Glutamil Transferasi (GGT)",
    "gamma glutamil transferasi": "Gamma Glutamil Transferasi (GGT)",
    "creatinina": "Creatinina Sierica",
    "creatininemia": "Creatinina Sierica",
    "tsh": "Tireotropina (TSH)",
    "ormone tireotropo": "Tireotropina (TSH)",
    "ferritina": "Ferritina",
    "emoglobina": "Emoglobina (Hb)",
    "hb": "Emoglobina (Hb)",
    "pcr": "Proteina C Reattiva (PCR)",
    "proteina c reattiva": "Proteina C Reattiva (PCR)",
    "vitamina d": "Vitamina D (25-OH)",
    "25 oh vitamina d": "Vitamina D (25-OH)"
}

class BiomarkerAlgorithmRegistry:
    def __init__(self):
        self.ready = True

    def find_algorithm(self, name: str) -> Tuple[BaseBiomarkerAlgorithm, str]:
        cleaned = name.strip().lower()
        standard_name = SYNONYMS_TO_STANDARD.get(cleaned)
        if not standard_name:
            for syn, std in SYNONYMS_TO_STANDARD.items():
                if syn in cleaned:
                    standard_name = std
                    break

        if standard_name and standard_name in ALGORITHM_REGISTRY:
            return ALGORITHM_REGISTRY[standard_name], standard_name

        generic_algo = BaseBiomarkerAlgorithm(
            standard_name=name.strip(),
            category="Altro",
            default_unit="",
            default_min=None,
            default_max=None
        )
        return generic_algo, name.strip()

biomarker_registry = BiomarkerAlgorithmRegistry()
