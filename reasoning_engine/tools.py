"""Graph query primitives for the ATLAS reasoning engine."""

import atexit
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver

logger = logging.getLogger(__name__)

_driver: Optional[Driver] = None

WRITE_PATTERN = re.compile(
    r"\b(MERGE|CREATE|SET|DELETE|REMOVE|DROP|ADD)\b", re.IGNORECASE
)


def _init_driver() -> Driver:
    """Lazily initialize a module-level Neo4j driver from dotenv."""
    global _driver
    if _driver is not None:
        return _driver

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        raise EnvironmentError(
            "Missing NEO4J_URI, NEO4J_USER, or NEO4J_PASSWORD in .env"
        )

    _driver = GraphDatabase.driver(uri, auth=(user, password))
    atexit.register(_driver.close)
    logger.info("Neo4j driver initialized at %s", uri)
    return _driver


def _to_python(value: Any) -> Any:
    """Recursively convert Neo4j types to JSON-serializable Python."""
    from neo4j.graph import Node, Relationship, Path as Neo4jPath
    import neo4j.time

    if isinstance(value, dict):
        return {k: _to_python(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_python(v) for v in value]
    if isinstance(value, Node):
        return {
            "labels": list(value.labels),
            "properties": _to_python(dict(value)),
        }
    if isinstance(value, Relationship):
        return {
            "type": value.type,
            "properties": _to_python(dict(value)),
        }
    if isinstance(value, Neo4jPath):
        return {
            "nodes": [_to_python(n) for n in value.nodes],
            "relationships": [_to_python(r) for r in value.relationships],
        }
    if isinstance(value, neo4j.time.DateTime):
        return value.iso_format()
    if isinstance(value, (neo4j.time.Date, neo4j.time.Time, neo4j.time.Duration)):
        return str(value)
    return value


def _send_query(
    cypher: str, params: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Execute a Cypher query and return a result dict."""
    driver = _init_driver()
    with driver.session() as session:
        try:
            result = session.run(cypher, params or {})
            records = [_to_python(record.data()) for record in result]
            return {"status": "success", "records": records}
        except Exception as e:
            return {"status": "error", "error_message": str(e)}


def _is_write_query(query: str) -> bool:
    """Check if a Cypher query contains write operations."""
    return WRITE_PATTERN.search(query) is not None


# ── Tool 1: Schema introspection ──────────────────────────────────────


def get_physical_schema() -> dict[str, Any]:
    """Returns the full ATLAS knowledge graph schema: all node labels,
    relationship types, and their properties.

    ALWAYS call this first before any investigation. Never assume the
    schema from training data — always inspect it from the live graph.
    """
    labels = _send_query("CALL db.labels() YIELD label RETURN label")
    rel_types = _send_query(
        "CALL db.relationshipTypes() YIELD relationshipType "
        "RETURN relationshipType"
    )
    node_props = _send_query(
        "CALL db.schema.nodeTypeProperties() "
        "YIELD nodeType, propertyName, propertyTypes "
        "RETURN nodeType, propertyName, propertyTypes"
    )
    rel_props = _send_query(
        "CALL db.schema.relTypeProperties() "
        "YIELD relType, propertyName, propertyTypes "
        "RETURN relType, propertyName, propertyTypes"
    )
    return {
        "status": "success",
        "schema": {
            "node_labels": labels.get("records", []),
            "relationship_types": rel_types.get("records", []),
            "node_properties": node_props.get("records", []),
            "relationship_properties": rel_props.get("records", []),
        },
    }


# ── Tool 2: Count and summarize ───────────────────────────────────────


def count_and_summarize(
    label: str, property_name: Optional[str] = None
) -> dict[str, Any]:
    """Get node count and optional property value distribution for a label.

    Use this to understand data scale and what property values exist
    before writing filtering queries.

    Args:
        label: Node label, e.g. Technique, Mitigation, Tactic, CaseStudy.
        property_name: Optional property to show value frequency, e.g.
            platforms, maturity, lifecycle_phases, categories.
    """
    count_result = _send_query(
        f"MATCH (n:`{label}`) RETURN count(n) AS count"
    )
    count = 0
    if count_result.get("records"):
        count = count_result["records"][0].get("count", 0)

    distribution: list[dict] = []
    if property_name:
        dist_result = _send_query(
            f"MATCH (n:`{label}`) "
            f"UNWIND n.`{property_name}` AS val "
            f"RETURN val, count(*) AS frequency "
            f"ORDER BY frequency DESC LIMIT 20"
        )
        distribution = dist_result.get("records", [])

    return {
        "status": "success",
        "label": label,
        "count": count,
        "distribution": distribution,
    }


# ── Tool 3: Neighbor traversal ────────────────────────────────────────


def get_node_neighbors(
    node_id: str,
    label: str,
    relationship_type: Optional[str] = None,
    depth: int = 1,
) -> dict[str, Any]:
    """Find nodes connected to a specific ATLAS entity.

    Args:
        node_id: ATLAS ID, e.g. AML.T0054, AML.TA0002, AML.CS0012, LLM01.
        label: Node label, e.g. Technique, Tactic, Mitigation, CaseStudy.
        relationship_type: Optional filter, e.g. MITIGATES, ACHIEVES,
            MAPS_TO, LEADS_TO, SATISFIES, USES, STEP_OF, IN_TACTIC.
        depth: Traversal hops (1-3, default 1).
    """
    depth = max(1, min(depth, 3))
    rel_filter = f":{relationship_type}" if relationship_type else ""
    query = (
        f"MATCH path = (n:`{label}` {{id: $node_id}})"
        f"-[r{rel_filter}*1..{depth}]-(neighbor) "
        f"RETURN labels(neighbor)[0] AS label, "
        f"neighbor.id AS id, neighbor.name AS name, "
        f"type(last(relationships(path))) AS via, "
        f"length(path) AS hops "
        f"LIMIT 50"
    )
    return _send_query(query, {"node_id": node_id})


# ── Tool 4: Path finding ──────────────────────────────────────────────


def find_paths_between(
    source_id: str,
    source_label: str,
    target_id: str,
    target_label: str,
    max_depth: int = 5,
) -> dict[str, Any]:
    """Find shortest paths connecting two nodes in the ATLAS graph.

    Use this when asked how two entities relate indirectly — e.g. how a
    CaseStudy connects to a RegulatoryArticle through the graph.

    Args:
        source_id: ID of the start node, e.g. AML.CS0012.
        source_label: Label of the start node, e.g. CaseStudy.
        target_id: ID of the end node, e.g. EU_AIA_Art15.
        target_label: Label of the end node, e.g. RegulatoryArticle.
        max_depth: Maximum path length in hops (1-6, default 5).
    """
    max_depth = max(1, min(max_depth, 6))
    query = (
        f"MATCH path = shortestPath("
        f"(s:`{source_label}` {{id: $source_id}})"
        f"-[*1..{max_depth}]-"
        f"(t:`{target_label}` {{id: $target_id}}))"
        f" RETURN [n IN nodes(path) | n.name] AS node_names,"
        f" [n IN nodes(path) | n.id] AS node_ids,"
        f" [r IN relationships(path) | type(r)] AS rel_types,"
        f" length(path) AS path_length"
        f" LIMIT 5"
    )
    return _send_query(query, {"source_id": source_id, "target_id": target_id})


# ── Tool 5: Arbitrary read-only Cypher ────────────────────────────────


def read_neo4j_cypher(
    query: str, params: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Execute any read-only Cypher query against the ATLAS graph.

    Use for complex aggregations, multi-hop patterns, or anything not
    covered by the other tools. Always include LIMIT (default 25).
    Use parameterised queries — pass values in params dict, not f-strings.

    Args:
        query: A read-only Cypher query string.
        params: Optional parameters dict for the query.
    """
    if _is_write_query(query):
        return {
            "status": "error",
            "error_message": "Write operations are not permitted "
            "in the reasoning engine.",
        }
    return _send_query(query, params)


# ── Tool 6: Investigation completion ──────────────────────────────────


def finished(answer: str) -> str:
    """Signal that the investigation is complete and deliver the final answer.

    Call this ONLY after you have made at least 3 tool calls and have
    sufficient graph evidence to fully support your answer.

    The answer must:
    - Cite every technique, mitigation, and case study with its ATLAS ID
    - Embed [Q1], [Q2]... markers after every factual claim, where the
      number refers to the tool call that produced that fact
    - Note coverage gaps (techniques with no mitigations) explicitly
    - Not contain any technique names or IDs not found in query results

    Args:
        answer: The complete, grounded, cited threat assessment or response.
    """
    return answer
