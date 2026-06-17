"""Entrypoint: load ATLAS data into Neo4j (schema -> parse -> validate)."""

import logging
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = PROJECT_ROOT / "data" / "ATLAS-2026.05.yaml"

sys.path.insert(0, str(PROJECT_ROOT))

from ingest.parse import (
    ingest_case_studies,
    ingest_mitigations,
    ingest_relationships,
    ingest_tactics,
    ingest_techniques,
    load_yaml,
)
from ingest.schema import apply_schema
from ingest.validate import validate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_env_var(name: str) -> str:
    """Read a required environment variable."""
    import os

    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required env var: {name}. Check .env file.")
    return value


def main() -> None:
    """Load ATLAS data into Neo4j: schema -> parse -> validate."""
    console = Console()
    start = time.time()

    load_dotenv(PROJECT_ROOT / ".env")
    uri = _get_env_var("NEO4J_URI")
    user = _get_env_var("NEO4J_USER")
    password = _get_env_var("NEO4J_PASSWORD")

    console.print(f"[bold]Connecting to Neo4j at {uri}...[/bold]")

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()
        console.print("[green]Connected.[/green]")

        with driver.session() as session:
            console.print("\n[bold]1. Applying schema constraints and indexes...[/bold]")
            apply_schema(session)

            console.print("\n[bold]2. Loading YAML data...[/bold]")
            if not YAML_PATH.exists():
                raise FileNotFoundError(f"YAML file not found: {YAML_PATH}")
            data = load_yaml(YAML_PATH)

            console.print("\n[bold]3. Ingesting nodes...[/bold]")
            ingest_tactics(session, data["tactics"])
            ingest_techniques(session, data["techniques"])
            ingest_mitigations(session, data["mitigations"])
            ingest_case_studies(session, data["case-studies"])

            console.print("\n[bold]4. Ingesting relationships...[/bold]")
            ingest_relationships(session, data["relationships"])

            console.print("\n[bold]5. Validating graph...[/bold]")
            validate(session)

    elapsed = time.time() - start
    console.print(f"\n[bold green]Done in {elapsed:.1f}s[/bold green]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        Console().print(f"[bold red]Error: {e}[/bold red]")
        logger.exception("Load failed")
        sys.exit(1)
