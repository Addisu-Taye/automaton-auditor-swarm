"""
src/tools/repo_tools.py

Forensic Tools for Repository Analysis
Production Module - Automaton Auditor Swarm v3.0.0

Capabilities:
- Sandboxed repository cloning (tempfile isolation)
- Git history extraction with commit metadata
- AST-based LangGraph structure verification
- Security-compliant system interactions

Compliance:
- Protocol A.4: Safe Tool Engineering
- Protocol A.2: State Management Rigor verification
- Protocol A.1: Git Forensic Analysis
"""

import os
import tempfile
import ast
from typing import List, Dict, Any
from git import Repo


# =============================================================================
# GIT TOOLS (Sandboxed Operations)
# =============================================================================

def clone_repo_sandboxed(repo_url: str) -> str:
    """
    Security Protocol: Never clone into working directory.
    Uses tempfile.TemporaryDirectory() for isolation.
    """
    temp_dir = tempfile.TemporaryDirectory(prefix="auditor_repo_")
    try:
        Repo.clone_from(repo_url, temp_dir.name)
        return temp_dir.name
    except Exception as e:
        temp_dir.cleanup()
        raise Exception(f"Git Clone Failed: {str(e)}")


def extract_git_history(repo_path: str) -> List[Dict[str, Any]]:
    """
    Forensic Protocol: Extract atomic commit history.
    Detects 'bulk upload' vs 'iterative development'.
    """
    try:
        repo = Repo(repo_path)
        commits = []
        for commit in repo.iter_commits():
            commits.append({
                "hash": commit.hexsha,
                "short_hash": commit.hexsha[:7],
                "message": commit.message.strip(),
                "timestamp": commit.committed_datetime.isoformat(),
                "author": str(commit.author)
            })
        commits.reverse()  # Chronological order (oldest first)
        return commits
    except Exception as e:
        return [{"error": str(e), "hash": "unknown"}]


def extract_git_history_formatted(repo_path: str) -> str:
    """
    Format git history for forensic analysis.
    """
    commits = extract_git_history(repo_path)
    formatted = []
    for commit in commits:
        if "error" not in commit:
            formatted.append(f"{commit['short_hash']} - {commit['timestamp']} - {commit['message']}")
    return "\n".join(formatted)


# =============================================================================
# AST TOOLS (Deep Code Parsing)
# =============================================================================

class LangGraphASTVisitor(ast.NodeVisitor):
    """
    Deep AST Parsing: Verifies actual LangGraph structure, not just string matching.
    """
    
    def __init__(self):
        self.state_graphs: List[Dict[str, Any]] = []
        self.pydantic_models: List[str] = []
        self.typed_dicts: List[str] = []
        self.reducers: List[Dict[str, Any]] = []
        self.add_edge_calls: List[Dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Detect Pydantic BaseModel and TypedDict inheritance."""
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == "BaseModel":
                    self.pydantic_models.append(node.name)
            if isinstance(base, ast.Name):
                if base.id == "TypedDict":
                    self.typed_dicts.append(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect StateGraph instantiation and reducer usage."""
        # Detect StateGraph instantiation
        if isinstance(node.func, ast.Name):
            if node.func.id == "StateGraph":
                self.state_graphs.append({
                    "line": node.lineno,
                    "col": node.col_offset,
                    "type": "StateGraph"
                })
        
        # Detect reducer usage (operator.add, operator.ior)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["add", "ior"]:
                self.reducers.append({
                    "line": node.lineno,
                    "func": node.func.attr
                })
        
        # Detect builder.add_edge() calls
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "add_edge":
                edge_info = {"line": node.lineno, "args": []}
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        edge_info["args"].append(arg.value)
                self.add_edge_calls.append(edge_info)
        
        self.generic_visit(node)


def analyze_graph_structure(file_path: str) -> Dict[str, Any]:
    """
    Forensic Protocol: Analyze Python file for LangGraph structure.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        visitor = LangGraphASTVisitor()
        visitor.visit(tree)
        
        return {
            "success": True,
            "file": file_path,
            "found_state_graph": len(visitor.state_graphs) > 0,
            "found_pydantic": len(visitor.pydantic_models) > 0,
            "found_typed_dict": len(visitor.typed_dicts) > 0,
            "found_reducers": len(visitor.reducers) > 0,
            "found_add_edge": len(visitor.add_edge_calls) > 0,
            "details": {
                "state_graphs": visitor.state_graphs,
                "pydantic_models": visitor.pydantic_models,
                "typed_dicts": visitor.typed_dicts,
                "reducers": visitor.reducers,
                "edge_calls": visitor.add_edge_calls
            }
        }
        
    except SyntaxError as e:
        return {
            "success": False,
            "file": file_path,
            "error": f"SyntaxError: {str(e)}",
            "line": e.lineno
        }
    except Exception as e:
        return {
            "success": False,
            "file": file_path,
            "error": str(e)
        }


def verify_parallel_architecture(file_path: str) -> Dict[str, Any]:
    """
    Forensic Protocol: Verify parallel fan-out/fan-in architecture.
    
    Analyzes add_edge calls to determine if parallel branches exist.
    
    Args:
        file_path: Path to graph definition file
        
    Returns:
        Dictionary containing parallelism analysis
    """
    analysis = analyze_graph_structure(file_path)
    
    if not analysis.get("success"):
        return {
            "parallel_detected": False,
            "error": analysis.get("error"),
            "rationale": "Could not parse file"
        }
    
    edge_calls = analysis["details"].get("edge_calls", [])
    
    # Detect fan-out: single source -> multiple destinations
    source_counts: Dict[str, List[str]] = {}
    for edge in edge_calls:
        args = edge.get("args", [])
        if len(args) >= 2:
            source = args[0]
            target = args[1]
            if source not in source_counts:
                source_counts[source] = []
            source_counts[source].append(target)
    
    # Fan-out detected if one source has multiple targets
    fan_out_detected = any(len(targets) > 1 for targets in source_counts.values())
    
    return {
        "parallel_detected": fan_out_detected,
        "fan_out_sources": [src for src, targets in source_counts.items() if len(targets) > 1],
        "edge_count": len(edge_calls),
        "rationale": "Fan-out detected" if fan_out_detected else "Linear flow detected"
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_file_tree(repo_path: str, max_depth: int = 3) -> List[str]:
    """
    Extract file tree structure for forensic inventory.
    """
    files = []
    
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv', 'node_modules']]
        
        depth = root.replace(repo_path, '').count(os.sep)
        if depth >= max_depth:
            dirs.clear()
            continue
        
        for filename in filenames:
            if not filename.startswith('.') and not filename.endswith('.pyc'):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, repo_path)
                files.append(rel_path)
    
    return sorted(files)


def check_file_exists(repo_path: str, relative_path: str) -> bool:
    """
    Verify existence of claimed file path.
    """
    full_path = os.path.join(repo_path, relative_path)
    return os.path.isfile(full_path)