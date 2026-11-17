import datetime
from typing import Dict, Any, List, Optional
from app.database.connection import get_db_connection
from app.profiles.profile_manager import profile_manager

PROTOCOLLO_DONNA = [
    {
        "id": "f_amh",
        "nome": "Dosaggio AMH (Ormone Anti-Mulleriano)",
        "categoria": "Riserva Ovarica",
        "tempistica": "In qualsiasi giorno del ciclo",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 50,
        "descrizione": "Valuta il patrimonio follicolare residuo nelle ovaie. Fondamentale per stimare la finestra temporale riproduttiva.",
        "biomarcatore_match": "Ormone Anti-Mulleriano (AMH)"
    },
    {
        "id": "f_fsh_e2",
        "nome": "FSH Basale + 17-Beta Estradiolo (E2)",
        "categoria": "Profilo Ormonale Basale",
        "tempistica": "Giorno 2, 3 o 4 del ciclo mestruale",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 50,
        "descrizione": "Verifica l'efficienza ipofisaria nella stimolazione ovarica iniziale e l'assenza di reclutamento follicolare prematuro.",
        "biomarcatore_match": "Ormone Follicolo-Stimolante (FSH Basale)"
    },
    {
        "id": "f_lh",
        "nome": "Dosaggio LH e Rapporto LH/FSH",
        "categoria": "Profilo Ormonale Basale",
        "tempistica": "Giorno 2, 3 o 4 del ciclo mestruale",
        "frequenza_mesi": 12,
        "eta_min": 18,
        "eta_max": 45,
        "descrizione": "Rapporto LH/FSH > 2.0 indica possibile Sindrome dell'Ovaio Policistico (PCOS).",
        "biomarcatore_match": "Ormone Luteinizzante (LH)"
    },
    {
        "id": "f_progesterone",
        "nome": "Progesterone Plasmatico a Meta Fase Luteale",
        "categoria": "Funzione Ovulatoria",
        "tempistica": "Giorno 21 (o 7 giorni post-ovulazione accertata)",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 48,
        "descrizione": "Conferma l'avvenuta ovulazione e la qualita secretiva del corpo luteo per consentire l'impianto della blastocisti.",
        "biomarcatore_match": "Progesterone (Fase Luteale / Giorno 21)"
    },
    {
        "id": "f_prolattina",
        "nome": "Prolattina Serica (PRL)",
        "categoria": "Asse Ipotalamo-Ipofisi",
        "tempistica": "A riposo (almeno 2 ore dopo il risveglio)",
        "frequenza_mesi": 12,
        "eta_min": 18,
        "eta_max": 48,
        "descrizione": "L'iperprolattinemia inibisce la secrezione pulsatile di GnRH causando anovulazione o difetti della fase luteale.",
        "biomarcatore_match": "Prolattina"
    },
    {
        "id": "f_tiroide",
        "nome": "Pannello Tiroideo per Fertilita (TSH, FT3, FT4, Anti-TPO)",
        "categoria": "Equilibrio Endocrino",
        "tempistica": "In qualsiasi momento",
        "frequenza_mesi": 12,
        "eta_min": 18,
        "eta_max": 50,
        "descrizione": "In ambito riproduttivo e pre-concezionale il target ottimale di TSH e < 2.5 uUI/mL.",
        "biomarcatore_match": "Tireotropina (TSH)"
    },
    {
        "id": "f_afc_echo",
        "nome": "Ecografia Pelvica Transvaginale con Conta Follicoli Antrali (AFC)",
        "categoria": "Diagnostica Strumentale per Immagini",
        "tempistica": "Giorno 3-5 del ciclo",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 50,
        "descrizione": "Conta dei follicoli 2-9 mm per ovaio e misurazione dello spessore endometriale basale.",
        "biomarcatore_match": "Conta Follicoli Antrali (AFC)"
    },
    {
        "id": "f_istero",
        "nome": "Valutazione Pervietà Tubarica (Isterosalpingografia / HyCoSy)",
        "categoria": "Diagnostica Strumentale per Immagini",
        "tempistica": "Fase follicolare pre-ovulatoria (giorni 7-11)",
        "frequenza_mesi": 24,
        "eta_min": 25,
        "eta_max": 45,
        "descrizione": "Verifica della canalizzazione e pervietà bilaterale delle tube di Falloppio.",
        "biomarcatore_match": "Pervietà Tubarica"
    },
    {
        "id": "f_tamponi",
        "nome": "Screening Infettivo Cervico-Vaginale (Chlamydia, Mycoplasma, Ureaplasma)",
        "categoria": "Screening Infettivologico",
        "tempistica": "Fuori dal flusso mestruale",
        "frequenza_mesi": 12,
        "eta_min": 18,
        "eta_max": 50,
        "descrizione": "Le infezioni endocervicali asintomatiche possono causare salpingite e ostruzione tubarica infiammatoria.",
        "biomarcatore_match": "Tampone Cervicale"
    },
    {
        "id": "f_rm_endometriosi",
        "nome": "Risonanza Magnetica Pelvica per Endometriosi Profonda ed Adenomiosi",
        "categoria": "Diagnostica Strumentale per Immagini",
        "tempistica": "Preferibilmente fase secretiva o con preparazione intestinale",
        "frequenza_mesi": 24,
        "eta_min": 25,
        "eta_max": 45,
        "descrizione": "Mappatura dei noduli endometriosici retrocervicali, setto retto-vaginale e adenomiosi miometriale.",
        "biomarcatore_match": "Risonanza Magnetica Pelvica"
    }
]

