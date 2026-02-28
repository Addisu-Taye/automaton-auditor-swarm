"""
src/state.py

Central State Management for Automaton Auditor Swarm
Production Module v3.0.0

Compliance:
- Protocol S.1: Pydantic BaseModel for structured data
- Protocol S.2: Annotated[...] with reducers for parallel execution
- Protocol S.3: Immutable evidence collection pattern
"""

from typing import Dict, List, Optional, Annotated, Any, TypedDict
from pydantic import BaseModel, Field
import operator
from datetime import datetime, timezone


# =============================================================================
# EVIDENCE SCHEMA (Immutable Forensic Record)
# =============================================================================

class Evidence(BaseModel):
    """
    Immutable record of forensic evidence collected by Detective nodes.
    
    Each piece of evidence is:
    - Traceable: Links to specific goal/rubric dimension
    - Verifiable: Contains confidence score and rationale
    - Citable: References specific artifact locations
    """
    
    goal: str = Field(..., description="Rubric dimension ID this evidence supports")
    found: bool = Field(..., description="Whether the expected artifact was found")
    content: str = Field(..., description="Detailed description of the evidence")
    location: str = Field(..., description="File path, URL, or artifact location")
    rationale: str = Field(..., description="Reasoning behind the finding")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    artifact_type: str = Field(..., description="Type: git_clone, ast_analysis, document, etc.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When evidence was collected")
    
    class Config:
        frozen = True  # Immutable after creation


# =============================================================================
# JUDICIAL OPINION SCHEMA (Structured Judge Output)
# =============================================================================

class JudicialOpinion(BaseModel):
    """
    Structured output from Judicial nodes (Prosecutor, Defense, TechLead).
    
    Each opinion is:
    - Scored: 1-5 integer score per rubric dimension
    - Argued: Detailed reasoning for the score
    - Cited: References to specific evidence supporting the argument
    """
    
    judge: str = Field(..., description="Judge persona: Prosecutor, Defense, or TechLead")
    criterion_id: str = Field(..., description="Rubric dimension ID being evaluated")
    score: int = Field(..., ge=1, le=5, description="Score from 1-5")
    argument: str = Field(..., description="Detailed argument supporting the score")
    cited_evidence: List[str] = Field(default_factory=list, description="Evidence locations cited")
    
    class Config:
        frozen = True  # Immutable after creation


# =============================================================================
# AUDIT REPORT SCHEMA (Final Output)
# =============================================================================

class AuditReport(BaseModel):
    """
    Structured audit report output from ChiefJustice synthesis.
    
    Used for API response serialization and report generation.
    """
    repo_url: str = Field(..., description="Audited repository URL")
    overall_score: float = Field(..., ge=0.0, le=5.0, description="Overall score 0.0-5.0")
    criteria_evaluated: int = Field(..., ge=0, description="Number of criteria evaluated")
    executive_summary: str = Field(..., description="Executive summary text")
    criteria: List[Dict[str, Any]] = Field(default_factory=list, description="Per-criterion results")
    remediation_plan: str = Field(..., description="Prioritized remediation plan")
    report_markdown: str = Field(..., description="Full markdown report")
    
    class Config:
        arbitrary_types_allowed = True


# =============================================================================
# AGENT STATE (Central State Container)
# =============================================================================

class AgentState(TypedDict):
    """
    Central state container for the Automaton Auditor Swarm.
    
    Uses Annotated[...] with reducers for proper parallel execution:
    - operator.ior (|) for dict merging: {**a, **b}
    - operator.add (+) for list concatenation: a + b
    
    State fields are updated by nodes returning partial dicts, which are
    merged using the specified reducer. This enables safe parallel execution.
    """
    
    # =====================================================================
    # INPUT PARAMETERS (Set at graph start, not modified by nodes)
    # =====================================================================
    
    repo_url: Optional[str]
    """GitHub repository URL to audit"""
    
    pdf_path: Optional[str]
    """Path to architectural report PDF for cross-reference"""
    
    rubric_dimensions: Optional[List[Dict]]
    """Machine-readable rubric dimensions (loaded from JSON)"""
    
    mode: str
    """Audit mode: 'detective' (interim) or 'full' (final)"""
    
    output_path: Optional[str]
    """Path to save final markdown report"""
    
    # =====================================================================
    # ACCUMULATED EVIDENCE (Dict reducer: operator.ior for merging)
    # =====================================================================
    
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]
    """
    Collected evidence organized by detective node:
    {
        "repo_investigator": [Evidence(...), ...],
        "doc_analyst": [Evidence(...), ...],
        "vision_inspector": [Evidence(...), ...],
        "evidence_aggregator": [Evidence(...), ...]
    }
    
    Reducer: operator.ior (|) merges dicts: {**a, **b}
    """
    
    # =====================================================================
    # ACCUMULATED OPINIONS (Dict reducer: operator.ior for merging)
    # =====================================================================
    
    opinions: Annotated[Dict[str, List[JudicialOpinion]], operator.ior]
    """
    Judicial opinions organized by judge node:
    {
        "prosecutor": [JudicialOpinion(...), ...],
        "defense": [JudicialOpinion(...), ...],
        "techlead": [JudicialOpinion(...), ...],
        "aggregator": [JudicialOpinion(...), ...]
    }
    
    Reducer: operator.ior (|) merges dicts: {**a, **b}
    """
    
    # =====================================================================
    # ERROR TRACKING (List reducer: operator.add for concatenation)
    # =====================================================================
    
    errors: Annotated[List[str], operator.add]
    """
    Accumulated error messages from all nodes.
    
    Reducer: operator.add (+) concatenates lists: a + b
    """
    
    # =====================================================================
    # FINAL OUTPUT (Set by ChiefJustice, not modified)
    # =====================================================================
    
    final_report: Optional[Dict]
    """Structured final report from ChiefJustice synthesis"""
    
    report_markdown: Optional[str]
    """Serialized markdown report for output"""


# =============================================================================
# STATE UTILITIES
# =============================================================================

def create_initial_state(
    repo_url: str,
    pdf_path: Optional[str] = None,
    rubric_dimensions: Optional[List[Dict]] = None,
    mode: str = "full",
    output_path: Optional[str] = None
) -> AgentState:
    """
    Create a new AgentState with initial input parameters.
    
    Args:
        repo_url: GitHub repository URL to audit
        pdf_path: Optional path to architectural report PDF
        rubric_dimensions: Optional list of rubric dimension dicts
        mode: Audit mode ('detective' or 'full')
        output_path: Optional path to save final report
        
    Returns:
        AgentState with input parameters and empty accumulators
    """
    return AgentState(
        repo_url=repo_url,
        pdf_path=pdf_path,
        rubric_dimensions=rubric_dimensions,
        mode=mode,
        output_path=output_path,
        evidences={},  # Start with empty dict for merging
        opinions={},   # Start with empty dict for merging
        errors=[],     # Start with empty list for concatenation
        final_report=None,
        report_markdown=None
    )