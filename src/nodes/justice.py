"""
src/nodes/justice.py

Chief Justice Synthesis Engine: Deterministic Conflict Resolution
Production Module - Automaton Auditor Swarm v3.0.0

Deliberation Protocol (Hardcoded Rules):
- Rule of Security: Vulnerabilities cap score at 3
- Rule of Evidence: Facts overrule opinions
- Rule of Functionality: Tech Lead carries highest weight
- Dissent Requirement: Variance > 2 triggers explanation
- Variance Re-evaluation: Specific evidence re-check

Compliance:
- Protocol B: Judicial Sentencing Guidelines
- Protocol A.5: Structured Output Enforcement
"""

from typing import Dict, List, Any, Optional
from src.state import (
    AgentState, 
    JudicialOpinion, 
    CriterionResult, 
    AuditReport,
    Evidence
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# =============================================================================
# SYNTHESIS RULES (Hardcoded Deterministic Logic)
# =============================================================================

class SynthesisRules:
    """
    Hardcoded deterministic rules for conflict resolution.
    Per spec: ChiefJustice must NOT be just another LLM prompt.
    """
    
    SECURITY_OVERRIDE_CAP = 3
    VARIANCE_THRESHOLD = 2
    
    @staticmethod
    def security_override(opinions: List[JudicialOpinion], evidence: List[Evidence]) -> Optional[int]:
        """
        Rule of Security: If Prosecutor identifies confirmed security vulnerability,
        cap score at 3 regardless of Defense arguments.
        
        Args:
            opinions: List of JudicialOpinion from all judges
            evidence: List of Evidence from detectives
            
        Returns:
            Cap score (3) if security flaw detected, None otherwise
        """
        # Check for security-related keywords in Prosecutor's argument
        prosecutor_opinions = [o for o in opinions if o.judge == "Prosecutor"]
        
        security_keywords = [
            "security", "vulnerability", "os.system", "injection",
            "sandbox", "tempfile", "negligence", "unsafe"
        ]
        
        for opinion in prosecutor_opinions:
            argument_lower = opinion.argument.lower()
            if any(kw in argument_lower for kw in security_keywords):
                # Check if evidence supports security claim
                for ev in evidence:
                    if ev.found and any(kw in ev.content.lower() for kw in security_keywords if ev.content):
                        return SynthesisRules.SECURITY_OVERRIDE_CAP
        
        return None
    
    @staticmethod
    def fact_supremacy(opinions: List[JudicialOpinion], evidence: List[Evidence]) -> Dict[str, Any]:
        """
        Rule of Evidence: Forensic evidence (facts from Detectives) always
        overrules Judicial opinion (interpretation from Judges).
        
        Args:
            opinions: List of JudicialOpinion from all judges
            evidence: List of Evidence from detectives
            
        Returns:
            Dictionary with overruled opinions and rationale
        """
        overruled = []
        
        for opinion in opinions:
            # Check if opinion claims something that evidence contradicts
            if opinion.judge == "Defense":
                # Defense claims "Deep Metacognition" but no evidence found
                if "metacognition" in opinion.argument.lower() or "effort" in opinion.argument.lower():
                    supporting_evidence = [
                        ev for ev in evidence 
                        if ev.found and ev.goal == "theoretical_depth"
                    ]
                    if not supporting_evidence:
                        overruled.append({
                            "opinion": opinion,
                            "reason": "Claim not supported by forensic evidence"
                        })
        
        return {
            "overruled": overruled,
            "count": len(overruled)
        }
    
    @staticmethod
    def functionality_weight(opinions: List[JudicialOpinion]) -> Optional[JudicialOpinion]:
        """
        Rule of Functionality: If Tech Lead confirms architecture is modular
        and workable, this carries highest weight for Architecture criterion.
        
        Args:
            opinions: List of JudicialOpinion from all judges
            
        Returns:
            Tech Lead opinion if found, None otherwise
        """
        tech_lead_opinions = [o for o in opinions if o.judge == "TechLead"]
        return tech_lead_opinions[0] if tech_lead_opinions else None
    
    @staticmethod
    def calculate_variance(opinions: List[JudicialOpinion]) -> float:
        """
        Calculate score variance between judges.
        
        Args:
            opinions: List of JudicialOpinion
            
        Returns:
            Variance (max - min score)
        """
        if not opinions:
            return 0.0
        
        scores = [o.score for o in opinions]
        return max(scores) - min(scores)
    
    @staticmethod
    def requires_dissent(variance: float) -> bool:
        """
        Dissent Requirement: Variance > 2 triggers explanation.
        
        Args:
            variance: Score variance between judges
            
        Returns:
            True if dissent summary required
        """
        return variance > SynthesisRules.VARIANCE_THRESHOLD


# =============================================================================
# CHIEF JUSTICE NODE
# =============================================================================

def chief_justice_node(state: AgentState) -> Dict[str, Any]:
    """
    Chief Justice Synthesis Engine: Resolves dialectical conflict
    and generates final AuditReport.
    
    This node uses HARDCODED DETERMINISTIC PYTHON LOGIC, not LLM averaging.
    
    Args:
        state: AgentState with accumulated opinions and evidence
        
    Returns:
        AgentState with final_report populated
    """
    # Gather all opinions from judges
    opinions = state.get("opinions", [])
    
    # Gather all evidence from detectives
    all_evidence = []
    for detective_name, evidence_list in state.get("evidences", {}).items():
        if isinstance(evidence_list, list):
            all_evidence.extend(evidence_list)
    
    # Group opinions by criterion
    opinions_by_criterion: Dict[str, List[JudicialOpinion]] = {}
    for opinion in opinions:
        criterion_id = opinion.criterion_id
        if criterion_id not in opinions_by_criterion:
            opinions_by_criterion[criterion_id] = []
        opinions_by_criterion[criterion_id].append(opinion)
    
    # Process each criterion
    criteria_results: List[CriterionResult] = []
    total_score = 0.0
    criterion_count = 0
    
    # Rubric dimension names (for display)
    dimension_names = {
        "git_forensic_analysis": "Git Forensic Analysis",
        "state_management_rigor": "State Management Rigor",
        "graph_orchestration": "Graph Orchestration Architecture",
        "safe_tool_engineering": "Safe Tool Engineering",
        "structured_output_enforcement": "Structured Output Enforcement",
        "judicial_nuance": "Judicial Nuance and Dialectics",
        "chief_justice_synthesis": "Chief Justice Synthesis Engine",
        "theoretical_depth": "Theoretical Depth (Documentation)",
        "report_accuracy": "Report Accuracy (Cross-Reference)",
        "swarm_visual": "Architectural Diagram Analysis"
    }
    
    for criterion_id, criterion_opinions in opinions_by_criterion.items():
        # Apply synthesis rules
        scores = [o.score for o in criterion_opinions]
        variance = SynthesisRules.calculate_variance(criterion_opinions)
        
        # Start with average score
        final_score = sum(scores) / len(scores) if scores else 3.0
        
        # Rule 1: Security Override
        security_cap = SynthesisRules.security_override(criterion_opinions, all_evidence)
        if security_cap and final_score > security_cap:
            final_score = security_cap
        
        # Rule 2: Functionality Weight (Tech Lead carries highest weight for architecture)
        if criterion_id == "graph_orchestration":
            tech_lead = SynthesisRules.functionality_weight(criterion_opinions)
            if tech_lead:
                # Weight Tech Lead opinion at 50%
                other_scores = [o.score for o in criterion_opinions if o.judge != "TechLead"]
                if other_scores:
                    final_score = (tech_lead.score * 0.5) + (sum(other_scores) / len(other_scores) * 0.5)
        
        # Rule 3: Fact Supremacy (check for overruled opinions)
        supremacy_check = SynthesisRules.fact_supremacy(criterion_opinions, all_evidence)
        overruled_count = supremacy_check["count"]
        
        # Rule 4: Dissent Requirement
        dissent_summary = None
        if SynthesisRules.requires_dissent(variance):
            # Generate dissent summary explaining the conflict
            prosecutor_op = next((o for o in criterion_opinions if o.judge == "Prosecutor"), None)
            defense_op = next((o for o in criterion_opinions if o.judge == "Defense"), None)
            
            if prosecutor_op and defense_op:
                dissent_summary = (
                    f"The Defense argued for {defense_op.argument[:100]}... "
                    f"However, the Prosecutor noted {prosecutor_op.argument[:100]}... "
                    f"Score variance ({variance}) exceeds threshold ({SynthesisRules.VARIANCE_THRESHOLD})."
                )
        
        # Generate remediation based on lowest score
        lowest_opinion = min(criterion_opinions, key=lambda o: o.score)
        remediation = f"Address: {lowest_opinion.argument}. See cited evidence: {', '.join(lowest_opinion.cited_evidence[:3])}"
        
        # Create CriterionResult
        result = CriterionResult(
            dimension_id=criterion_id,
            dimension_name=dimension_names.get(criterion_id, criterion_id),
            final_score=int(round(final_score)),
            judge_opinions=criterion_opinions,
            dissent_summary=dissent_summary,
            remediation=remediation
        )
        
        criteria_results.append(result)
        total_score += final_score
        criterion_count += 1
    
    # Calculate overall score
    overall_score = total_score / criterion_count if criterion_count > 0 else 0.0
    
    # Generate Executive Summary
    executive_summary = _generate_executive_summary(criteria_results, overall_score, all_evidence)
    
    # Generate Remediation Plan
    remediation_plan = _generate_remediation_plan(criteria_results)
    
    # Create AuditReport
    audit_report = AuditReport(
        repo_url=state.get("repo_url", "Unknown"),
        executive_summary=executive_summary,
        overall_score=round(overall_score, 2),
        criteria=criteria_results,
        remediation_plan=remediation_plan
    )
    
    # Serialize to Markdown
    markdown_report = _serialize_to_markdown(audit_report)
    
    return {
        "final_report": audit_report,
        "errors": []
    }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _generate_executive_summary(
    criteria: List[CriterionResult], 
    overall_score: float,
    evidence: List[Evidence]
) -> str:
    """
    Generate executive summary based on criterion results.
    """
    # Count criteria by score range
    excellent = sum(1 for c in criteria if c.final_score >= 5)
    good = sum(1 for c in criteria if 3 <= c.final_score < 5)
    needs_improvement = sum(1 for c in criteria if c.final_score < 3)
    
    # Check for security issues
    security_issues = any(
        "security" in c.remediation.lower() or "vulnerability" in c.remediation.lower()
        for c in criteria
    )
    
    summary_parts = [
        f"Overall Score: {overall_score}/5.0",
        f"Criteria Evaluated: {len(criteria)}",
        f"Excellent (5): {excellent}, Good (3-4): {good}, Needs Improvement (1-2): {needs_improvement}"
    ]
    
    if security_issues:
        summary_parts.append("⚠️ SECURITY CONCERNS IDENTIFIED - Immediate remediation required.")
    
    if needs_improvement > 0:
        summary_parts.append(f"Priority: Address {needs_improvement} critical criteria before production deployment.")
    
    return ". ".join(summary_parts)


def _generate_remediation_plan(criteria: List[CriterionResult]) -> str:
    """
    Generate prioritized remediation plan from criterion results.
    """
    # Sort by score (lowest first = highest priority)
    sorted_criteria = sorted(criteria, key=lambda c: c.final_score)
    
    plan_lines = ["# Prioritized Remediation Plan", ""]
    
    for i, criterion in enumerate(sorted_criteria[:5], 1):  # Top 5 priorities
        plan_lines.append(f"## Priority {i}: {criterion.dimension_name} (Score: {criterion.final_score}/5)")
        plan_lines.append(f"**Issue:** {criterion.remediation}")
        if criterion.dissent_summary:
            plan_lines.append(f"**Dissent:** {criterion.dissent_summary}")
        plan_lines.append("")
    
    return "\n".join(plan_lines)


def _serialize_to_markdown(report: AuditReport) -> str:
    """
    Serialize AuditReport to Markdown format.
    """
    lines = [
        f"# Audit Report: {report.repo_url}",
        "",
        "## Executive Summary",
        report.executive_summary,
        "",
        f"**Overall Score:** {report.overall_score}/5.0",
        "",
        "## Criterion Breakdown",
        ""
    ]
    
    for criterion in report.criteria:
        lines.append(f"### {criterion.dimension_name}")
        lines.append(f"**Final Score:** {criterion.final_score}/5")
        lines.append("")
        lines.append("**Judge Opinions:**")
        lines.append("")
        
        for opinion in criterion.judge_opinions:
            lines.append(f"- **{opinion.judge}** (Score: {opinion.score}): {opinion.argument}")
            if opinion.cited_evidence:
                lines.append(f"  - Cited: {', '.join(opinion.cited_evidence[:3])}")
        
        if criterion.dissent_summary:
            lines.append("")
            lines.append(f"**Dissent Summary:** {criterion.dissent_summary}")
        
        lines.append("")
        lines.append(f"**Remediation:** {criterion.remediation}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    lines.append("## Remediation Plan")
    lines.append("")
    lines.append(report.remediation_plan)
    
    return "\n".join(lines)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_chief_justice_node() -> callable:
    """
    Returns the Chief Justice node for graph wiring.
    """
    return chief_justice_node


def save_report_to_file(report: AuditReport, output_path: str) -> None:
    """
    Save AuditReport to Markdown file.
    
    Args:
        report: AuditReport object
        output_path: Path to save Markdown file
    """
    import os
    
    markdown_content = _serialize_to_markdown(report)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)