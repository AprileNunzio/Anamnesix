from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.security.session import session_manager
from app.fertility.checkup_engine import fertility_checkup_engine
from app.fertility.report_generator import fertility_report_generator
from app.imaging.image_analyzer import clinical_imaging_analyzer

router = APIRouter(prefix="/api/fertility", tags=["Medicina Riproduttiva & Fertilita"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

class FertilityReportRequest(BaseModel):
    profile_id: Optional[str] = None
    scan_notes: Optional[str] = None

@router.get("/checkups", dependencies=[Depends(verify_session)])
def get_fertility_checkups(profile_id: Optional[str] = None):
    return fertility_checkup_engine.evaluate_checkups(profile_id=profile_id)

@router.post("/report", dependencies=[Depends(verify_session)])
async def generate_fertility_report(req: FertilityReportRequest):
    try:
        report = await fertility_report_generator.generate_comprehensive_report(
            profile_id=req.profile_id,
            scan_notes=req.scan_notes
        )
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore generazione relazione fertilita: {str(e)}")

@router.post("/scan-analyze", dependencies=[Depends(verify_session)])
async def analyze_diagnostic_scan(
    file: Optional[UploadFile] = File(None),
    report_text: Optional[str] = Form(None),
    clinical_context: Optional[str] = Form(None)
):
    image_bytes = None
    mime_type = "image/png"

    if file:
        image_bytes = await file.read()
        filename = file.filename or "scan.png"
        if filename.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        elif filename.lower().endswith(".pdf"):
            mime_type = "application/pdf"

    if not image_bytes and not report_text:
        raise HTTPException(status_code=400, detail="Inserire un'immagine TAC/RM/scansione oppure il testo del referto radiologico.")

    try:
        analysis = await clinical_imaging_analyzer.analyze_scan(
            image_bytes=image_bytes,
            mime_type=mime_type,
            report_text=report_text,
            clinical_context=clinical_context
        )
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore analisi strumentale AI: {str(e)}")
