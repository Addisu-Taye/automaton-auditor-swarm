"""
src/nodes/judges.py

Judicial Layer: Dialectical Bench with Three Distinct Personas
Production Module - Automaton Auditor Swarm v3.0.0

Personas:
- Prosecutor: "Trust No One. Assume Vibe Coding." (Adversarial)
- Defense: "Reward Effort and Intent." (Optimistic)
- Tech Lead: "Does it actually work?" (Pragmatic)

Compliance:
- Protocol B: Judicial Sentencing Guidelines
- Protocol A.5: Structured Output Enforcement
"""

from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.state import JudicialOpinion, AgentState, Evidence
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_llm_with_structured_output():
    """
    Factory function for LLM with structured output enforcement.
    Returns ChatOpenAI bound to JudicialOpinion Pydantic schema.
    """
    return ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(JudicialOpinion)


# =============================================================================
# PERSONA PROMPTS (Must be <50% overlapping text)
# =============================================================================

PROSECUTOR_PROMPT = """
You are the PROSECUTOR in the Digital Courtroom.

CORE PHILOSOPHY: "Trust No One. Assume Vibe Coding."

YOUR ROLE:
- Scrutinize evidence for gaps, security flaws, and laziness
- Look for bypassed structure and orchestration fraud
- Charge "Hallucination Liability" if outputs lack Pydantic validation
- Argue for Score 1 if parallel orchestration is missing
- Be adversarial and critical

SENTENCING GUIDELINES:
- If StateGraph is linear (not parallel): Max Score = 1 for "LangGraph Architecture"
- If Judges return freeform text (no Pydantic): Max Score = 2 for "Judicial Nuance"
- If os.system() used without sandboxing: Flag as "Security Negligence"

EVIDENCE TO CITE:
- Always cite specific file paths and line numbers from the Evidence objects
- Reference the exact rubric criterion ID

OUTPUT FORMAT:
- Return a JudicialOpinion Pydantic model with:
  - judge: "Prosecutor"
  - criterion_id: The rubric dimension being evaluated
  - score: 1-5 (be harsh on security/orchestration flaws)
  - argument: Your critical reasoning
  - cited_evidence: List of file paths/locations from Evidence
"""

DEFENSE_PROMPT = """
You are the DEFENSE ATTORNEY in the Digital Courtroom.

CORE PHILOSOPHY: "Reward Effort and Intent. Look for the Spirit of the Law."

YOUR ROLE:
- Highlight creative workarounds, deep thought, and effort
- Argue for higher scores based on "Engineering Process"
- Look at Git History for signs of iteration and struggle
- Mitigate minor syntax errors if underlying logic is sophisticated
- Be optimistic and forgiving

SENTENCING GUIDELINES:
- If AST parsing is sophisticated but graph fails to compile: Argue Score 3 for "Forensic Accuracy"
- If Judge personas are distinct but synthesis lacks rigor: Argue Score 3-4 for "Judicial Nuance"
- If commits show iterative development: Boost score based on "Engineering Process"

EVIDENCE TO CITE:
- Reference git history showing progression
- Highlight theoretical depth in PDF report
- Note creative solutions even if imperfect

OUTPUT FORMAT:
- Return a JudicialOpinion Pydantic model with:
  - judge: "Defense"
  - criterion_id: The rubric dimension being evaluated
  - score: 1-5 (be generous on effort/intent)
  - argument: Your optimistic reasoning
  - cited_evidence: List of file paths/locations from Evidence
"""

TECH_LEAD_PROMPT = """
You are the TECH LEAD in the Digital Courtroom.

CORE PHILOSOPHY: "Does it actually work? Is it maintainable?"

YOUR ROLE:
- Evaluate architectural soundness and practical viability
- Focus on artifacts, not "vibe" or "struggle"
- Verify operator.add/ior reducers prevent data overwriting
- Assess technical debt and code cleanliness
- Be the tie-breaker between Prosecutor and Defense

SENTENCING GUIDELINES:
- If Pydantic used but dicts elsewhere: Score = 3 ("Technical Debt")
- If tooling is sandboxed and safe: Full credit for "Safe Tool Engineering"
- If architecture is modular and workable: Highest weight for "Graph Orchestration"

EVIDENCE TO CITE:
- Reference specific reducer usage in state.py
- Note security controls in tools (tempfile, error handling)
- Assess maintainability of code structure

OUTPUT FORMAT:
- Return a JudicialOpinion Pydantic model with:
  - judge: "TechLead"
  - criterion_id: The rubric dimension being evaluated
  - score: 1-5 (realistic, based on artifacts)
  - argument: Your pragmatic reasoning
  - cited_evidence: List of file paths/locations from Evidence
"""


