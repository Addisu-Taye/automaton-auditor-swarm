import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Evidence(BaseModel):
    """Forensic evidence collected by Detectives. Immutable facts."""
    found: bool = Field(description="Whether the artifact exists")
    content: Optional[str] = Field(default=None, description="Snippet or content")
    location: str = Field(description="File path, commit hash, or page number")
    confidence: float = Field(description="0.0 to 1.0 confidence score")
    artifact_type: str = Field(description="e.g., git_log, ast_node, pdf_text")


class JudicialOpinion(BaseModel):
    """Structured output from Judges. Must be validated."""
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str
    score: int = Field(ge=1, le=5)
    argument: str
    cited_evidence: List[str] = Field(description="List of evidence locations cited")


class AgentState(TypedDict):
    """
    Master State Graph Schema.
    Uses Annotated reducers to handle parallel execution safely.
    """
    repo_url: str
    pdf_path: Optional[str]
    rubric_dimensions: List[Dict]
    
    # Reducer: Dict merge (ior) for evidence collection from parallel detectives
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]
    
    # Reducer: List append (add) for opinions from parallel judges
    opinions: Annotated[List[JudicialOpinion], operator.add]
    
    final_report: str
    errors: List[str]