PROTOCOLLO_UOMO = [
    {
        "id": "m_spermiogramma",
        "nome": "Spermiogramma Completo secondo Criteri WHO 6th Edition",
        "categoria": "Seminologia Clinica",
        "tempistica": "Dopo 3-5 giorni di astinenza eiaculatoria rigorosa",
        "frequenza_mesi": 3,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "Analisi quantitativa di volume, concentrazione, motilita progressiva PR e morfologia Kruger.",
        "biomarcatore_match": "Concentrazione Spermatozoi (Spermiogramma WHO 6th)"
    },
    {
        "id": "m_frammentazione",
        "nome": "Test di Frammentazione del DNA Spermatico (DFI - SCSA/TUNEL)",
        "categoria": "Genomica Seminale",
        "tempistica": "Stesse modalita di astinenza dello spermiogramma",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "Quantifica le rotture a singolo e doppio filamento del DNA. DFI > 25-30% riduce l'impianto e raddoppia l'abortivita precoce.",
        "biomarcatore_match": "Indice di Frammentazione DNA Spermatico (DFI %)"
    },
    {
        "id": "m_spermiocoltura",
        "nome": "Spermiocoltura con Antibiogramma per Germi Comuni, Miceti e Ureaplasmi",
        "categoria": "Screening Infettivologico",
        "tempistica": "Dopo accurata igiene locale",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "Esclude leucocitospermia batterica e prostatovescicoliti che producono citochine citotossiche per gli spermatozoi.",
        "biomarcatore_match": "Spermiocoltura"
    },
    {
        "id": "m_ecocolordoppler",
        "nome": "Ecocolordoppler Plesso Pampiniforme e Scrotale (Varicocele)",
        "categoria": "Diagnostica Strumentale per Immagini",
        "tempistica": "In clino e ortostatismo con manovra di Valsalva",
        "frequenza_mesi": 12,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "Grading del reflusso venoso secondo Sarteschi e misurazione volumetrica didimaria con ecografo.",
        "biomarcatore_match": "Ecocolordoppler Scrotale"
    },
    {
        "id": "m_testosterone",
        "nome": "Testosterone Totale, Libero ed SHBG",
        "categoria": "Profilo Endocrino Andrologico",
        "tempistica": "Prelievo mattutino tra le 07:30 e le 09:30",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "Valuta la funzionalita delle cellule di Leydig necessaria al supporto della spermatogenesi.",
        "biomarcatore_match": "Testosterone Totale"
    },
    {
        "id": "m_fsh_lh",
        "nome": "FSH, LH ed Inibina B Maschile",
        "categoria": "Profilo Endocrino Andrologico",
        "tempistica": "Prelievo ematico a digiuno",
        "frequenza_mesi": 6,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "FSH elevato riflette un danno primario dell'epitelio seminifero (Sertoli). L'inibina B e il marker diretto di spermatogenesi attiva.",
        "biomarcatore_match": "Ormone Follicolo-Stimolante (FSH Basale)"
    },
    {
        "id": "m_genetica",
        "nome": "Cariotipo su Sangue Periferico e Microdelezioni Cromosoma Y (AZFa, AZFb, AZFc)",
        "categoria": "Genetica Medica Riproduttiva",
        "tempistica": "Prelievo ematico per genetica",
        "frequenza_mesi": 999,
        "eta_min": 18,
        "eta_max": 65,
        "descrizione": "Raccomandato in caso di concentrazione < 5 milioni/mL o azoospermia per escludere sindrome di Klinefelter o delezioni AZF.",
        "biomarcatore_match": "Mappa Cromosomica"
    }
]

