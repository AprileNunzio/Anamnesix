from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from app.database.models import DailyHealthMetricsCreate
from app.database.repository import (
    save_daily_health_metrics,
    list_daily_health_metrics,
    get_latest_daily_health_metrics,
    delete_daily_health_metrics
)
from app.profiles.profile_manager import profile_manager

router = APIRouter(prefix="/api/health-metrics", tags=["Metriche Salute e Wearable"])

@router.post("/save")
def create_health_metric_entry(payload: DailyHealthMetricsCreate) -> Dict[str, Any]:
    profile_id = payload.profile_id or profile_manager.get_active_profile_id()
    data_dict = payload.dict(exclude={"profile_id"})
    record_id = save_daily_health_metrics(profile_id=profile_id, data=data_dict)
    return {
        "success": True,
        "id": record_id,
        "messaggio": "Dati salute e parametri vitali salvati con successo."
    }

@router.get("/history")
def get_health_metrics_history(profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    return list_daily_health_metrics(profile_id=eff_profile)

@router.get("/latest")
def get_latest_health_metrics_entry(profile_id: Optional[str] = None) -> Dict[str, Any]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    latest = get_latest_daily_health_metrics(profile_id=eff_profile)
    return latest or {}

@router.delete("/{record_id}")
def remove_health_metric_entry(record_id: str, profile_id: Optional[str] = None) -> Dict[str, Any]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    deleted = delete_daily_health_metrics(record_id=record_id, profile_id=eff_profile)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dato vitale non trovato.")
    return {"success": True, "messaggio": "Dato vitale rimosso con successo."}
