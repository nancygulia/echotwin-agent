"""
Conversationalist Agent
----------------
Job: Let the user talk TO their digital twin. Takes a question,
retrieves relevant memories from ChromaDB (via TwinBuilderAgent),
and uses Gemini to answer AS the twin — based on real personality
traits and past entries, not generic AI responses.
"""

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class ConversationalistAgent:
    """Lets the user have a conversation with their digital twin."""

    def __init__(self, twin_builder, model_name: str = "gemini-2.5-flash"):
        """
        Args:
            twin_builder: An instance of TwinBuilderAgent (so we can search memories).
            model_name: Which Gemini model to use for generating responses.
        """
        self.twin_builder = twin_builder
        self.model = genai.GenerativeModel(model_name)
        self.twin_profile = self._load_twin_profile()
        self.conversation_history = []

    def _load_twin_profile(self) -> dict:
        """Loads the twin's personality profile from the JSON file saved by TwinBuilderAgent."""
        profile_path = "data/twin_profile.json"
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                return json.load(f)
        return {}

    def ask_twin(self, question: str) -> str:
        """
        Asks the digital twin a question and gets a response that reflects
        the real person's personality, values, and past experiences.

        Args:
            question: The question to ask the twin.

        Returns:
            The twin's response as a string.
        """
        # Step 1: Search for relevant memories related to this question
        relevant_memories = self.twin_builder.search_memories(question, n_results=3)
        memories_text = "\n".join(f"- {m}" for m in relevant_memories) if relevant_memories else "No specific memories found."

        # Step 2: Build a prompt that makes Gemini respond AS the twin
        prompt = f"""
You are a digital twin of a real person. You must respond AS this person,
using their personality, values, and real memories below. Stay completely
in character. Do not say you are an AI.

PERSONALITY PROFILE:
- Core values: {', '.join(self.twin_profile.get('core_values', []))}
- Personality traits: {', '.join(self.twin_profile.get('personality_traits', []))}
- Decision style: {self.twin_profile.get('decision_style', '')}
- Communication style: {self.twin_profile.get('communication_style', '')}
- Summary: {self.twin_profile.get('summary', '')}

RELEVANT MEMORIES (real things this person has said/decided):
{memories_text}

QUESTION FROM THE USER:
{question}

Respond as this person would, in first person ("I think...", "I believe...").
Keep the response natural, conversational, and true to their personality
and communication style. 2-4 sentences is ideal.
"""

        response = self.model.generate_content(prompt)
        answer = response.text.strip()

        # Step 3: Save this exchange to conversation history
        self.conversation_history.append({"question": question, "answer": answer})

        return answer

    def get_conversation_history(self) -> list[dict]:
        """Returns the full conversation history so far."""
        return self.conversation_history


# Quick manual test
if __name__ == "__main__":
    from collector_agent import CollectorAgent
    from analyzer_agent import AnalyzerAgent
    from twin_builder_agent import TwinBuilderAgent

    collector = CollectorAgent()
    collector.collect_entry("I believe honesty matters more than comfort.", category="value")
    collector.collect_entry("I quit my stable job to start my own startup in 2025.", category="decision")
    collector.collect_entry("I'm scared of failing my GATE exam.", category="fear")
    collector.collect_entry("My goal is a Google internship by Dec 2026.", category="goal")
    collector.collect_entry("I love solving DSA problems at night.", category="habit")

    analyzer = AnalyzerAgent()
    analysis = analyzer.analyze_entries(collector.get_all_entries())

    builder = TwinBuilderAgent()
    builder.build_twin(collector.get_all_entries(), analysis)

    conversationalist = ConversationalistAgent(twin_builder=builder)

    print("Asking the twin: 'Should I take a risky career decision?'\n")
    answer = conversationalist.ask_twin("Should I take a risky career decision?")
    print("Twin says:", answer)

    print("\nAsking the twin: 'What matters most to you?'\n")
    answer2 = conversationalist.ask_twin("What matters most to you?")
    print("Twin says:", answer2)