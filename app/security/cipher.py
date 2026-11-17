import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12

def zeroize_bytes(buffer: bytearray) -> None:
    for i in range(len(buffer)):
        buffer[i] = 0

def encrypt_bytes(data: bytes, key: bytes, associated_data: bytes | None = None) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext_with_tag = aesgcm.encrypt(nonce, data, associated_data)
    return nonce + ciphertext_with_tag

def decrypt_bytes(payload: bytes, key: bytes, associated_data: bytes | None = None) -> bytes:
    if len(payload) < NONCE_SIZE + 16:
        raise ValueError("Payload crittografico non valido o corrotto.")
    nonce = payload[:NONCE_SIZE]
    ciphertext_with_tag = payload[NONCE_SIZE:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data)

def encrypt_string(text: str, key: bytes) -> str:
    import base64
    raw_encrypted = encrypt_bytes(text.encode("utf-8"), key)
    return base64.b64encode(raw_encrypted).decode("utf-8")

def decrypt_string(encoded_text: str, key: bytes) -> str:
    import base64
    raw_payload = base64.b64decode(encoded_text.encode("utf-8"))
    decrypted_bytes = decrypt_bytes(raw_payload, key)
    return decrypted_bytes.decode("utf-8")
