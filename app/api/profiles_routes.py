from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.security.session import session_manager
from app.profiles.profile_manager import profile_manager

router = APIRouter(prefix="/api/profiles", tags=["Profili Familiari"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata. Inserire la password.")

class ProfileCreateRequest(BaseModel):
    nome: str
    cognome: str
    parentela: str
    data_nascita: str
    sesso: str
    gruppo_sanguigno: Optional[str] = None
    note_anamnestiche: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    nome: str
    cognome: str
    parentela: str
    data_nascita: str
    sesso: str
    gruppo_sanguigno: Optional[str] = None
    note_anamnestiche: Optional[str] = None

@router.get("", dependencies=[Depends(verify_session)])
def list_profiles():
    profiles = profile_manager.list_profiles()
    active_id = profile_manager.get_active_profile_id()
    return {
        "active_profile_id": active_id,
        "profiles": profiles
    }

@router.post("", dependencies=[Depends(verify_session)])
def create_profile(req: ProfileCreateRequest):
    new_p = profile_manager.create_profile(
        nome=req.nome,
        cognome=req.cognome,
        parentela=req.parentela,
        data_nascita=req.data_nascita,
        sesso=req.sesso,
        gruppo_sanguigno=req.gruppo_sanguigno,
        note_anamnestiche=req.note_anamnestiche
    )
    return {"status": "success", "profile": new_p}

@router.post("/active/{profile_id}", dependencies=[Depends(verify_session)])
def set_active_profile(profile_id: str):
    success = profile_manager.set_active_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profilo non trovato.")
    return {"status": "success", "active_profile_id": profile_id}

@router.put("/{profile_id}", dependencies=[Depends(verify_session)])
def update_profile(profile_id: str, req: ProfileUpdateRequest):
    updated = profile_manager.update_profile(
        profile_id=profile_id,
        nome=req.nome,
        cognome=req.cognome,
        parentela=req.parentela,
        data_nascita=req.data_nascita,
        sesso=req.sesso,
        gruppo_sanguigno=req.gruppo_sanguigno,
        note_anamnestiche=req.note_anamnestiche
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Profilo non trovato.")
    return {"status": "success", "profile": updated}

@router.delete("/{profile_id}", dependencies=[Depends(verify_session)])
def delete_profile(profile_id: str):
    success = profile_manager.delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profilo non trovato o impossibile eliminare.")
    return {"status": "success", "messaggio": "Profilo rimosso."}
