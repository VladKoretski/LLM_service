import time
import hashlib
from typing import Optional, Dict, Tuple
from app.core.config import settings

class SimpleCache:
    def __init__(self, ttl: int = settings.cache_ttl_seconds):
        self._store: Dict[str, Tuple[float, str]] = {}
        self._ttl = ttl

    def _make_key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[str]:
        key = self._make_key(text)
        if key in self._store:
            timestamp, value = self._store[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._store[key]
        return None

    def set(self, text: str, value: str):
        key = self._make_key(text)
        self._store[key] = (time.time(), value)