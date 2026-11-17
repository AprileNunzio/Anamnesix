from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from app.database.models import BodyCompositionCreate
from app.database.repository import (
    save_body_composition,
    list_body_composition,
    get_latest_body_composition,
    delete_body_composition
)
from app.profiles.profile_manager import profile_manager

router = APIRouter(prefix="/api/body-composition", tags=["Composizione Corporea"])

@router.post("/save")
def create_body_composition_entry(payload: BodyCompositionCreate) -> Dict[str, Any]:
    profile_id = payload.profile_id or profile_manager.get_active_profile_id()
    data_dict = payload.dict(exclude={"profile_id"})
    if payload.peso_kg and payload.altezza_cm and payload.altezza_cm > 0:
        altezza_m = payload.altezza_cm / 100.0
        data_dict["bmi"] = round(payload.peso_kg / (altezza_m * altezza_m), 1)
    record_id = save_body_composition(profile_id=profile_id, data=data_dict)
    return {
        "success": True,
        "id": record_id,
        "messaggio": "Misurazione corporea registrata con successo."
    }

@router.get("/history")
def get_body_composition_history(profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    return list_body_composition(profile_id=eff_profile)

@router.get("/latest")
def get_latest_body_composition_entry(profile_id: Optional[str] = None) -> Dict[str, Any]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    latest = get_latest_body_composition(profile_id=eff_profile)
    return latest or {}

@router.delete("/{record_id}")
def remove_body_composition_entry(record_id: str, profile_id: Optional[str] = None) -> Dict[str, Any]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    deleted = delete_body_composition(record_id=record_id, profile_id=eff_profile)
    if not deleted:
        raise HTTPException(status_code=404, detail="Misurazione non trovata.")
    return {"success": True, "messaggio": "Misurazione eliminata."}
