"""Parse ATLAS YAML and ingest nodes + edges into Neo4j."""

import logging
from pathlib import Path
from typing import Any

import yaml
from neo4j import Session

logger = logging.getLogger(__name__)

REQUIRED_TOP_LEVEL_KEYS = {
    "tactics",
    "techniques",
    "mitigations",
    "case-studies",
    "relationships",
}

# ── Batched Cypher templates (UNWIND for single-transaction ingestion) ──

BATCH_MERGE_TACTICS = """
UNWIND $items AS item
MERGE (t:Tactic {id: item.id})
SET t.name          = item.name,
    t.description   = item.description,
    t.attack_ref_id = item.attack_ref_id,
    t.created_date  = item.created_date,
    t.modified_date = item.modified_date
"""

BATCH_MERGE_TECHNIQUES = """
UNWIND $items AS item
MERGE (t:Technique {id: item.id})
SET t.name            = item.name,
    t.description     = item.description,
    t.platforms       = item.platforms,
    t.maturity        = item.maturity,
    t.is_subtechnique = false,
    t.attack_ref_id   = item.attack_ref_id,
    t.created_date    = item.created_date,
    t.modified_date   = item.modified_date
"""

BATCH_MERGE_MITIGATIONS = """
UNWIND $items AS item
MERGE (m:Mitigation {id: item.id})
SET m.name             = item.name,
    m.description      = item.description,
    m.lifecycle_phases  = item.lifecycle_phases,
    m.categories        = item.categories,
    m.created_date      = item.created_date,
    m.modified_date     = item.modified_date
"""

BATCH_MERGE_CASE_STUDIES = """
UNWIND $items AS item
MERGE (cs:CaseStudy {id: item.id})
SET cs.name          = item.name,
    cs.description   = item.description,
    cs.type          = item.type,
    cs.actor         = item.actor,
    cs.target        = item.target,
    cs.date          = item.date,
    cs.reporter      = item.reporter,
    cs.created_date  = item.created_date,
    cs.modified_date = item.modified_date
"""

BATCH_MERGE_ACHIEVES = """
UNWIND $items AS item
MATCH (tech:Technique {id: item.source})
MATCH (tac:Tactic {id: item.target})
MERGE (tech)-[:ACHIEVES]->(tac)
"""

BATCH_MERGE_SPECIALIZES = """
UNWIND $items AS item
MATCH (sub:Technique {id: item.source})
MATCH (parent:Technique {id: item.target})
MERGE (sub)-[:SPECIALIZES]->(parent)
SET sub.is_subtechnique = true
"""

BATCH_MERGE_MITIGATES = """
UNWIND $items AS item
MATCH (m:Mitigation {id: item.source})
MATCH (t:Technique {id: item.target})
MERGE (m)-[r:MITIGATES]->(t)
SET r.description = item.description
"""

MERGE_ATTACK_STEP = """
MERGE (s:AttackStep {id: $step_id})
SET s.step_id     = $raw_step_id,
    s.description = $description,
    s.tactic_id   = $tactic_id
WITH s
MATCH (cs:CaseStudy {id: $cs_id})
MERGE (s)-[:STEP_OF]->(cs)
WITH s
MATCH (t:Technique {id: $technique_id})
MERGE (s)-[:USES]->(t)
WITH s
MATCH (tac:Tactic {id: $tactic_id})
MERGE (s)-[:IN_TACTIC]->(tac)
"""

MERGE_LEADS_TO = """
MATCH (src:AttackStep {id: $src_id})
MATCH (tgt:AttackStep {id: $tgt_id})
MERGE (src)-[:LEADS_TO]->(tgt)
"""


# ── YAML loading ─────────────────────────────────────────────────────


def load_yaml(path: Path) -> dict[str, Any]:
    """Load and parse the ATLAS YAML file."""
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    missing = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"YAML missing required top-level keys: {missing}")

    return data


# ── Helpers ──────────────────────────────────────────────────────────


def _str(value: Any) -> str:
    """Convert a value to string, handling dates that PyYAML parses as datetime.date."""
    if value is None:
        return ""
    return str(value)


def _get_attack_ref_id(entity: dict[str, Any]) -> str:
    """Extract ATT&CK reference ID if present."""
    ref = entity.get("attack-reference")
    if ref and isinstance(ref, dict):
        return ref.get("id", "")
    return ""


# ── Node ingestion (batched) ────────────────────────────────────────


def ingest_tactics(session: Session, tactics: dict[str, dict]) -> int:
    """Ingest all tactic nodes in a single batched transaction."""
    items = [
        {
            "id": tactic_id,
            "name": tactic["name"],
            "description": tactic.get("description", ""),
            "attack_ref_id": _get_attack_ref_id(tactic),
            "created_date": _str(tactic.get("created-date")),
            "modified_date": _str(tactic.get("modified-date")),
        }
        for tactic_id, tactic in tactics.items()
    ]
    session.run(BATCH_MERGE_TACTICS, items=items)
    logger.info("Ingested %d tactics", len(items))
    return len(items)


def ingest_techniques(session: Session, techniques: dict[str, dict]) -> int:
    """Ingest all technique nodes in a single batched transaction."""
    items = [
        {
            "id": tech_id,
            "name": tech["name"],
            "description": tech.get("description", ""),
            "platforms": tech.get("platforms", []),
            "maturity": tech.get("maturity", ""),
            "attack_ref_id": _get_attack_ref_id(tech),
            "created_date": _str(tech.get("created-date")),
            "modified_date": _str(tech.get("modified-date")),
        }
        for tech_id, tech in techniques.items()
    ]
    session.run(BATCH_MERGE_TECHNIQUES, items=items)
    logger.info("Ingested %d techniques", len(items))
    return len(items)


