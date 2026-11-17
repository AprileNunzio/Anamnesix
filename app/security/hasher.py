import os
from pathlib import Path
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from app.config.settings import SALT_FILE_PATH, ensure_directories_exist

ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4
ARGON2_KEY_LEN = 32
SALT_LENGTH = 16

def get_or_create_salt() -> bytes:
    ensure_directories_exist()
    if SALT_FILE_PATH.exists():
        return SALT_FILE_PATH.read_bytes()
    new_salt = os.urandom(SALT_LENGTH)
    SALT_FILE_PATH.write_bytes(new_salt)
    return new_salt

def derive_key(password: str, salt: bytes | None = None) -> bytes:
    if salt is None:
        salt = get_or_create_salt()
    kdf = Argon2id(
        salt=salt,
        length=ARGON2_KEY_LEN,
        iterations=ARGON2_TIME_COST,
        lanes=ARGON2_PARALLELISM,
        memory_cost=ARGON2_MEMORY_COST,
        ad=None,
        secret=None
    )
    return kdf.derive(password.encode("utf-8"))

def verify_master_key(test_key: bytes, stored_hash: bytes) -> bool:
    import hmac
    return hmac.compare_digest(test_key, stored_hash)
