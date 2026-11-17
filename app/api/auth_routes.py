from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.security.hasher import derive_key, get_or_create_salt
from app.security.session import session_manager
from app.security.dpapi import protect_data, unprotect_data
from app.config.settings import CONFIG_DIR, ensure_directories_exist
from app.database.connection import init_database
from app.profiles.profile_manager import profile_manager

router = APIRouter(prefix="/api/auth", tags=["Autenticazione"])

MASTER_VERIFIER_PATH = CONFIG_DIR / "verifier.bin"
DPAPI_VAULT_PATH = CONFIG_DIR / "dpapi.bin"

class PasswordRequest(BaseModel):
    password: str
    enable_dpapi: bool = False

class UnlockStatusResponse(BaseModel):
    is_authenticated: bool
    dpapi_available: bool
    is_initial_setup: bool
    active_profile_id: Optional[str] = None

@router.get("/status", response_model=UnlockStatusResponse)
def get_auth_status():
    ensure_directories_exist()
    is_init = not MASTER_VERIFIER_PATH.exists()
    dpapi_avail = DPAPI_VAULT_PATH.exists()
    auth = not session_manager.is_locked()
    active_id = profile_manager.get_active_profile_id() if auth else None
    return UnlockStatusResponse(
        is_authenticated=auth,
        dpapi_available=dpapi_avail,
        is_initial_setup=is_init,
        active_profile_id=active_id
    )

@router.post("/setup")
def setup_master_password(req: PasswordRequest):
    ensure_directories_exist()
    if MASTER_VERIFIER_PATH.exists():
        raise HTTPException(status_code=400, detail="Master password gia configurata.")
    key = derive_key(req.password)
    from app.security.cipher import encrypt_bytes
    verifier = encrypt_bytes(b"ANAMNESIX_VAULT_OK", key)
    MASTER_VERIFIER_PATH.write_bytes(verifier)

    if req.enable_dpapi:
        try:
            protected_key = protect_data(key)
            DPAPI_VAULT_PATH.write_bytes(protected_key)
        except Exception as e:
            last_dpapi_error = str(e)

    session_manager.unlock(key, dpapi_enabled=req.enable_dpapi)
    init_database()
    profile_manager.get_active_profile_id()
    return {"status": "success", "messaggio": "Archivio cifrato configurato con successo."}

@router.post("/unlock")
def unlock_vault(req: PasswordRequest):
    ensure_directories_exist()
    if not MASTER_VERIFIER_PATH.exists():
        raise HTTPException(status_code=400, detail="Archivio non ancora inizializzato.")
    key = derive_key(req.password)
    from app.security.cipher import decrypt_bytes
    try:
        verifier = MASTER_VERIFIER_PATH.read_bytes()
        check = decrypt_bytes(verifier, key)
        if check != b"ANAMNESIX_VAULT_OK":
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=401, detail="Master password errata.")

    if req.enable_dpapi:
        try:
            protected_key = protect_data(key)
            DPAPI_VAULT_PATH.write_bytes(protected_key)
        except Exception as e:
            last_dpapi_error = str(e)

    session_manager.unlock(key, dpapi_enabled=req.enable_dpapi)
    init_database()
    profile_manager.get_active_profile_id()
    return {"status": "success", "messaggio": "Archivio sbloccato."}

@router.post("/unlock-dpapi")
def unlock_with_dpapi():
    if not DPAPI_VAULT_PATH.exists():
        raise HTTPException(status_code=400, detail="Sblocco rapido DPAPI non configurato.")
    try:
        protected_key = DPAPI_VAULT_PATH.read_bytes()
        key = unprotect_data(protected_key)
        from app.security.cipher import decrypt_bytes
        verifier = MASTER_VERIFIER_PATH.read_bytes()
        check = decrypt_bytes(verifier, key)
        if check != b"ANAMNESIX_VAULT_OK":
            raise ValueError()
        session_manager.unlock(key, dpapi_enabled=True)
        init_database()
        profile_manager.get_active_profile_id()
        return {"status": "success", "messaggio": "Sblocco rapido DPAPI effettuato."}
    except Exception:
        raise HTTPException(status_code=401, detail="Impossibile sbloccare con credenziali DPAPI.")

@router.post("/lock")
def lock_vault():
    session_manager.lock()
    return {"status": "success", "messaggio": "Archivio bloccato con successo."}
