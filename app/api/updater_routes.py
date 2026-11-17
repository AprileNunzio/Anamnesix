import threading
from fastapi import APIRouter, HTTPException, Depends
from app.security.session import session_manager
from app.updater.github_updater import github_updater

router = APIRouter(prefix="/api/updater", tags=["Auto Aggiornamento"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

@router.get("/check", dependencies=[Depends(verify_session)])
async def check_updates():
    return await github_updater.check_for_updates()

@router.post("/apply", dependencies=[Depends(verify_session)])
async def apply_updates():
    success = await github_updater.apply_update()
    if not success:
        raise HTTPException(status_code=500, detail="Impossibile applicare l'aggiornamento da GitHub.")
    return {"status": "success", "messaggio": "Aggiornamento applicato con successo."}

@router.post("/restart", dependencies=[Depends(verify_session)])
def trigger_restart():
    threading.Timer(0.5, github_updater.restart_application).start()
    return {"status": "success", "messaggio": "Riavvio completo dell'applicazione avviato."}
