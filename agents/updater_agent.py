"""
Updater Agent
----------------
Job: Keep the digital twin evolving over time. When new entries are
added, re-analyze the full set and update the twin's personality
profile so it stays accurate to who the person is NOW.
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()


class UpdaterAgent:
    """Keeps the digital twin's personality profile up to date."""

    def __init__(self, analyzer, twin_builder):
        """
        Args:
            analyzer: An instance of AnalyzerAgent.
            twin_builder: An instance of TwinBuilderAgent.
        """
        self.analyzer = analyzer
        self.twin_builder = twin_builder

    def add_new_entry(self, collector, raw_text: str, category: str = "general") -> dict:
        """
        Adds a single new entry and updates the twin's profile.

        Args:
            collector: An instance of CollectorAgent.
            raw_text: The new text entry to add.
            category: The category of the new entry.

        Returns:
            The updated twin profile.
        """
        # Step 1: Add the new entry to the collector
        new_entry = collector.collect_entry(raw_text, category=category)
        print(f"New entry added: [{category}] {raw_text}")

        # Step 2: Re-analyze ALL entries including the new one
        all_entries = collector.get_all_entries()
        print(f"Re-analyzing {len(all_entries)} total entries...")
        updated_analysis = self.analyzer.analyze_entries(all_entries)

        # Step 3: Store the new entry in ChromaDB
        self.twin_builder.collection.add(
            ids=[new_entry["id"]],
            documents=[new_entry["text"]],
            metadatas=[{
                "category": new_entry["category"],
                "timestamp": new_entry["timestamp"],
            }],
        )

        # Step 4: Rebuild and save the updated twin profile
        updated_profile = {
            "core_values": updated_analysis.get("core_values", []),
            "personality_traits": updated_analysis.get("personality_traits", []),
            "decision_style": updated_analysis.get("decision_style", ""),
            "communication_style": updated_analysis.get("communication_style", ""),
            "summary": updated_analysis.get("summary", ""),
            "total_memories": len(all_entries),
        }

        os.makedirs("data", exist_ok=True)
        with open("data/twin_profile.json", "w") as f:
            json.dump(updated_profile, f, indent=2)

        print("Twin profile updated successfully!")
        return updated_profile

    def get_current_profile(self) -> dict:
        """Loads and returns the current saved twin profile."""
        profile_path = "data/twin_profile.json"
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                return json.load(f)
        return {}


# Quick manual test
if __name__ == "__main__":
    from collector_agent import CollectorAgent
    from analyzer_agent import AnalyzerAgent
    from twin_builder_agent import TwinBuilderAgent

    # Set up all agents
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

    # Now test the updater with a brand new entry
    updater = UpdaterAgent(analyzer=analyzer, twin_builder=builder)

    print("\n--- Adding a new entry ---")
    updated = updater.add_new_entry(
        collector=collector,
        raw_text="I recently started meditating every morning to stay focused.",
        category="habit"
    )

    print("\nUpdated twin profile:")
    print(json.dumps(updated, indent=2))