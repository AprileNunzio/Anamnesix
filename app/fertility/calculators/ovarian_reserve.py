from typing import Dict, Any, Optional

def calculate_ovarian_reserve(age: int, amh: Optional[float] = None, afc: Optional[int] = None) -> Dict[str, Any]:
    score = 100.0
    giudizio = "Normale"
    dettagli = []

    if age > 42:
        score -= 40.0
        dettagli.append(f"Eta biologica ({age} anni) con fisiologico declino ovocitario qualitativo e quantitativo.")
    elif age > 38:
        score -= 25.0
        dettagli.append(f"Eta materna ({age} anni) in fascia di progressiva riduzione della coorte follicolare.")
    elif age > 35:
        score -= 10.0
        dettagli.append(f"Eta materna ({age} anni) corrispondente a inizio della fase di transizione fertile.")

    if amh is not None:
        if amh < 0.5:
            score -= 35.0
            dettagli.append(f"AMH critico ({amh} ng/mL): riserva follicolare primaria gravemente ridotta.")
        elif amh < 1.1:
            score -= 20.0
            dettagli.append(f"AMH ridotto ({amh} ng/mL): potenziale risposta ovarica limitata.")
        elif amh > 5.0:
            score -= 5.0
            dettagli.append(f"AMH elevato ({amh} ng/mL): indicativo di PCO/PCOS, monitorare per iperstimolazione.")
        else:
            dettagli.append(f"AMH ottimo ({amh} ng/mL): riserva follicolare perfettamente conservata.")

    if afc is not None:
        if afc < 5:
            score -= 25.0
            dettagli.append(f"Conta Follicoli Antrali ridotta ({afc} follicoli totali): pool follicolare immediatamente arruolabile basso.")
        elif afc < 8:
            score -= 10.0
            dettagli.append(f"Conta Follicoli Antrali borderline ({afc} follicoli totali).")
        elif afc > 20:
            dettagli.append(f"Conta Follicoli Antrali molto ricca ({afc} follicoli totali): morfologia ovarica multifollicolare/policistica.")
        else:
            dettagli.append(f"Conta Follicoli Antrali adeguata ({afc} follicoli totali).")

    final_score = max(5.0, min(100.0, score))

    if final_score < 40:
        giudizio = "Riserva Ovarica Severamente Ridotta"
    elif final_score < 65:
        giudizio = "Riserva Ovarica Moderatamente Ridotta"
    elif final_score < 85:
        giudizio = "Riserva Ovarica Discreta"
    else:
        giudizio = "Riserva Ovarica Ottimale"

    return {
        "punteggio_riserva": round(final_score, 1),
        "classificazione": giudizio,
        "eta": age,
        "amh": amh,
        "afc": afc,
        "osservazioni": dettagli
    }
