"""
src/nodes/judges.py

Judicial Layer: Dialectical Evaluation Nodes
Production Module - Automaton Auditor Swarm v3.0.0

Nodes:
- prosecutor_node: Adversarial evaluation, seeks flaws and security gaps
- defense_node: Optimistic evaluation, rewards effort and creative solutions  
- tech_lead_node: Pragmatic evaluation, focuses on maintainability and viability

Compliance:
- Protocol B.1: Structured Output Enforcement (Pydantic JudicialOpinion)
- Protocol B.2: Judicial Nuance (distinct persona prompts)
- Protocol B.3: Evidence-Based Scoring (cited evidence required)
- Protocol B.4: LangSmith Tracing for observability and debugging
"""

import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LangChain imports for LLM and tracing
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables (includes LangSmith config)
load_dotenv()

from src.state import Evidence, JudicialOpinion, AgentState


# =============================================================================
# LANGSMITH TRACING CONFIGURATION
# =============================================================================

# Ensure LangSmith tracing is enabled via environment variables
# These should be set in .env file:
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=ls__your-api-key-here
# LANGCHAIN_PROJECT=automaton-auditor-swarm
# LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

def _get_llm_with_tracing():
    """
    Initialize ChatOpenAI with LangSmith tracing enabled.
    
    Tracing is automatically enabled when LANGCHAIN_TRACING_V2=true is set.
    All LLM calls will be logged to LangSmith dashboard.
    
    Returns:
        ChatOpenAI instance configured for tracing
    """
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.1,  # Low temperature for consistent evaluations
        max_tokens=2000,
        # Callbacks are auto-attached when tracing is enabled via env vars
        # No need to explicitly pass callbacks list
    )


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

# =============================================================================
# PROSECUTOR PROMPT (Adversarial)
# =============================================================================

PROSECUTOR_PROMPT = """
You are the PROSECUTOR in the Automaton Auditor Digital Courtroom.

## Your Role:
- Be adversarial, skeptical, and detail-oriented
- Seek security vulnerabilities, architectural flaws, evidence of negligence
- Challenge claims that lack irrefutable forensic evidence
- Score harshly when evidence is circumstantial or missing

## Scoring Guidelines:
- Score 5: Only for irrefutable evidence of excellence with zero gaps
- Score 4: Strong evidence with minor, non-critical gaps
- Score 3: Adequate but with notable gaps or inconsistencies
- Score 2: Significant gaps, potential security or reliability concerns
- Score 1: Critical flaws, missing core requirements, or negligence

## CRITICAL: Evidence Source Mapping
For each criterion, evaluate based on the PRIMARY evidence source:

| Criterion | Primary Evidence Source |
|-----------|----------------------|
| git_forensic_analysis | repo_investigator |
| state_management_rigor | repo_investigator |
| graph_orchestration | repo_investigator |
| safe_tool_engineering | repo_investigator |
| structured_output_enforcement | repo_investigator |
| judicial_nuance | repo_investigator |
| chief_justice_synthesis | repo_investigator |
| theoretical_depth | doc_analyst |
| report_accuracy | doc_analyst + repo_investigator |
| swarm_visual | vision_inspector |

⚠️ IMPORTANT: For graph_orchestration, evaluate SOLELY based on RepoInvestigator evidence.
Do NOT penalize for missing PDF evidence when evaluating graph structure.

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
# DEFENSE PROMPT (Optimistic)
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
(See table in Prosecutor prompt - same mapping applies)

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
# TECH LEAD PROMPT (Pragmatic)
# =============================================================================

TECH_LEAD_PROMPT = """
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
(See table in Prosecutor prompt - same mapping applies)

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
# HELPER FUNCTIONS
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
    PRIMARY_SOURCES = {
        "git_forensic_analysis": "repo_investigator",
        "state_management_rigor": "repo_investigator",
        "graph_orchestration": "repo_investigator",
        "safe_tool_engineering": "repo_investigator",
        "structured_output_enforcement": "repo_investigator",
        "judicial_nuance": "repo_investigator",
        "chief_justice_synthesis": "repo_investigator",
        "theoretical_depth": "doc_analyst",
        "report_accuracy": "doc_analyst",
        "swarm_visual": "vision_inspector",
    }
    
    source = PRIMARY_SOURCES.get(criterion_id, "repo_investigator")
    source_evidence = evidences.get(source, [])
    criterion_evidence = [e for e in source_evidence if e.goal == criterion_id]
    
    if criterion_evidence:
        return criterion_evidence[0].content, source
    elif source_evidence:
        return source_evidence[0].content, source
    else:
        return "No evidence available for this criterion.", source

