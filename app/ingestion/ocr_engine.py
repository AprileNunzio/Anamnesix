import cv2
import numpy as np
import pytesseract
from PIL import Image
import io

class UltraOCREngine:
    def __init__(self, tesseract_cmd: str | None = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def preprocess_image(self, image_np: np.ndarray) -> np.ndarray:
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(gray)

        denoised = cv2.bilateralFilter(contrast_enhanced, d=9, sigmaColor=75, sigmaSpace=75)

        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh == 0))
        if len(coords) > 50:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if abs(angle) > 0.5 and abs(angle) < 45.0:
                (h, w) = thresh.shape[:2]
                center = (w // 2, h // 2)
                m = cv2.getRotationMatrix2D(center, angle, 1.0)
                thresh = cv2.warpAffine(
                    thresh, m, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        return cleaned

    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            rgb_np = np.array(pil_image)
            processed_np = self.preprocess_image(rgb_np)
            custom_config = r"--oem 3 --psm 6 -l ita+eng"
            text = pytesseract.image_to_string(processed_np, config=custom_config)
            return text.strip()
        except Exception:
            try:
                pil_image = Image.open(io.BytesIO(image_bytes))
                return pytesseract.image_to_string(pil_image, lang="ita+eng").strip()
            except Exception:
                return ""

ocr_engine = UltraOCREngine()
