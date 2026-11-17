from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional
from app.security.session import session_manager
from app.export.pdf_dossier import pdf_dossier_generator

router = APIRouter(prefix="/api/export", tags=["Esportazione Clinica"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

class ExportPdfRequest(BaseModel):
    profile_id: Optional[str] = None
    password: Optional[str] = None

@router.post("/pdf", dependencies=[Depends(verify_session)])
def export_pdf_dossier(req: ExportPdfRequest):
    try:
        pdf_bytes = pdf_dossier_generator.generate_dossier(
            profile_id=req.profile_id,
            password=req.password if req.password and req.password.strip() else None
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Anamnesix_Dossier_Clinico.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore generazione PDF dossier: {str(e)}")
