"""
Collector Agent
----------------
Job: Take raw personal input from the user (journal entries, opinions,
short answers to prompts) and turn it into clean, structured "memory entries"
that the rest of the system can use.
"""

import datetime
import uuid


class CollectorAgent:
    """Collects raw user input and converts it into structured memory entries."""

    def __init__(self):
        # In-memory list for now; later this will be replaced by ChromaDB storage
        self.collected_entries = []

    def collect_entry(self, raw_text: str, category: str = "general") -> dict:
        """
        Takes one piece of raw text from the user and wraps it into
        a structured entry with metadata.

        Args:
            raw_text: The actual text the user wrote (opinion, story, answer).
            category: What kind of entry this is (e.g. "opinion", "habit", "decision").

        Returns:
            A dictionary representing one structured memory entry.
        """
        entry = {
            "id": str(uuid.uuid4()),
            "text": raw_text.strip(),
            "category": category,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self.collected_entries.append(entry)
        return entry

    def collect_batch(self, entries: list[dict]) -> list[dict]:
        """
        Takes multiple entries at once.
        Each item in `entries` should be a dict like:
        {"text": "...", "category": "..."}
        """
        results = []
        for item in entries:
            structured = self.collect_entry(
                raw_text=item.get("text", ""),
                category=item.get("category", "general"),
            )
            results.append(structured)
        return results

    def get_all_entries(self) -> list[dict]:
        """Returns everything collected so far."""
        return self.collected_entries


# Quick manual test — only runs if you execute this file directly
if __name__ == "__main__":
    agent = CollectorAgent()
    agent.collect_entry("I believe honesty matters more than comfort.", category="value")
    agent.collect_entry("I quit my stable job to start my own startup in 2025.", category="decision")
    agent.collect_entry("I'm scared of failing my GATE exam.", category="fear")
    agent.collect_entry("I want to crack a Google internship by Dec 2026.", category="goal")
    for e in agent.get_all_entries():
        print(e)