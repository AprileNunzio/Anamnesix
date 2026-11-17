import json
import math
from typing import List, Dict, Any, Tuple
from app.config.settings import VECTOR_INDEX_PATH
from app.security.cipher import encrypt_bytes, decrypt_bytes
from app.security.session import session_manager

class LocalVectorIndex:
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.documents: List[Dict[str, Any]] = []

    def _hash_token(self, token: str) -> int:
        h = 2166136261
        for ch in token:
            h = (h ^ ord(ch)) * 16777619
            h &= 0xFFFFFFFF
        return h % self.dimension

    def _embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        words = text.lower().replace(",", " ").replace(";", " ").replace(":", " ").split()
        if not words:
            return vector
        for w in words:
            idx = self._hash_token(w)
            vector[idx] += 1.0
            if len(w) > 3:
                for i in range(len(w) - 2):
                    trigram = w[i:i+3]
                    t_idx = self._hash_token(trigram)
                    vector[t_idx] += 0.5
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [v / norm for v in vector]
        return vector

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> None:
        vector = self._embed_text(text)
        self.documents.append({
            "id": doc_id,
            "text": text,
            "vector": vector,
            "metadata": metadata
        })

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        q_vec = self._embed_text(query)
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for doc in self.documents:
            dot_product = sum(a * b for a, b in zip(q_vec, doc["vector"]))
            scored.append((dot_product, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[:top_k]:
            results.append({
                "score": float(score),
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"]
            })
        return results

    def save_to_disk(self) -> None:
        key = session_manager.get_key()
        raw_json = json.dumps(self.documents).encode("utf-8")
        encrypted = encrypt_bytes(raw_json, key)
        VECTOR_INDEX_PATH.write_bytes(encrypted)

    def load_from_disk(self) -> None:
        if not VECTOR_INDEX_PATH.exists():
            self.documents = []
            return
        key = session_manager.get_key()
        encrypted = VECTOR_INDEX_PATH.read_bytes()
        decrypted = decrypt_bytes(encrypted, key)
        self.documents = json.loads(decrypted.decode("utf-8"))

vector_index = LocalVectorIndex()
