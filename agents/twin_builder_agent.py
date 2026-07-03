"""
Twin Builder Agent
----------------
Job: Take the Analyzer's personality data + the original raw entries,
then store everything in ChromaDB (vector database) so the twin can
"remember" things and retrieve relevant memories later.
"""

import json
import os
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using Gemini's embedding model directly."""

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_document",
            )
            embeddings.append(result["embedding"])
        return embeddings


class TwinBuilderAgent:
    """Builds and stores the digital twin's personality + memory in ChromaDB."""

    def __init__(self, persist_directory: str = "data/chroma_db"):
        # ChromaDB client that saves data to disk (so it persists between runs)
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Our custom Gemini embedding function (converts text into vectors)
        self.embedding_function = GeminiEmbeddingFunction()

        # Collection = like a "table" in ChromaDB, holds all the twin's memories
        self.collection = self.client.get_or_create_collection(
            name="echotwin_memories",
            embedding_function=self.embedding_function,
        )

    def build_twin(self, entries: list[dict], analysis: dict) -> dict:
        """
        Stores raw entries as searchable memories, and saves the
        personality analysis as the twin's "core profile".

        Args:
            entries: List of structured entries from CollectorAgent.
            analysis: The personality JSON from AnalyzerAgent.

        Returns:
            A dictionary representing the complete twin profile.
        """
        # Store each entry as a separate memory in ChromaDB
        for entry in entries:
            self.collection.add(
                ids=[entry["id"]],
                documents=[entry["text"]],
                metadatas=[{
                    "category": entry["category"],
                    "timestamp": entry["timestamp"],
                }],
            )

        # Build the twin's core profile combining everything
        twin_profile = {
            "core_values": analysis.get("core_values", []),
            "personality_traits": analysis.get("personality_traits", []),
            "decision_style": analysis.get("decision_style", ""),
            "communication_style": analysis.get("communication_style", ""),
            "summary": analysis.get("summary", ""),
            "total_memories": len(entries),
        }

        # Save the profile to a local JSON file too (simple backup)
        os.makedirs("data", exist_ok=True)
        with open("data/twin_profile.json", "w") as f:
            json.dump(twin_profile, f, indent=2)

        return twin_profile

    def search_memories(self, query: str, n_results: int = 3) -> list[str]:
        """
        Searches stored memories for ones most relevant to a query.
        Used later by the Conversationalist Agent.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        return results["documents"][0] if results["documents"] else []


# Quick manual test
if __name__ == "__main__":
    from collector_agent import CollectorAgent
    from analyzer_agent import AnalyzerAgent

    collector = CollectorAgent()
    collector.collect_entry("I believe honesty matters more than comfort.", category="value")
    collector.collect_entry("I quit my stable job to start my own startup in 2025.", category="decision")
    collector.collect_entry("I'm scared of failing my GATE exam.", category="fear")
    collector.collect_entry("My goal is a Google internship by Dec 2026.", category="goal")
    collector.collect_entry("I love solving DSA problems at night.", category="habit")

    analyzer = AnalyzerAgent()
    analysis = analyzer.analyze_entries(collector.get_all_entries())

    builder = TwinBuilderAgent()
    profile = builder.build_twin(collector.get_all_entries(), analysis)

    print("Twin profile built:")
    print(json.dumps(profile, indent=2))

    print("\nSearching memories for 'career':")
    results = builder.search_memories("career")
    for r in results:
        print(" -", r)