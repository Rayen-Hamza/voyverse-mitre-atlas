"""Execute example Cypher queries and display results as rich tables."""

import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase, Session
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CYPHER_PATH = PROJECT_ROOT / "queries" / "example_queries.cypher"

MAX_TEXT_LEN = 80

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_cypher_file(path: Path) -> list[dict[str, str]]:
    """Parse .cypher file into list of {title, query} dicts."""
    text = path.read_text(encoding="utf-8")
    queries: list[dict[str, str]] = []
    current_comments: list[str] = []
    current_query_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("//"):
            if current_query_lines:
                _flush_block(queries, current_comments, current_query_lines)
                current_comments = []
                current_query_lines = []
            current_comments.append(stripped.lstrip("/ "))
        elif stripped:
            current_query_lines.append(line)

    if current_query_lines:
        _flush_block(queries, current_comments, current_query_lines)

    return queries


def _flush_block(
    queries: list[dict[str, str]],
    comments: list[str],
    query_lines: list[str],
) -> None:
    """Join comment lines into title and query lines into Cypher, append to list."""
    title = " ".join(comments)
    query = "\n".join(query_lines).rstrip().rstrip(";")
    queries.append({"title": title, "query": query})


def _truncate(value: str) -> str:
    """Truncate text to MAX_TEXT_LEN chars."""
    if len(value) > MAX_TEXT_LEN:
        return value[: MAX_TEXT_LEN - 3] + "..."
    return value


def _format_value(value: Any) -> str:
    """Format a Neo4j result value for display."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return _truncate(str(value))


def run_query(
    session: Session, title: str, query: str, console: Console
) -> int:
    """Execute a single query and print results as a rich table. Returns row count."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")

    result = session.run(query)
    records = list(result)

    if not records:
        console.print("[yellow]No results returned.[/yellow]")
        return 0

    keys = records[0].keys()

    table = Table(show_lines=False)
    for key in keys:
        table.add_column(key, overflow="fold")

    for record in records:
        row = [_format_value(record[key]) for key in keys]
        table.add_row(*row)

    console.print(table)
    console.print(f"[dim]{len(records)} rows returned[/dim]")
    return len(records)


def _get_env_var(name: str) -> str:
    """Read a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required env var: {name}. Check .env file.")
    return value


def main() -> None:
    """Load queries, connect to Neo4j, run all, display results."""
    console = Console()

    load_dotenv(PROJECT_ROOT / ".env")
    uri = _get_env_var("NEO4J_URI")
    user = _get_env_var("NEO4J_USER")
    password = _get_env_var("NEO4J_PASSWORD")

    queries = parse_cypher_file(CYPHER_PATH)
    console.print(f"[bold]Loaded {len(queries)} queries from {CYPHER_PATH.name}[/bold]")

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()

        with driver.session() as session:
            total_rows = 0
            for q in queries:
                rows = run_query(session, q["title"], q["query"], console)
                total_rows += rows

    console.print(f"\n[bold green]All queries complete. {total_rows} total rows.[/bold green]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        Console().print(f"[bold red]Error: {e}[/bold red]")
        logger.exception("Query runner failed")
        sys.exit(1)
