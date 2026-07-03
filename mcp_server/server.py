"""
MCP Server for EchoTwin Agent
------------------------------
Exposes EchoTwin's core functions as MCP tools so external agents
and systems can interact with the digital twin in a standardized way.
This is required by the Kaggle AI Agents competition.
"""

import json
import sys
import os

# Add parent directory to path so we can import our agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from agents.collector_agent import CollectorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.twin_builder_agent import TwinBuilderAgent
from agents.conversationalist_agent import ConversationalistAgent
from agents.updater_agent import UpdaterAgent

# Initialize all agents
collector = CollectorAgent()
analyzer = AnalyzerAgent()
builder = TwinBuilderAgent()
conversationalist = ConversationalistAgent(twin_builder=builder)
updater = UpdaterAgent(analyzer=analyzer, twin_builder=builder)

# Create the MCP server
app = Server("echotwin-mcp-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Lists all tools exposed by EchoTwin's MCP server."""
    return [
        types.Tool(
            name="collect_entry",
            description="Add a new personal entry (opinion, decision, habit, goal, fear) to build the digital twin.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The personal text entry to add."
                    },
                    "category": {
                        "type": "string",
                        "description": "Category of the entry: value, decision, habit, goal, fear, opinion, general.",
                        "default": "general"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="ask_twin",
            description="Ask the digital twin a question. It responds as the real person would, based on their personality and memories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the digital twin."
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="search_memories",
            description="Search the twin's stored memories for entries relevant to a topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic or keyword to search memories for."
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of memories to return (default 3).",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_twin_profile",
            description="Get the current personality profile of the digital twin.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="update_twin",
            description="Add a new entry and automatically update the twin's personality profile.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The new entry text."
                    },
                    "category": {
                        "type": "string",
                        "description": "Category of the entry.",
                        "default": "general"
                    }
                },
                "required": ["text"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handles tool calls from external agents or systems."""

    if name == "collect_entry":
        entry = collector.collect_entry(
            raw_text=arguments["text"],
            category=arguments.get("category", "general")
        )
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": True, "entry": entry})
        )]

    elif name == "ask_twin":
        # Load latest profile before answering
        conversationalist.twin_profile = conversationalist._load_twin_profile()
        answer = conversationalist.ask_twin(arguments["question"])
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": True, "answer": answer})
        )]

    elif name == "search_memories":
        memories = builder.search_memories(
            query=arguments["query"],
            n_results=arguments.get("n_results", 3)
        )
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": True, "memories": memories})
        )]

    elif name == "get_twin_profile":
        profile = updater.get_current_profile()
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": True, "profile": profile})
        )]

    elif name == "update_twin":
        updated_profile = updater.add_new_entry(
            collector=collector,
            raw_text=arguments["text"],
            category=arguments.get("category", "general")
        )
        return [types.TextContent(
            type="text",
            text=json.dumps({"success": True, "updated_profile": updated_profile})
        )]

    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


async def main():
    """Runs the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())