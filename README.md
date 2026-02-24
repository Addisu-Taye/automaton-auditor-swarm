# 🤖⚖️ Automaton Auditor Swarm

> **Autonomous Governance at Scale** — A Deep LangGraph Multi-Agent System for Forensic Code Auditing

## 🎯 Mission

Engineer a "Digital Courtroom" that automates quality assurance for AI-generated code. When 1,000 agents generate features concurrently, humans cannot review every PR. This swarm scales governance through specialized forensic roles.

## 🏛️ Architecture: The Digital Courtroom
┌─────────────────────────────────────┐
│ LAYER 1: DETECTIVE SWARM (Facts) │
│ ├─ RepoInvestigator: AST + Git forensics
│ ├─ DocAnalyst: PDF cross-reference
│ └─ VisionInspector: Diagram analysis
└────────────┬────────────────────────
│ Fan-In: Evidence Aggregation
▼
┌─────────────────────────────────────┐
│ LAYER 2: JUDICIAL BENCH (Opinion) │
│ ├─ Prosecutor: "Trust No One" 🔍
│ ├─ Defense: "Spirit of the Law" ⚖️
│ └─ Tech Lead: "Does it work?" 🔧
└────────────┬────────────────────────
│ Fan-In: Conflict Resolution
▼
┌─────────────────────────────────────┐
│ LAYER 3: CHIEF JUSTICE (Verdict) │
│ ├─ Deterministic synthesis rules
│ ├─ Security override enforcement
│ └─ Executive-grade remediation plan
└─────────────────────────────────────┘

## ✨ Score 5 Compliance Features

| Feature | Implementation |
|---------|---------------|
| 🔐 **Pydantic State Schema** | `AgentState` with `operator.add`/`operator.ior` reducers |
| 🕵️ **AST-Based Forensics** | Python `ast` module parsing (not regex) |
| 🧱 **Sandboxed Tooling** | `tempfile.TemporaryDirectory()` for git clone |
| ⚡ **Parallel Orchestration** | Fan-out/fan-in via LangGraph `StateGraph` |
| 📋 **Structured Output** | `.with_structured_output(JudicialOpinion)` |
| 🔄 **Feedback Loop** | Self-audit + peer-audit workflow |

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/Addisu-Taye/automaton-auditor-swarm
cd automaton-auditor-swarm
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Add OPENAI_API_KEY, LANGCHAIN_API_KEY

# 3. Run the swarm against a target repo
python src/main.py

# 4. View audit output
cat audit/report_onpeer_generated/verdict.md
📁 Project Structure
automaton-auditor-swarm/
├── src/
│   ├── graph.py              # LangGraph StateGraph definition
│   ├── state.py              # Pydantic AgentState schema
│   ├── main.py               # Entry point
│   ├── nodes/
│   │   ├── detectives.py     # Repo/Doc/Vision investigative agents
│   │   ├── judges.py         # Prosecutor/Defense/TechLead personas
│   │   └── justice.py        # Chief Justice synthesis engine
│   └── tools/
│       ├── git_tools.py      # Sandboxed git operations
│       └── ast_tools.py      # AST-based code structure analysis
├── rubric/
│   └── week2_rubric.json     # Machine-readable "Constitution"
├── audit/
│   ├── report_onself_generated/   # Self-audit output
│   ├── report_onpeer_generated/   # Peer audit output  
│   ├── report_bypeer_received/    # Peer's audit of your work
│   └── langsmith_logs/            # Tracing evidence
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

🧪 Testing & Observability
LangSmith Tracing: Set LANGCHAIN_TRACING_V2=true to debug multi-agent chains
Pytest Suite: pytest tests/ validates state reducers and tool sandboxing
AST Unit Tests: Verifies LangGraphASTVisitor identifies StateGraph patterns
⚖️ License
MIT — Built for the 10 Academy TRP1 Challenge Week 2: "The Automaton Auditor"
📬 Contact
Author: Addisu Taye
Repository: https://github.com/Addisu-Taye/automaton-auditor-swarm
