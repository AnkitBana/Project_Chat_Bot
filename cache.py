"""
Distributed cache with Redis backend and local LRU fallback.

- If Redis is available: uses Redis (shared across all server instances)
- If Redis is not available: falls back to local LRU cache transparently

This means the same code works in both development (no Redis) and
production (Redis running) without any changes.
"""
import os
import json
import hashlib
import re
import time
from collections import OrderedDict
from datetime import datetime
from typing import Optional


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def _key(question: str) -> str:
    return "nova:cache:" + hashlib.md5(_normalize(question).encode()).hexdigest()


# ── Redis backend ─────────────────────────────────────────────────────────────

class RedisCache:
    """
    Redis-backed cache. TTL defaults to 24 hours.
    Tracks hit counts in a separate Redis key.
    """

    DEFAULT_TTL = 86_400   # 24 hours

    def __init__(self, url: str = "redis://localhost:6379/0", ttl: int = DEFAULT_TTL):
        import redis as _redis
        self._r   = _redis.from_url(url, decode_responses=True)
        self._ttl = ttl
        self._r.ping()   # raise immediately if unreachable

    def get(self, question: str) -> Optional[str]:
        k = _key(question)
        val = self._r.get(k)
        if val:
            self._r.incr(k + ":hits")
            self._r.expire(k, self._ttl)   # refresh TTL on hit
        return val

    def set(self, question: str, reply: str):
        k = _key(question)
        self._r.setex(k, self._ttl, reply)

    def clear(self):
        keys = self._r.keys("nova:cache:*")
        if keys:
            self._r.delete(*keys)

    def stats(self) -> dict:
        keys  = self._r.keys("nova:cache:[0-9a-f]*")
        hits  = sum(int(self._r.get(k + ":hits") or 0) for k in keys)
        return {
            "backend":     "redis",
            "entries":     len(keys),
            "total_hits":  hits,
            "max_size":    "unlimited",
        }


# ── Local LRU fallback ────────────────────────────────────────────────────────

class LocalLRUCache:
    """
    In-process LRU cache with JSON persistence (existing implementation).
    Used automatically when Redis is not available.
    """

    def __init__(self, max_size: int = 200, persist_path: str = "./data/response_cache.json"):
        self.max_size     = max_size
        self.persist_path = persist_path
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._load()

    def get(self, question: str) -> Optional[str]:
        k = _key(question)
        if k in self._cache:
            entry = self._cache.pop(k)
            self._cache[k] = entry
            entry["hits"] += 1
            return entry["reply"]
        return None

    def set(self, question: str, reply: str):
        k = _key(question)
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        self._cache[k] = {
            "question":  question,
            "reply":     reply,
            "hits":      0,
            "cached_at": datetime.now().isoformat(),
        }
        self._save()

    def clear(self):
        self._cache.clear()
        self._save()

    def stats(self) -> dict:
        hits = sum(e["hits"] for e in self._cache.values())
        return {
            "backend":    "local_lru",
            "entries":    len(self._cache),
            "max_size":   self.max_size,
            "total_hits": hits,
        }

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
                for e in json.load(f):
                    self._cache[_key(e["question"])] = e
        except Exception:
            pass


# ── Auto-selecting factory ─────────────────────────────────────────────────────

def _build_cache():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        c = RedisCache(url=redis_url)
        print(f"  [Cache] Redis connected at {redis_url}")
        return c
    except Exception as e:
        print(f"  [Cache] Redis unavailable ({e.__class__.__name__}), using local LRU fallback")
        return LocalLRUCache()


_cache_instance = None

def get_cache():
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = _build_cache()
    return _cache_instance
