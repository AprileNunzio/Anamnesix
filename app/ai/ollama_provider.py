import json
import httpx
from typing import List, Dict, Any, Optional

class OllamaProvider:
    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url.rstrip("/")

    def set_base_url(self, new_url: str) -> None:
        self.base_url = new_url.rstrip("/")

    async def list_models(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    for m in data.get("models", []):
                        name = m.get("name", "")
                        details = m.get("details", {})
                        is_vision = "vision" in name.lower() or "llava" in name.lower()
                        models.append({
                            "name": name,
                            "size": m.get("size", 0),
                            "parameter_size": details.get("parameter_size", ""),
                            "is_vision": is_vision
                        })
                    return models
                return []
        except Exception:
            return []

    async def is_available(self) -> bool:
        url = f"{self.base_url}/api/version"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        format_json: bool = False
    ) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if format_json:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=180.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Errore Ollama {res.status_code}: {res.text}")
            data = res.json()
            return data.get("message", {}).get("content", "")

    async def generate_with_image(
        self,
        model: str,
        prompt: str,
        image_base64: str,
        system_prompt: Optional[str] = None
    ) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "format": "json"
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=240.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Errore Vision Ollama {res.status_code}: {res.text}")
            data = res.json()
            return data.get("response", "")

ollama_provider = OllamaProvider()
