"""Neo4j schema setup: uniqueness constraints and property indexes."""

import logging

from neo4j import Session

logger = logging.getLogger(__name__)

CONSTRAINTS: list[str] = [
    "CREATE CONSTRAINT tactic_id IF NOT EXISTS FOR (t:Tactic) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT technique_id IF NOT EXISTS FOR (t:Technique) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT mitigation_id IF NOT EXISTS FOR (m:Mitigation) REQUIRE m.id IS UNIQUE",
    "CREATE CONSTRAINT case_study_id IF NOT EXISTS FOR (c:CaseStudy) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT attack_step_id IF NOT EXISTS FOR (s:AttackStep) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT owasp_id IF NOT EXISTS FOR (o:OWASPRisk) REQUIRE o.id IS UNIQUE",
    "CREATE CONSTRAINT regulatory_id IF NOT EXISTS FOR (r:RegulatoryArticle) REQUIRE r.id IS UNIQUE",
]

INDEXES: list[str] = [
    "CREATE INDEX technique_platform IF NOT EXISTS FOR (t:Technique) ON (t.platforms)",
    "CREATE INDEX technique_maturity IF NOT EXISTS FOR (t:Technique) ON (t.maturity)",
    "CREATE INDEX mitigation_lifecycle IF NOT EXISTS FOR (m:Mitigation) ON (m.lifecycle_phases)",
]


def create_constraints(session: Session) -> int:
    """Execute uniqueness constraints on all node types."""
    for stmt in CONSTRAINTS:
        name = stmt.split("CONSTRAINT ")[1].split(" IF")[0]
        logger.info("Creating constraint: %s", name)
        session.run(stmt)
    return len(CONSTRAINTS)


def create_indexes(session: Session) -> int:
    """Execute property indexes for query performance."""
    for stmt in INDEXES:
        name = stmt.split("INDEX ")[1].split(" IF")[0]
        logger.info("Creating index: %s", name)
        session.run(stmt)
    return len(INDEXES)


def apply_schema(session: Session) -> None:
    """Apply all constraints and indexes. Idempotent — safe to rerun."""
    constraint_count = create_constraints(session)
    index_count = create_indexes(session)
    logger.info(
        "Schema applied: %d constraints, %d indexes",
        constraint_count,
        index_count,
    )
