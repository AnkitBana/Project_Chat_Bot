"""
Agentic RAG with dual-mode retrieval:

  1. Semantic search via ChromaDB (if available)  ← meaning-based
  2. BM25 keyword search fallback                 ← word-based

Both modes are used together when ChromaDB is available:
  semantic_score * 0.7 + bm25_score * 0.3  (hybrid ranking)

Install ChromaDB:  pip install chromadb
Without it:        pure BM25 works automatically
"""
import os
import json
import math
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime


# ── Document model ────────────────────────────────────────────────────────────

class Document:
    def __init__(self, content: str, source: str, metadata: Dict = {}):
        self.doc_id   = str(uuid.uuid4())[:8]
        self.content  = content
        self.source   = source
        self.metadata = metadata
        self.chunks   = self._chunk(content)

    @staticmethod
    def _chunk(text: str, size: int = 400, overlap: int = 80) -> List[str]:
        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i:i + size]))
            i += max(1, size - overlap)
        return chunks or [text]


# ── ChromaDB semantic backend ─────────────────────────────────────────────────

class ChromaBackend:
    COLLECTION = "nova_rag"

    def __init__(self, persist_dir: str = "./data/chroma"):
        import chromadb
        from chromadb.utils import embedding_functions
        self._client = chromadb.PersistentClient(path=persist_dir)
        # Use a lightweight local embedding model (no API key needed)
        self._ef = embedding_functions.DefaultEmbeddingFunction()
        self._col = self._client.get_or_create_collection(
            name=self.COLLECTION,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: List[str], source: str, doc_id: str):
        ids  = [f"{doc_id}_{i}" for i in range(len(chunks))]
        meta = [{"source": source, "chunk_idx": i} for i in range(len(chunks))]
        self._col.upsert(documents=chunks, ids=ids, metadatas=meta)

    def query(self, query: str, top_k: int = 4) -> List[Dict]:
        if self._col.count() == 0:
            return []
        results = self._col.query(
            query_texts=[query],
            n_results=min(top_k, self._col.count()),
            include=["documents", "metadatas", "distances"],
        )
        out = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            out.append({
                "content": doc,
                "source":  meta.get("source", "?"),
                "score":   round(1 - dist, 3),   # cosine distance → similarity
                "method":  "semantic",
            })
        return out

    def count(self) -> int:
        return self._col.count()

    def clear(self):
        self._client.delete_collection(self.COLLECTION)
        self._col = self._client.get_or_create_collection(
            self.COLLECTION, embedding_function=self._ef
        )


# ── BM25 keyword backend ──────────────────────────────────────────────────────

class BM25Backend:
    def __init__(self):
        self._entries: List[Dict] = []   # {"chunk": str, "source": str}

    def add(self, chunks: List[str], source: str):
        for c in chunks:
            self._entries.append({"chunk": c, "source": source})

    def query(self, query: str, top_k: int = 4) -> List[Dict]:
        terms  = _tokenize(query)
        scored = []
        N      = max(1, len(self._entries))
        avg_len = max(1, sum(len(_tokenize(e["chunk"])) for e in self._entries) / N)

        for entry in self._entries:
            score = _bm25(terms, entry["chunk"], N, len(self._entries), avg_len)
            if score > 0:
                scored.append((score, entry))

        scored.sort(reverse=True)
        return [
            {"content": e["chunk"], "source": e["source"],
             "score": round(s, 3), "method": "bm25"}
            for s, e in scored[:top_k]
        ]

    def count(self) -> int:
        return len(self._entries)

    def clear(self):
        self._entries.clear()


# ── Unified RAG engine ────────────────────────────────────────────────────────

