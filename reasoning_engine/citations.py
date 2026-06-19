"""Tool call interception and citation injection for the reasoning engine."""

import functools
import re
from dataclasses import dataclass, field
from typing import Any, Callable

ATLAS_ID_PATTERN = re.compile(
    r"AML\.[TMC][A-Z]?\d+(?:\.\d+)?|LLM\d{2}|EU_AIA_Art\d+"
)
BARE_ID_PATTERN = re.compile(
    r"(AML\.[TMC][A-Z]?\d+(?:\.\d+)?|LLM\d{2}|EU_AIA_Art\d+)"
    r"(?!\s*\[Q\d+\])"
)


@dataclass
class ToolCallEntry:
    """A single logged tool call with its reference ID."""

    ref: str
    tool: str
    input: dict[str, Any]
    result: Any


@dataclass
class CitationLog:
    """Wraps tool functions to log every call with a sequential ref ID."""

    entries: list[ToolCallEntry] = field(default_factory=list)

    def wrap(self, tool_fn: Callable) -> Callable:
        """Wrap a tool function to log every call."""

        @functools.wraps(tool_fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = tool_fn(*args, **kwargs)
            ref = f"Q{len(self.entries) + 1}"
            self.entries.append(
                ToolCallEntry(
                    ref=ref,
                    tool=tool_fn.__name__,
                    input=kwargs,
                    result=result,
                )
            )
            return result

        return wrapper

    def inject_citations(self, answer: str) -> str:
        """Inject [Qn] markers after bare ATLAS IDs in the answer.

        Scans tool call results to build an ID-to-ref lookup, then
        inserts markers where the LLM forgot to place them. Skips
        IDs that already have a [Q] marker immediately following.
        """
        id_to_ref = self._build_id_lookup()

        def _replace(match: re.Match) -> str:
            atlas_id = match.group(0)
            ref = id_to_ref.get(atlas_id)
            return f"{atlas_id} [{ref}]" if ref else atlas_id

        return BARE_ID_PATTERN.sub(_replace, answer)

    def _build_id_lookup(self) -> dict[str, str]:
        """Map each ATLAS ID to the first ref that returned it."""
        lookup: dict[str, str] = {}
        for entry in self.entries:
            for atlas_id in ATLAS_ID_PATTERN.findall(str(entry.result)):
                if atlas_id not in lookup:
                    lookup[atlas_id] = entry.ref
        return lookup
