import json
from typing import Dict, Any, List, Optional
from app.ai.ollama_provider import ollama_provider
from app.ai.gemini_provider import gemini_provider
from app.ai.pii_scrubber import pii_scrubber
from app.database.repository import get_config_value
from app.security.cipher import decrypt_string
from app.security.session import session_manager

CLINICAL_EXTRACTION_SYSTEM_PROMPT = """
Sei un medico analista ed esperto di biochimica clinica e patologia clinica.
Il tuo compito e estrarre e normalizzare con assoluta precisione tutti i parametri clinici presenti nel testo del referto medico.
Devi rispondere ESCLUSIVAMENTE con un oggetto JSON valido privo di markdown e commenti, con questa struttura:
{
  "data_prelievo": "AAAA-MM-GG",
  "laboratorio": "Nome laboratorio o sconosciuto",
  "note_generali": "Note o osservazioni globali sul referto",
  "analiti": [
    {
      "categoria": "Nome categoria tra: Emocromo, Profilo Lipidico, Funzionalita Epatica, Funzionalita Renale, Tiroide, Elettroliti, Vitamine, Ormoni, Urine, Diagnostica per Immagini, Coagulazione, Altro",
      "nome_esame_originale": "Nome esatto riportato sul referto",
      "nome_standardizzato": "Nome clinico standardizzato italiano",
      "valore_numerico": 0.0,
      "valore_testuale": null,
      "unita_misura": "es. mg/dL, g/dL, UI/L, etc.",
      "range_min": 0.0,
      "range_max": 0.0,
      "stato_flag": "Uno tra: NORMALE, BASSO, ALTO, CRITICO_BASSO, CRITICO_ALTO",
      "note_referto": null
    }
  ]
}
Se un valore e testuale (es. Negativo, Assenti), imposta valore_numerico a null e compila valore_testuale.
Assicurati che range_min e range_max siano estratti come numeri float quando disponibili.
"""

class AIRouter:
    def __init__(self):
        self.default_provider = "ollama"
        self.ollama_model = "llama3.1:latest"
        self.ollama_vision_model = "llama3.2-vision:latest"
        self.gemini_model = "gemini-2.5-flash"
        self.pii_scrubbing_enabled = True

    def reload_config(self) -> None:
        try:
            if not session_manager.is_locked():
                key = session_manager.get_key()
                enc_gemini = get_config_value("gemini_api_key")
                if enc_gemini:
                    api_key = decrypt_string(enc_gemini, key)
                    gemini_provider.set_api_key(api_key)

                enc_provider = get_config_value("ai_provider")
                if enc_provider:
                    self.default_provider = decrypt_string(enc_provider, key)

                enc_ollama_model = get_config_value("ollama_model")
                if enc_ollama_model:
                    self.ollama_model = decrypt_string(enc_ollama_model, key)

                enc_ollama_vision = get_config_value("ollama_vision_model")
                if enc_ollama_vision:
                    self.ollama_vision_model = decrypt_string(enc_ollama_vision, key)

                enc_gemini_model = get_config_value("gemini_model")
                if enc_gemini_model:
                    self.gemini_model = decrypt_string(enc_gemini_model, key)

                enc_pii = get_config_value("pii_scrubbing")
                if enc_pii:
                    self.pii_scrubbing_enabled = decrypt_string(enc_pii, key) == "true"
        except Exception as err:
            self.last_config_error = str(err)

    async def find_installed_vision_model(self) -> Optional[str]:
        models = await ollama_provider.list_models()
        if not models:
            return None
        names = [m.get("name", "") for m in models]
        if self.ollama_vision_model in names:
            return self.ollama_vision_model
        for m in models:
            if m.get("is_vision"):
                return m.get("name")
        for n in names:
            lower = n.lower()
            if "vision" in lower or "llava" in lower or "minicpm" in lower or "vl" in lower:
                return n
        return None

    async def extract_clinical_data(
        self,
        document_text: str,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        self.reload_config()
        text_to_process = document_text
        pii_map = {}

        if self.default_provider == "gemini":
            if self.pii_scrubbing_enabled and text_to_process:
                text_to_process, pii_map = pii_scrubber.scrub(text_to_process)
            prompt = f"Analizza attentamente questa scansione o referto clinico ed estrai tutti gli analiti in formato JSON:\n\n{text_to_process}"
            raw_response = await gemini_provider.generate_content(
                model=self.gemini_model,
                prompt=prompt,
                system_instruction=CLINICAL_EXTRACTION_SYSTEM_PROMPT,
                image_bytes=image_bytes,
                mime_type=mime_type or "image/png",
                format_json=True
            )
        else:
            vision_model = await self.find_installed_vision_model() if image_bytes else None
            has_text = bool(text_to_process and len(text_to_process.strip()) > 25)

            if vision_model and image_bytes:
                import base64
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                raw_response = await ollama_provider.generate_with_image(
                    model=vision_model,
                    prompt="Estrai tutti gli analiti, valori numerici, unita di misura e range di riferimento da questa immagine in formato JSON strutturato.",
                    image_base64=b64,
                    system_prompt=CLINICAL_EXTRACTION_SYSTEM_PROMPT
                )
            elif has_text:
                messages = [
                    {"role": "system", "content": CLINICAL_EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Referto:\n{text_to_process}"}
                ]
                raw_response = await ollama_provider.chat(
                    model=self.ollama_model,
                    messages=messages,
                    format_json=True
                )
            elif image_bytes:
                from app.ingestion.ocr_engine import ocr_engine
                ocr_text = ocr_engine.extract_text_from_bytes(image_bytes)
                if ocr_text and len(ocr_text.strip()) > 10:
                    messages = [
                        {"role": "system", "content": CLINICAL_EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Referto:\n{ocr_text}"}
                    ]
                    raw_response = await ollama_provider.chat(
                        model=self.ollama_model,
                        messages=messages,
                        format_json=True
                    )
                else:
                    models = await ollama_provider.list_models()
                    names = [m.get("name", "") for m in models]
                    raise RuntimeError(
                        f"Il documento caricato e una scansione/foto priva di testo digitale vettoriale. "
                        f"Per consentire all'AI la lettura visiva di foto da cellulare, configura la tua chiave Google Gemini in Impostazioni "
                        f"(consigliata, gratuita e istantanea) oppure installa un modello visivo locale digitando nel terminale 'ollama pull llama3.2-vision'. "
                        f"Modelli locali attuali: {names}."
                    )
            else:
                raise RuntimeError("Nessun testo o immagine estratta dal documento caricato.")

        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        if pii_map and "laboratorio" in data and data["laboratorio"] in pii_map:
            data["laboratorio"] = pii_map[data["laboratorio"]]

        return data

    async def generate_response(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.2
    ) -> str:
        self.reload_config()
        prompt_to_send = user_prompt
        pii_map = {}

        if self.default_provider == "gemini":
            if self.pii_scrubbing_enabled:
                prompt_to_send, pii_map = pii_scrubber.scrub(prompt_to_send)
            response = await gemini_provider.generate_content(
                model=self.gemini_model,
                prompt=prompt_to_send,
                system_instruction=system_instruction,
                temperature=temperature,
                format_json=False
            )
            if pii_map:
                response = pii_scrubber.restore(response, pii_map)
            return response
        else:
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_to_send}
            ]
            return await ollama_provider.chat(
                model=self.ollama_model,
                messages=messages,
                temperature=temperature,
                format_json=False
            )

ai_router = AIRouter()
