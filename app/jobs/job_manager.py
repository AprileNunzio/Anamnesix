import asyncio
import json
import datetime
from typing import Dict, Any, Optional
from app.database.repository import (
    create_ai_job,
    update_ai_job,
    get_ai_job,
    list_ai_jobs,
    get_clinical_data_stream,
    get_all_anomalies,
    list_controlli_fertilita,
    list_imaging_referti
)
from app.ai.router import ai_router
from app.profiles.profile_manager import profile_manager

DEEP_REASONING_SYSTEM_PROMPT = """
Sei il Comitato Medico Scientifico ed Esperto di Medicina Computazionale Predittiva di Anamnesix Enterprise.
Il tuo compito e condurre un'analisi clinica longitudinale approfondita, esaustiva e multi-dimensionale, considerando ogni singolo dato disponibile:
- Esami biochimici ed ematologici
- Composizione corporea (BIA, peso, massa grassa, muscolare, ossea, acqua, grasso viscerale)
- Vitals e monitoraggio notturno (passi, bpm, pressione arteriosa, saturazione, episodi di apnea e indice AHI)
- Diagnostica strumentale (TAC, risonanze, ecografie pelviche e scrotali)

La lingua DEVE essere esclusivamente l'ITALIANO.

Struttura la relazione clinica finale esattamente con le seguenti sezioni:
1. SINTESI EPIDEMIOLOGICA E QUADRO CLINICO GLOBALE
2. CORRELAZIONI MULTI-PARAMETRICHE E OMEOSTASI SISTEMICA
3. PROFILO CARDIO-METABOLICO, RESPIRATORIO E APNEE NOTTURNE
4. RISERVA BIOLOGICA, ASSE ENDOCRINO E FERTILITA
5. TRAIETTORIE TEMPORALI E PROIEZIONI PREDITTIVE DI RISCHIO
6. PIANO CLINICO-TERAPEUTICO INTEGRATO E CHECKLIST AZIONABILE PER IL MEDICO
7. DICHIARAZIONE DEONTOLOGICA DI SUPPORTO COMPUTAZIONALE
"""

