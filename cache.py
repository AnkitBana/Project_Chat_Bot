"""
Response cache — returns instant answers for repeated questions.
Uses normalized question text as key, LRU eviction, optional disk persistence.
"""
import os
import json
import hashlib
from collections import OrderedDict
from datetime import datetime
from typing import Optional


class ResponseCache:
    """
    LRU in-memory cache with optional disk persistence.
    Normalizes questions before lookup so minor variations still hit the cache.
    """

    def __init__(self, max_size: int = 200, persist_path: str = "./data/response_cache.json"):
        self.max_size = max_size
        self.persist_path = persist_path
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._load()

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, question: str) -> Optional[str]:
        """Return cached reply if available, else None."""
        key = self._key(question)
        if key in self._cache:
            entry = self._cache.pop(key)
            self._cache[key] = entry          # move to end (most recently used)
            entry["hits"] += 1
            return entry["reply"]
        return None

    def set(self, question: str, reply: str):
        """Store a reply in the cache."""
        key = self._key(question)
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        self._cache[key] = {
            "question": question,
            "reply": reply,
            "hits": 0,
            "cached_at": datetime.now().isoformat(),
        }
        self._save()

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._save()

    def stats(self) -> dict:
        total_hits = sum(e["hits"] for e in self._cache.values())
        return {
            "entries": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """Lowercase, strip punctuation/whitespace for consistent matching."""
        import re
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
        text = re.sub(r"\s+", " ", text)       # collapse whitespace
        return text

    def _key(self, question: str) -> str:
        normalized = self._normalize(question)
        return hashlib.md5(normalized.encode()).hexdigest()

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(list(self._cache.values()), f, indent=2)
        except Exception:
            pass

    def _load(self):
        try:
            if not os.path.exists(self.persist_path):
                return
            with open(self.persist_path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            for e in entries:
                key = self._key(e["question"])
                self._cache[key] = e
        except Exception:
            pass


# ── Module-level singleton ────────────────────────────────────────────────────
_cache = ResponseCache()

def get_cache() -> ResponseCache:
    return _cache
