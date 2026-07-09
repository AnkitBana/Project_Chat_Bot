"""
Conversation memory management using LangChain message objects.
"""
import json
import os
from typing import List, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class MemoryManager:
    """
    Simple in-memory conversation history manager.
    Stores messages as LangChain message objects.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.messages: List[BaseMessage] = []

    def add_message(self, user_input: str, ai_output: str):
        """Record a conversation turn."""
        self.messages.append(HumanMessage(content=user_input))
        self.messages.append(AIMessage(content=ai_output))

    def get_messages(self) -> List[BaseMessage]:
        """Return all stored messages."""
        return self.messages

    def clear(self):
        """Clear conversation history."""
        self.messages = []

    def save(self, filepath: Optional[str] = None) -> str:
        """Save conversation history to JSON."""
        if not filepath:
            os.makedirs("./data/memory", exist_ok=True)
            filepath = f"./data/memory/{self.session_id}.json"
        data = [
            {"type": m.__class__.__name__, "content": m.content}
            for m in self.messages
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    def load(self, filepath: str):
        """Load conversation history from JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = []
        for item in data:
            if item["type"] == "HumanMessage":
                self.messages.append(HumanMessage(content=item["content"]))
            elif item["type"] == "AIMessage":
                self.messages.append(AIMessage(content=item["content"]))

    def get_stats(self) -> dict:
        """Return memory stats."""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "turns": len(self.messages) // 2,
        }
