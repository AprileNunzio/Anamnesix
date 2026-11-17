from typing import Dict, Any, Optional, List

def evaluate_semen_sample(
    volume_ml: Optional[float] = None,
    concentration_m_ml: Optional[float] = None,
    progressive_motility_pct: Optional[float] = None,
    total_motility_pct: Optional[float] = None,
    normal_morphology_pct: Optional[float] = None,
    leukocytes_m_ml: Optional[float] = None,
    ph: Optional[float] = None
) -> Dict[str, Any]:
    anomalies: List[str] = []
    diagnosi: List[str] = []

    if volume_ml is not None:
        if volume_ml < 1.4:
            anomalies.append(f"Volume seminale ridotto ({volume_ml} mL, rif WHO: >= 1.4 mL)")
            diagnosi.append("Ipospermia")
        elif volume_ml > 6.0:
            anomalies.append(f"Volume seminale eccessivo ({volume_ml} mL)")
            diagnosi.append("Iperspermia")

    if concentration_m_ml is not None:
        if concentration_m_ml == 0.0:
            anomalies.append("Assenza totale di nemaspermi")
            diagnosi.append("Azoospermia")
        elif concentration_m_ml < 16.0:
            anomalies.append(f"Concentrazione inferiore al cut-off WHO ({concentration_m_ml} M/mL, rif: >= 16 M/mL)")
            diagnosi.append("Oligozoospermia")

    if progressive_motility_pct is not None:
        if progressive_motility_pct < 30.0:
            anomalies.append(f"Motilita progressiva ridotta ({progressive_motility_pct}%, rif: >= 30%)")
            diagnosi.append("Astenozoospermia")

    if normal_morphology_pct is not None:
        if normal_morphology_pct < 4.0:
            anomalies.append(f"Morfologia tipica deficitaria ({normal_morphology_pct}%, rif WHO: >= 4%)")
            diagnosi.append("Teratozoospermia")

    if leukocytes_m_ml is not None and leukocytes_m_ml > 1.0:
        anomalies.append(f"Presenza di leucociti seminali sopra la soglia infiammatoria ({leukocytes_m_ml} M/mL, rif: < 1.0 M/mL)")
        diagnosi.append("Leucocitospermia")

    if "Oligozoospermia" in diagnosi and "Astenozoospermia" in diagnosi and "Teratozoospermia" in diagnosi:
        diagnosi_principale = "Oligoastenoteratozoospermia (Sindrome OAT)"
    elif "Azoospermia" in diagnosi:
        diagnosi_principale = "Azoospermia"
    elif not diagnosi:
        diagnosi_principale = "Normozoospermia (Campione Esemplare nei Limiti WHO 2021)"
    else:
        diagnosi_principale = " + ".join(diagnosi)

    indice_fertilita = 100.0 - (len(anomalies) * 22.0)
    indice_fertilita = max(10.0, min(100.0, indice_fertilita))

    return {
        "diagnosi_clinica": diagnosi_principale,
        "punteggio_qualita_seminale": round(indice_fertilita, 1),
        "anomalie_rilevate": anomalies,
        "parametri_analizzati": {
            "volume_ml": volume_ml,
            "concentrazione_m_ml": concentration_m_ml,
            "motilita_progressiva_pct": progressive_motility_pct,
            "motilita_totale_pct": total_motility_pct,
            "morfologia_normale_pct": normal_morphology_pct,
            "leucociti_m_ml": leukocytes_m_ml,
            "ph": ph
        }
    }