def _invoke_judge_llm(prompt: str, judge_name: str, criterion_id: str) -> JudicialOpinion:
    """
    Invoke LLM for judge evaluation with LangSmith tracing.
    
    Tracing is automatically enabled when LANGCHAIN_TRACING_V2=true is set
    in environment variables. No explicit context manager needed.
    
    Args:
        prompt: Formatted prompt for the judge
        judge_name: Name of the judge persona (for tracing metadata)
        criterion_id: Rubric dimension being evaluated
        
    Returns:
        JudicialOpinion with score, argument, and cited evidence
    """
    try:
        # Initialize LLM - tracing auto-attached via env vars
        llm = _get_llm_with_tracing()
        
        # Create structured output parser
        parser = PydanticOutputParser(pydantic_object=JudicialOpinionSchema)
        
        # Create prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a judicial evaluator. Respond ONLY with valid JSON matching the schema."),
            ("user", "{prompt}\n\n{format_instructions}")
        ])
        
        # Format prompt with parser instructions
        formatted_prompt = chat_prompt.format(
            prompt=prompt,
            format_instructions=parser.get_format_instructions()
        )
        
        # Invoke LLM - tracing automatically enabled via LANGCHAIN_TRACING_V2=true
        response = llm.invoke(formatted_prompt)
        
        # Parse structured output
        parsed = parser.parse(response.content)
        
        # Convert to JudicialOpinion model
        return JudicialOpinion(
            judge=judge_name,
            criterion_id=criterion_id,
            score=parsed.score,
            argument=parsed.argument,
            cited_evidence=parsed.cited_evidence
        )
        
    except Exception as e:
        # Fallback opinion if LLM call fails
        return JudicialOpinion(
            judge=judge_name,
            criterion_id=criterion_id,
            score=3,
            argument=f"LLM evaluation failed: {str(e)}. Using default neutral score.",
            cited_evidence=["error_fallback"]
        )


# =============================================================================
# JUDGE NODES (LangGraph-Compatible Functions with Tracing)
# =============================================================================

