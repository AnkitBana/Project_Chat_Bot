"""
Tool definitions for AI agents — web search, file ops, API calls, scraping.
"""
import os
import json
import requests
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
from ddgs import DDGS
from bs4 import BeautifulSoup


@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo. Use for current events or facts."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{i}. {r['title']}\n   URL: {r['href']}\n   {r['body']}"
            for i, r in enumerate(results, 1)
        )
    except Exception as e:
        return f"Search error: {e}"


@tool
def read_file(filepath: str) -> str:
    """Read content from a text or JSON file."""
    try:
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                return json.dumps(json.load(f), indent=2)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Read error: {e}"


@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file. Creates the file if it doesn't exist."""
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Write error: {e}"


@tool
def scrape_webpage(url: str) -> str:
    """Scrape and extract text content from a webpage URL."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        lines = (line.strip() for line in soup.get_text().splitlines())
        text = "\n".join(chunk for chunk in lines if chunk)
        return text[:4000]
    except Exception as e:
        return f"Scrape error: {e}"


@tool
def api_call(url: str, method: str = "GET", data: Optional[str] = None) -> str:
    """Make an HTTP API call. method can be GET or POST. data is optional JSON string."""
    try:
        body = json.loads(data) if data else None
        response = requests.request(method.upper(), url, json=body, timeout=15)
        try:
            return json.dumps({"status": response.status_code, "body": response.json()}, indent=2)
        except Exception:
            return json.dumps({"status": response.status_code, "body": response.text}, indent=2)
    except Exception as e:
        return f"API call error: {e}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a safe mathematical expression like '25 * 47' or '(10 + 5) / 3'."""
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "Error: only basic math operators allowed."
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_tools() -> list:
    """Return all available tools."""
    return [web_search, read_file, write_file, scrape_webpage, api_call, calculate, get_current_time]
