import re
from typing import Tuple, Dict

CODICE_FISCALE_REGEX = re.compile(r"\b[A-Za-z]{6}[0-9LlMmNnPpQqRrSsTtUuVv]{2}[A-EHLMPR-Ta-ehlpmpr-t][0-9LlMmNnPpQqRrSsTtUuVv]{2}[A-Za-z][0-9LlMmNnPpQqRrSsTtUuVv]{3}[A-Za-z]\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(r"(\+39\s?)?((0\d{1,4}\s?\d{5,8})|(3\d{2}\s?\d{6,7}))\b")
ADDRESS_REGEX = re.compile(r"\b(via|viale|corso|piazza|vicolo|strada|largo)\s+[A-Za-zÀ-ÿ'\s]+,\s*\d+\b", re.IGNORECASE)
PATIENT_PREFIX_REGEX = re.compile(r"(paziente|sig\.|sig\.ra|dott\.|paziente:\s*|assistito:\s*)([A-ZÀ-ÿa-z'\s]{3,35})(?=\n|,|\s{2,}|data)", re.IGNORECASE)

class PIIScrubber:
    def __init__(self):
        self.active = True

    def scrub(self, text: str) -> Tuple[str, Dict[str, str]]:
        mapping = {}
        scrubbed = text

        cf_matches = CODICE_FISCALE_REGEX.findall(scrubbed)
        for i, match in enumerate(set(cf_matches)):
            token = f"[CODICE_FISCALE_{i+1}]"
            mapping[token] = match
            scrubbed = scrubbed.replace(match, token)

        email_matches = EMAIL_REGEX.findall(scrubbed)
        for i, match in enumerate(set(email_matches)):
            token = f"[EMAIL_{i+1}]"
            mapping[token] = match
            scrubbed = scrubbed.replace(match, token)

        phone_matches = PHONE_REGEX.findall(scrubbed)
        for i, match_tuple in enumerate(phone_matches):
            raw_match = match_tuple[1] if match_tuple[1] else match_tuple[0]
            if raw_match:
                token = f"[TELEFONO_{i+1}]"
                mapping[token] = raw_match
                scrubbed = scrubbed.replace(raw_match, token)

        addr_matches = ADDRESS_REGEX.findall(scrubbed)
        for i, match in enumerate(set(addr_matches)):
            token = f"[INDIRIZZO_{i+1}]"
            mapping[token] = match
            scrubbed = scrubbed.replace(match, token)

        def replace_patient(match_obj):
            prefix = match_obj.group(1)
            name = match_obj.group(2).strip()
            token = "[NOME_PAZIENTE]"
            mapping[token] = name
            return f"{prefix} {token}"

        scrubbed = PATIENT_PREFIX_REGEX.sub(replace_patient, scrubbed)

        return scrubbed, mapping

    def restore(self, scrubbed_text: str, mapping: Dict[str, str]) -> str:
        restored = scrubbed_text
        for token, original in mapping.items():
            restored = restored.replace(token, original)
        return restored

pii_scrubber = PIIScrubber()