class RAGEngine:
    """
    Hybrid RAG: semantic (ChromaDB) + keyword (BM25).
    Falls back to BM25-only if ChromaDB is not installed.
    Persists BM25 index to disk; Chroma persists its own data.
    """

    STORE_PATH = "./data/rag_store.json"

    def __init__(self):
        self._docs:  List[Document] = []
        self._bm25  = BM25Backend()
        self._chroma: Optional[ChromaBackend] = None
        self._chroma_available = False

        # Try to load Chroma
        try:
            self._chroma = ChromaBackend()
            self._chroma_available = True
            print("  [RAG] ChromaDB loaded — semantic search enabled")
        except ImportError:
            print("  [RAG] ChromaDB not installed — using BM25 only  (pip install chromadb to enable semantic search)")
        except Exception as e:
            print(f"  [RAG] ChromaDB error: {e} — using BM25 only")

        self._load_bm25()

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_text(self, text: str, source: str = "manual", metadata: Dict = {}) -> str:
        doc = Document(text, source, metadata)
        self._docs.append(doc)
        self._bm25.add(doc.chunks, source)
        if self._chroma_available and self._chroma:
            self._chroma.add(doc.chunks, source, doc.doc_id)
        self._save_bm25()
        mode = "semantic + keyword" if self._chroma_available else "keyword (BM25)"
        return f"Ingested '{source}' — {len(doc.chunks)} chunks ({mode})"

    def ingest_file(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            return self.ingest_text(text, source=os.path.basename(filepath),
                                    metadata={"filepath": filepath})
        except Exception as e:
            return f"Ingest error: {e}"

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict]:
        """Hybrid retrieval: combine semantic + BM25 scores."""
        if not self._docs and (not self._chroma_available or self._chroma.count() == 0):
            return []

        bm25_results = {r["content"]: r for r in self._bm25.query(query, top_k * 2)}

        if self._chroma_available and self._chroma:
            sem_results = {r["content"]: r for r in self._chroma.query(query, top_k * 2)}
            # Hybrid merge: semantic 70% + bm25 30%
            all_keys = set(bm25_results) | set(sem_results)
            merged = []
            for k in all_keys:
                sem_s  = sem_results.get(k, {}).get("score", 0) * 0.7
                bm25_s = bm25_results.get(k, {}).get("score", 0) * 0.3
                entry  = sem_results.get(k) or bm25_results[k]
                merged.append({**entry, "score": round(sem_s + bm25_s, 3),
                                "method": "hybrid"})
            merged.sort(key=lambda x: x["score"], reverse=True)
            return merged[:top_k]

        return list(bm25_results.values())[:top_k]

    def format_context(self, query: str, top_k: int = 4) -> str:
        results = self.retrieve(query, top_k)
        if not results:
            return ""
        lines = ["[Retrieved Context]"]
        for i, r in enumerate(results, 1):
            method = r.get("method", "?")
            lines.append(
                f"{i}. (source: {r['source']}, score: {r['score']}, method: {method})\n"
                f"   {r['content'][:300]}"
            )
        return "\n".join(lines)

    def list_sources(self) -> List[str]:
        return list({d.source for d in self._docs})

    def get_stats(self) -> Dict[str, Any]:
        return {
            "documents":      len(self._docs),
            "total_chunks":   sum(len(d.chunks) for d in self._docs),
            "sources":        self.list_sources(),
            "semantic_index": self._chroma.count() if self._chroma_available and self._chroma else 0,
            "bm25_entries":   self._bm25.count(),
            "mode":           "hybrid" if self._chroma_available else "bm25_only",
        }

    def clear(self):
        self._docs.clear()
        self._bm25.clear()
        if self._chroma_available and self._chroma:
            self._chroma.clear()
        self._save_bm25()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save_bm25(self):
        try:
            os.makedirs(os.path.dirname(self.STORE_PATH), exist_ok=True)
            data = [{"content": d.content, "source": d.source, "metadata": d.metadata}
                    for d in self._docs]
            with open(self.STORE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load_bm25(self):
        try:
            if not os.path.exists(self.STORE_PATH):
                return
            with open(self.STORE_PATH, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    doc = Document(item["content"], item["source"], item.get("metadata", {}))
                    self._docs.append(doc)
                    self._bm25.add(doc.chunks, doc.source)
                    # Note: Chroma already persisted its own index, no re-add needed
        except Exception:
            pass


# ── BM25 helpers ──────────────────────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

def _bm25(query_terms, chunk, N, df_total, avg_len, k1=1.5, b=0.75) -> float:
    chunk_terms = _tokenize(chunk)
    tf_map = {}
    for t in chunk_terms:
        tf_map[t] = tf_map.get(t, 0) + 1
    score = 0.0
    for term in set(query_terms):
        df  = max(1, df_total // 10)   # approximate df
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
        tf  = tf_map.get(term, 0)
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * len(chunk_terms) / avg_len))
        score  += idf * tf_norm
    return score


# ── Module singleton ──────────────────────────────────────────────────────────

_rag = RAGEngine()

def get_rag() -> RAGEngine:
    return _rag
