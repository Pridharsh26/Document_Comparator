import logging
from typing import List

from models.schemas import ComparisonResult, RuleChange
from utils.helpers import normalize_text

logger = logging.getLogger(__name__)


def generate_plain_language_impact(change: RuleChange) -> str:
    parts = []
    if change.change_type.value == "MODIFIED":
        parts.append("This rule has been modified.")
        if change.what_changed:
            for numeric in change.what_changed:
                parts.append(
                    f"A numeric value changed from {numeric.old_value} to {numeric.new_value}."
                )
    elif change.change_type.value == "ADDED":
        parts.append("A new rule has been added.")
    elif change.change_type.value == "REMOVED":
        parts.append("A rule has been removed.")
    return " ".join(parts)


def build_narrative_report(comparison: ComparisonResult) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("EXECUTIVE SUMMARY")
    lines.append("=" * 60)
    lines.append(
        f"Total Legacy Rules: {comparison.summary.total_legacy_rules} | "
        f"Total Modernized Rules: {comparison.summary.total_modernized_rules}"
    )
    lines.append(
        f"Added: {comparison.summary.added} | Removed: {comparison.summary.removed} | "
        f"Modified: {comparison.summary.modified} | Unchanged: {comparison.summary.unchanged}"
    )
    lines.append("")
    lines.append("OVERALL STATISTICS")
    lines.append("-" * 60)
    lines.append(f"Added Rules: {comparison.summary.added}")
    lines.append(f"Removed Rules: {comparison.summary.removed}")
    lines.append(f"Modified Rules: {comparison.summary.modified}")
    lines.append("")
    lines.append("ADDED RULES")
    lines.append("-" * 60)
    added = [c for c in comparison.changes if c.change_type.value == "ADDED"]
    if not added:
        lines.append("No added rules detected.")
    for idx, change in enumerate(added, 1):
        lines.append(f"{idx}. {change.modernized_rule}")
    lines.append("")
    lines.append("REMOVED RULES")
    lines.append("-" * 60)
    removed = [c for c in comparison.changes if c.change_type.value == "REMOVED"]
    if not removed:
        lines.append("No removed rules detected.")
    for idx, change in enumerate(removed, 1):
        lines.append(f"{idx}. {change.legacy_rule}")
    lines.append("")
    lines.append("MODIFIED RULES")
    lines.append("-" * 60)
    modified = [c for c in comparison.changes if c.change_type.value == "MODIFIED"]
    if not modified:
        lines.append("No modified rules detected.")
    for idx, change in enumerate(modified, 1):
        lines.append(f"Change {idx}:")
        lines.append(f"  Old: {change.legacy_rule}")
        lines.append(f"  New: {change.modernized_rule}")
        if change.what_changed:
            for numeric in change.what_changed:
                lines.append(f"  Numeric change: {numeric.old_value} -> {numeric.new_value}")
    lines.append("")
    lines.append("DETAILED IMPACT ANALYSIS")
    lines.append("-" * 60)
    for idx, change in enumerate(comparison.changes, 1):
        lines.append(f"Impact {idx}: {change.change_type.value}")
        explanation = change.business_explanation or generate_plain_language_impact(change)
        lines.append(f"  Explanation: {explanation}")
        lines.append(f"  Impact Level: {change.impact_level}")
        lines.append(f"  Risk Level: {change.risk_level}")
        lines.append(f"  Priority Level: {change.priority_level}")
        if change.affected_parties:
            lines.append(f"  Affected Parties: {', '.join(change.affected_parties)}")
        if change.benefits:
            lines.append(f"  Benefits: {'; '.join(change.benefits)}")
        if change.drawbacks:
            lines.append(f"  Drawbacks: {'; '.join(change.drawbacks)}")
        if change.recommendations:
            lines.append(f"  Recommendations: {'; '.join(change.recommendations)}")
    lines.append("")
    lines.append("BUSINESS RECOMMENDATIONS")
    lines.append("-" * 60)
    if comparison.business_recommendations:
        for rec in comparison.business_recommendations:
            lines.append(f"- {rec}")
    else:
        lines.append("Review modified rules with stakeholders and update relevant SOPs.")
    lines.append("")
    lines.append("RISK ASSESSMENT")
    lines.append("-" * 60)
    lines.append(comparison.risk_assessment or "Medium risk due to policy and numeric changes.")
    lines.append("=" * 60)
    lines.append("CONCLUSION")
    lines.append("=" * 60)
    lines.append(
        f"A total of {len(comparison.changes)} meaningful changes were detected. "
        "Please review the modified rules and plan accordingly."
    )
    return "\n".join(lines)
