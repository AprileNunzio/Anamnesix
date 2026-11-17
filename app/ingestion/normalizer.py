from typing import Dict, Any, Optional
from app.database.models import AnalitaBase
from app.biomarkers.registry import biomarker_registry

class BiomarkerNormalizer:
    def __init__(self):
        self.ready = True

    def normalize_item(
        self,
        item: Dict[str, Any],
        default_data: str,
        default_lab: str
    ) -> AnalitaBase:
        orig_name = item.get("nome_esame_originale", "").strip()
        val_num = item.get("valore_numerico")
        val_txt = item.get("valore_testuale")
        unit = item.get("unita_misura", "").strip()
        r_min = item.get("range_min")
        r_max = item.get("range_max")
        dt = item.get("data_prelievo") or default_data
        lab = item.get("laboratorio") or default_lab
        note = item.get("note_referto")

        algorithm, standard_name = biomarker_registry.find_algorithm(orig_name or item.get("nome_standardizzato", ""))

        processed_result = algorithm.process(
            original_name=orig_name or standard_name,
            val_num=val_num,
            val_txt=val_txt,
            unit=unit,
            r_min=r_min,
            r_max=r_max,
            data_prelievo=dt,
            laboratorio=lab,
            note=note
        )

        return AnalitaBase(
            categoria=processed_result.categoria,
            nome_esame_originale=processed_result.nome_esame_originale,
            nome_standardizzato=processed_result.nome_standardizzato,
            valore_numerico=processed_result.valore_numerico,
            valore_testuale=processed_result.valore_testuale,
            unita_misura=processed_result.unita_misura,
            range_min=processed_result.range_min,
            range_max=processed_result.range_max,
            stato_flag=processed_result.stato_flag,
            data_prelievo=processed_result.data_prelievo,
            laboratorio=processed_result.laboratorio,
            note_referto=processed_result.note_referto
        )

biomarker_normalizer = BiomarkerNormalizer()
