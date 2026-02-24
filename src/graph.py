"""
src/graph.py

LangGraph StateGraph Orchestration - Detective Layer
Production Module - Automaton Auditor Swarm v3.0.0

Architecture:
- Parallel Fan-Out: Detectives run concurrently
- Fan-In: EvidenceAggregator synchronizes before Judicial layer
- Typed State: Pydantic models with operator reducers

Compliance:
- Protocol A.1: Git Forensic Analysis workflow
- Protocol A.2: State Management Rigor
- Protocol A.3: Graph Orchestration Architecture
"""

from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from src.state import AgentState, Evidence, JudicialOpinion, AuditReport
from src.nodes.detectives import (
    repo_investigator,
    doc_analyst,
    vision_inspector,
    evidence_aggregator
)


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

def build_detective_graph() -> CompiledStateGraph:
    """
    Build and compile the Detective Layer StateGraph.
    
    Architecture:
    ```
    START → [RepoInvestigator || DocAnalyst || VisionInspector] 
            → EvidenceAggregator → END
    ```
    
    Returns:
        Compiled LangGraph StateGraph ready for execution
    """
    # Initialize StateGraph with typed AgentState
    graph = StateGraph(AgentState)
    
    # =========================================================================
    # LAYER 1: DETECTIVE NODES (Parallel Fan-Out)
    # =========================================================================
    
    # RepoInvestigator: Code repository forensic analysis
    graph.add_node("repo_investigator", repo_investigator)
    
    # DocAnalyst: PDF report ingestion and cross-reference
    graph.add_node("doc_analyst", doc_analyst)
    
    # VisionInspector: Architectural diagram analysis
    graph.add_node("vision_inspector", vision_inspector)
    
    # EvidenceAggregator: Synchronization node (Fan-In)
    graph.add_node("evidence_aggregator", evidence_aggregator)
    
    # =========================================================================
    # GRAPH WIRING (Parallel Execution)
    # =========================================================================
    
    # Entry Point: All detectives start in parallel
    graph.set_entry_point("repo_investigator")
    
    # Fan-Out: Detectives run concurrently
    # Note: LangGraph executes nodes in parallel when multiple edges exist
    graph.add_edge("repo_investigator", "doc_analyst")
    graph.add_edge("repo_investigator", "vision_inspector")
    
    # Fan-In: All detectives synchronize at EvidenceAggregator
    graph.add_edge("doc_analyst", "evidence_aggregator")
    graph.add_edge("vision_inspector", "evidence_aggregator")
    
    # Exit: After aggregation, graph completes (Judicial layer not yet wired)
    graph.add_edge("evidence_aggregator", END)
    
    # Compile with LangSmith tracing enabled
    app = graph.compile()
    
    return app


# =============================================================================
# FULL GRAPH (Detectives + Judicial Layer - For Final Submission)
# =============================================================================

def build_full_auditor_graph() -> CompiledStateGraph:
    """
    Build and compile the complete Digital Courtroom StateGraph.
    
    Architecture:
    ```
    START → [Detectives Parallel] → EvidenceAggregator 
            → [Judges Parallel] → ChiefJustice → END
    ```
    
    Note: Requires judges.py and justice.py (Final Submission)
    
    Returns:
        Compiled LangGraph StateGraph ready for execution
    """
    # Import judicial layer (will fail until judges.py/justice.py exist)
    try:
        from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
        from src.nodes.justice import chief_justice_node
        judicial_layer_available = True
    except ImportError:
        judicial_layer_available = False
    
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
    # LAYER 2: JUDICIAL NODES (Parallel Fan-Out) - If Available
    # =========================================================================
    
    if judicial_layer_available:
        graph.add_node("prosecutor", prosecutor_node)
        graph.add_node("defense", defense_node)
        graph.add_node("tech_lead", tech_lead_node)
        graph.add_node("chief_justice", chief_justice_node)
    
    # =========================================================================
    # GRAPH WIRING
    # =========================================================================
    
    # Entry Point
    graph.set_entry_point("repo_investigator")
    
    # Detective Fan-Out
    graph.add_edge("repo_investigator", "doc_analyst")
    graph.add_edge("repo_investigator", "vision_inspector")
    
    # Detective Fan-In
    graph.add_edge("doc_analyst", "evidence_aggregator")
    graph.add_edge("vision_inspector", "evidence_aggregator")
    
    if judicial_layer_available:
        # Judicial Fan-Out
        graph.add_edge("evidence_aggregator", "prosecutor")
        graph.add_edge("evidence_aggregator", "defense")
        graph.add_edge("evidence_aggregator", "tech_lead")
        
        # Judicial Fan-In
        graph.add_edge("prosecutor", "chief_justice")
        graph.add_edge("defense", "chief_justice")
        graph.add_edge("tech_lead", "chief_justice")
        
        # Exit
        graph.add_edge("chief_justice", END)
    else:
        # Exit (Detective layer only - Interim Submission)
        graph.add_edge("evidence_aggregator", END)
    
    # Compile with LangSmith tracing enabled
    app = graph.compile()
    
    return app


