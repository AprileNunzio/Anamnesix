from typing import Dict, Any
from app.analytics.health_score import health_score_calculator
from app.analytics.radar_anomalies import radar_anomalies_engine
from app.analytics.correlations import correlation_engine
from app.ai.router import ai_router

SECOND_OPINION_SYSTEM_PROMPT = """
Sei un medico internista e patologo clinico di altissimo livello.
Il tuo compito e redigere un rapporto clinico approfondito (Second Opinion Informativa) basato sui dati di laboratorio forniti.
Il referto deve essere rigoroso, scientifico, ma al tempo stesso comprensibile per il paziente.
La lingua DEVE essere esclusivamente l'ITALIANO.
Devi strutturare il rapporto esattamente nelle seguenti sezioni con titoli chiari:

SEZIONE 1: SINTESI ESECUTIVA
Riassunto sintetico e chiaro dello stato di salute generale, dei punti di forza e delle principali alterazioni riscontrate.

SEZIONE 2: ANALISI DETTAGLIATA PER SISTEMI ED APPARATI
Esame approfondito suddiviso per:
- Assetto Cardiovascolare e Lipidico
- Equilibrio Metabolico e Glucidico
- Funzionalita Epatica e Biliare
- Funzionalita Renale ed Elettrolitica
- Quadro Ematologico e Assetto Marziale
- Assetto Tiroideo ed Endocrino
- Indici di Flogosi ed Infiammazione

SEZIONE 3: TREND E VARIAZIONI SIGNIFICATIVE
Confronto con le misurazioni storiche passate: quali valori stanno migliorando, quali peggiorano e quali sono stabili.

SEZIONE 4: CORRELAZIONI MULTI-PARAMETRO E IPOTESI CLINICHE
Valutazione incrociata tra esami diversi (es. correlazione ferro-emoglobina, glucosio-trigliceridi, ormoni tiroidei).

SEZIONE 5: DOMANDE CONSIGLIATE PER IL MEDICO CURANTE O SPECIALISTA
Elenco puntato di 4-6 domande precise e clinicamente mirate che il paziente puo porre al proprio medico durante la visita.

SEZIONE 6: AVVISO MEDICO E PRIVACY
Dichiarazione di supporto informativo non sostitutivo del giudizio diagnostico medico.
"""

class SecondOpinionService:
    def __init__(self):
        self.ready = True

    async def generate_report(self, profile_id: str | None = None) -> str:
        scores = health_score_calculator.calculate_scores(profile_id=profile_id)
        anomalies = radar_anomalies_engine.get_ranked_anomalies(profile_id=profile_id)
        correlations = correlation_engine.evaluate_correlations(profile_id=profile_id)

        prompt = f"""
DATI PAZIENTE DA ANALIZZARE:

Punteggio Salute Globale: {scores.get('overall_score')}/100 ({scores.get('stato_sintetico')})

Punteggi per Sistemi:
{scores.get('sistemi')}

Biomarcatori Attualmente Fuori Range (Ordinati per criticita):
{anomalies}

Correlazioni Cliniche Rilevate Automaticamente dal Sistema:
{correlations}

Redigi il rapporto completo di Second Opinion strutturato secondo le istruzioni fornite.
"""
        response = await ai_router.generate_response(
            system_instruction=SECOND_OPINION_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.2
        )
        return response

second_opinion_service = SecondOpinionService()
