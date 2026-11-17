import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, List
from app.config.settings import get_profile_docs_dir
from app.security.cipher import encrypt_bytes
from app.security.session import session_manager
from app.profiles.profile_manager import profile_manager
from app.ingestion.pdf_parser import pdf_parser
from app.ingestion.ocr_engine import ocr_engine
from app.ingestion.normalizer import biomarker_normalizer
from app.ai.router import ai_router
from app.database.models import RefertoCreate
from app.database.repository import create_referto, save_analiti_for_referto

class IngestionPipeline:
    def __init__(self):
        self.ready = True

    async def process_document(
        self,
        file_bytes: bytes,
        filename: str,
        profile_id: str | None = None
    ) -> Dict[str, Any]:
        if not profile_id:
            profile_id = profile_manager.get_active_profile_id()

        key = session_manager.get_key()
        file_id = str(uuid.uuid4())
        suffix = Path(filename).suffix.lower()

        docs_dir = get_profile_docs_dir(profile_id)
        enc_file_path = docs_dir / f"{file_id}.enc"

        encrypted_file = encrypt_bytes(file_bytes, key)
        enc_file_path.write_bytes(encrypted_file)

        extracted_text = ""
        first_page_image: bytes | None = None
        mime_type = "application/pdf" if suffix == ".pdf" else "image/png"

        if suffix == ".pdf":
            extracted_text, page_images = pdf_parser.extract_text_and_pages(file_bytes)
            if page_images:
                first_page_image = page_images[0]
        else:
            first_page_image = file_bytes
            extracted_text = ocr_engine.extract_text_from_bytes(file_bytes)
            mime_type = "image/jpeg" if suffix in [".jpg", ".jpeg"] else "image/png"

        raw_ai_data = await ai_router.extract_clinical_data(
            document_text=extracted_text,
            image_bytes=first_page_image,
            mime_type=mime_type
        )

        today_iso = datetime.date.today().isoformat()
        data_prelievo = raw_ai_data.get("data_prelievo") or today_iso
        laboratorio = raw_ai_data.get("laboratorio") or "Laboratorio Clinico"
        note_generali = raw_ai_data.get("note_generali") or f"File originario: {filename}"

        normalized_analiti = []
        for raw_item in raw_ai_data.get("analiti", []):
            norm_item = biomarker_normalizer.normalize_item(
                item=raw_item,
                default_data=data_prelievo,
                default_lab=laboratorio
            )
            normalized_analiti.append(norm_item)

        referto_create = RefertoCreate(
            data_prelievo=data_prelievo,
            laboratorio=laboratorio,
            file_path=str(enc_file_path),
            note=note_generali,
            stato_revisione="BOZZA"
        )

        referto_id = create_referto(referto_create)
        save_analiti_for_referto(referto_id, normalized_analiti)

        import base64
        preview_b64 = base64.b64encode(first_page_image).decode("utf-8") if first_page_image else ""

        return {
            "referto_id": referto_id,
            "filename": filename,
            "data_prelievo": data_prelievo,
            "laboratorio": laboratorio,
            "note": note_generali,
            "preview_image_base64": preview_b64,
            "extracted_text": extracted_text,
            "analiti": [a.model_dump() for a in normalized_analiti]
        }

ingestion_pipeline = IngestionPipeline()
