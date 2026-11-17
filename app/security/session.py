import time
from app.security.cipher import zeroize_bytes

class SessionManager:
    def __init__(self, timeout_minutes: int = 15):
        self._key_buffer: bytearray | None = None
        self._timeout_seconds: int = timeout_minutes * 60
        self._last_activity: float = 0.0
        self._is_authenticated: bool = False
        self._dpapi_enabled: bool = False

    def unlock(self, key_bytes: bytes, dpapi_enabled: bool = False) -> None:
        self.lock()
        self._key_buffer = bytearray(key_bytes)
        self._last_activity = time.time()
        self._is_authenticated = True
        self._dpapi_enabled = dpapi_enabled

    def lock(self) -> None:
        if self._key_buffer is not None:
            zeroize_bytes(self._key_buffer)
            self._key_buffer = None
        self._is_authenticated = False
        self._last_activity = 0.0

    def touch(self) -> None:
        if self._is_authenticated:
            self._last_activity = time.time()

    def is_locked(self) -> bool:
        if not self._is_authenticated or self._key_buffer is None:
            return True
        if (time.time() - self._last_activity) > self._timeout_seconds:
            self.lock()
            return True
        return False

    def get_key(self) -> bytes:
        if self.is_locked():
            raise PermissionError("Sessione bloccata o scaduta per inattivita.")
        self.touch()
        return bytes(self._key_buffer)

    def set_timeout(self, minutes: int) -> None:
        if minutes < 1:
            minutes = 1
        self._timeout_seconds = minutes * 60

    def is_dpapi_enabled(self) -> bool:
        return self._dpapi_enabled

session_manager = SessionManager(timeout_minutes=15)