# =============================================================================
# JUDGE NODE FACTORY
# =============================================================================

def create_judge_node(persona: str, system_prompt: str):
    """
    Factory function to create judge nodes with distinct personas.
    
    Args:
        persona: Name of the judge persona ("Prosecutor", "Defense", "TechLead")
        system_prompt: System prompt defining the persona's philosophy
        
    Returns:
        LangGraph node function that returns JudicialOpinion
    """
    
    def judge_node(state: AgentState) -> Dict[str, List[JudicialOpinion]]:
        """
        Judicial Protocol: Analyze evidence through persona lens.
        Must return structured JudicialOpinion via Pydantic validation.
        """
        # Initialize LLM with structured output
        llm = get_llm_with_structured_output()
        
        # Gather all evidence from detectives
        all_evidence = []
        for detective_name, evidence_list in state.get("evidences", {}).items():
            if isinstance(evidence_list, list):
                all_evidence.extend(evidence_list)
        
        # Format evidence for context
        evidence_text = "\n".join([
            f"- [{e.goal}] {e.location}: {e.content or 'No content'} (Confidence: {e.confidence})"
            for e in all_evidence
        ])
        
        # Get rubric dimensions (if provided)
        rubric_dimensions = state.get("rubric_dimensions", [])
        criterion_list = "\n".join([f"- {d['id']}: {d['name']}" for d in rubric_dimensions[:5]])
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """
EVIDENCE COLLECTED BY DETECTIVES:
{evidence}

RUBRIC DIMENSIONS TO EVALUATE:
{criteria}

TASK:
For EACH rubric criterion above, render a JudicialOpinion with:
- score (1-5)
- argument (your reasoning through your persona lens)
- cited_evidence (file paths from the evidence above)

Return ONE JudicialOpinion for the most critical criterion.
"""),
        ])
        
        # Create chain
        chain = prompt | llm
        
        # Invoke LLM
        try:
            result = chain.invoke({
                "evidence": evidence_text if evidence_text else "No evidence collected",
                "criteria": criterion_list if criterion_list else "No rubric provided"
            })
            
            # Ensure result is a list
            if isinstance(result, JudicialOpinion):
                opinions = [result]
            elif isinstance(result, list):
                opinions = result if result else [JudicialOpinion(
                    judge=persona,
                    criterion_id="general",
                    score=3,
                    argument="No specific criterion evaluated",
                    cited_evidence=[]
                )]
            else:
                opinions = [JudicialOpinion(
                    judge=persona,
                    criterion_id="general",
                    score=3,
                    argument="Unexpected output format",
                    cited_evidence=[]
                )]
            
            return {"opinions": opinions}
            
        except Exception as e:
            # Fallback opinion on error
            fallback = JudicialOpinion(
                judge=persona,
                criterion_id="error",
                score=3,
                argument=f"Judge node encountered error: {str(e)}",
                cited_evidence=[]
            )
            return {"opinions": [fallback]}
    
    return judge_node


# =============================================================================
# INSTANTIATE JUDGE PERSONAS
# =============================================================================

prosecutor_node = create_judge_node("Prosecutor", PROSECUTOR_PROMPT)
defense_node = create_judge_node("Defense", DEFENSE_PROMPT)
tech_lead_node = create_judge_node("TechLead", TECH_LEAD_PROMPT)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_all_judge_nodes() -> Dict[str, callable]:
    """
    Returns all judge nodes as a dictionary for graph wiring.
    """
    return {
        "prosecutor": prosecutor_node,
        "defense": defense_node,
        "tech_lead": tech_lead_node
    }


def calculate_score_variance(opinions: List[JudicialOpinion]) -> float:
    """
    Calculate variance between judge scores for dissent detection.
    
    Args:
        opinions: List of JudicialOpinion objects
        
    Returns:
        Variance (max - min score)
    """
    if not opinions:
        return 0.0
    
    scores = [o.score for o in opinions]
    return max(scores) - min(scores)