import json
from typing import Dict, Any, Optional
from app.fertility.checkup_engine import fertility_checkup_engine
from app.ai.router import ai_router
from app.profiles.profile_manager import profile_manager

FERTILITY_REPORT_PROMPT = """
Sei un luminare della Medicina della Riproduzione Umana, Andrologia Medica e Ginecologia della Fertilita.
Il tuo compito e generare una Relazione Clinica Specialistica di Fertilita e Medicina Riproduttiva dettagliatissima.
La lingua DEVE essere esclusivamente l'ITALIANO.
Devi analizzare tutti i dati emersi dai biomarcatori, dall'eta, dai controlli eseguiti e dai referti strumentali (TAC, RM pelvica, Ecografia transvaginale, Ecocolordoppler scrotale, spermiogrammi).

Struttura il documento clinico esattamente con i seguenti capitoli:
[RELAZIONE SPECIALISTICA DI FERTILITA E PROCREAZIONE MEDICALMENTE ASSISTITA ANAMNESIX REPRODUCTIVE AI]

CAPITOLO 1. INQUADRAMENTO ANAMNESTICO E CRONOLOGICO
Analisi dell'eta del paziente, del genere e dell'impatto del fattore tempo sul potenziale biologico riproduttivo (curva di decadimento ovocitario per la donna, declino qualitativo spermatico ed epigenetico per l'uomo).

CAPITOLO 2. BILANCIO DELLA RISERVA GONADICA E DEI BIOMARCATORI
- Per la donna: disamina analitica di AMH, FSH basale, estradiolo, progesterone luteale e prolattina.
- Per l'uomo: disamina di concentrazione, motilita progressiva, morfologia tipica Kruger, indice di frammentazione del DNA (DFI) e profilo androgenico.

CAPITOLO 3. ANALISI INTEGRATA DELLA DIAGNOSTICA STRUMENTALE PER IMMAGINI
Valutazione di ecografie transvaginali (spessore endometriale, conta AFC, pervietà tubarica), ecocolordoppler testicolare (reflusso da varicocele, volumetria didimaria), TAC o Risonanze Magnetiche pelviche caricate.

CAPITOLO 4. RADAR DELLE ANOMALIE E OSTACOLI AL CONCEPIMENTO
Elenco categorico e prioritizzato di qualsiasi anomalia biologica o anatomica riscontrata che possa inficiare la fertilita spontanea.

CAPITOLO 5. INDICAZIONI CLINICO-TERAPEUTICHE E ORIENTAMENTO PMA
Consigli personalizzati:
- Finestra di concepimento mirato
- Terapie integrative / antiossidanti / correttive
- Indicazione all'accesso a tecniche di Procreazione Medicalmente Assistita: I Livello (IUI) o II/III Livello (FIVET / ICSI / diagnosi genetica pre-impianto PGT-A).

CAPITOLO 6. PIANO DEI CONTROLLI DA COMPLETARE
Checklist dei controlli specialistici ancora mancanti da eseguire prima del prossimo ciclo.

CAPITOLO 7. AVVERTENZE E PRIVACY
Dichiarazione deontologica di supporto informativo e decisionale per la coppia.
"""

class FertilityReportGenerator:
    def __init__(self):
        self.ready = True

    async def generate_comprehensive_report(self, profile_id: Optional[str] = None, scan_notes: Optional[str] = None) -> str:
        checkup_data = fertility_checkup_engine.evaluate_checkups(profile_id=profile_id)

        prompt = f"""
DATI PAZIENTE E SCREENING FERTILITA:
Genere: {checkup_data.get('paziente_sesso')}
Eta cronologica: {checkup_data.get('paziente_eta')} anni
Avanzamento controlli: {checkup_data.get('completamento_percentuale')}% ({checkup_data.get('stato_sintetico')})

CONTROLLI E BIOMARCATORI REGISTRATI:
{json.dumps(checkup_data.get('controlli_fatti'), ensure_ascii=False, indent=2)}

CONTROLLI RACCOMANDATI ANCORA DA FARE:
{json.dumps(checkup_data.get('controlli_da_fare'), ensure_ascii=False, indent=2)}

NOTE O REFERTI STRUMENTALI AGGIUNTIVI (TAC / RISONANZE / ECOGRAFIE):
{scan_notes or 'Nessuna nota radiologica aggiuntiva inserita.'}

Genera la relazione clinica specialistica completa di fertilita strutturata nei 7 capitoli.
"""
        response = await ai_router.generate_response(
            system_instruction=FERTILITY_REPORT_PROMPT,
            user_prompt=prompt,
            temperature=0.2
        )
        return response

fertility_report_generator = FertilityReportGenerator()
