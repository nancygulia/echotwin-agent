\# EchoTwin Agent — Your Digital Twin



What if AI could think like you, speak like you, and remember what matters to you?



EchoTwin is my answer to that question. It's a multi-agent system that learns who you are from your own words — your opinions, decisions, habits, fears, and goals — and builds a living digital twin you can actually have a conversation with.



Built for the Kaggle AI Agents: Intensive Vibe Coding Capstone Project 2026, powered by Google ADK + Gemini.



\---



\## The Idea



I kept thinking — what's the most personal thing an AI agent could do? Not search the web. Not summarize documents. But actually \*become\* someone. Learn their values. Understand how they think. And respond the way they would.



That's EchoTwin. You feed it real things about yourself. It builds a model of your personality. Then you — or anyone — can talk to your twin and get answers that sound, feel, and think like you.



\---



\## How It Works



EchoTwin has 5 specialized agents working together:



\*\*1. Collector Agent\*\*

Takes anything you write about yourself — opinions, decisions, habits, goals, fears — and structures it into clean memory entries with categories and timestamps.



\*\*2. Analyzer Agent\*\*

Sends all your entries to Gemini and asks it to extract your core values, personality traits, decision-making style, and communication style. Returns structured JSON.



\*\*3. Twin Builder Agent\*\*

Converts every memory into a vector embedding using Gemini's embedding model and stores them in ChromaDB. Also saves your personality profile as a JSON file. This is what gives your twin its "memory."



\*\*4. Conversationalist Agent\*\*

When you ask your twin a question, this agent searches ChromaDB for the most relevant memories, combines them with your personality profile, and prompts Gemini to respond in first person — as you.



\*\*5. Updater Agent\*\*

Life changes. So does your twin. Add a new entry anytime and the Updater re-analyzes everything and refreshes your personality profile automatically.



All 5 agents are connected through an MCP Server that exposes them as callable tools to any external system.



\---



\## Architecture





User Input

↓

Orchestrator (Google ADK)

↓

┌─────────────────────────────────────────┐

│  Collector     │  Analyzer    │ Twin Builder  │

│    Agent       │   Agent      │    Agent      │

├─────────────────────────────────────────┤

│  Conversa-     │  Updater     │               │

│  tionalist     │   Agent      │               │

└─────────────────────────────────────────┘

↓

MCP Server

↓

ChromaDB (memory) + Gemini API (brain)

↓

Deployed via Antigravity (agy)

\---



\## The 5 Agents



| Agent | Job |

|       |     |

| \*\*Collector Agent\*\* | Takes raw personal input and structures it into memory entries with category + timestamp |

| \*\*Analyzer Agent\*\* | Uses Gemini to extract personality traits, values, decision style from entries |

| \*\*Twin Builder Agent\*\* | Stores entries in ChromaDB as embeddings, builds the core personality profile |

| \*\*Conversationalist Agent\*\* | Searches memories, responds AS the twin using the real person's personality |

| \*\*Updater Agent\*\* | Adds new entries and re-analyzes to keep the twin evolving over time |



\---



\## Key Concepts Demonstrated



| Kaggle Requirement | How EchoTwin Demonstrates It |

|---|---|

| Agent / Multi-agent system (ADK) | 5 specialized agents orchestrated by Google ADK |

| MCP Server | Full MCP server exposing 5 tools: collect, ask, search, profile, update |

| Security features | API keys in `.env`, `.gitignore` protection, no hardcoded secrets |

| Agent skills | Semantic memory search, personality analysis, twin conversation |

| Deployability | Deployed via Antigravity CLI |



\---



\## Setup



\### 1. Clone

```bash

git clone https://github.com/nancygulia/echotwin-agent.git

cd echotwin-agent

```



\### 2. Virtual environment

```bash

python -m venv venv

venv\\Scripts\\activate

```



\### 3. Install dependencies

```bash

pip install -r requirements.txt

```



\### 4. Add your Gemini API key

Create a `.env` file:

GEMINI\_API\_KEY=your\_key\_here

Get a free key at https://aistudio.google.com/apikey



\### 5. Run

```bash

python main.py

```



\---



\## Usage



\*\*Setup phase\*\* — tell your twin about yourself:

\- Enter personal entries one by one

\- Choose a category: value, decision, habit, goal, fear, opinion

\- Type `done` when finished

\- EchoTwin analyzes and builds your twin automatically



\*\*Chat phase\*\* — talk to your twin:

\- Ask it anything

\- Type `add` to add new memories

\- Type `profile` to see your personality profile

\- Type `quit` to exit (everything is saved)



\---



\## Tech Stack



\- \*\*Google ADK\*\* — multi-agent orchestration

\- \*\*Gemini 2.5 Flash\*\* — personality analysis + twin responses

\- \*\*Gemini Embedding\*\* — semantic memory search

\- \*\*ChromaDB\*\* — local vector database for persistent memory

\- \*\*MCP\*\* — Model Context Protocol server

\- \*\*FastAPI + Uvicorn\*\* — web API layer

\- \*\*Python Dotenv\*\* — secure key management

\- \*\*Antigravity CLI\*\* — deployment



\---



\## Project Structure

echotwin-agent/

├── agents/

│   ├── collector\_agent.py

│   ├── analyzer\_agent.py

│   ├── twin\_builder\_agent.py

│   ├── conversationalist\_agent.py

│   └── updater\_agent.py

├── mcp\_server/

│   └── server.py

├── data/                  # auto-created by ChromaDB

├── main.py

├── requirements.txt

├── .env                   # not committed

├── .gitignore

└── README.md



\---



\## Security



\- API keys live only in `.env` — never in code

\- `.gitignore` ensures `.env` and `data/` never reach GitHub

\- No credentials anywhere in the codebase



\---



\## Author



Nancy Gulia

B.Tech Computer Science (IoT), 6th Semester

Kaggle AI Agents Capstone 2026