def ingest_mitigations(session: Session, mitigations: dict[str, dict]) -> int:
    """Ingest all mitigation nodes in a single batched transaction."""
    items = [
        {
            "id": mit_id,
            "name": mit["name"],
            "description": mit.get("description", ""),
            "lifecycle_phases": mit.get("lifecycle-phases", []),
            "categories": mit.get("categories", []),
            "created_date": _str(mit.get("created-date")),
            "modified_date": _str(mit.get("modified-date")),
        }
        for mit_id, mit in mitigations.items()
    ]
    session.run(BATCH_MERGE_MITIGATIONS, items=items)
    logger.info("Ingested %d mitigations", len(items))
    return len(items)


def ingest_case_studies(session: Session, case_studies: dict[str, dict]) -> int:
    """Ingest all case study nodes in a single batched transaction."""
    items = []
    for cs_id, cs in case_studies.items():
        reporter = cs.get("reporter", "")
        if not reporter:
            logger.debug("Case study %s has no reporter field", cs_id)

        items.append({
            "id": cs_id,
            "name": cs["name"],
            "description": cs.get("description", ""),
            "type": cs.get("type", ""),
            "actor": cs.get("actor", ""),
            "target": cs.get("target", ""),
            "date": _str(cs.get("date")),
            "reporter": reporter or "",
            "created_date": _str(cs.get("created-date")),
            "modified_date": _str(cs.get("modified-date")),
        })

    session.run(BATCH_MERGE_CASE_STUDIES, items=items)
    logger.info("Ingested %d case studies", len(items))
    return len(items)


# ── Relationship ingestion ───────────────────────────────────────────


def _ingest_achieves(session: Session, entries: list[dict]) -> int:
    """Create ACHIEVES edges in a single batch."""
    items = [{"source": e["source"], "target": e["target"]} for e in entries]
    session.run(BATCH_MERGE_ACHIEVES, items=items)
    return len(items)


def _ingest_specializes(session: Session, entries: list[dict]) -> int:
    """Create SPECIALIZES edges and set is_subtechnique=true in a single batch."""
    items = [{"source": e["source"], "target": e["target"]} for e in entries]
    session.run(BATCH_MERGE_SPECIALIZES, items=items)
    return len(items)


def _ingest_mitigates(session: Session, entries: list[dict]) -> int:
    """Create MITIGATES edges with description in a single batch."""
    items = [
        {
            "source": e["source"],
            "target": e["target"],
            "description": e.get("description", ""),
        }
        for e in entries
    ]
    session.run(BATCH_MERGE_MITIGATES, items=items)
    return len(items)


def _ingest_employs(session: Session, cs_id: str, entries: list[dict]) -> int:
    """Two-pass ingestion of a case study's attack chain.

    Pass 1: create AttackStep nodes + STEP_OF, USES, IN_TACTIC edges.
    Pass 2: resolve leads-to into LEADS_TO edges between steps.

    Attack steps are ingested individually (not UNWIND) because the
    MERGE_ATTACK_STEP query creates the node and three edges in one
    statement — UNWIND with multiple MATCHes and MERGEs on different
    node types can cause cartesian product issues in Neo4j.
    """
    # Pass 1: create all AttackStep nodes
    for entry in entries:
        step_node_id = f"{cs_id}_{entry['step-id']}"

        tactic_id = entry.get("tactic", "")
        technique_id = entry.get("target", "")
        if not tactic_id:
            logger.warning(
                "Attack step %s has no tactic — IN_TACTIC edge will be missing",
                step_node_id,
            )
        if not technique_id:
            logger.warning(
                "Attack step %s has no target technique — USES edge will be missing",
                step_node_id,
            )

        session.run(
            MERGE_ATTACK_STEP,
            step_id=step_node_id,
            raw_step_id=entry["step-id"],
            description=entry.get("description", ""),
            tactic_id=tactic_id,
            cs_id=cs_id,
            technique_id=technique_id,
        )

    # Pass 2: create LEADS_TO edges (all target nodes now exist)
    for entry in entries:
        source_node_id = f"{cs_id}_{entry['step-id']}"
        leads_to = entry.get("leads-to") or []
        for next_step_id in leads_to:
            target_node_id = f"{cs_id}_{next_step_id}"
            session.run(
                MERGE_LEADS_TO,
                src_id=source_node_id,
                tgt_id=target_node_id,
            )

    return len(entries)


def ingest_relationships(
    session: Session, relationships: dict[str, dict]
) -> dict[str, int]:
    """Ingest all relationships, collecting entries by type for batching."""
    all_achieves: list[dict] = []
    all_specializes: list[dict] = []
    all_mitigates: list[dict] = []
    employs_by_cs: dict[str, list[dict]] = {}
    sequences_count = 0

    for entity_id, rel_types in relationships.items():
        for rel_type, entries in rel_types.items():
            if rel_type == "achieves":
                all_achieves.extend(entries)
            elif rel_type == "specializes":
                all_specializes.extend(entries)
            elif rel_type == "mitigates":
                all_mitigates.extend(entries)
            elif rel_type == "employs":
                employs_by_cs[entity_id] = entries
            elif rel_type == "sequences":
                sequences_count += len(entries)
            else:
                logger.warning("Unknown relationship type: %s", rel_type)

    counts: dict[str, int] = {
        "achieves": _ingest_achieves(session, all_achieves),
        "specializes": _ingest_specializes(session, all_specializes),
        "mitigates": _ingest_mitigates(session, all_mitigates),
        "employs": sum(
            _ingest_employs(session, cs_id, entries)
            for cs_id, entries in employs_by_cs.items()
        ),
        "sequences_skipped": sequences_count,
    }

    logger.info("Relationship counts: %s", counts)
    return counts