def prosecutor_node(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
    """
    Judicial Protocol: Adversarial Evaluation.
    
    Tracing: All LLM invocations are logged to LangSmith with:
    - Prompt content
    - Response content
    - Token usage and latency
    - Judge persona metadata
    """
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    opinions: List[JudicialOpinion] = []
    
    for dimension in rubric_dimensions:
        criterion_id = dimension.get("id")
        criterion_name = dimension.get("name")
        primary_content, primary_source = _get_primary_evidence(evidences, criterion_id)
        
        evidence_header = EVIDENCE_HEADER.format(
            repo_evidence=_format_evidence_for_prompt(evidences, "repo_investigator"),
            doc_evidence=_format_evidence_for_prompt(evidences, "doc_analyst"),
            vision_evidence=_format_evidence_for_prompt(evidences, "vision_inspector"),
            aggregator_evidence=_format_evidence_for_prompt(evidences, "evidence_aggregator")
        )
        
        prompt = PROSECUTOR_PROMPT.format(
            evidence_header=evidence_header,
            criterion_name=criterion_name,
            primary_evidence_content=primary_content
        )
        
        # Invoke LLM with tracing (replaces placeholder)
        opinion = _invoke_judge_llm(prompt, "Prosecutor", criterion_id)
        opinions.append(opinion)
    
    return {"opinions": {"prosecutor": opinions}}


def defense_node(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
    """
    Judicial Protocol: Optimistic Evaluation.
    
    Tracing: All LLM invocations are logged to LangSmith with:
    - Prompt content
    - Response content
    - Token usage and latency
    - Judge persona metadata
    """
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    opinions: List[JudicialOpinion] = []
    
    for dimension in rubric_dimensions:
        criterion_id = dimension.get("id")
        criterion_name = dimension.get("name")
        primary_content, primary_source = _get_primary_evidence(evidences, criterion_id)
        
        evidence_header = EVIDENCE_HEADER.format(
            repo_evidence=_format_evidence_for_prompt(evidences, "repo_investigator"),
            doc_evidence=_format_evidence_for_prompt(evidences, "doc_analyst"),
            vision_evidence=_format_evidence_for_prompt(evidences, "vision_inspector"),
            aggregator_evidence=_format_evidence_for_prompt(evidences, "evidence_aggregator")
        )
        
        prompt = DEFENSE_PROMPT.format(
            evidence_header=evidence_header,
            criterion_name=criterion_name,
            primary_evidence_content=primary_content
        )
        
        # Invoke LLM with tracing (replaces placeholder)
        opinion = _invoke_judge_llm(prompt, "Defense", criterion_id)
        opinions.append(opinion)
    
    return {"opinions": {"defense": opinions}}


def tech_lead_node(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
    """
    Judicial Protocol: Pragmatic Evaluation.
    
    Tracing: All LLM invocations are logged to LangSmith with:
    - Prompt content
    - Response content
    - Token usage and latency
    - Judge persona metadata
    """
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    opinions: List[JudicialOpinion] = []
    
    for dimension in rubric_dimensions:
        criterion_id = dimension.get("id")
        criterion_name = dimension.get("name")
        primary_content, primary_source = _get_primary_evidence(evidences, criterion_id)
        
        evidence_header = EVIDENCE_HEADER.format(
            repo_evidence=_format_evidence_for_prompt(evidences, "repo_investigator"),
            doc_evidence=_format_evidence_for_prompt(evidences, "doc_analyst"),
            vision_evidence=_format_evidence_for_prompt(evidences, "vision_inspector"),
            aggregator_evidence=_format_evidence_for_prompt(evidences, "evidence_aggregator")
        )
        
        prompt = TECH_LEAD_PROMPT.format(
            evidence_header=evidence_header,
            criterion_name=criterion_name,
            primary_evidence_content=primary_content
        )
        
        # Invoke LLM with tracing (replaces placeholder)
        opinion = _invoke_judge_llm(prompt, "TechLead", criterion_id)
        opinions.append(opinion)
    
    return {"opinions": {"techlead": opinions}}


def judge_aggregator_node(state: AgentState) -> Dict[str, Any]:
    """
    Synchronization Node: Collects all judge opinions before Chief Justice.
    
    Note: This node does not invoke LLMs, so no tracing is needed.
    It only aggregates existing opinions from judge nodes.
    """
    opinions = state.get("opinions", {})
    errors = state.get("errors", [])
    
    opinion_counts = {judge: len(opinion_list) for judge, opinion_list in opinions.items()}
    required_judges = ["prosecutor", "defense", "techlead"]
    missing_judges = [j for j in required_judges if j not in opinion_counts]
    
    if missing_judges:
        errors.append(f"Missing opinions from judges: {missing_judges}")
    
    aggregator_opinion = JudicialOpinion(
        judge="Aggregator",
        criterion_id="evidence_validation",
        score=5 if not missing_judges else 2,
        argument=f"Collected opinions from {len(opinion_counts)}/3 judges",
        cited_evidence=list(opinion_counts.keys())
    )
    
    return {"opinions": {"aggregator": [aggregator_opinion]}, "errors": errors}