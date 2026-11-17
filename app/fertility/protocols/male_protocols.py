from typing import Dict, Any, List

def get_male_fertility_protocol(age: int) -> Dict[str, Any]:
    if age < 35:
        fascia = "Meno di 35 anni (Giovane Andrologico)"
        priorita = "Ottimizzazione stile di vita, esclusione varicocele e flogosi delle vie seminali."
    elif 35 <= age <= 45:
        fascia = "35 - 45 anni (Stabilita Riproduttiva)"
        priorita = "Screening integrato stress ossidativo, frammentazione DNA e integrita dell'asse ipotalamo-ipofisi-testicolo."
    else:
        fascia = "Oltre 45 anni (Declino Spermatico Progressivo)"
        priorita = "Aumento statistico di mutazioni de novo, frammentazione DNA raddoppiata e rischio aneuploidie; indicata selezione ICSI con MACS/PICSI."

    controlli_primo_livello = [
        {"nome": "Spermiogramma Completo (Criteri WHO 6a Edizione 2021)", "parametri": "Volume, pH, concentrazione (M/mL), motilita totale e progressiva (PR%), morfologia (forme normali %), leucociti", "obbligatorio": True},
        {"nome": "Spermiocoltura con Antibiogramma", "parametri": "Ricerca germi comuni, miceti e protozoi nel secreto seminale", "obbligatorio": True},
        {"nome": "Visita Andrologica Specialistica", "parametri": "Valutazione volume testicolare (orchidometro di Prader), consistenza epididimi, reflusso plesso pampiniforme", "obbligatorio": True}
    ]

    controlli_secondo_livello = [
        {"nome": "Ecocolordoppler Scrotale e Testicolare", "parametri": "Didimi, epididimi, diametro vene plesso pampiniforme a riposo e sotto torchio addominale (Valsalva)", "obbligatorio": True},
        {"nome": "Ecografia Prostato-Vescicolare Transrettale (TRUS)", "parametri": "Esclusione ostruzioni dotti eiaculatori, cisti otricolari e prostatiti croniche", "obbligatorio": False},
        {"nome": "Profilo Ormonale Andrologico", "parametri": "Testosterone Totale, Testosterone Libero, SHBG, LH, FSH, Prolattina, 17-Beta Estradiolo", "obbligatorio": True}
    ]

    controlli_terzo_livello = [
        {"nome": "Test di Frammentazione del DNA Spermatico (DFI)", "parametri": "Percentuale di rotture a singolo e doppio filamento nel DNA nemaspermico (TUNEL o SCSA)", "obbligatorio": age >= 40 or age < 40},
        {"nome": "Mappa Cromosomica (Cariotipo Costituzionale)", "parametri": "Esclusione sindrome di Klinefelter (47,XXY) o traslocazioni bilanciate", "obbligatorio": True},
        {"nome": "Ricerca Microdelezioni Cromosoma Y (AZFa, AZFb, AZFc)", "parametri": "Analisi multiplex PCR in caso di concentrazione < 5 milioni/mL", "obbligatorio": False},
        {"nome": "Analisi Genetica Gene CFTR (Fibrosi Cistica)", "parametri": "Obbligatoria in caso di assenza congenita dei vasi deferenti (CBAVD) o azoospermia ostruttiva", "obbligatorio": False}
    ]

    return {
        "genere": "Maschile",
        "eta": age,
        "fascia_clinica": fascia,
        "strategia_prioritaria": priorita,
        "controlli_primo_livello": controlli_primo_livello,
        "controlli_secondo_livello": controlli_secondo_livello,
        "controlli_terzo_livello": controlli_terzo_livello
    }
