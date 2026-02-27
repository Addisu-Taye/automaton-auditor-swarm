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

import ast
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import tempfile
import subprocess
import git


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


def verify_graph_structure(file_path: str) -> Dict[str, Any]:
    """
    Use AST parsing to verify LangGraph StateGraph structure.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary with graph analysis results
    """
    result = {
        "success": False,
        "found_state_graph": False,
        "found_parallel_pattern": False,
        "fan_out_nodes": [],
        "fan_in_nodes": [],
        "conditional_edges": [],
        "error": None
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        # Track StateGraph instantiation
        state_graph_vars = []
        # Track add_edge calls for parallelism detection
        edge_targets = defaultdict(list)
        
        class GraphVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                # Look for: builder = StateGraph(AgentState)
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id == "StateGraph":
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    state_graph_vars.append(target.id)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Look for: builder.add_edge() or builder.add_conditional_edges()
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("add_edge", "add_conditional_edges"):
                        # Extract edge information
                        if node.args:
                            edge_info = {"type": node.func.attr, "args": []}
                            for arg in node.args:
                                if isinstance(arg, ast.Constant):
                                    edge_info["args"].append(arg.value)
                                elif isinstance(arg, ast.Str):  # Python <3.8
                                    edge_info["args"].append(arg.s)
                            edge_targets[node.func.attr].append(edge_info)
                self.generic_visit(node)
        
        visitor = GraphVisitor()
        visitor.visit(tree)
        
        result["success"] = True
        result["found_state_graph"] = len(state_graph_vars) > 0
        
        # Detect parallel fan-out/fan-in pattern
        # Look for multiple edges from same source (fan-out) or to same target (fan-in)
        for edge_type, edges in edge_targets.items():
            sources = [e["args"][0] for e in edges if len(e["args"]) > 0]
            targets = [e["args"][-1] for e in edges if len(e["args"]) > 0]
            
            # Fan-out: same source, multiple targets
            from collections import Counter
            source_counts = Counter(sources)
            fan_out = [src for src, count in source_counts.items() if count > 1]
            result["fan_out_nodes"].extend(fan_out)
            
            # Fan-in: multiple sources, same target
            target_counts = Counter(targets)
            fan_in = [tgt for tgt, count in target_counts.items() if count > 1]
            result["fan_in_nodes"].extend(fan_in)
            
            # Conditional edges indicate error handling
            if edge_type == "add_conditional_edges":
                result["conditional_edges"].extend(edges)
        
        result["found_parallel_pattern"] = (
            len(result["fan_out_nodes"]) > 0 or 
            len(result["fan_in_nodes"]) > 0 or
            len(result["conditional_edges"]) > 0
        )
        
    except FileNotFoundError:
        result["error"] = f"File not found: {file_path}"
    except SyntaxError as e:
        result["error"] = f"Syntax error parsing {file_path}: {e}"
    except Exception as e:
        result["error"] = f"Unexpected error: {type(e).__name__}: {e}"
    
    return result

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

def get_file_tree(repo_path: str, max_depth: int = 4) -> List[str]:
    """
    Get a list of all files in the repository, normalized to forward slashes.
    
    Args:
        repo_path: Path to the cloned repository
        max_depth: Maximum directory depth to traverse
        
    Returns:
        List of relative file paths with forward slashes, sorted
    """
    files = []
    repo_path = Path(repo_path).resolve()
    
    for path in repo_path.rglob("*"):
        if path.is_file():
            # Skip hidden files and common non-code files
            if path.name.startswith(".") or path.suffix in {".pyc", ".pyo", ".pyd"}:
                continue
            
            # Calculate relative path
            try:
                rel_path = path.relative_to(repo_path)
                # Normalize to forward slashes for cross-platform comparison
                rel_path_str = str(rel_path).replace(os.sep, "/")
                
                # Check depth
                depth = len(rel_path.parts)
                if depth <= max_depth:
                    files.append(rel_path_str)
            except ValueError:
                # Path is not relative to repo_path, skip
                continue
    
    return sorted(files)


def check_file_exists(repo_path: str, relative_path: str) -> bool:
    """
    Verify existence of claimed file path.
    
    Evidence Class: Report Accuracy (Protocol A.2)
    Used for cross-referencing PDF claims against actual repo structure.
    
    Args:
        repo_path: Path to cloned repository
        relative_path: Relative path to verify (e.g., "src/state.py")
        
    Returns:
        True if file exists, False otherwise
    """
    # Normalize paths for cross-platform compatibility
    repo_path = os.path.normpath(repo_path)
    relative_path = os.path.normpath(relative_path)
    
    full_path = os.path.join(repo_path, relative_path)
    return os.path.isfile(full_path)


def get_file_tree(repo_path: str, max_depth: int = 3) -> List[str]:
    """
    Extract file tree structure for forensic inventory.
    Returns paths with forward slashes for cross-platform comparison.
    """
    files = []
    repo_path = os.path.normpath(repo_path)
    
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
                # Normalize to forward slashes for cross-platform comparison
                rel_path = rel_path.replace(os.sep, '/')
                files.append(rel_path)
    
    return sorted(files)
    # =============================================================================
# AST ANALYSIS UTILITIES
# =============================================================================

def analyze_graph_structure(file_path: str) -> Dict[str, Any]:
    """
    Use AST parsing to analyze Python file for LangGraph/Pydantic patterns.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary with analysis results:
        - success: bool - Whether parsing succeeded
        - found_pydantic: bool - Whether Pydantic BaseModel was found
        - found_state_graph: bool - Whether LangGraph StateGraph was found
        - details: dict - Additional details about found patterns
        - error: str - Error message if parsing failed
    """
    import ast
    
    result = {
        "success": False,
        "found_pydantic": False,
        "found_state_graph": False,
        "details": {
            "pydantic_models": [],
            "reducers": [],
            "state_graph_vars": []
        },
        "error": None
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        # Track imports
        has_pydantic = False
        has_langgraph = False
        
        # Track class definitions
        pydantic_models = []
        reducers = []
        
        # Track StateGraph instantiation
        state_graph_vars = []
        
        class AnalysisVisitor(ast.NodeVisitor):
            def visit_ImportFrom(self, node):
                nonlocal has_pydantic, has_langgraph
                if node.module:
                    if "pydantic" in node.module:
                        has_pydantic = True
                    if "langgraph" in node.module:
                        has_langgraph = True
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check for Pydantic BaseModel inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id in ("BaseModel", "TypedDict"):
                            pydantic_models.append(node.name)
                    elif isinstance(base, ast.Attribute):
                        if base.attr in ("BaseModel", "TypedDict"):
                            pydantic_models.append(node.name)
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                # Look for Annotated[..., operator.add] or operator.ior patterns
                if isinstance(node.value, ast.Subscript):
                    # Check for Annotated type hints with reducers
                    if isinstance(node.value.value, ast.Name):
                        if node.value.value.id == "Annotated":
                            # Look for operator.add or operator.ior in slice
                            slice_val = node.value.slice
                            if isinstance(slice_val, ast.Tuple):
                                for elt in slice_val.elts:
                                    if isinstance(elt, ast.Attribute):
                                        if elt.attr in ("add", "ior"):
                                            reducers.append(f"operator.{elt.attr}")
                                    elif isinstance(elt, ast.Name):
                                        if elt.id in ("add", "ior"):
                                            reducers.append(f"operator.{elt.id}")
                
                # Look for: builder = StateGraph(AgentState)
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id == "StateGraph":
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    state_graph_vars.append(target.id)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Look for builder.add_edge() calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("add_edge", "add_conditional_edges"):
                        # This indicates graph structure
                        pass
                self.generic_visit(node)
        
        visitor = AnalysisVisitor()
        visitor.visit(tree)
        
        result["success"] = True
        result["found_pydantic"] = has_pydantic and len(pydantic_models) > 0
        result["found_state_graph"] = has_langgraph and len(state_graph_vars) > 0
        result["details"]["pydantic_models"] = pydantic_models
        result["details"]["reducers"] = list(set(reducers))
        result["details"]["state_graph_vars"] = state_graph_vars
        
    except FileNotFoundError:
        result["error"] = f"File not found: {file_path}"
    except SyntaxError as e:
        result["error"] = f"Syntax error parsing {file_path}: {e}"
    except Exception as e:
        result["error"] = f"Unexpected error: {type(e).__name__}: {e}"
    
    return result
# =============================================================================
# RUBRIC UTILITIES
# =============================================================================

def load_rubric(rubric_path: str) -> List[Dict[str, Any]]:
    """
    Load rubric dimensions from JSON file.
    
    Args:
        rubric_path: Path to rubric JSON file
        
    Returns:
        List of rubric dimension dictionaries with id, name, and evaluation criteria
        
    Raises:
        FileNotFoundError: If rubric file doesn't exist
        json.JSONDecodeError: If rubric file is invalid JSON
    """
    import json
    from pathlib import Path
    
    rubric_file = Path(rubric_path)
    
    if not rubric_file.exists():
        # Return default rubric if file doesn't exist
        return _get_default_rubric()
    
    with open(rubric_file, "r", encoding="utf-8") as f:
        rubric_data = json.load(f)
    
    # Handle both list format and dict with "dimensions" key
    if isinstance(rubric_data, list):
        return rubric_data
    elif isinstance(rubric_data, dict):
        return rubric_data.get("dimensions", rubric_data.get("criteria", []))
    else:
        return _get_default_rubric()


def _get_default_rubric() -> List[Dict[str, Any]]:
    """
    Return default Week 2 TRP1 rubric dimensions.
    
    Returns:
        List of 10 default rubric dimensions
    """
    return [
        {
            "id": "git_forensic_analysis",
            "name": "Git Forensic Analysis",
            "target_artifact": "github_repo",
            "forensic_instruction": "Run 'git log --oneline --reverse' on the cloned repository. Count commits and check for progression.",
            "success_pattern": "More than 3 commits showing clear progression from setup to tool engineering to graph orchestration.",
            "failure_pattern": "Single 'init' commit or bulk upload of all code at once."
        },
        {
            "id": "state_management_rigor",
            "name": "State Management Rigor",
            "target_artifact": "github_repo",
            "forensic_instruction": "Scan for state definitions using AST parsing. Verify Pydantic BaseModel and Annotated reducers.",
            "success_pattern": "AgentState uses TypedDict or BaseModel with Annotated reducers (operator.add, operator.ior).",
            "failure_pattern": "Plain Python dicts used for state. No Pydantic models. No reducers."
        },
        {
            "id": "graph_orchestration",
            "name": "Graph Orchestration Architecture",
            "target_artifact": "github_repo",
            "forensic_instruction": "Scan for StateGraph builder with parallel fan-out/fan-in patterns.",
            "success_pattern": "Two distinct parallel fan-out/fan-in patterns: one for Detectives, one for Judges.",
            "failure_pattern": "Purely linear flow with no parallel branches or synchronization nodes."
        },
        {
            "id": "safe_tool_engineering",
            "name": "Safe Tool Engineering",
            "target_artifact": "github_repo",
            "forensic_instruction": "Scan for repository cloning logic with sandboxing verification.",
            "success_pattern": "All git operations run inside tempfile.TemporaryDirectory(). No raw os.system() calls.",
            "failure_pattern": "Raw os.system('git clone') drops code into live working directory."
        },
        {
            "id": "structured_output_enforcement",
            "name": "Structured Output Enforcement",
            "target_artifact": "github_repo",
            "forensic_instruction": "Scan Judge nodes for .with_structured_output() or .bind_tools() usage.",
            "success_pattern": "All Judge LLM calls use .with_structured_output(JudicialOpinion) with retry logic.",
            "failure_pattern": "Judge nodes call LLMs with plain prompts and parse freeform text responses."
        },
        {
            "id": "judicial_nuance",
            "name": "Judicial Nuance and Dialectics",
            "target_artifact": "github_repo",
            "forensic_instruction": "Verify three distinct personas with conflicting system prompts.",
            "success_pattern": "Three clearly distinct personas (adversarial, forgiving, pragmatic) producing different scores.",
            "failure_pattern": "Single agent or three judges sharing 90%+ prompt text with identical outputs."
        },
        {
            "id": "chief_justice_synthesis",
            "name": "Chief Justice Synthesis Engine",
            "target_artifact": "github_repo",
            "forensic_instruction": "Verify deterministic Python logic for conflict resolution, not just LLM averaging.",
            "success_pattern": "Hardcoded rules (security override, fact supremacy) with markdown report output.",
            "failure_pattern": "ChiefJustice is just another LLM prompt that averages scores."
        },
        {
            "id": "theoretical_depth",
            "name": "Theoretical Depth (Documentation)",
            "target_artifact": "pdf_report",
            "forensic_instruction": "Search PDF for key terms: Dialectical Synthesis, Fan-In/Fan-Out, Metacognition.",
            "success_pattern": "Terms appear in detailed architectural explanations with implementation connections.",
            "failure_pattern": "Terms appear only in executive summary without connection to actual implementation."
        },
        {
            "id": "report_accuracy",
            "name": "Report Accuracy (Cross-Reference)",
            "target_artifact": "pdf_report",
            "forensic_instruction": "Extract file paths from PDF and cross-reference with actual repo structure.",
            "success_pattern": "All file paths mentioned in report exist in repo. Zero hallucinated paths.",
            "failure_pattern": "Report references files that do not exist. Multiple hallucinated paths detected."
        },
        {
            "id": "swarm_visual",
            "name": "Architectural Diagram Analysis",
            "target_artifact": "pdf_images",
            "forensic_instruction": "Extract and classify diagrams from PDF. Verify parallel flow visualization.",
            "success_pattern": "Diagram accurately represents StateGraph with clear parallel branches for Detectives and Judges.",
            "failure_pattern": "Generic box-and-arrow diagram with no indication of parallelism or no diagram present."
        }
    ]