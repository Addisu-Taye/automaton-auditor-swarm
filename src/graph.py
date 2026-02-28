"""
src/graph.py - Main Graph Orchestration for Automaton Auditor Swarm
Production Module v3.0.0
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# LangGraph imports
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# Local imports
from src.state import AgentState, Evidence, JudicialOpinion, AuditReport, create_initial_state
from src.nodes.detectives import (
    repo_investigator,
    doc_analyst,
    vision_inspector,
    evidence_aggregator
)
from src.nodes.judges import (
    prosecutor_node,
    defense_node,
    tech_lead_node,
    judge_aggregator_node
)
from src.nodes.justice import chief_justice_node
from src.tools.repo_tools import load_rubric


def build_full_auditor_graph() -> StateGraph:
    """Build the complete Automaton Auditor StateGraph."""
    builder = StateGraph(AgentState)
    
    # Detective Layer (Parallel Fan-Out)
    builder.add_node("repo_investigator", repo_investigator)
    builder.add_node("doc_analyst", doc_analyst)
    builder.add_node("vision_inspector", vision_inspector)
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    builder.add_edge(START, "vision_inspector")
    
    # Evidence Aggregation (Fan-In)
    builder.add_node("evidence_aggregator", evidence_aggregator)
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    builder.add_edge("vision_inspector", "evidence_aggregator")
    
    # Judicial Layer (Parallel Fan-Out)
    builder.add_node("prosecutor", prosecutor_node)
    builder.add_node("defense", defense_node)
    builder.add_node("techlead", tech_lead_node)
    builder.add_edge("evidence_aggregator", "prosecutor")
    builder.add_edge("evidence_aggregator", "defense")
    builder.add_edge("evidence_aggregator", "techlead")
    
    # Judge Aggregation (Fan-In)
    builder.add_node("judge_aggregator", judge_aggregator_node)
    builder.add_edge("prosecutor", "judge_aggregator")
    builder.add_edge("defense", "judge_aggregator")
    builder.add_edge("techlead", "judge_aggregator")
    
    # Chief Justice Synthesis
    builder.add_node("chief_justice", chief_justice_node)
    builder.add_edge("judge_aggregator", "chief_justice")
    builder.add_edge("chief_justice", END)
    
    # Compile with memory saver
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


def run_full_audit(
    repo_url: str,
    pdf_path: Optional[str] = None,
    rubric_dimensions: Optional[List[Dict]] = None,
    mode: str = "full",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Execute a complete audit using the Automaton Auditor Swarm."""
    
    # Load default rubric if not provided
    if rubric_dimensions is None:
        rubric_path = Path(__file__).parent.parent / "rubric" / "week2_rubric.json"
        rubric_dimensions = load_rubric(str(rubric_path))
    
    # Create initial state
    initial_state = create_initial_state(
        repo_url=repo_url,
        pdf_path=pdf_path,
        rubric_dimensions=rubric_dimensions,
        mode=mode,
        output_path=output_path
    )
    
    # Build and compile graph
    graph = build_full_auditor_graph()
    
    # Execute graph
    config = {"configurable": {"thread_id": f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"}}
    
    # Invoke graph - tracing auto-enabled via LANGCHAIN_TRACING_V2 env var
    result = graph.invoke(initial_state, config=config)
    
    # Save report to file if output_path specified
    if output_path and result.get("report_markdown"):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["report_markdown"])
    
    return result


def main():
    """Command-line interface for running audits."""
    parser = argparse.ArgumentParser(
        description="Automaton Auditor Swarm - Autonomous Code Auditing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--repo-url", "-r", required=True, help="GitHub repository URL to audit")
    parser.add_argument("--pdf-path", "-p", default=None, help="Path to architectural report PDF")
    parser.add_argument("--rubric-path", default=None, help="Path to custom rubric JSON")
    parser.add_argument("--mode", "-m", choices=["detective", "full"], default="full", help="Audit mode")
    parser.add_argument("--output", "-o", default=None, help="Path to save final markdown report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Load rubric
    if args.rubric_path:
        rubric_dimensions = load_rubric(args.rubric_path)
    else:
        rubric_path = Path(__file__).parent.parent / "rubric" / "week2_rubric.json"
        rubric_dimensions = load_rubric(str(rubric_path))
    
    print(f"✅ Loaded {len(rubric_dimensions)} rubric dimensions")
    print(f"🚀 Starting Audit: {args.mode} mode")
    print(f"   Repository: {args.repo_url}")
    if args.pdf_path:
        print(f"   PDF Report: {args.pdf_path}")
    
    try:
        result = run_full_audit(
            repo_url=args.repo_url,
            pdf_path=args.pdf_path,
            rubric_dimensions=rubric_dimensions,
            mode=args.mode,
            output_path=args.output
        )
        
        final_report = result.get("final_report", {})
        print(f"\n✅ Audit Complete")
        print(f"   Overall Score: {final_report.get('overall_score', 'N/A')}/5.0")
        print(f"   Criteria Evaluated: {final_report.get('criteria_evaluated', 0)}")
        
        criteria = final_report.get("criteria", [])
        excellent = sum(1 for c in criteria if c.get("final_score", 0) >= 5)
        good = sum(1 for c in criteria if 3 <= c.get("final_score", 0) < 5)
        needs_work = sum(1 for c in criteria if c.get("final_score", 0) < 3)
        print(f"   Excellent (5): {excellent}, Good (3-4): {good}, Needs Improvement (1-2): {needs_work}")
        
        if args.output:
            print(f"   Report saved: {args.output}")
        
        overall = final_report.get("overall_score", 0)
        if overall >= 4:
            sys.exit(0)
        elif overall >= 3:
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"\n❌ Audit Failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()