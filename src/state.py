"""
src/state.py

Pydantic State Definitions for Automaton Auditor Swarm
Production Module - v3.0.0

Compliance:
- Protocol A.2: State Management Rigor
- Protocol A.5: Structured Output Enforcement
"""

import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# =============================================================================
# DETECTIVE OUTPUT: EVIDENCE
# =============================================================================

class Evidence(BaseModel):
    """
    Structured evidence collected by Detective agents.
    Immutable facts only - no opinions or judgments.
    
    Compliance: Protocol A (Forensic Evidence Collection Standards)
    """
    goal: str = Field(description="Rubric dimension ID this evidence addresses")
    found: bool = Field(description="Whether the artifact exists")
    content: Optional[str] = Field(default=None, description="Evidence content or snippet")
    location: str = Field(description="File path, commit hash, or page number")
    rationale: str = Field(description="Rationale for confidence assessment")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    artifact_type: str = Field(description="Type: git_history, ast_analysis, document, etc.")


# =============================================================================
# JUDGE OUTPUT: JUDICIAL OPINION
# =============================================================================

class JudicialOpinion(BaseModel):
    """
    Structured opinion from a Judge persona.
    Must be validated via .with_structured_output().
    
    Compliance: Protocol A.5 (Structured Output Enforcement)
    """
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str = Field(description="Rubric dimension ID being evaluated")
    score: int = Field(ge=1, le=5, description="Score 1-5 per rubric")
    argument: str = Field(description="Reasoning for the score")
    cited_evidence: List[str] = Field(description="List of evidence locations cited")


# =============================================================================
# CHIEF JUSTICE OUTPUT: CRITERION RESULT & AUDIT REPORT
# =============================================================================

class CriterionResult(BaseModel):
    """
    Final result for a single rubric dimension after synthesis.
    
    Compliance: Protocol B (Judicial Sentencing Guidelines)
    """
    dimension_id: str
    dimension_name: str
    final_score: int = Field(ge=1, le=5)
    judge_opinions: List[JudicialOpinion]
    dissent_summary: Optional[str] = Field(
        default=None,
        description="Required when score variance > 2"
    )
    remediation: str = Field(
        description="Specific file-level instructions for improvement"
    )


class AuditReport(BaseModel):
    """
    Final production-grade audit report.
    Serialized to Markdown for output.
    
    Compliance: Executive Grade Report Quality requirement
    """
    repo_url: str
    executive_summary: str
    overall_score: float = Field(ge=1.0, le=5.0)
    criteria: List[CriterionResult]
    remediation_plan: str


# =============================================================================
# GRAPH STATE: AGENTSTATE
# =============================================================================

class AgentState(TypedDict):
    """
    Master State Graph Schema for LangGraph.
    
    Uses Annotated reducers to handle parallel execution safely:
    - operator.ior: Dict merge for evidences (prevents overwrite)
    - operator.add: List append for opinions (accumulates all views)
    
    Compliance: Protocol A.2 (State Management Rigor)
    """
    # Input parameters
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[Dict]
    
    # Evidence collection (Dict merge reducer)
    evidences: Annotated[
        Dict[str, List[Evidence]],
        operator.ior  # Dict merge: prevents parallel agents from overwriting
    ]
    
    # Judicial opinions (List append reducer)
    opinions: Annotated[
        List[JudicialOpinion],
        operator.add  # List append: accumulates all judge perspectives
    ]
    
    # Final output
    final_report: AuditReport
    
    # Error tracking
    errors: List[str]