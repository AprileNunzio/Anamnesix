import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.config.settings import (
    PROFILES_METADATA_PATH,
    ensure_directories_exist,
    get_profile_db_path,
    get_profile_docs_dir
)
from app.security.cipher import encrypt_bytes, decrypt_bytes
from app.security.session import session_manager
from app.database.connection import init_profile_database

class FamilyMember(BaseModel):
    id: str
    nome: str
    cognome: str
    parentela: str
    data_nascita: str
    sesso: str
    gruppo_sanguigno: Optional[str] = None
    note_anamnestiche: Optional[str] = None
    data_creazione: str

class ProfileManager:
    def __init__(self):
        self._active_profile_id: Optional[str] = None

    def get_active_profile_id(self) -> str:
        if not self._active_profile_id:
            profiles = self.list_profiles()
            if profiles:
                self._active_profile_id = profiles[0]["id"]
            else:
                default_profile = self.create_profile(
                    nome="Principale",
                    cognome="Utente",
                    parentela="Intestatario",
                    data_nascita="1980-01-01",
                    sesso="M",
                    gruppo_sanguigno="0+",
                    note_anamnestiche="Profilo clinico predefinito"
                )
                self._active_profile_id = default_profile["id"]
        return self._active_profile_id

    def set_active_profile(self, profile_id: str) -> bool:
        profiles = self.list_profiles()
        for p in profiles:
            if p["id"] == profile_id:
                self._active_profile_id = profile_id
                init_profile_database(profile_id)
                return True
        return False

    def list_profiles(self) -> List[Dict[str, Any]]:
        ensure_directories_exist()
        if not PROFILES_METADATA_PATH.exists():
            return []
        try:
            key = session_manager.get_key()
            encrypted_data = PROFILES_METADATA_PATH.read_bytes()
            decrypted = decrypt_bytes(encrypted_data, key)
            return json.loads(decrypted.decode("utf-8"))
        except Exception:
            return []

    def save_profiles_list(self, profiles: List[Dict[str, Any]]) -> None:
        ensure_directories_exist()
        key = session_manager.get_key()
        raw_json = json.dumps(profiles, ensure_ascii=False).encode("utf-8")
        encrypted = encrypt_bytes(raw_json, key)
        PROFILES_METADATA_PATH.write_bytes(encrypted)

    def create_profile(
        self,
        nome: str,
        cognome: str,
        parentela: str,
        data_nascita: str,
        sesso: str,
        gruppo_sanguigno: Optional[str] = None,
        note_anamnestiche: Optional[str] = None
    ) -> Dict[str, Any]:
        profiles = self.list_profiles()
        new_id = str(uuid.uuid4())
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        new_member = {
            "id": new_id,
            "nome": nome.strip(),
            "cognome": cognome.strip(),
            "parentela": parentela.strip(),
            "data_nascita": data_nascita.strip(),
            "sesso": sesso.strip().upper(),
            "gruppo_sanguigno": gruppo_sanguigno.strip() if gruppo_sanguigno else "",
            "note_anamnestiche": note_anamnestiche.strip() if note_anamnestiche else "",
            "data_creazione": now_iso
        }
        profiles.append(new_member)
        self.save_profiles_list(profiles)
        get_profile_docs_dir(new_id)
        init_profile_database(new_id)
        if not self._active_profile_id:
            self._active_profile_id = new_id
        return new_member

    def update_profile(
        self,
        profile_id: str,
        nome: str,
        cognome: str,
        parentela: str,
        data_nascita: str,
        sesso: str,
        gruppo_sanguigno: Optional[str] = None,
        note_anamnestiche: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        profiles = self.list_profiles()
        for p in profiles:
            if p["id"] == profile_id:
                p["nome"] = nome.strip()
                p["cognome"] = cognome.strip()
                p["parentela"] = parentela.strip()
                p["data_nascita"] = data_nascita.strip()
                p["sesso"] = sesso.strip().upper()
                p["gruppo_sanguigno"] = gruppo_sanguigno.strip() if gruppo_sanguigno else ""
                p["note_anamnestiche"] = note_anamnestiche.strip() if note_anamnestiche else ""
                self.save_profiles_list(profiles)
                return p
        return None

    def delete_profile(self, profile_id: str) -> bool:
        profiles = self.list_profiles()
        filtered = [p for p in profiles if p["id"] != profile_id]
        if len(filtered) == len(profiles):
            return False
        self.save_profiles_list(filtered)
        if self._active_profile_id == profile_id:
            self._active_profile_id = filtered[0]["id"] if filtered else None
        return True

profile_manager = ProfileManager()
