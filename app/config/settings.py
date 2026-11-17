import os
import sys
from pathlib import Path

def get_base_storage_dir() -> Path:
    if sys.platform == "win32":
        user_profile = os.environ.get("USERPROFILE", "")
        if user_profile:
            base = Path(user_profile) / "Documents" / "Anamnesix"
        else:
            base = Path.home() / "Documents" / "Anamnesix"
    else:
        base = Path.home() / "Documents" / "Anamnesix"
    return base

BASE_DIR = get_base_storage_dir()
VAULT_DIR = BASE_DIR / "vault"
PROFILES_DIR = VAULT_DIR / "profiles"
DOCUMENTS_DIR = BASE_DIR / "documents"
BACKUPS_DIR = BASE_DIR / "backups"
CONFIG_DIR = BASE_DIR / "config"

GLOBAL_CONFIG_PATH = CONFIG_DIR / "global_config.enc"
PROFILES_METADATA_PATH = VAULT_DIR / "profiles_metadata.enc"
SALT_FILE_PATH = CONFIG_DIR / "salt.bin"

DEFAULT_HOST = "127.0.0.1"
APP_NAME = "Anamnesix"
APP_VERSION = "1.0.0"
GITHUB_REPO = "AprileNunzio/Anamnesix"

def ensure_directories_exist() -> None:
    for directory in [BASE_DIR, VAULT_DIR, PROFILES_DIR, DOCUMENTS_DIR, BACKUPS_DIR, CONFIG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def get_profile_db_path(profile_id: str) -> Path:
    profile_vault = PROFILES_DIR / profile_id
    profile_vault.mkdir(parents=True, exist_ok=True)
    return profile_vault / "anamnesix.db"

def get_profile_docs_dir(profile_id: str) -> Path:
    profile_docs = DOCUMENTS_DIR / profile_id
    profile_docs.mkdir(parents=True, exist_ok=True)
    return profile_docs

def get_profile_vector_path(profile_id: str) -> Path:
    profile_vault = PROFILES_DIR / profile_id
    profile_vault.mkdir(parents=True, exist_ok=True)
    return profile_vault / "vectors.bin"
