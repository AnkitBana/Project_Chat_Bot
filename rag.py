"""
Agentic RAG — ingests documents and retrieves relevant context before LLM calls.
Uses simple TF-IDF style scoring (no external vector DB needed).
"""
import os
import json
import math
import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class Document:
    def __init__(self, content: str, source: str, metadata: Dict = {}):
        self.doc_id   = f"{source}_{datetime.now().strftime('%H%M%S%f')[:10]}"
        self.content  = content
        self.source   = source
        self.metadata = metadata
        self.chunks   = self._chunk(content)

    @staticmethod
    def _chunk(text: str, size: int = 400, overlap: int = 80) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i:i + size]))
            i += size - overlap
        return chunks


class RAGEngine:
    """
    Lightweight RAG engine using BM25-style scoring.
    No external dependencies — pure Python.
    """

    STORE_PATH = "./data/rag_store.json"

    def __init__(self):
        self._docs: List[Document] = []
        self._load()

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_text(self, text: str, source: str = "manual", metadata: Dict = {}) -> str:
        """Add raw text to the knowledge base."""
        doc = Document(text, source, metadata)
        self._docs.append(doc)
        self._save()
        return f"Ingested '{source}' — {len(doc.chunks)} chunks stored."

    def ingest_file(self, filepath: str) -> str:
        """Read a file and ingest its content."""
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            source = os.path.basename(filepath)
            return self.ingest_text(text, source=source, metadata={"filepath": filepath})
        except Exception as e:
            return f"Ingest error: {e}"

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Return the top_k most relevant chunks for a query."""
        if not self._docs:
            return []

        query_terms = self._tokenize(query)
        scored: List[tuple] = []

        for doc in self._docs:
            for chunk in doc.chunks:
                score = self._bm25_score(query_terms, chunk)
                if score > 0:
                    scored.append((score, chunk, doc.source))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"score": round(s, 3), "content": c, "source": src}
            for s, c, src in scored[:top_k]
        ]

    def format_context(self, query: str, top_k: int = 4) -> str:
        """Return retrieved context as a formatted string for the LLM prompt."""
        results = self.retrieve(query, top_k)
        if not results:
            return ""
        lines = ["[Retrieved Context]"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. (Source: {r['source']}, Score: {r['score']})\n   {r['content'][:300]}")
        return "\n".join(lines)

    def list_sources(self) -> List[str]:
        return list({d.source for d in self._docs})

    def get_stats(self) -> Dict[str, Any]:
        total_chunks = sum(len(d.chunks) for d in self._docs)
        return {
            "documents":    len(self._docs),
            "total_chunks": total_chunks,
            "sources":      self.list_sources(),
        }

    def clear(self):
        self._docs = []
        self._save()

    # ── BM25 scoring ─────────────────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def _bm25_score(self, query_terms: List[str], chunk: str,
                    k1: float = 1.5, b: float = 0.75) -> float:
        chunk_terms = self._tokenize(chunk)
        chunk_len   = len(chunk_terms)
        avg_len     = max(1, sum(len(self._tokenize(" ".join(d.chunks))) for d in self._docs)
                         / max(1, len(self._docs)))
        term_freq   = {}
        for t in chunk_terms:
            term_freq[t] = term_freq.get(t, 0) + 1

        score = 0.0
        N = max(1, sum(len(d.chunks) for d in self._docs))
        for term in set(query_terms):
            df  = sum(1 for d in self._docs for c in d.chunks if term in self._tokenize(c))
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            tf  = term_freq.get(term, 0)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * chunk_len / avg_len))
            score  += idf * tf_norm
        return score

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.STORE_PATH), exist_ok=True)
            data = [
                {"content": d.content, "source": d.source, "metadata": d.metadata}
                for d in self._docs
            ]
            with open(self.STORE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load(self):
        try:
            if not os.path.exists(self.STORE_PATH):
                return
            with open(self.STORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                doc = Document(item["content"], item["source"], item.get("metadata", {}))
                self._docs.append(doc)
        except Exception:
            pass


# ── Module singleton ──────────────────────────────────────────────────────────
_rag = RAGEngine()

def get_rag() -> RAGEngine:
    return _rag