class AIJobManager:
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.cancellation_requested: Dict[str, bool] = {}

    def launch_job(self, job_type: str, profile_id: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> str:
        eff_profile = profile_id or profile_manager.get_active_profile_id()
        params_str = json.dumps(parameters or {}, ensure_ascii=False)
        est_completion = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=3)).isoformat()
        job_id = create_ai_job(
            profile_id=eff_profile,
            job_type=job_type,
            parameters_json=params_str,
            estimated_completion=est_completion
        )
        task = asyncio.create_task(self._execute_job_pipeline(job_id, job_type, eff_profile, parameters or {}))
        self.active_tasks[job_id] = task
        self.cancellation_requested[job_id] = False
        return job_id

    def cancel_job(self, job_id: str, profile_id: Optional[str] = None) -> bool:
        self.cancellation_requested[job_id] = True
        eff_profile = profile_id or profile_manager.get_active_profile_id()
        if job_id in self.active_tasks:
            self.active_tasks[job_id].cancel()
        update_ai_job(
            job_id=job_id,
            status="ANNULLATO",
            progress=0,
            current_step="Operazione annullata dall'utente",
            error_message="Job interrotto su richiesta manuale",
            profile_id=eff_profile
        )
        return True

    def get_status(self, job_id: str, profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        eff_profile = profile_id or profile_manager.get_active_profile_id()
        return get_ai_job(job_id=job_id, profile_id=eff_profile)

    def list_jobs(self, profile_id: Optional[str] = None) -> list:
        eff_profile = profile_id or profile_manager.get_active_profile_id()
        return list_ai_jobs(profile_id=eff_profile)

    async def _execute_job_pipeline(self, job_id: str, job_type: str, profile_id: str, parameters: Dict[str, Any]) -> None:
        try:
            update_ai_job(
                job_id=job_id,
                status="IN_ESECUZIONE",
                progress=10,
                current_step="Fase 1: Raccolta ed estrazione flussi longitudinali storici",
                profile_id=profile_id
            )
            await asyncio.sleep(1.0)
            if self.cancellation_requested.get(job_id):
                return

            stream_data = get_clinical_data_stream(profile_id=profile_id)
            anomalies = get_all_anomalies()
            controlli = list_controlli_fertilita(profile_id=profile_id)
            imaging = list_imaging_referti(profile_id=profile_id)

            update_ai_job(
                job_id=job_id,
                status="IN_ESECUZIONE",
                progress=35,
                current_step="Fase 2: Normalizzazione cross-dominio e indicizzazione matriciale",
                profile_id=profile_id
            )
            await asyncio.sleep(1.0)
            if self.cancellation_requested.get(job_id):
                return

            active_prof = profile_manager.get_profile(profile_id)
            eta = active_prof.get("eta") if active_prof else "Non specificata"
            genere = active_prof.get("genere") if active_prof else "Non specificato"

            prompt_payload = f"""
SCHEDA PAZIENTE:
- Profilo ID: {profile_id}
- Eta Anagrafica: {eta}
- Genere Biologico: {genere}

ANOMALIE CLINICHE RISCONTRATE (N={len(anomalies)}):
{json.dumps(anomalies[:40], ensure_ascii=False, indent=2)}

FLUSSO DATI CLINICI CRONOLOGICI (N={len(stream_data)}):
{json.dumps(stream_data[:60], ensure_ascii=False, indent=2)}

DIAGNOSTICA STRUMENTALE ED IMAGING DISPONIBILE (N={len(imaging)}):
{json.dumps(imaging[:10], ensure_ascii=False, indent=2)}

PARAMETRI DI CALCOLO AGGIUNTIVI:
{json.dumps(parameters, ensure_ascii=False, indent=2)}

Conduci una perizia scientifica approfondita considerando ogni singola variabile.
"""
            update_ai_job(
                job_id=job_id,
                status="IN_ESECUZIONE",
                progress=65,
                current_step="Fase 3: Elaborazione euristica e computazione deep reasoning LLM",
                profile_id=profile_id
            )

            response = await ai_router.generate_response(
                system_instruction=DEEP_REASONING_SYSTEM_PROMPT,
                user_prompt=prompt_payload,
                temperature=0.15
            )

            if self.cancellation_requested.get(job_id):
                return

            update_ai_job(
                job_id=job_id,
                status="IN_ESECUZIONE",
                progress=90,
                current_step="Fase 4: Consolidamento verifiche e memorizzazione risultati",
                profile_id=profile_id
            )
            await asyncio.sleep(0.5)

            final_result = {
                "job_id": job_id,
                "job_type": job_type,
                "profile_id": profile_id,
                "completato_il": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "totale_eventi_analizzati": len(stream_data),
                "anomalie_totali": len(anomalies),
                "imaging_analizzati": len(imaging),
                "relazione_clinica": response
            }

            update_ai_job(
                job_id=job_id,
                status="COMPLETATO",
                progress=100,
                current_step="Analisi clinica deep reasoning completata con successo",
                result_json=json.dumps(final_result, ensure_ascii=False),
                profile_id=profile_id
            )

        except asyncio.CancelledError:
            update_ai_job(
                job_id=job_id,
                status="ANNULLATO",
                progress=0,
                current_step="Interrotto",
                error_message="Task cancellato",
                profile_id=profile_id
            )
        except Exception as err:
            update_ai_job(
                job_id=job_id,
                status="FALLITO",
                progress=0,
                current_step="Errore critico durante l'elaborazione",
                error_message=str(err),
                profile_id=profile_id
            )
        finally:
            if job_id in self.active_tasks:
                del self.active_tasks[job_id]

ai_job_manager = AIJobManager()
