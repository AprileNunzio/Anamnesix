from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.security.session import session_manager
from app.security.cipher import encrypt_string, decrypt_string
from app.database.repository import set_config_value, get_config_value
from app.ai.ollama_provider import ollama_provider
from app.ai.router import ai_router
from app.biomarkers.scanner import biomarker_auto_scanner

router = APIRouter(prefix="/api/settings", tags=["Impostazioni"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

class SettingsPayload(BaseModel):
    ai_provider: str
    ollama_model: str
    ollama_vision_model: Optional[str] = "llama3.2-vision:latest"
    ollama_url: Optional[str] = "http://127.0.0.1:11434"
    gemini_api_key: Optional[str] = None
    gemini_model: str
    pii_scrubbing: bool = True
    auto_lock_minutes: int = 15

@router.get("", dependencies=[Depends(verify_session)])
def get_settings():
    key = session_manager.get_key()

    provider = "ollama"
    enc_provider = get_config_value("ai_provider")
    if enc_provider:
        provider = decrypt_string(enc_provider, key)

    ollama_model = "llama3.1:latest"
    enc_om = get_config_value("ollama_model")
    if enc_om:
        ollama_model = decrypt_string(enc_om, key)

    ollama_vision_model = "llama3.2-vision:latest"
    enc_ovm = get_config_value("ollama_vision_model")
    if enc_ovm:
        ollama_vision_model = decrypt_string(enc_ovm, key)

    gemini_key = ""
    enc_gk = get_config_value("gemini_api_key")
    if enc_gk:
        gemini_key = decrypt_string(enc_gk, key)

    gemini_model = "gemini-2.5-flash"
    enc_gm = get_config_value("gemini_model")
    if enc_gm:
        gemini_model = decrypt_string(enc_gm, key)

    pii = True
    enc_pii = get_config_value("pii_scrubbing")
    if enc_pii:
        pii = decrypt_string(enc_pii, key) == "true"

    return {
        "ai_provider": provider,
        "ollama_model": ollama_model,
        "ollama_vision_model": ollama_vision_model,
        "ollama_url": ollama_provider.base_url,
        "has_gemini_key": bool(gemini_key),
        "gemini_api_key": gemini_key,
        "gemini_model": gemini_model,
        "pii_scrubbing": pii,
        "auto_lock_minutes": 15
    }

@router.post("", dependencies=[Depends(verify_session)])
def save_settings(payload: SettingsPayload):
    key = session_manager.get_key()

    set_config_value("ai_provider", encrypt_string(payload.ai_provider, key))
    set_config_value("ollama_model", encrypt_string(payload.ollama_model, key))
    if payload.ollama_vision_model:
        set_config_value("ollama_vision_model", encrypt_string(payload.ollama_vision_model, key))
    if payload.ollama_url:
        ollama_provider.set_base_url(payload.ollama_url)

    if payload.gemini_api_key is not None:
        set_config_value("gemini_api_key", encrypt_string(payload.gemini_api_key, key))

    set_config_value("gemini_model", encrypt_string(payload.gemini_model, key))
    set_config_value("pii_scrubbing", encrypt_string("true" if payload.pii_scrubbing else "false", key))

    session_manager.set_timeout(payload.auto_lock_minutes)
    ai_router.reload_config()

    return {"status": "success", "messaggio": "Impostazioni aggiornate."}

@router.get("/ollama-models", dependencies=[Depends(verify_session)])
async def get_ollama_models():
    models = await ollama_provider.list_models()
    is_up = await ollama_provider.is_available()
    return {
        "available": is_up,
        "models": models
    }

@router.post("/reload-system", dependencies=[Depends(verify_session)])
def reload_system_and_biomarkers():
    scan_report = biomarker_auto_scanner.scan_and_register_all()
    ai_router.reload_config()
    return {
        "success": True,
        "messaggio": "Ricaricamento a caldo completato. Algoritmi e configurazioni sincronizzati.",
        "biomarker_scan": scan_report
    }