class FertilityCheckupEngine:
    def __init__(self):
        self.ready = True

    def calculate_age(self, data_nascita: str) -> int:
        try:
            parts = data_nascita.split("-")
            birth = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            today = datetime.date.today()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except Exception:
            return 32

    def evaluate_checkups(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        if not profile_id:
            profile_id = profile_manager.get_active_profile_id()

        profiles = profile_manager.list_profiles()
        current = next((p for p in profiles if p["id"] == profile_id), None)

        sesso = current.get("sesso", "F").upper() if current else "F"
        data_nascita = current.get("data_nascita", "1992-01-01") if current else "1992-01-01"
        eta = self.calculate_age(data_nascita)

        is_female = sesso in ["F", "FEMMINILE", "DONNA"]
        protocollo_base = PROTOCOLLO_DONNA if is_female else PROTOCOLLO_UOMO

        conn = get_db_connection(profile_id=profile_id)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nome_standardizzato, valore_numerico, valore_testuale, unita_misura,
                       stato_flag, data_prelievo, laboratorio
                FROM analiti
                ORDER BY data_prelievo DESC
                """
            )
            analiti_presenti = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        controlli_fatti = []
        controlli_da_fare = []

        for item in protocollo_base:
            match_name = item["biomarcatore_match"].lower()
            found = next((a for a in analiti_presenti if match_name in a["nome_standardizzato"].lower()), None)

            if found:
                controlli_fatti.append({
                    "id": item["id"],
                    "nome": item["nome"],
                    "categoria": item["categoria"],
                    "data_esecuzione": found["data_prelievo"],
                    "valore": found["valore_numerico"] if found["valore_numerico"] is not None else found["valore_testuale"],
                    "unita": found["unita_misura"],
                    "stato": found["stato_flag"],
                    "laboratorio": found["laboratorio"],
                    "descrizione": item["descrizione"]
                })
            else:
                controlli_da_fare.append({
                    "id": item["id"],
                    "nome": item["nome"],
                    "categoria": item["categoria"],
                    "tempistica": item["tempistica"],
                    "priorita": "ALTA" if eta >= 35 else "MEDIA",
                    "descrizione": item["descrizione"]
                })

        totale = len(protocollo_base)
        completamento_pct = round((len(controlli_fatti) / totale) * 100.0, 1) if totale > 0 else 0.0

        stato_sintetico = "Iniziale"
        if completamento_pct >= 80.0:
            stato_sintetico = "Quadro Diagnostico Completo"
        elif completamento_pct >= 40.0:
            stato_sintetico = "Screening in Corso"

        return {
            "paziente_sesso": "Donna" if is_female else "Uomo",
            "paziente_eta": eta,
            "completamento_percentuale": completamento_pct,
            "stato_sintetico": stato_sintetico,
            "totale_controlli_protocollo": totale,
            "controlli_fatti": controlli_fatti,
            "controlli_da_fare": controlli_da_fare
        }

fertility_checkup_engine = FertilityCheckupEngine()
