from src.state import AgentState, JudicialOpinion
from typing import List


def chief_justice_node(state: AgentState) -> AgentState:
    """
    Synthesis Engine: Resolves dialectical conflict.
    Implements Hardcoded Rules (Security Override, Fact Supremacy).
    """
    opinions = state.get("opinions", [])
    
    # Rule of Security: Check for security flags in Prosecutor opinion
    security_flaw = any(
        "Security Negligence" in op.argument 
        for op in opinions 
        if op.judge == "Prosecutor"
    )
    
    # Rule of Evidence: Check for Hallucination
    hallucination = any(
        "Hallucination" in op.argument 
        for op in opinions 
        if op.judge == "Prosecutor"
    )
    
    final_score = 0
    dissent_summary = ""
    
    # Simple aggregation logic for template (Expand for production)
    if opinions:
        scores = [op.score for op in opinions]
        final_score = sum(scores) // len(scores)
        
        # Dissent Requirement
        scores_vari = max(scores) - min(scores)
        if scores_vari > 2:
            dissent_summary = "Significant disagreement detected between Prosecutor and Defense."
    
    # Security Override
    if security_flaw and final_score > 3:
        final_score = 3
        dissent_summary += " Score capped due to Security Negligence."

    report = f"""# Audit Report
## Verdict
Final Score: {final_score}/5

## Dissent
{dissent_summary}

## Remediation Plan
1. Review src/tools for sandboxing.
2. Verify Pydantic models in state.
"""
    
    return {"final_report": report}
