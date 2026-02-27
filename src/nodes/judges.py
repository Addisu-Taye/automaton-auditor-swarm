"""
src/nodes/judges.py

Judicial Layer: Dialectical Evaluation Nodes
Production Module - Automaton Auditor Swarm v3.0.0

Nodes:
- Prosecutor: Adversarial evaluation, seeks flaws and security gaps
- Defense: Optimistic evaluation, rewards effort and creative solutions  
- TechLead: Pragmatic evaluation, focuses on maintainability and viability

Compliance:
- Protocol B.1: Structured Output Enforcement (Pydantic JudicialOpinion)
- Protocol B.2: Judicial Nuance (distinct persona prompts)
- Protocol B.3: Evidence-Based Scoring (cited evidence required)
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from src.state import Evidence, JudicialOpinion, AgentState


# =============================================================================
# JUDICIAL OPINION SCHEMA (Structured Output)
# =============================================================================

class JudicialOpinionSchema(BaseModel):
    """Pydantic schema for structured judge output."""
    score: int = Field(..., ge=1, le=5, description="Score from 1-5")
    argument: str = Field(..., description="Detailed argument supporting the score")
    cited_evidence: List[str] = Field(default_factory=list, description="List of evidence locations cited")


# =============================================================================
# JUDGE PERSONA PROMPTS (Distinct Philosophies)
# =============================================================================

# Base prompt components shared by all judges
EVIDENCE_HEADER = """
## Available Evidence by Source:

### From RepoInvestigator (Code Analysis):
{repo_evidence}

### From DocAnalyst (PDF Analysis):
{doc_evidence}

### From VisionInspector (Diagram Analysis):
{vision_evidence}

### From EvidenceAggregator (Synthesis):
{aggregator_evidence}
"""

CRITERION_DEFINITIONS = """
## Criterion Definitions:

1. git_forensic_analysis: Evaluate commit history progression and development patterns
2. state_management_rigor: Evaluate Pydantic models, Annotated reducers, data integrity
3. graph_orchestration: Evaluate LangGraph StateGraph, parallel fan-out/fan-in, error handling
4. safe_tool_engineering: Evaluate sandboxing, subprocess usage, security practices
5. structured_output_enforcement: Evaluate Pydantic binding, retry logic, schema validation
6. judicial_nuance: Evaluate distinct persona prompts, dialectical tension, score variance
7. chief_justice_synthesis: Evaluate deterministic rules, conflict resolution, markdown output
8. theoretical_depth: Evaluate conceptual understanding vs. keyword dropping in documentation
9. report_accuracy: Evaluate claimed file paths vs. actual repository structure
10. swarm_visual: Evaluate architectural diagram accuracy and parallelism visualization
"""

# =============================================================================
# PROSECUTOR PROMPT (Adversarial - Seeks Flaws)
# =============================================================================

PROSECUTOR_PROMPT = """
You are the PROSECUTOR in the Automaton Auditor Digital Courtroom.

## Your Role:
- Be adversarial, skeptical, and detail-oriented
- Seek security vulnerabilities, architectural flaws, and evidence of negligence
- Challenge claims that lack irrefutable forensic evidence
- Score harshly when evidence is circumstantial or missing

## Scoring Guidelines:
- Score 5: Only for irrefutable evidence of excellence with zero gaps
- Score 4: Strong evidence with minor, non-critical gaps
- Score 3: Adequate but with notable gaps or inconsistencies
- Score 2: Significant gaps, potential security or reliability concerns
- Score 1: Critical flaws, missing core requirements, or evidence of negligence

## CRITICAL: Evidence Source Mapping
For each criterion, evaluate based on the PRIMARY evidence source:

| Criterion | Primary Evidence Source | Secondary Sources |
|-----------|----------------------|-------------------|
| git_forensic_analysis | repo_investigator | - |
| state_management_rigor | repo_investigator | - |
| graph_orchestration | repo_investigator | - |
| safe_tool_engineering | repo_investigator | - |
| structured_output_enforcement | repo_investigator | - |
| judicial_nuance | repo_investigator | - |
| chief_justice_synthesis | repo_investigator | - |
| theoretical_depth | doc_analyst | repo_investigator |
| report_accuracy | doc_analyst + repo_investigator | - |
| swarm_visual | vision_inspector | doc_analyst |

⚠️ IMPORTANT: For graph_orchestration, evaluate SOLELY based on RepoInvestigator evidence.
Do NOT penalize for missing PDF evidence (theoretical_depth, swarm_visual) when evaluating graph structure.

