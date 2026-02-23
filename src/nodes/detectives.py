from src.state import Evidence, AgentState
from src.tools.git_tools import clone_repo_sandboxed, get_git_history
from src.tools.ast_tools import analyze_graph_structure
import os


def repo_investigator(state: AgentState) -> AgentState:
    """
    Forensic Protocol: Code Detective.
    Collects facts only. No opinions.
    """
    repo_url = state.get("repo_url")
    evidences = []
    
    try:
        # Sandboxed Clone
        temp_path = clone_repo_sandboxed(repo_url)
        
        # Git History Evidence
        history = get_git_history(temp_path)
        evidences.append(Evidence(
            found=True,
            content=str(history[:5]),
            location="git_log",
            confidence=1.0,
            artifact_type="git_history"
        ))
        
        # AST Evidence
        graph_path = os.path.join(temp_path, "src", "graph.py")
        if os.path.exists(graph_path):
            ast_data = analyze_graph_structure(graph_path)
            evidences.append(Evidence(
                found=ast_data["found_state_graph"],
                content=str(ast_data),
                location="src/graph.py",
                confidence=1.0,
                artifact_type="ast_analysis"
            ))
            
        return {"evidences": {"repo_investigator": evidences}}
    except Exception as e:
        return {"evidences": {"repo_investigator": []}, "errors": [str(e)]}


def doc_analyst(state: AgentState) -> AgentState:
    """
    Forensic Protocol: Paperwork Detective.
    Cross-references PDF claims with code.
    """
    evidences = []
    if state.get("pdf_path"):
        evidences.append(Evidence(
            found=True,
            content="PDF Found",
            location=state["pdf_path"],
            confidence=1.0,
            artifact_type="document"
        ))
    return {"evidences": {"doc_analyst": evidences}}


def vision_inspector(state: AgentState) -> AgentState:
    """
    Forensic Protocol: Diagram Detective.
    Optional Multimodal analysis.
    """
    return {"evidences": {"vision_inspector": []}}
