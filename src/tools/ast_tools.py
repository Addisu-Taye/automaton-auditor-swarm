import ast
import os
from typing import List, Dict


class LangGraphASTVisitor(ast.NodeVisitor):
    """
    Deep AST Parsing: Verifies actual LangGraph structure, not just string matching.
    """
    
    def __init__(self):
        self.state_graphs = []
        self.pydantic_models = []
        self.reducers = []

    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == "BaseModel":
                    self.pydantic_models.append(node.name)
            if isinstance(base, ast.Name):
                if base.id == "TypedDict":
                    self.pydantic_models.append(node.name)
        self.generic_visit(node)

    def visit_Call(self, node):
        # Detect StateGraph instantiation
        if isinstance(node.func, ast.Name) and node.func.id == "StateGraph":
            self.state_graphs.append({"line": node.lineno, "type": "StateGraph"})
        
        # Detect Reducers (operator.add, operator.ior)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["add", "ior"]:
                self.reducers.append({"line": node.lineno, "func": node.func.attr})
        self.generic_visit(node)


def analyze_graph_structure(file_path: str) -> Dict:
    """
    Returns structural evidence of LangGraph implementation.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    visitor = LangGraphASTVisitor()
    visitor.visit(tree)
    
    return {
        "found_state_graph": len(visitor.state_graphs) > 0,
        "found_pydantic": len(visitor.pydantic_models) > 0,
        "found_reducers": len(visitor.reducers) > 0,
        "details": {
            "models": visitor.pydantic_models,
            "reducers": visitor.reducers
        }
    }
