"""Post-load validation: count nodes/edges and verify graph integrity."""

import logging

from neo4j import Session
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)

NODE_LABELS = ["Tactic", "Technique", "Mitigation", "CaseStudy", "AttackStep"]
EDGE_TYPES = [
    "ACHIEVES",
    "SPECIALIZES",
    "MITIGATES",
    "STEP_OF",
    "USES",
    "IN_TACTIC",
    "LEADS_TO",
]

EXPECTED_NODE_COUNTS: dict[str, int] = {
    "Tactic": 16,
    "Technique": 170,
    "Mitigation": 35,
    "CaseStudy": 57,
}

EXPECTED_SUBTECHNIQUE_COUNT = 69


def count_nodes(session: Session) -> dict[str, int]:
    """Count all node types in the graph."""
    counts: dict[str, int] = {}
    for label in NODE_LABELS:
        # Neo4j labels cannot be passed as parameters — f-string is required here.
        result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
        counts[label] = result.single()["count"]
    return counts


def count_edges(session: Session) -> dict[str, int]:
    """Count all relationship types in the graph."""
    counts: dict[str, int] = {}
    for edge_type in EDGE_TYPES:
        # Neo4j relationship types cannot be passed as parameters.
        result = session.run(
            f"MATCH ()-[r:{edge_type}]->() RETURN count(r) AS count"
        )
        counts[edge_type] = result.single()["count"]
    return counts


def count_subtechniques(session: Session) -> int:
    """Count techniques where is_subtechnique=true."""
    result = session.run(
        "MATCH (t:Technique) WHERE t.is_subtechnique = true "
        "RETURN count(t) AS count"
    )
    return result.single()["count"]


def check_orphans(session: Session) -> dict[str, int]:
    """Check for parent techniques with no ACHIEVES and mitigations with no MITIGATES."""
    results: dict[str, int] = {}

    r = session.run(
        "MATCH (t:Technique) "
        "WHERE NOT (t)-[:ACHIEVES]->() AND NOT t.is_subtechnique "
        "RETURN count(t) AS count"
    )
    results["techniques_no_achieves"] = r.single()["count"]

    r = session.run(
        "MATCH (m:Mitigation) "
        "WHERE NOT (m)-[:MITIGATES]->() "
        "RETURN count(m) AS count"
    )
    results["mitigations_no_mitigates"] = r.single()["count"]

    return results


def check_attack_step_consistency(session: Session) -> dict[str, int]:
    """Check that every AttackStep has STEP_OF, USES, and IN_TACTIC edges."""
    results: dict[str, int] = {}

    r = session.run(
        "MATCH (s:AttackStep) WHERE NOT (s)-[:STEP_OF]->(:CaseStudy) "
        "RETURN count(s) AS count"
    )
    results["steps_no_step_of"] = r.single()["count"]

    r = session.run(
        "MATCH (s:AttackStep) WHERE NOT (s)-[:USES]->(:Technique) "
        "RETURN count(s) AS count"
    )
    results["steps_no_uses"] = r.single()["count"]

    r = session.run(
        "MATCH (s:AttackStep) WHERE NOT (s)-[:IN_TACTIC]->(:Tactic) "
        "RETURN count(s) AS count"
    )
    results["steps_no_in_tactic"] = r.single()["count"]

    r = session.run(
        "MATCH (cs:CaseStudy) WHERE NOT (:AttackStep)-[:STEP_OF]->(cs) "
        "RETURN count(cs) AS count"
    )
    results["case_studies_no_steps"] = r.single()["count"]

    return results


def validate(session: Session) -> bool:
    """Run all validation checks, print summary, raise if core counts are zero."""
    console = Console()
    node_counts = count_nodes(session)
    edge_counts = count_edges(session)
    sub_count = count_subtechniques(session)
    orphans = check_orphans(session)
    step_consistency = check_attack_step_consistency(session)

    parent_count = node_counts.get("Technique", 0) - sub_count
    warnings: list[str] = []

    # Build summary table
    table = Table(title="Validation Report", show_header=False)
    table.add_column("Item", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Status")

    table.add_section()
    for label, count in node_counts.items():
        extra = ""
        if label == "Technique":
            extra = f"  ({parent_count} parent + {sub_count} sub)"

        status = ""
        if label in EXPECTED_NODE_COUNTS:
            expected = EXPECTED_NODE_COUNTS[label]
            if count != expected:
                status = f"EXPECTED {expected}"
                warnings.append(f"{label}: got {count}, expected {expected}")
            else:
                status = "OK"
        table.add_row(label, str(count) + extra, status)

    if sub_count != EXPECTED_SUBTECHNIQUE_COUNT:
        warnings.append(
            f"Subtechniques: got {sub_count}, expected {EXPECTED_SUBTECHNIQUE_COUNT}"
        )

    table.add_section()
    for edge_type, count in edge_counts.items():
        table.add_row(edge_type + " edges", str(count), "")

    table.add_section()
    for check_name, count in orphans.items():
        status = "OK" if count == 0 else f"WARNING: {count}"
        table.add_row(check_name, str(count), status)

    table.add_section()
    for check_name, count in step_consistency.items():
        status = "OK" if count == 0 else f"WARNING: {count}"
        if count > 0:
            warnings.append(f"{check_name}: {count} orphaned")
        table.add_row(check_name, str(count), status)

    console.print(table)

    # Fail loudly if any core count is zero
    for label in ["Tactic", "Technique", "Mitigation", "CaseStudy", "AttackStep"]:
        if node_counts.get(label, 0) == 0:
            raise ValueError(
                f"Validation failed: {label} count is 0 — ingestion likely broke"
            )

    for warning in warnings:
        logger.warning("Validation: %s", warning)

    if warnings:
        console.print(
            f"[bold yellow]{len(warnings)} validation warning(s) — see above[/bold yellow]"
        )

    logger.info("Validation passed")
    return True
