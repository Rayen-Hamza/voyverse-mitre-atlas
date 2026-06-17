"""Wipe Neo4j database and reload from scratch."""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from scripts.load import main as load_main

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


def wipe_database() -> None:
    """Delete all nodes and relationships from Neo4j."""
    console = Console()
    load_dotenv(PROJECT_ROOT / ".env")

    uri = _get_env_var("NEO4J_URI")
    user = _get_env_var("NEO4J_USER")
    password = _get_env_var("NEO4J_PASSWORD")

    console.print(f"[bold red]Wiping all data from {uri}...[/bold red]")

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            result = session.run(
                "MATCH (n) RETURN count(n) AS count"
            )
            node_count = result.single()["count"]
            console.print(f"Deleting {node_count} nodes...")

            session.run("MATCH (n) DETACH DELETE n")

    console.print("[green]Database wiped.[/green]")


if __name__ == "__main__":
    try:
        wipe_database()
        Console().print("\n[bold]Reloading from scratch...[/bold]\n")
        load_main()
    except Exception as e:
        Console().print(f"[bold red]Error: {e}[/bold red]")
        logger.exception("Reset failed")
        sys.exit(1)
