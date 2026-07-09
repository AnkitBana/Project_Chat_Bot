"""
Extended tools: Wikipedia search and local file summarizer.
"""
import os
import json
from langchain_core.tools import tool
from ddgs import DDGS


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual information about a topic."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"site:wikipedia.org {query}", max_results=3))
        if not results:
            return "No Wikipedia results found."
        return "\n\n".join(
            f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}"
            for r in results
        )
    except Exception as e:
        return f"Wikipedia search error: {e}"


@tool
def news_search(query: str) -> str:
    """Search for the latest news articles on a topic."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=5))
        if not results:
            return "No news found."
        return "\n\n".join(
            f"{i}. {r['title']}\n   Source: {r.get('source','?')}  Date: {r.get('date','?')}\n   {r['body']}"
            for i, r in enumerate(results, 1)
        )
    except Exception as e:
        return f"News search error: {e}"


@tool
def summarize_local_file(filepath: str) -> str:
    """
    Read a local file and return its content with basic stats.
    Supports .txt, .md, .py, .json files.
    """
    try:
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            content = json.dumps(data, indent=2)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        lines = content.splitlines()
        words = len(content.split())
        preview = "\n".join(lines[:40])
        return (
            f"File: {filepath}\n"
            f"Lines: {len(lines)} | Words: {words} | Size: {len(content)} chars\n"
            f"{'='*40}\n{preview}"
            + ("\n... (truncated)" if len(lines) > 40 else "")
        )
    except Exception as e:
        return f"File read error: {e}"


@tool
def list_directory(path: str = ".") -> str:
    """List files and folders in a directory."""
    try:
        items = os.listdir(path)
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        dirs  = [d for d in items if os.path.isdir(os.path.join(path, d))]
        return (
            f"Directory: {os.path.abspath(path)}\n"
            f"Folders ({len(dirs)}): {', '.join(dirs) or 'none'}\n"
            f"Files   ({len(files)}): {', '.join(files) or 'none'}"
        )
    except Exception as e:
        return f"Directory error: {e}"


def get_extra_tools() -> list:
    return [wikipedia_search, news_search, summarize_local_file, list_directory]
