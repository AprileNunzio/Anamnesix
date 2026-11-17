from typing import Dict, Any, List

def get_female_fertility_protocol(age: int) -> Dict[str, Any]:
    if age < 30:
        fascia = "Meno di 30 anni (Alta Riserva)"
        tempo_attesa = "12 mesi di tentativi mirati spontanei prima di indagini invasive."
        priorita = "Bassa urgenza cronologica; focus su ovulazione regolare e pervieta tubarica."
    elif 30 <= age <= 35:
        fascia = "30 - 35 anni (Fisiologica Fertilita)"
        tempo_attesa = "12 mesi di tentativi naturali; 6 mesi se presenti fattori di rischio (cicli irregolari, dismenorrea severa)."
        priorita = "Verifica bilancio ormonale Day 3 e screening ecografico transvaginale."
    elif 36 <= age <= 37:
        fascia = "36 - 37 anni (Transizione Fertile)"
        tempo_attesa = "Non oltre 6 mesi di tentativi prima di avviare il percorso diagnostico completo."
        priorita = "Stima accurata riserva ovarica (AMH + AFC) e valutazione immediata pervieta tubarica."
    elif 38 <= age <= 40:
        fascia = "38 - 40 anni (Declino Ovocitario Attivo)"
        tempo_attesa = "Massimo 3-6 mesi; indicata consulenza di Procreazione Medicalmente Assistita senza indugi."
        priorita = "PMA di II livello (FIVET/ICSI), diagnosi genetica pre-impianto per aneuploidie ovocitarie (PGT-A)."
    else:
        fascia = "Oltre 40 anni (Bassa Riserva / Over 40)"
        tempo_attesa = "Avvio diagnostico immediato al primo consulto."
        priorita = "Valutazione riserva follicolare residua, counseling su eterologa (ovodonazione) o stimolazioni personalizzate in doppio blocco."

    controlli_primo_livello = [
        {"nome": "Dosaggi Ormonali Basali (Giorno 2-3)", "parametri": "AMH, FSH, LH, 17-Beta Estradiolo, Prolattina, TSH", "obbligatorio": True},
        {"nome": "Progesterone Luteale (Giorno 20-22)", "parametri": "Progesterone per conferma ovulazione e tenuta fase luteale", "obbligatorio": True},
        {"nome": "Ecografia Pelvica Transvaginale 3D", "parametri": "Conta Follicoli Antrali (AFC bilateralmente), morfologia uterina, spessore endometriale", "obbligatorio": True},
        {"nome": "Screening Infettivo Completo", "parametri": "HIV, HBsAg, Anti-HCV, VDRL-TPHA, Rubeo, Toxoplasmosi, CMV", "obbligatorio": True},
        {"nome": "Tamponi Cervico-Vaginali Molecolari", "parametri": "Chlamydia Trachomatis, Mycoplasma Hominis, Ureaplasma Urealyticum, Gonococco", "obbligatorio": True}
    ]

    controlli_secondo_livello = [
        {"nome": "Valutazione Pervieta Tubarica (HyCoSy / Isterosalpingografia)", "parametri": "Perviota bilaterale, presenza di idrosalpinge, spasmi tubarici", "obbligatorio": age >= 35 or age < 35},
        {"nome": "Isteroscopia Diagnostica con Biopsia", "parametri": "Ricerca endometrite cronica plasmacellulare (CD138), polipi, setti o sinechie", "obbligatorio": False},
        {"nome": "Risonanza Magnetica (RMN) Pelvica ad Alto Campo", "parametri": "Mappatura endometriosi profonda infiltrante, adenomiosi miometriale, miomi sottomucosi", "obbligatorio": False},
        {"nome": "Pannello Trombofilia e Autoimmunita", "parametri": "Fattore V Leiden, Mutazione Protrombina G20210A, MTHFR, Anticorpi Antifosfolipidi (aPL), LAC", "obbligatorio": False}
    ]

    controlli_terzo_livello = [
        {"nome": "Mappa Cromosomica (Cariotipo da Sangue Periferico)", "parametri": "Rilevamento traslocazioni bilanciate o mosaicismi", "obbligatorio": True},
        {"nome": "Screening Genetico Fibrosi Cistica (CFTR)", "parametri": "Mutazioni del gene CFTR per compatibilita di coppia", "obbligatorio": True},
        {"nome": "Biopsia Endometriale Recettivita (Test ERA / EMMA / ALICE)", "parametri": "Finestra d'impianto molecolare e microbioma endometriale", "obbligatorio": False}
    ]

    return {
        "genere": "Femminile",
        "eta": age,
        "fascia_clinica": fascia,
        "tempo_attesa_raccomandato": tempo_attesa,
        "strategia_prioritaria": priorita,
        "controlli_primo_livello": controlli_primo_livello,
        "controlli_secondo_livello": controlli_secondo_livello,
        "controlli_terzo_livello": controlli_terzo_livello
    }
