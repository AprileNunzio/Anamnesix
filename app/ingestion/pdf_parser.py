import io
from typing import List, Tuple
from app.ingestion.ocr_engine import ocr_engine

class PDFParser:
    def __init__(self, scanned_threshold_chars: int = 50):
        self.scanned_threshold = scanned_threshold_chars

    def extract_with_pymupdf(self, pdf_bytes: bytes) -> Tuple[List[str], List[bytes]]:
        import fitz
        text_pages = []
        page_images = []
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                text = page.get_text("text").strip()

                img_bytes = None
                try:
                    zoom = 2.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")
                except Exception:
                    img_bytes = None

                if not img_bytes:
                    try:
                        images_list = page.get_images()
                        if images_list:
                            first_xref = images_list[0][0]
                            base_img = doc.extract_image(first_xref)
                            img_bytes = base_img.get("image")
                    except Exception:
                        img_bytes = None

                if img_bytes:
                    opt_bytes = ocr_engine.prepare_image_bytes_for_vision(img_bytes)
                    page_images.append(opt_bytes)

                if len(text) < self.scanned_threshold and img_bytes:
                    ocr_text = ocr_engine.extract_text_from_bytes(img_bytes)
                    text_pages.append(ocr_text if ocr_text else text)
                else:
                    text_pages.append(text)
            return text_pages, page_images
        finally:
            doc.close()

    def extract_with_pypdf(self, pdf_bytes: bytes) -> Tuple[List[str], List[bytes]]:
        import pypdf
        text_pages = []
        page_images = []
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            txt = page.extract_text() or ""
            text_pages.append(txt.strip())
            try:
                for img_obj in page.images:
                    opt = ocr_engine.prepare_image_bytes_for_vision(img_obj.data)
                    page_images.append(opt)
            except Exception:
                continue
        return text_pages, page_images

    def extract_text_and_pages(self, pdf_bytes: bytes) -> Tuple[str, List[bytes]]:
        text_pages = []
        page_images = []

        try:
            text_pages, page_images = self.extract_with_pymupdf(pdf_bytes)
        except Exception:
            text_pages, page_images = [], []

        if not text_pages or not any(t.strip() for t in text_pages):
            try:
                p_text, p_images = self.extract_with_pypdf(pdf_bytes)
                if any(t.strip() for t in p_text):
                    text_pages = p_text
                if not page_images and p_images:
                    page_images = p_images
            except Exception:
                text_pages, page_images = text_pages, page_images

        combined_text = "\n\n--- PAGINA SUCCESSIVA ---\n\n".join(t for t in text_pages if t)
        return combined_text, page_images

pdf_parser = PDFParser()