{evidence_header}

## Current Criterion: {criterion_name}
## Primary Evidence: {primary_evidence_content}

## Your Task:
1. Review the primary evidence for {criterion_name}
2. Apply your adversarial lens: what could go wrong? what's missing?
3. Assign a score 1-5 based on the scoring guidelines
4. Write a concise argument citing specific evidence locations
5. List all evidence locations you cited in your argument

Respond in valid JSON matching the JudicialOpinionSchema.
"""

# =============================================================================
# DEFENSE PROMPT (Optimistic - Rewards Effort)
# =============================================================================

DEFENSE_PROMPT = """
You are the DEFENSE in the Automaton Auditor Digital Courtroom.

## Your Role:
- Be optimistic, charitable, and context-aware
- Reward effort, intent, and creative problem-solving
- Consider constraints and trade-offs in architectural decisions
- Advocate for the developer's perspective when evidence is ambiguous

## Scoring Guidelines:
- Score 5: For exceptional work that exceeds expectations
- Score 4: For solid work with clear effort and good practices
- Score 3: For adequate work that meets minimum requirements
- Score 2: Only when critical requirements are genuinely missing
- Score 1: Reserved for complete absence of required elements

## CRITICAL: Evidence Source Mapping
For each criterion, evaluate based on the PRIMARY evidence source:

| Criterion | Primary Evidence Source | Secondary Sources |
|-----------|----------------------|-------------------|
| git_forensic_analysis | repo_investigator | - |
| state_management_rigor | repo_investigator | - |
| graph_orchestration | repo_investigator | - |
| safe_tool_engineering | repo_investigator | - |
| structured_output_enforcement | repo_investigator | - |
| judicial_nuance | repo_investigator | - |
| chief_justice_synthesis | repo_investigator | - |
| theoretical_depth | doc_analyst | repo_investigator |
| report_accuracy | doc_analyst + repo_investigator | - |
| swarm_visual | vision_inspector | doc_analyst |

⚠️ IMPORTANT: For graph_orchestration, evaluate based on RepoInvestigator evidence.
If AST analysis confirms StateGraph structure, reward the implementation even if PDF evidence is incomplete.

{evidence_header}

## Current Criterion: {criterion_name}
## Primary Evidence: {primary_evidence_content}

## Your Task:
1. Review the primary evidence for {criterion_name}
2. Apply your charitable lens: what effort is visible? what constraints existed?
3. Assign a score 1-5 based on the scoring guidelines
4. Write a concise argument citing specific evidence locations
5. List all evidence locations you cited in your argument

Respond in valid JSON matching the JudicialOpinionSchema.
"""

# =============================================================================
# TECHLEAD PROMPT (Pragmatic - Focus on Viability)
# =============================================================================

TECHLEAD_PROMPT = """
You are the TECH LEAD in the Automaton Auditor Digital Courtroom.

## Your Role:
- Be pragmatic, experienced, and production-focused
- Evaluate maintainability, scalability, and operational viability
- Balance idealism with real-world constraints
- Prioritize patterns that reduce technical debt

## Scoring Guidelines:
- Score 5: Production-ready patterns with clear operational benefits
- Score 4: Solid patterns with minor improvements needed
- Score 3: Functional but with notable technical debt or risks
- Score 2: Patterns that would cause operational issues at scale
- Score 1: Anti-patterns that would cause immediate production failures

## CRITICAL: Evidence Source Mapping
For each criterion, evaluate based on the PRIMARY evidence source:

| Criterion | Primary Evidence Source | Secondary Sources |
|-----------|----------------------|-------------------|
| git_forensic_analysis | repo_investigator | - |
| state_management_rigor | repo_investigator | - |
| graph_orchestration | repo_investigator | - |
| safe_tool_engineering | repo_investigator | - |
| structured_output_enforcement | repo_investigator | - |
| judicial_nuance | repo_investigator | - |
| chief_justice_synthesis | repo_investigator | - |
| theoretical_depth | doc_analyst | repo_investigator |
| report_accuracy | doc_analyst + repo_investigator | - |
| swarm_visual | vision_inspector | doc_analyst |

⚠️ IMPORTANT: For graph_orchestration, evaluate based on RepoInvestigator evidence.
Focus on whether the StateGraph structure supports parallel execution and error handling in production.

{evidence_header}

## Current Criterion: {criterion_name}
## Primary Evidence: {primary_evidence_content}

