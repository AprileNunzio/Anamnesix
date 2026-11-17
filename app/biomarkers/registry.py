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
from app.biomarkers.fertilita.donna.amh.algorithm import amh_algorithm
from app.biomarkers.fertilita.donna.fsh.algorithm import fsh_donna_algorithm
from app.biomarkers.fertilita.donna.estradiolo.algorithm import estradiolo_algorithm
from app.biomarkers.fertilita.donna.progesterone.algorithm import progesterone_algorithm
from app.biomarkers.fertilita.uomo.spermiogramma_concentrazione.algorithm import spermiogramma_concentrazione_algorithm
from app.biomarkers.fertilita.uomo.spermiogramma_motilita.algorithm import spermiogramma_motilita_algorithm
from app.biomarkers.fertilita.uomo.spermiogramma_morfologia.algorithm import spermiogramma_morfologia_algorithm
from app.biomarkers.fertilita.uomo.frammentazione_dna.algorithm import frammentazione_dna_algorithm
from app.biomarkers.fertilita.uomo.testosterone_totale.algorithm import testosterone_totale_algorithm

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
    "Vitamina D (25-OH)": vitamina_d_algorithm,
    "Ormone Anti-Mulleriano (AMH)": amh_algorithm,
    "Ormone Follicolo-Stimolante (FSH Basale)": fsh_donna_algorithm,
    "17-Beta Estradiolo (E2)": estradiolo_algorithm,
    "Progesterone (Fase Luteale / Giorno 21)": progesterone_algorithm,
    "Concentrazione Spermatozoi (Spermiogramma WHO 6th)": spermiogramma_concentrazione_algorithm,
    "Motilita Progressiva Spermatozoi (PR %)": spermiogramma_motilita_algorithm,
    "Morfologia Tipica Spermatozoi (Kruger %)": spermiogramma_morfologia_algorithm,
    "Indice di Frammentazione DNA Spermatico (DFI %)": frammentazione_dna_algorithm,
    "Testosterone Totale": testosterone_totale_algorithm
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
    "25 oh vitamina d": "Vitamina D (25-OH)",
    "amh": "Ormone Anti-Mulleriano (AMH)",
    "ormone anti mulleriano": "Ormone Anti-Mulleriano (AMH)",
    "ormone antimulleriano": "Ormone Anti-Mulleriano (AMH)",
    "fsh": "Ormone Follicolo-Stimolante (FSH Basale)",
    "fsh basale": "Ormone Follicolo-Stimolante (FSH Basale)",
    "estradiolo": "17-Beta Estradiolo (E2)",
    "17 beta estradiolo": "17-Beta Estradiolo (E2)",
    "e2": "17-Beta Estradiolo (E2)",
    "progesterone": "Progesterone (Fase Luteale / Giorno 21)",
    "progesterone giorno 21": "Progesterone (Fase Luteale / Giorno 21)",
    "concentrazione spermatozoi": "Concentrazione Spermatozoi (Spermiogramma WHO 6th)",
    "numero spermatozoi": "Concentrazione Spermatozoi (Spermiogramma WHO 6th)",
    "spermatozoi ml": "Concentrazione Spermatozoi (Spermiogramma WHO 6th)",
    "motilita progressiva": "Motilita Progressiva Spermatozoi (PR %)",
    "mobilita progressiva": "Motilita Progressiva Spermatozoi (PR %)",
    "motilita spermatozoi": "Motilita Progressiva Spermatozoi (PR %)",
    "morfologia tipica": "Morfologia Tipica Spermatozoi (Kruger %)",
    "forme tipiche": "Morfologia Tipica Spermatozoi (Kruger %)",
    "forme normali": "Morfologia Tipica Spermatozoi (Kruger %)",
    "morfologia kruger": "Morfologia Tipica Spermatozoi (Kruger %)",
    "frammentazione dna": "Indice di Frammentazione DNA Spermatico (DFI %)",
    "frammentazione dna spermatico": "Indice di Frammentazione DNA Spermatico (DFI %)",
    "dfi": "Indice di Frammentazione DNA Spermatico (DFI %)",
    "testosterone": "Testosterone Totale",
    "testosterone totale": "Testosterone Totale"
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
