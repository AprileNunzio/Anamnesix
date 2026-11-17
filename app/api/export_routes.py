import io
import csv
import json
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional
from app.security.session import session_manager
from app.export.pdf_dossier import pdf_dossier_generator
from app.database.repository import get_clinical_data_stream
from app.profiles.profile_manager import profile_manager

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

@router.get("/clinical-stream", dependencies=[Depends(verify_session)])
def export_clinical_stream(format: str = "csv", profile_id: Optional[str] = None):
    eff_profile = profile_id or profile_manager.get_active_profile_id()
    stream_rows = get_clinical_data_stream(profile_id=eff_profile)

    if format.lower() == "json":
        json_bytes = json.dumps(stream_rows, ensure_ascii=False, indent=2).encode("utf-8")
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=Anamnesix_Flusso_Clinico_Cronologico.json"}
        )

    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        "Data Evento",
        "Tipo Flusso",
        "Categoria",
        "Parametro Clinico",
        "Dettaglio Originale",
        "Valore Numerico",
        "Valore Testuale",
        "Unita Misura",
        "Range Min",
        "Range Max",
        "Stato Flag",
        "Sorgente Laboratorio",
        "Note"
    ])
    for r in stream_rows:
        writer.writerow([
            r.get("data_evento") or "",
            r.get("tipo_flusso") or "",
            r.get("categoria") or "",
            r.get("nome_parametro") or "",
            r.get("dettaglio_originale") or "",
            r.get("valore_numerico") if r.get("valore_numerico") is not None else "",
            r.get("valore_testuale") or "",
            r.get("unita_misura") or "",
            r.get("range_min") if r.get("range_min") is not None else "",
            r.get("range_max") if r.get("range_max") is not None else "",
            r.get("stato_flag") or "",
            r.get("sorgente") or "",
            r.get("note") or ""
        ])

    csv_data = output.getvalue().encode("utf-8")
    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=Anamnesix_Flusso_Clinico_Cronologico.csv"}
    )