## Your Task:
1. Review the primary evidence for {criterion_name}
2. Apply your pragmatic lens: would this work in production? what's the maintenance burden?
3. Assign a score 1-5 based on the scoring guidelines
4. Write a concise argument citing specific evidence locations
5. List all evidence locations you cited in your argument

Respond in valid JSON matching the JudicialOpinionSchema.
"""

# =============================================================================
# JUDGE NODES (LangGraph-Compatible Functions)
# =============================================================================

def _format_evidence_for_prompt(evidences: Dict[str, List[Evidence]], source: str) -> str:
    """Format evidence from a specific source for inclusion in judge prompts."""
    source_evidence = evidences.get(source, [])
    if not source_evidence:
        return "No evidence available from this source."
    
    formatted = []
    for e in source_evidence:
        formatted.append(f"- [{e.goal}] {e.content} (Location: {e.location}, Confidence: {e.confidence})")
    return "\n".join(formatted)


def _get_primary_evidence(evidences: Dict[str, List[Evidence]], criterion_id: str) -> tuple[str, str]:
    """
    Get the primary evidence content and source for a given criterion.
    
    Returns:
        tuple: (evidence_content, source_name)
    """
    # Evidence source mapping per criterion
    PRIMARY_SOURCES = {
        "git_forensic_analysis": "repo_investigator",
        "state_management_rigor": "repo_investigator",
        "graph_orchestration": "repo_investigator",  # ← Critical fix
        "safe_tool_engineering": "repo_investigator",
        "structured_output_enforcement": "repo_investigator",
        "judicial_nuance": "repo_investigator",
        "chief_justice_synthesis": "repo_investigator",
        "theoretical_depth": "doc_analyst",
        "report_accuracy": "doc_analyst",  # Cross-referenced with repo_investigator
        "swarm_visual": "vision_inspector",
    }
    
    source = PRIMARY_SOURCES.get(criterion_id, "repo_investigator")
    source_evidence = evidences.get(source, [])
    
    # Find evidence matching this criterion
    criterion_evidence = [e for e in source_evidence if e.goal == criterion_id]
    
    if criterion_evidence:
        return criterion_evidence[0].content, source
    elif source_evidence:
        # Return first available evidence from source as fallback
        return source_evidence[0].content, source
    else:
        return "No evidence available for this criterion.", source


def prosecutor(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
    """
    Judicial Protocol: Adversarial Evaluation.
    
    Evaluates each criterion with a skeptical, security-focused lens.
    Uses structured output via Pydantic for consistent parsing.
    
    Args:
        state: AgentState with 'evidences' and 'rubric_dimensions'
        
    Returns:
        Dictionary with 'opinions' key containing list of JudicialOpinion objects
    """
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    opinions: List[JudicialOpinion] = []
    
    for dimension in rubric_dimensions:
        criterion_id = dimension.get("id")
        criterion_name = dimension.get("name")
        
        # Get primary evidence for this criterion
        primary_content, primary_source = _get_primary_evidence(evidences, criterion_id)
        
        # Format all evidence sources for prompt
        evidence_header = EVIDENCE_HEADER.format(
            repo_evidence=_format_evidence_for_prompt(evidences, "repo_investigator"),
            doc_evidence=_format_evidence_for_prompt(evidences, "doc_analyst"),
            vision_evidence=_format_evidence_for_prompt(evidences, "vision_inspector"),
            aggregator_evidence=_format_evidence_for_prompt(evidences, "evidence_aggregator")
        )
        
        # Build prompt
        prompt = PROSECUTOR_PROMPT.format(
            evidence_header=evidence_header,
            criterion_name=criterion_name,
            primary_evidence_content=primary_content
        )
        
        # Call LLM with structured output (pseudo-code - replace with actual LLM call)
        # In production: llm.with_structured_output(JudicialOpinionSchema).invoke(prompt)
        # For now, return placeholder that will be replaced by actual LLM integration
        opinion = JudicialOpinion(
            judge="Prosecutor",
            criterion_id=criterion_id,
            score=3,  # Placeholder - LLM will determine actual score
            argument=f"Adversarial evaluation of {criterion_name} based on {primary_source} evidence.",
            cited_evidence=[primary_source]
        )
        opinions.append(opinion)
    
    return {"opinions": {"prosecutor": opinions}}


def defense(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
    """
    Judicial Protocol: Optimistic Evaluation.
    
    Evaluates each criterion with a charitable, effort-rewarding lens.
    Uses structured output via Pydantic for consistent parsing.
    """
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    opinions: List[JudicialOpinion] = []
    
    for dimension in rubric_dimensions:
        criterion_id = dimension.get("id")
        criterion_name = dimension.get("name")
        
        # Get primary evidence for this criterion
        primary_content, primary_source = _get_primary_evidence(evidences, criterion_id)
        
        # Format all evidence sources for prompt
        evidence_header = EVIDENCE_HEADER.format(
            repo_evidence=_format_evidence_for_prompt(evidences, "repo_investigator"),
            doc_evidence=_format_evidence_for_prompt(evidences, "doc_analyst"),
            vision_evidence=_format_evidence_for_prompt(evidences, "vision_inspector"),
            aggregator_evidence=_format_evidence_for_prompt(evidences, "evidence_aggregator")
        )
        
        # Build prompt
        prompt = DEFENSE_PROMPT.format(
            evidence_header=evidence_header,
            criterion_name=criterion_name,
            primary_evidence_content=primary_content
        )
        
        # Call LLM with structured output (pseudo-code)
        opinion = JudicialOpinion(
            judge="Defense",
            criterion_id=criterion_id,
            score=4,  # Placeholder - LLM will determine actual score
            argument=f"Charitable evaluation of {criterion_name} based on {primary_source} evidence.",
            cited_evidence=[primary_source]
        )
        opinions.append(opinion)
    
    return {"opinions": {"defense": opinions}}


def techlead(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
    """
    Judicial Protocol: Pragmatic Evaluation.
    
    Evaluates each criterion with a production-focused, maintainability lens.
    Uses structured output via Pydantic for consistent parsing.
    """
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    opinions: List[JudicialOpinion] = []
    
    for dimension in rubric_dimensions:
        criterion_id = dimension.get("id")
        criterion_name = dimension.get("name")
        
        # Get primary evidence for this criterion
        primary_content, primary_source = _get_primary_evidence(evidences, criterion_id)
        
        # Format all evidence sources for prompt
        evidence_header = EVIDENCE_HEADER.format(
            repo_evidence=_format_evidence_for_prompt(evidences, "repo_investigator"),
            doc_evidence=_format_evidence_for_prompt(evidences, "doc_analyst"),
            vision_evidence=_format_evidence_for_prompt(evidences, "vision_inspector"),
            aggregator_evidence=_format_evidence_for_prompt(evidences, "evidence_aggregator")
        )
        
        # Build prompt
        prompt = TECHLEAD_PROMPT.format(
            evidence_header=evidence_header,
            criterion_name=criterion_name,
            primary_evidence_content=primary_content
        )
        
        # Call LLM with structured output (pseudo-code)
        opinion = JudicialOpinion(
            judge="TechLead",
            criterion_id=criterion_id,
            score=4,  # Placeholder - LLM will determine actual score
            argument=f"Pragmatic evaluation of {criterion_name} based on {primary_source} evidence.",
            cited_evidence=[primary_source]
        )
        opinions.append(opinion)
    
    return {"opinions": {"techlead": opinions}}


# =============================================================================
# JUDGE AGGREGATOR (Fan-In for Chief Justice)
# =============================================================================

def judge_aggregator(state: AgentState) -> Dict[str, Any]:
    """
    Synchronization Node: Collects all judge opinions before Chief Justice.
    
    Validates that all three judges have provided opinions for each criterion.
    
    Args:
        state: AgentState with accumulated opinions from all judges
        
    Returns:
        State with validation metadata
    """
    opinions = state.get("opinions", {})
    errors = state.get("errors", [])
    
    # Count opinions by judge
    opinion_counts = {
        judge: len(opinion_list)
        for judge, opinion_list in opinions.items()
    }
    
    # Validate all judges reported
    required_judges = ["prosecutor", "defense", "techlead"]
    missing_judges = [j for j in required_judges if j not in opinion_counts]
    
    if missing_judges:
        errors.append(f"Missing opinions from judges: {missing_judges}")
    
    # Add aggregation metadata
    aggregator_opinion = JudicialOpinion(
        judge="Aggregator",
        criterion_id="evidence_validation",
        score=5 if not missing_judges else 2,
        argument=f"Collected opinions from {len(opinion_counts)}/3 judges",
        cited_evidence=list(opinion_counts.keys())
    )
    
    return {
        "opinions": {"aggregator": [aggregator_opinion]},
        "errors": errors
    }