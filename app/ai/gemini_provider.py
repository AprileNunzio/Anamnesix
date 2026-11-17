import json
import httpx
from typing import List, Dict, Any, Optional

class GeminiProvider:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    async def generate_content(
        self,
        model: str,
        prompt: str,
        system_instruction: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        temperature: float = 0.2,
        format_json: bool = True
    ) -> str:
        if not self.api_key:
            raise ValueError("Chiave API Gemini mancante o non configurata.")

        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"

        parts: List[Dict[str, Any]] = []

        if image_bytes and mime_type:
            import base64
            b64_data = base64.b64encode(image_bytes).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })

        parts.append({"text": prompt})

        contents = [{"role": "user", "parts": parts}]

        body: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "topP": 0.95
            }
        }

        if format_json:
            body["generationConfig"]["responseMimeType"] = "application/json"

        if system_instruction:
            body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(url, json=body)
            if res.status_code != 200:
                raise RuntimeError(f"Errore chiamata Gemini {res.status_code}: {res.text}")
            data = res.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Nessuna risposta ricevuta da Gemini.")
            text_result = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return text_result

gemini_provider = GeminiProvider()
