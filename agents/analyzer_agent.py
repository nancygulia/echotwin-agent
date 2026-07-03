"""
Analyzer Agent
----------------
Job: Take structured entries from the Collector Agent and use Gemini
to extract personality traits, values, and behavioral patterns.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load the GEMINI_API_KEY from your .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class AnalyzerAgent:
    """Analyzes structured entries to extract personality traits using Gemini."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def analyze_entries(self, entries: list[dict]) -> dict:
        """
        Takes a list of structured entries (from CollectorAgent) and asks
        Gemini to extract personality traits, values, and patterns.

        Args:
            entries: List of dicts like {"text": ..., "category": ...}

        Returns:
            A dictionary with extracted traits, values, and a summary.
        """
        # Combine all entry texts into one block for the prompt
        combined_text = "\n".join(
            f"- ({e['category']}) {e['text']}" for e in entries
        )

        prompt = f"""
You are a personality analysis engine. Below are personal entries written
by a single person (their opinions, decisions, habits, fears, goals).

Entries:
{combined_text}

Analyze these entries and return ONLY a valid JSON object with this exact structure:
{{
  "core_values": ["value1", "value2", ...],
  "personality_traits": ["trait1", "trait2", ...],
  "decision_style": "a short description of how this person makes decisions",
  "communication_style": "a short description of how this person communicates",
  "summary": "a 2-3 sentence summary of who this person is"
}}

Return ONLY the JSON object, no extra text, no markdown formatting.
"""

        response = self.model.generate_content(prompt)
        raw_output = response.text.strip()

        # Clean up in case Gemini wraps the JSON in markdown code blocks
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`")
            raw_output = raw_output.replace("json", "", 1).strip()

        try:
            analysis = json.loads(raw_output)
        except json.JSONDecodeError:
            analysis = {"error": "Could not parse Gemini response", "raw": raw_output}

        return analysis


# Quick manual test
if __name__ == "__main__":
    from collector_agent import CollectorAgent

    collector = CollectorAgent()
    collector.collect_entry("I believe honesty matters more than comfort.", category="value")
    collector.collect_entry("I quit my stable job to start my own startup in 2025.", category="decision")
    collector.collect_entry("I'm scared of failing my GATE exam.", category="fear")
    collector.collect_entry("My goal is a Google internship by Dec 2026.", category="goal")
    collector.collect_entry("I love solving DSA problems at night.", category="habit")

    analyzer = AnalyzerAgent()
    result = analyzer.analyze_entries(collector.get_all_entries())

    print(json.dumps(result, indent=2))