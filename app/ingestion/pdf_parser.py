import io
import fitz
from typing import List, Tuple
from app.ingestion.ocr_engine import ocr_engine

class PDFParser:
    def __init__(self, scanned_threshold_chars: int = 40):
        self.scanned_threshold = scanned_threshold_chars

    def extract_text_and_pages(self, pdf_bytes: bytes) -> Tuple[str, List[bytes]]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text_pages = []
        page_images = []

        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                text = page.get_text("text").strip()

                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                page_images.append(img_bytes)

                if len(text) < self.scanned_threshold:
                    ocr_text = ocr_engine.extract_text_from_bytes(img_bytes)
                    if ocr_text:
                        full_text_pages.append(ocr_text)
                    else:
                        full_text_pages.append(text)
                else:
                    full_text_pages.append(text)

            combined_text = "\n\n--- PAGINA SUCCESSIVA ---\n\n".join(full_text_pages)
            return combined_text, page_images
        finally:
            doc.close()

pdf_parser = PDFParser()
