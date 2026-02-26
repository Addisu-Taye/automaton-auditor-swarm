"""
src/graph.py

LangGraph StateGraph Orchestration - Complete Digital Courtroom
Production Module - Automaton Auditor Swarm v3.0.0

Architecture:
- Layer 1: Detectives (Parallel Fan-Out) → EvidenceAggregator (Fan-In)
- Layer 2: Judges (Parallel Fan-Out) → ChiefJustice (Fan-In) → END

Compliance:
- Protocol A.3: Graph Orchestration Architecture
- Protocol A.2: State Management Rigor with typed reducers
- Protocol B: Judicial Sentencing Guidelines integration
"""

from typing import Dict, List, Any, Optional, Callable
from langgraph.graph import StateGraph, END, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from src.state import AgentState, Evidence, JudicialOpinion, AuditReport
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
    get_all_judge_nodes
)
from src.nodes.justice import chief_justice_node, get_chief_justice_node


# =============================================================================
# CONDITIONAL EDGE FUNCTIONS
# =============================================================================

def route_after_detectives(state: AgentState) -> str:
    """
    Conditional routing after Detective layer.
    
    Routes to Judges if evidence collected successfully.
    Routes to error handler if critical evidence missing.
    """
    errors = state.get("errors", [])
    evidences = state.get("evidences", {})
    
    # Check for critical errors
    if any("clone failed" in e.lower() or "git" in e.lower() for e in errors):
        return "handle_missing_evidence"
    
    # Check if minimum evidence collected
    detective_evidence_count = sum(
        len(ev_list) for ev_list in evidences.values()
        if isinstance(ev_list, list)
    )
    
    if detective_evidence_count >= 3:  # Minimum threshold
        return "judges_parallel"
    else:
        return "handle_missing_evidence"


def route_after_judges(state: AgentState) -> str:
    """
    Conditional routing after Judicial layer.
    
    Routes to ChiefJustice if opinions collected.
    Routes to error handler if judges failed.
    """
    opinions = state.get("opinions", [])
    errors = state.get("errors", [])
    
    if len(opinions) >= 3:  # All three judges reported
        return "chief_justice"
    elif errors:
        return "handle_judge_error"
    else:
        return "chief_justice"  # Proceed with partial opinions


def handle_missing_evidence(state: AgentState) -> Dict[str, Any]:
    """
    Error handler for missing detective evidence.
    
    Generates fallback evidence and routes to judges with warning.
    """
    errors = state.get("errors", [])
    
    # Create fallback evidence
    fallback_evidence = Evidence(
        goal="error_handling",
        found=False,
        content=f"Detective layer encountered errors: {errors}",
        location="evidence_aggregator",
        rationale="Fallback evidence generated due to collection failure",
        confidence=0.3,
        artifact_type="error"
    )
    
    return {
        "evidences": {"error_handler": [fallback_evidence]},
        "errors": []  # Clear errors to allow continuation
    }


def handle_judge_error(state: AgentState) -> Dict[str, Any]:
    """
    Error handler for judge node failures.
    
    Generates fallback opinions and routes to ChiefJustice.
    """
    from src.state import JudicialOpinion
    
    errors = state.get("errors", [])
    
    # Create fallback opinions from each persona
    fallback_opinions = [
        JudicialOpinion(
            judge=persona,
            criterion_id="error",
            score=3,
            argument=f"Judge node encountered error: {errors}",
            cited_evidence=[]
        )
        for persona in ["Prosecutor", "Defense", "TechLead"]
    ]
    
    return {
        "opinions": fallback_opinions,
        "errors": []
    }


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

