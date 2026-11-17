import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.jobs.job_manager import ai_job_manager
from app.profiles.profile_manager import profile_manager

router = APIRouter(prefix="/api/jobs", tags=["AI Long-Running Jobs"])

class JobLaunchRequest(BaseModel):
    job_type: str = "LONGITUDINAL_DEEP_ANALYSIS"
    profile_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

@router.post("/launch")
def launch_ai_job(payload: JobLaunchRequest) -> Dict[str, Any]:
    profile_id = payload.profile_id or profile_manager.get_active_profile_id()
    job_id = ai_job_manager.launch_job(
        job_type=payload.job_type,
        profile_id=profile_id,
        parameters=payload.parameters
    )
    return {
        "success": True,
        "job_id": job_id,
        "messaggio": "Job di elaborazione deep reasoning avviato in background."
    }

@router.get("/status/{job_id}")
def check_job_status(job_id: str, profile_id: Optional[str] = None) -> Dict[str, Any]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    status = ai_job_manager.get_status(job_id=job_id, profile_id=eff_profile)
    if not status:
        raise HTTPException(status_code=404, detail="Job non trovato.")
    return status

@router.get("/list")
def list_all_jobs(profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    return ai_job_manager.list_jobs(profile_id=eff_profile)

@router.post("/cancel/{job_id}")
def cancel_job_execution(job_id: str, profile_id: Optional[str] = None) -> Dict[str, Any]:
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    success = ai_job_manager.cancel_job(job_id=job_id, profile_id=eff_profile)
    return {"success": success, "messaggio": "Segnale di annullamento inviato al job."}
