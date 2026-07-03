"""
EchoTwin Agent — Main Entry Point
-----------------------------------
Ties all 5 agents together into one interactive experience.
Run this file to start building and talking to your digital twin.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from agents.collector_agent import CollectorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.twin_builder_agent import TwinBuilderAgent
from agents.conversationalist_agent import ConversationalistAgent
from agents.updater_agent import UpdaterAgent


def print_banner():
    print("\n" + "="*60)
    print("          ECHOTWIN AGENT — Your Digital Twin")
    print("="*60)
    print("Build a digital twin that thinks, speaks, and")
    print("responds exactly like YOU — powered by Google ADK")
    print("="*60 + "\n")


def setup_phase(collector, analyzer, builder):
    """Phase 1: Collect initial entries to build the twin."""
    print(" SETUP PHASE — Tell your twin about yourself")
    print("-"*50)
    print("Enter personal entries (opinions, decisions, habits,")
    print("goals, fears). Type 'done' when finished.\n")

    categories = ["value", "decision", "habit", "goal", "fear", "opinion", "general"]

    while True:
        text = input("Entry text (or 'done'): ").strip()
        if text.lower() == "done":
            break
        if not text:
            continue

        print(f"Categories: {', '.join(categories)}")
        category = input("Category: ").strip().lower()
        if category not in categories:
            category = "general"

        collector.collect_entry(text, category=category)
        print(f" Entry added!\n")

    entries = collector.get_all_entries()
    if not entries:
        print("No entries added. Using default examples...")
        collector.collect_entry("I believe honesty matters more than comfort.", category="value")
        collector.collect_entry("I quit my stable job to start my own startup.", category="decision")
        collector.collect_entry("My goal is to get a top tech internship.", category="goal")
        collector.collect_entry("I love solving problems late at night.", category="habit")
        entries = collector.get_all_entries()

    print(f"\n Analyzing {len(entries)} entries with Gemini...")
    analysis = analyzer.analyze_entries(entries)

    print(" Building your twin's personality model...")
    profile = builder.build_twin(entries, analysis)

    print("\n Twin built successfully!")
    print(f"   Core values: {', '.join(profile.get('core_values', []))}")
    print(f"   Traits: {', '.join(profile.get('personality_traits', []))}")
    print(f"   Total memories: {profile.get('total_memories', 0)}")
    return profile


def chat_phase(conversationalist, updater, collector):
    """Phase 2: Interactive chat with the digital twin."""
    print("\n" + "="*60)
    print("💬 CHAT PHASE — Talk to your digital twin")
    print("="*60)
    print("Commands:")
    print("  'add' — add a new entry and update the twin")
    print("  'profile' — view current twin profile")
    print("  'quit' — exit EchoTwin")
    print("-"*50 + "\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\n Goodbye! Your twin's memories are saved.")
            break

        elif user_input.lower() == "profile":
            profile = updater.get_current_profile()
            print("\n Current Twin Profile:")
            print(f"   Values: {', '.join(profile.get('core_values', []))}")
            print(f"   Traits: {', '.join(profile.get('personality_traits', []))}")
            print(f"   Summary: {profile.get('summary', '')}\n")

        elif user_input.lower() == "add":
            text = input("New entry text: ").strip()
            category = input("Category: ").strip().lower() or "general"
            print(" Updating twin...")
            updater.add_new_entry(collector=collector, raw_text=text, category=category)
            print(" Twin updated!\n")

        else:
            print("\n Twin: ", end="")
            answer = conversationalist.ask_twin(user_input)
            print(answer + "\n")


def main():
    print_banner()

    # Initialize all agents
    collector = CollectorAgent()
    analyzer = AnalyzerAgent()
    builder = TwinBuilderAgent()
    conversationalist = ConversationalistAgent(twin_builder=builder)
    updater = UpdaterAgent(analyzer=analyzer, twin_builder=builder)

    # Phase 1: Setup
    setup_phase(collector, analyzer, builder)

    # Phase 2: Chat
    chat_phase(conversationalist, updater, collector)


if __name__ == "__main__":
    main()