def build_full_auditor_graph() -> CompiledStateGraph:
    """
    Build and compile the complete Digital Courtroom StateGraph.
    
    Architecture Flow:
    ```
    START 
      │
      ▼
    [Detectives Parallel Fan-Out]
      ├── RepoInvestigator
      ├── DocAnalyst
      └── VisionInspector
      │
      ▼
    EvidenceAggregator (Fan-In)
      │
      ▼
    [Judges Parallel Fan-Out]
      ├── Prosecutor
      ├── Defense
      └── TechLead
      │
      ▼
    ChiefJustice (Synthesis Engine)
      │
      ▼
    END (AuditReport in state.final_report)
    ```
    
    Returns:
        Compiled LangGraph StateGraph ready for production execution
    """
    # Initialize StateGraph with typed AgentState
    graph = StateGraph(AgentState)
    
    # =========================================================================
    # LAYER 1: DETECTIVE NODES (Parallel Fan-Out)
    # =========================================================================
    
    graph.add_node("repo_investigator", repo_investigator)
    graph.add_node("doc_analyst", doc_analyst)
    graph.add_node("vision_inspector", vision_inspector)
    graph.add_node("evidence_aggregator", evidence_aggregator)
    
    # =========================================================================
    # LAYER 2: JUDICIAL NODES (Parallel Fan-Out)
    # =========================================================================
    
    judge_nodes = get_all_judge_nodes()
    for node_name, node_func in judge_nodes.items():
        graph.add_node(node_name, node_func)
    
    # =========================================================================
    # LAYER 3: SYNTHESIS ENGINE
    # =========================================================================
    
    graph.add_node("chief_justice", chief_justice_node)
    
    # =========================================================================
    # ERROR HANDLING NODES
    # =========================================================================
    
    graph.add_node("handle_missing_evidence", handle_missing_evidence)
    graph.add_node("handle_judge_error", handle_judge_error)
    
    # =========================================================================
    # GRAPH WIRING: DETECTIVE LAYER
    # =========================================================================
    
    # Entry point: Start with RepoInvestigator
    graph.add_edge(START, "repo_investigator")
    
    # Fan-out: RepoInvestigator triggers parallel DocAnalyst and VisionInspector
    graph.add_edge("repo_investigator", "doc_analyst")
    graph.add_edge("repo_investigator", "vision_inspector")
    
    # Fan-in: All detectives synchronize at EvidenceAggregator
    graph.add_edge("doc_analyst", "evidence_aggregator")
    graph.add_edge("vision_inspector", "evidence_aggregator")
    
    # =========================================================================
    # GRAPH WIRING: CONDITIONAL ROUTING AFTER DETECTIVES
    # =========================================================================
    
    graph.add_conditional_edges(
        "evidence_aggregator",
        route_after_detectives,
        {
            "judges_parallel": "prosecutor",  # Route to first judge (triggers parallel)
            "handle_missing_evidence": "handle_missing_evidence"
        }
    )
    
    # =========================================================================
    # GRAPH WIRING: JUDICIAL LAYER
    # =========================================================================
    
    # Fan-out: EvidenceAggregator triggers all three judges in parallel
    # Note: LangGraph executes nodes in parallel when multiple edges exist from same source
    graph.add_edge("handle_missing_evidence", "prosecutor")
    graph.add_edge("handle_missing_evidence", "defense")
    graph.add_edge("handle_missing_evidence", "tech_lead")
    
    graph.add_edge("prosecutor", "chief_justice")
    graph.add_edge("defense", "chief_justice")
    graph.add_edge("tech_lead", "chief_justice")
    
    # =========================================================================
    # GRAPH WIRING: CONDITIONAL ROUTING AFTER JUDGES
    # =========================================================================
    
    # All judges route to ChiefJustice (with error handling fallback)
    graph.add_conditional_edges(
        "chief_justice",
        lambda s: "end",  # Always proceed to end after synthesis
        {"end": END}
    )
    
    # =========================================================================
    # COMPILE WITH LANGSMITH TRACING
    # =========================================================================
    
    app = graph.compile()
    
    return app


# =============================================================================
# DETECTIVE-ONLY GRAPH (For Interim Testing)
# =============================================================================

def build_detective_graph() -> CompiledStateGraph:
    """
    Build Detective Layer only (for interim testing without Judges).
    
    Returns:
        Compiled StateGraph with Detectives → EvidenceAggregator → END
    """
    graph = StateGraph(AgentState)
    
    # Add detective nodes
    graph.add_node("repo_investigator", repo_investigator)
    graph.add_node("doc_analyst", doc_analyst)
    graph.add_node("vision_inspector", vision_inspector)
    graph.add_node("evidence_aggregator", evidence_aggregator)
    
    # Wire detectives
    graph.add_edge(START, "repo_investigator")
    graph.add_edge("repo_investigator", "doc_analyst")
    graph.add_edge("repo_investigator", "vision_inspector")
    graph.add_edge("doc_analyst", "evidence_aggregator")
    graph.add_edge("vision_inspector", "evidence_aggregator")
    graph.add_edge("evidence_aggregator", END)
    
    return graph.compile()


