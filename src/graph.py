from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator, doc_analyst, vision_inspector
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
from src.nodes.justice import chief_justice_node


def build_auditor_graph():
    """
    Architecture: Hierarchical State Graph.
    Pattern: Fan-Out (Detectives) -> Fan-In -> Fan-Out (Judges) -> Fan-In (Justice)
    """
    graph = StateGraph(AgentState)
    
    # Layer 1: Detectives (Parallel)
    graph.add_node("repo_investigator", repo_investigator)
    graph.add_node("doc_analyst", doc_analyst)
    graph.add_node("vision_inspector", vision_inspector)
    
    # Layer 2: Judges (Parallel)
    graph.add_node("prosecutor", prosecutor_node)
    graph.add_node("defense", defense_node)
    graph.add_node("tech_lead", tech_lead_node)
    
    # Layer 3: Justice
    graph.add_node("chief_justice", chief_justice_node)
    
    # Entry Point
    graph.set_entry_point("repo_investigator")
    
    # Wiring Detectives (Parallel Fan-Out)
    graph.add_edge("repo_investigator", "doc_analyst")
    graph.add_edge("repo_investigator", "vision_inspector")
    
    # Synchronization (Fan-In to Judges)
    graph.add_edge("doc_analyst", "prosecutor")
    graph.add_edge("doc_analyst", "defense")
    graph.add_edge("doc_analyst", "tech_lead")
    
    # Wiring Judges to Justice
    graph.add_edge("prosecutor", "chief_justice")
    graph.add_edge("defense", "chief_justice")
    graph.add_edge("tech_lead", "chief_justice")
    
    # Exit
    graph.add_edge("chief_justice", END)
    
    return graph.compile()
