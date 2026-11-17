from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from app.security.session import session_manager
from app.database.models import RefertoRevisionPayload, ManualAnalitaCreate
from app.database.repository import (
    list_all_referti,
    get_referto_by_id,
    delete_referto,
    confirm_referto_revision,
    insert_manual_analita
)
from app.ingestion.pipeline import ingestion_pipeline
from app.profiles.profile_manager import profile_manager
from app.biomarkers.scanner import biomarker_auto_scanner

router = APIRouter(prefix="/api/referti", tags=["Referti Medici"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

@router.get("", dependencies=[Depends(verify_session)])
def list_referti():
    return list_all_referti()

@router.get("/{referto_id}", dependencies=[Depends(verify_session)])
def get_referto(referto_id: str):
    ref = get_referto_by_id(referto_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Referto non trovato.")
    return ref

@router.post("/upload", dependencies=[Depends(verify_session)])
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File vuoto.")

    filename = file.filename or "referto_scansionato.pdf"
    active_profile = profile_manager.get_active_profile_id()

    try:
        import base64
        from app.jobs.job_manager import ai_job_manager
        b64_str = base64.b64encode(content).decode("utf-8")
        job_id = ai_job_manager.launch_job(
            job_type="INGESTIONE_REFERTO",
            profile_id=active_profile,
            parameters={"filename": filename, "file_b64": b64_str}
        )
        return {
            "status": "processing",
            "job_id": job_id,
            "filename": filename,
            "messaggio": "Referto preso in carico in background. Puoi continuare a navigare."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'avvio dell'elaborazione: {str(e)}")

@router.post("/upload-sync", dependencies=[Depends(verify_session)])
async def upload_document_sync(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File vuoto.")

    filename = file.filename or "referto_scansionato.pdf"
    active_profile = profile_manager.get_active_profile_id()

    try:
        result = await ingestion_pipeline.process_document(
            file_bytes=content,
            filename=filename,
            profile_id=active_profile
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione del documento: {str(e)}")

@router.post("/confirm-revision", dependencies=[Depends(verify_session)])
def confirm_revision(payload: RefertoRevisionPayload):
    try:
        confirm_referto_revision(
            referto_id=payload.referto_id,
            data_prelievo=payload.data_prelievo,
            laboratorio=payload.laboratorio,
            note=payload.note,
            analiti=payload.analiti
        )
        return {"status": "success", "messaggio": "Referto validato e salvato nel database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel salvataggio della revisione: {str(e)}")

@router.post("/manual-entry", dependencies=[Depends(verify_session)])
def add_manual_analita(payload: ManualAnalitaCreate):
    try:
        eff_profile = payload.profile_id or profile_manager.get_active_profile_id()
        algo = biomarker_auto_scanner.resolve_or_create_algorithm(
            analyte_name=payload.nome_standardizzato or payload.nome_esame_originale,
            category=payload.categoria,
            default_unit=payload.unita_misura
        )
        result = algo.evaluate(
            value=payload.valore_numerico,
            text_value=payload.valore_testuale,
            custom_min=payload.range_min,
            custom_max=payload.range_max,
            unit=payload.unita_misura
        )
        data_to_save = {
            "categoria": payload.categoria,
            "nome_esame_originale": payload.nome_esame_originale,
            "nome_standardizzato": result.standard_name,
            "valore_numerico": result.value_numeric,
            "valore_testuale": result.value_text,
            "unita_misura": result.unit or payload.unita_misura,
            "range_min": result.range_min,
            "range_max": result.range_max,
            "stato_flag": result.status_flag,
            "data_prelievo": payload.data_prelievo,
            "laboratorio": payload.laboratorio,
            "note_referto": payload.note_referto or result.clinical_evaluation
        }
        analita_id = insert_manual_analita(profile_id=eff_profile, analita=data_to_save)
        return {
            "status": "success",
            "analita_id": analita_id,
            "valutazione": result.clinical_evaluation,
            "stato_flag": result.status_flag,
            "messaggio": "Esame clinico registrato con successo."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore inserimento manuale: {str(e)}")

@router.delete("/{referto_id}", dependencies=[Depends(verify_session)])
def remove_referto(referto_id: str):
    success = delete_referto(referto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Impossibile eliminare il referto specificato.")
    return {"status": "success", "messaggio": "Referto eliminato."}
