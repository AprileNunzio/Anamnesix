import os
import sys
import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pathlib import Path

class UltraOCREngine:
    def __init__(self, tesseract_cmd: str | None = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif sys.platform == "win32":
            candidates = [
                Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
                Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
                Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe"
            ]
            for c in candidates:
                if c.exists():
                    pytesseract.pytesseract.tesseract_cmd = str(c)
                    break

    def normalize_phone_resolution(self, image_np: np.ndarray, max_dim: int = 2048) -> np.ndarray:
        h, w = image_np.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(image_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return image_np

    def flatten_phone_illumination(self, gray: np.ndarray) -> np.ndarray:
        dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        bg = cv2.medianBlur(dilated, 21)
        diff = 255 - cv2.absdiff(gray, bg)
        norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        return norm

    def preprocess_image(self, image_np: np.ndarray) -> np.ndarray:
        resized = self.normalize_phone_resolution(image_np, max_dim=2048)

        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized

        flattened = self.flatten_phone_illumination(gray)

        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(flattened)

        denoised = cv2.bilateralFilter(enhanced, d=7, sigmaColor=50, sigmaSpace=50)

        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh == 0))
        if len(coords) > 60:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if 0.5 < abs(angle) < 45.0:
                h, w = thresh.shape[:2]
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

    def prepare_image_bytes_for_vision(self, image_bytes: bytes) -> bytes:
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            rgb_np = np.array(pil_image)
            resized = self.normalize_phone_resolution(rgb_np, max_dim=2048)
            success, enc = cv2.imencode(".png", cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
            if success:
                return enc.tobytes()
            return image_bytes
        except Exception:
            return image_bytes

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