# =============================================================================
# EXECUTION HELPERS
# =============================================================================

def run_full_audit(
    repo_url: str,
    pdf_path: Optional[str] = None,
    rubric_dimensions: Optional[List[Dict]] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute full Digital Courtroom audit against target repository.
    
    Args:
        repo_url: GitHub repository URL to audit
        pdf_path: Optional path to architectural report PDF
        rubric_dimensions: Optional list of rubric dimensions from JSON
        output_path: Optional path to save Markdown report
        
    Returns:
        Dictionary containing final audit report and metadata
    """
    from dotenv import load_dotenv
    import os
    import json
    
    # Load environment variables
    load_dotenv()
    
    # Build graph
    app = build_full_auditor_graph()
    
    # Load rubric if path provided
    if not rubric_dimensions:
        rubric_path = os.path.join("rubric", "week2_rubric.json")
        if os.path.exists(rubric_path):
            with open(rubric_path, "r", encoding="utf-8") as f:
                rubric_data = json.load(f)
                rubric_dimensions = rubric_data.get("dimensions", [])
    
    # Initialize state
    initial_state: AgentState = {
        "repo_url": repo_url,
        "pdf_path": pdf_path or "",
        "rubric_dimensions": rubric_dimensions or [],
        "evidences": {},
        "opinions": [],
        "final_report": None,
        "errors": []
    }
    
    # Execute graph
    result = app.invoke(initial_state)
    
    # Save report to file if path provided
    if output_path and result.get("final_report"):
        from src.nodes.justice import _serialize_to_markdown
        markdown_content = _serialize_to_markdown(result["final_report"])
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
    
    return result


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """
    Production entry point for Automaton Auditor Swarm.
    
    Usage:
        python src/graph.py --repo-url <URL> --pdf-path <PATH> --mode full
    """
    import argparse
    from dotenv import load_dotenv
    import os
    import sys
    
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Automaton Auditor Swarm - Digital Courtroom"
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        required=True,
        help="GitHub repository URL to audit"
    )
    parser.add_argument(
        "--pdf-path",
        type=str,
        default=None,
        help="Path to architectural report PDF"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["detective", "full"],
        default="full",
        help="Execution mode: 'detective' (Interim) or 'full' (Final)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for Markdown report"
    )
    
    args = parser.parse_args()
    
    # Load rubric
    rubric_path = os.path.join("rubric", "week2_rubric.json")
    rubric_dimensions = []
    
    if os.path.exists(rubric_path):
        import json
        with open(rubric_path, "r", encoding="utf-8") as f:
            rubric_data = json.load(f)
            rubric_dimensions = rubric_data.get("dimensions", [])
        print(f"✅ Loaded {len(rubric_dimensions)} rubric dimensions")
    else:
        print("⚠️ Rubric not found - running without dimensional targeting")
    
    # Execute audit
    print(f"🚀 Starting Audit: {args.mode} mode")
    print(f"   Repository: {args.repo_url}")
    print(f"   PDF Report: {args.pdf_path or 'Not provided'}")
    print()
    
    try:
        if args.mode == "detective":
            from src.graph import run_detective_audit
            result = run_detective_audit(
                repo_url=args.repo_url,
                pdf_path=args.pdf_path,
                rubric_dimensions=rubric_dimensions
            )
        else:
            result = run_full_audit(
                repo_url=args.repo_url,
                pdf_path=args.pdf_path,
                rubric_dimensions=rubric_dimensions,
                output_path=args.output
            )
        
        # Output results
        print("✅ Audit Complete")
        
        if result.get("final_report"):
            print(f"   Overall Score: {result['final_report'].overall_score}/5.0")
            print(f"   Criteria Evaluated: {len(result['final_report'].criteria)}")
        
        print(f"   Errors: {len(result.get('errors', []))}")
        
        # Report output location
        if args.output:
            print(f"   Report saved: {args.output}")
        else:
            print("   Report available in result['final_report']")
        
    except Exception as e:
        print(f"❌ Audit Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())