# =============================================================================
# EXECUTION HELPERS
# =============================================================================

def run_detective_audit(
    repo_url: str,
    pdf_path: Optional[str] = None,
    rubric_dimensions: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Execute Detective Layer audit against target repository.
    
    Args:
        repo_url: GitHub repository URL to audit
        pdf_path: Optional path to architectural report PDF
        rubric_dimensions: Optional list of rubric dimensions from JSON
        
    Returns:
        Dictionary containing aggregated evidence and metadata
    """
    # Build graph
    app = build_detective_graph()
    
    # Initialize state
    initial_state: AgentState = {
        "repo_url": repo_url,
        "pdf_path": pdf_path or "",
        "rubric_dimensions": rubric_dimensions or [],
        "evidences": {},
        "opinions": [],
        "final_report": "",
        "errors": []
    }
    
    # Execute graph
    result = app.invoke(initial_state)
    
    return result


def run_full_audit(
    repo_url: str,
    pdf_path: Optional[str] = None,
    rubric_dimensions: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Execute full Digital Courtroom audit (Detectives + Judges + Justice).
    
    Args:
        repo_url: GitHub repository URL to audit
        pdf_path: Optional path to architectural report PDF
        rubric_dimensions: Optional list of rubric dimensions from JSON
        
    Returns:
        Dictionary containing final audit report
    """
    # Build graph
    app = build_full_auditor_graph()
    
    # Initialize state
    initial_state: AgentState = {
        "repo_url": repo_url,
        "pdf_path": pdf_path or "",
        "rubric_dimensions": rubric_dimensions or [],
        "evidences": {},
        "opinions": [],
        "final_report": "",
        "errors": []
    }
    
    # Execute graph
    result = app.invoke(initial_state)
    
    return result


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Production entry point for Automaton Auditor Swarm.
    
    Usage:
        python src/graph.py --repo-url <URL> --pdf-path <PATH>
    """
    import argparse
    from dotenv import load_dotenv
    import os
    
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
        default="detective",
        help="Execution mode: 'detective' (Interim) or 'full' (Final)"
    )
    
    args = parser.parse_args()
    
    # Load rubric (if available)
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
            result = run_detective_audit(
                repo_url=args.repo_url,
                pdf_path=args.pdf_path,
                rubric_dimensions=rubric_dimensions
            )
        else:
            result = run_full_audit(
                repo_url=args.repo_url,
                pdf_path=args.pdf_path,
                rubric_dimensions=rubric_dimensions
            )
        
        # Output results
        print("✅ Audit Complete")
        print(f"   Evidences Collected: {len(result.get('evidences', {}))} detectives")
        print(f"   Errors: {len(result.get('errors', []))}")
        
        # Save report to file
        output_dir = "audit/report_onself_generated"
        os.makedirs(output_dir, exist_ok=True)
        
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"audit_{timestamp}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"   Report saved: {output_path}")
        
    except Exception as e:
        print(f"❌ Audit Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())