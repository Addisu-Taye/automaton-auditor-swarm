"""
src/nodes/justice.py

Chief Justice Synthesis Engine
Production Module - Automaton Auditor Swarm v3.0.0

Node:
- chief_justice_node: Deterministic synthesis of judicial opinions into final report

Compliance:
- Protocol C.1: Deterministic Synthesis Rules (hardcoded Python logic)
- Protocol C.2: Conflict Resolution (score variance handling)
- Protocol C.3: Executive Reporting (structured Markdown output)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import re

from src.state import JudicialOpinion, AgentState, Evidence


# =============================================================================
# CHIEF JUSTICE SYNTHESIS RULES (Deterministic Python Logic)
# =============================================================================

class SynthesisRules:
    """Hardcoded rules for Chief Justice conflict resolution."""
    
    @staticmethod
    def rule_of_security(prosecutor_score: int, security_evidence: List[str]) -> Optional[int]:
        """
        Rule 1: Security Override
        If Prosecutor identifies confirmed security vulnerability, cap score at 3.
        """
        security_keywords = ["security", "vulnerability", "injection", "auth", "credential", "exposure"]
        has_security_issue = any(
            kw in evidence.lower() 
            for evidence in security_evidence 
            for kw in security_keywords
        )
        
        if has_security_issue and prosecutor_score <= 2:
            return min(3, prosecutor_score)
        return None
    
    @staticmethod
    def rule_of_evidence(defense_claim: str, repo_evidence: List[Evidence]) -> Optional[bool]:
        """
        Rule 2: Fact Supremacy
        If Defense claims feature exists but RepoInvestigator found no evidence, overrule Defense.
        """
        # Extract claimed features from defense argument
        claimed_features = re.findall(r'"([^"]+)"|\'([^\']+)\'', defense_claim)
        claimed_features = [f[0] or f[1] for f in claimed_features]
        
        # Check if any claimed feature is contradicted by repo evidence
        for claim in claimed_features:
            if not claim:
                continue
            evidence_contradicts = any(
                claim.lower() in e.content.lower() and not e.found
                for e in repo_evidence
            )
            if evidence_contradicts:
                return False  # Overrule defense claim
        return None  # No contradiction found
    
    @staticmethod
    def rule_of_functionality(techlead_score: int, parallel_evidence: bool) -> int:
        """
        Rule 3: Functionality Weight
        If TechLead confirms parallel architecture, boost architecture-related scores.
        """
        if parallel_evidence and techlead_score >= 4:
            return min(5, techlead_score + 1)
        return techlead_score
    
    @staticmethod
    def rule_of_variance(scores: List[int], threshold: int = 2) -> bool:
        """
        Rule 4: Dissent Detection
        If score variance exceeds threshold, flag for re-evaluation.
        """
        if len(scores) < 2:
            return False
        return max(scores) - min(scores) > threshold


# =============================================================================
# HELPER FUNCTIONS (Defined before main function for proper scope)
# =============================================================================

def _apply_synthesis_rules(
    scores: List[int],
    arguments: Dict[str, str],
    cited: Dict[str, List[str]],
    evidences: Dict[str, List[Evidence]],
    criterion_id: str,
    judge_ops: List[JudicialOpinion]  # Added parameter to fix scope issue
) -> int:
    """Apply deterministic synthesis rules to determine final score."""
    
    # Start with median score (robust to outliers)
    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    if n % 2 == 0:
        base_score = (sorted_scores[n//2 - 1] + sorted_scores[n//2]) // 2
    else:
        base_score = sorted_scores[n//2]
    
    # Rule 1: Security Override
    security_evidence = cited.get("Prosecutor", [])
    security_cap = SynthesisRules.rule_of_security(
        arguments.get("Prosecutor", ""), 
        security_evidence
    )
    if security_cap is not None:
        base_score = min(base_score, security_cap)
    
    # Rule 2: Fact Supremacy (for report_accuracy criterion)
    if criterion_id == "report_accuracy":
        defense_claim = arguments.get("Defense", "")
        repo_evidence = evidences.get("repo_investigator", [])
        fact_check = SynthesisRules.rule_of_evidence(defense_claim, repo_evidence)
        if fact_check is False:
            # Reduce score if defense claim contradicted by evidence
            base_score = max(1, base_score - 1)
    
    # Rule 3: Functionality Weight (for graph_orchestration)
    if criterion_id == "graph_orchestration":
        # Check if parallel evidence exists in repo_investigator
        repo_evidence = evidences.get("repo_investigator", [])
        parallel_evidence = any(
            "Parallel: True" in e.content or "parallel_detected" in e.content.lower()
            for e in repo_evidence
        )
        # Get TechLead score safely
        techlead_score = base_score
        for op in judge_ops:
            if op.judge == "TechLead":
                techlead_score = op.score
                break
        base_score = SynthesisRules.rule_of_functionality(base_score, parallel_evidence)
    
    # Rule 4: Variance-based adjustment (minor)
    if SynthesisRules.rule_of_variance(scores):
        # High variance suggests ambiguity; lean conservative
        base_score = min(base_score, max(scores) - 1)
    
    return max(1, min(5, base_score))  # Clamp to 1-5


def _generate_dissent_summary(opinions: List[JudicialOpinion]) -> str:
    """Generate summary when judge scores diverge significantly."""
    scores = {op.judge: op.score for op in opinions}
    if not scores:
        return "No judge opinions available for dissent analysis."
    
    max_judge = max(scores, key=scores.get)
    min_judge = min(scores, key=scores.get)
    
    return (
        f"Significant dissent detected: {max_judge} scored {scores[max_judge]}/5 "
        f"while {min_judge} scored {scores[min_judge]}/5. "
        f"This {scores[max_judge] - scores[min_judge]}-point variance suggests "
        f"ambiguous evidence or legitimate architectural trade-offs."
    )


def _generate_remediation(
    criterion_name: str,
    score: int,
    opinions: List[JudicialOpinion]
) -> str:
    """Generate actionable remediation based on score and judge feedback."""
    
    if score >= 4:
        return f"✅ {criterion_name} meets expectations. Consider documenting best practices for team reference."
    elif score == 3:
        return f"⚠️ {criterion_name} is adequate but has room for improvement. Review judge feedback for specific enhancements."
    else:
        # Extract common themes from low-scoring opinions
        concerns = [
            op.argument for op in opinions 
            if op.score <= 2 and ("missing" in op.argument.lower() or "lack" in op.argument.lower())
        ]
        if concerns:
            return f"❌ Critical: {concerns[0][:200]}... Prioritize addressing this before production deployment."
        return f"❌ {criterion_name} requires significant improvement. Review all judge opinions for remediation guidance."


def _generate_executive_summary(
    overall_score: float,
    criteria_count: int,
    criteria: List[Dict]
) -> str:
    """Generate executive summary text."""
    
    # Count score distribution
    excellent = sum(1 for c in criteria if c["final_score"] >= 5)
    good = sum(1 for c in criteria if 3 <= c["final_score"] < 5)
    needs_work = sum(1 for c in criteria if c["final_score"] < 3)
    
    # Determine priority message
    if needs_work > 0:
        priority = f"⚠️ SECURITY CONCERNS IDENTIFIED - Immediate remediation required." if any(
            "security" in c["remediation"].lower() for c in criteria
        ) else f"Priority: Address {needs_work} critical criteria before production deployment."
    elif good > excellent:
        priority = "Ready for staging with minor refinements."
    else:
        priority = "Production-ready with optional optimizations."
    
    return (
        f"Overall Score: {overall_score:.2f}/5.0. Criteria Evaluated: {criteria_count}. "
        f"Excellent (5): {excellent}, Good (3-4): {good}, Needs Improvement (1-2): {needs_work}. "
        f"{priority}"
    )


def _generate_remediation_plan(criteria: List[Dict]) -> str:
    """Generate prioritized remediation plan in Markdown."""
    
    # Sort by score ascending (lowest first = highest priority)
    sorted_criteria = sorted(criteria, key=lambda c: c["final_score"])
    
    lines = ["# Prioritized Remediation Plan\n"]
    
    for i, crit in enumerate(sorted_criteria[:5], 1):  # Top 5 priorities
        score_emoji = "❌" if crit["final_score"] <= 2 else "⚠️" if crit["final_score"] <= 3 else "✅"
        lines.append(f"## Priority {i}: {crit['dimension_name']} (Score: {crit['final_score']}/5)")
        lines.append(f"{score_emoji} **Issue:** {crit['remediation']}\n")
    
    if len(criteria) > 5:
        lines.append(f"*...and {len(criteria) - 5} additional criteria with lower priority*\n")
    
    lines.append("---\n*Remediation priorities based on: score severity, security impact, and production readiness*")
    
    return "\n".join(lines)


def _serialize_to_markdown(
    repo_url: str,
    executive_summary: str,
    overall_score: float,
    criteria: List[Dict],
    remediation_plan: str
) -> str:
    """Serialize final report to executive-grade Markdown."""
    
    lines = [
        f"# Audit Report: {repo_url}\n",
        "## Executive Summary",
        executive_summary,
        "",
        f"**Overall Score:** {overall_score:.2f}/5.0\n",
        "## Criterion Breakdown\n"
    ]
    
    for crit in criteria:
        lines.append(f"### {crit['dimension_name']}")
        lines.append(f"**Final Score:** {crit['final_score']}/5\n")
        lines.append("**Judge Opinions:**\n")
        
        for op in crit["judge_opinions"]:
            lines.append(f"- **{op['judge']}** (Score: {op['score']}): {op['argument']}")
            if op.get("cited_evidence"):
                lines.append(f"  - Cited: {', '.join(op['cited_evidence'])}")
            lines.append("")
        
        if crit.get("dissent_summary"):
            lines.append(f"**Dissent Summary:** {crit['dissent_summary']}\n")
        
        lines.append(f"**Remediation:** {crit['remediation']}\n")
        lines.append("---\n")
    
    lines.append("## Remediation Plan\n")
    lines.append(remediation_plan)
    
    # Add footer with UTC timestamp
    lines.extend([
        "",
        "---",
        f"*Report generated by Automaton Auditor Swarm v3.0.0*",
        f"*Timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"*Methodology: Dialectical synthesis via Prosecutor/Defense/TechLead personas*"
    ])
    
    return "\n".join(lines)


# =============================================================================
# CHIEF JUSTICE NODE (Main Entry Point - Renamed to match graph.py imports)
# =============================================================================

def chief_justice_node(state: AgentState) -> Dict[str, Any]:
    """
    Synthesis Protocol: Chief Justice Final Report Generation.
    
    Aggregates judicial opinions using deterministic rules and generates
    an executive-grade Markdown audit report.
    
    Deterministic Rules Applied:
    1. Rule of Security: Security vulnerabilities cap scores at 3
    2. Rule of Evidence: Factual evidence overrides optimistic claims
    3. Rule of Functionality: Confirmed parallelism boosts architecture scores
    4. Rule of Variance: Score divergence >2 triggers dissent summary
    
    Args:
        state: AgentState with 'opinions', 'evidences', 'rubric_dimensions'
        
    Returns:
        Dictionary with 'final_report' containing structured audit results
    """
    opinions = state.get("opinions", {})
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])
    repo_url = state.get("repo_url", "Unknown")
    
    # Collect opinions by criterion
    criteria_opinions: Dict[str, List[JudicialOpinion]] = {}
    
    for judge_name, judge_opinions in opinions.items():
        if judge_name == "aggregator":
            continue
        for opinion in judge_opinions:
            cid = opinion.criterion_id
            if cid not in criteria_opinions:
                criteria_opinions[cid] = []
            criteria_opinions[cid].append(opinion)
    
    # Synthesize final scores and reports per criterion
    final_criteria = []
    overall_scores = []
    
    for dimension in rubric_dimensions:
        cid = dimension.get("id")
        cname = dimension.get("name")
        
        judge_ops = criteria_opinions.get(cid, [])
        if not judge_ops:
            continue
        
        # Extract scores and arguments
        scores = [op.score for op in judge_ops]
        arguments = {op.judge: op.argument for op in judge_ops}
        cited = {op.judge: op.cited_evidence for op in judge_ops}
        
        # Apply synthesis rules (pass judge_ops to fix scope issue)
        final_score = _apply_synthesis_rules(
            scores, arguments, cited, evidences, cid, judge_ops
        )
        overall_scores.append(final_score)
        
        # Check for dissent
        dissent_summary = None
        if SynthesisRules.rule_of_variance(scores):
            dissent_summary = _generate_dissent_summary(judge_ops)
        
        # Generate remediation
        remediation = _generate_remediation(cname, final_score, judge_ops)
        
        final_criteria.append({
            "dimension_id": cid,
            "dimension_name": cname,
            "final_score": final_score,
            "judge_opinions": [op.model_dump() for op in judge_ops],
            "dissent_summary": dissent_summary,
            "remediation": remediation
        })
    
    # Calculate overall score (weighted average)
    overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
    
    # Generate executive summary
    executive_summary = _generate_executive_summary(
        overall_score, len(final_criteria), final_criteria
    )
    
    # Generate prioritized remediation plan
    remediation_plan = _generate_remediation_plan(final_criteria)
    
    # Generate full markdown report
    report_markdown = _serialize_to_markdown(
        repo_url=repo_url,
        executive_summary=executive_summary,
        overall_score=overall_score,
        criteria=final_criteria,
        remediation_plan=remediation_plan
    )
    
    return {
        "final_report": {
            "repo_url": repo_url,
            "executive_summary": executive_summary,
            "overall_score": round(overall_score, 2),
            "criteria_evaluated": len(final_criteria),
            "criteria": final_criteria,
            "remediation_plan": remediation_plan
        },
        "report_markdown": report_markdown
    }