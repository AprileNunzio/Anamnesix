import os
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from app.biomarkers.base import BaseBiomarkerAlgorithm, BiomarkerResult
import app.biomarkers.registry as registry_module

class DynamicUniversalBiomarkerAlgorithm(BaseBiomarkerAlgorithm):
    def __init__(self, standard_name: str, category: str, default_unit: str = ""):
        self.standard_name = standard_name
        self.category = category
        self.default_unit = default_unit

    def evaluate(
        self,
        value: Optional[float],
        text_value: Optional[str] = None,
        custom_min: Optional[float] = None,
        custom_max: Optional[float] = None,
        unit: Optional[str] = None
    ) -> BiomarkerResult:
        eff_unit = unit or self.default_unit
        if value is None and text_value:
            txt_lower = text_value.lower().strip()
            if any(term in txt_lower for term in ["negativo", "assente", "assenti", "normale", "non rilevato", "tracce minime"]):
                flag = "NORMALE"
                desc = f"{self.standard_name}: Valore testuale regolare ({text_value})."
            elif any(term in txt_lower for term in ["positivo", "rilevato", "presente", "presenti", "reattivo"]):
                flag = "ALTO"
                desc = f"{self.standard_name}: Riscontro qualitativo positivo ({text_value}), richiede valutazione medica."
            else:
                flag = "NORMALE"
                desc = f"{self.standard_name}: Parametro testuale rilevato ({text_value})."
            return BiomarkerResult(
                standard_name=self.standard_name,
                category=self.category,
                value_numeric=None,
                value_text=text_value,
                unit=eff_unit,
                range_min=custom_min,
                range_max=custom_max,
                status_flag=flag,
                percentage_deviation=0.0,
                clinical_evaluation=desc
            )

        val = value if value is not None else 0.0
        ref_min = custom_min
        ref_max = custom_max

        flag = "NORMALE"
        dev = 0.0

        if ref_min is not None and val < ref_min:
            dev = ((ref_min - val) / ref_min) * 100.0 if ref_min != 0 else 0.0
            flag = "CRITICO_BASSO" if dev > 30.0 else "BASSO"
        elif ref_max is not None and val > ref_max:
            dev = ((val - ref_max) / ref_max) * 100.0 if ref_max != 0 else 0.0
            flag = "CRITICO_ALTO" if dev > 30.0 else "ALTO"

        if flag == "NORMALE":
            eval_text = f"{self.standard_name} pari a {val:.2f} {eff_unit}, perfettamente entro i parametri fisiologici."
        elif flag in ("BASSO", "CRITICO_BASSO"):
            eval_text = f"{self.standard_name} inferiore al valore di riferimento (-{dev:.1f}%). Valore riscontrato: {val:.2f} {eff_unit} (soglia minima: {ref_min})."
        else:
            eval_text = f"{self.standard_name} superiore alla soglia fisiologica (+{dev:.1f}%). Valore riscontrato: {val:.2f} {eff_unit} (soglia massima: {ref_max})."

        return BiomarkerResult(
            standard_name=self.standard_name,
            category=self.category,
            value_numeric=val,
            value_text=text_value,
            unit=eff_unit,
            range_min=ref_min,
            range_max=ref_max,
            status_flag=flag,
            percentage_deviation=round(dev, 2),
            clinical_evaluation=eval_text
        )

class BiomarkerAutoScanner:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).resolve().parent

    def scan_and_register_all(self) -> Dict[str, Any]:
        scanned_count = 0
        registered_count = 0
        discovered_algorithms: List[str] = []

        for root, _, files in os.walk(str(self.base_dir)):
            if "__pycache__" in root:
                continue
            for file_name in files:
                if file_name.endswith(".py") and file_name != "__init__.py" and file_name != "base.py" and file_name != "scanner.py" and file_name != "registry.py":
                    file_path = Path(root) / file_name
                    scanned_count += 1
                    try:
                        module_name = f"dynamic_biomarker_{file_path.stem}_{scanned_count}"
                        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = mod
                            spec.loader.exec_module(mod)
                            for attr_name in dir(mod):
                                attr_val = getattr(mod, attr_name)
                                if isinstance(attr_val, BaseBiomarkerAlgorithm) and not isinstance(attr_val, type):
                                    std_name = attr_val.standard_name
                                    registry_module.ALGORITHM_REGISTRY[std_name] = attr_val
                                    registry_module.SYNONYMS_TO_STANDARD[std_name.lower().strip()] = std_name
                                    discovered_algorithms.append(std_name)
                                    registered_count += 1
                    except Exception as err:
                        self.last_scan_error = str(err)

        return {
            "total_files_scanned": scanned_count,
            "total_algorithms_registered": len(registry_module.ALGORITHM_REGISTRY),
            "newly_discovered": registered_count,
            "algorithms": list(registry_module.ALGORITHM_REGISTRY.keys())
        }

    def resolve_or_create_algorithm(self, analyte_name: str, category: str = "Clinico Generale", default_unit: str = "") -> BaseBiomarkerAlgorithm:
        clean_name = analyte_name.strip()
        lower_name = clean_name.lower()
        std_name = registry_module.SYNONYMS_TO_STANDARD.get(lower_name, clean_name)
        if std_name in registry_module.ALGORITHM_REGISTRY:
            return registry_module.ALGORITHM_REGISTRY[std_name]
        dyn_algo = DynamicUniversalBiomarkerAlgorithm(
            standard_name=std_name,
            category=category,
            default_unit=default_unit
        )
        registry_module.ALGORITHM_REGISTRY[std_name] = dyn_algo
        registry_module.SYNONYMS_TO_STANDARD[lower_name] = std_name
        return dyn_algo

biomarker_auto_scanner = BiomarkerAutoScanner()
