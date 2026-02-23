# 🤖⚖️ Automaton Auditor Swarm

> **Autonomous Governance at Scale** — A Deep LangGraph Multi-Agent System

## 🎯 Mission
Engineer a "Digital Courtroom" that automates quality assurance for AI-generated code.

## 🏛️ Architecture
- **Detectives:** Parallel agents collecting forensic evidence (Git, AST, PDF)
- **Judges:** Dialectical bench (Prosecutor, Defense, Tech Lead)
- **Chief Justice:** Synthesis engine with hardcoded override rules

## 🚀 Quick Start
1. `pip install -r requirements.txt`
2. `cp .env.example .env`
3. `python src/main.py`

## 📁 Project Structure
- `src/graph.py`: LangGraph StateGraph definition
- `src/state.py`: Pydantic AgentState schema
- `audit/`: Forensic evidence and peer feedback loop