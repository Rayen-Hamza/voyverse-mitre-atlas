"""FastAPI backend with SSE streaming for the ATLAS reasoning engine."""

import asyncio
import functools
import json
import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from reasoning_engine.agent import build_agent
from reasoning_engine.citations import CitationLog
from reasoning_engine.tools import (
    count_and_summarize,
    find_paths_between,
    get_node_neighbors,
    get_physical_schema,
    read_neo4j_cypher,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="ATLAS Reasoning Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GRAPH_TOOLS = [
    get_physical_schema,
    count_and_summarize,
    get_node_neighbors,
    find_paths_between,
    read_neo4j_cypher,
]


class QueryRequest(BaseModel):
    question: str


def _sse_event(event_type: str, data: dict[str, Any]) -> str:
    """Format a server-sent event line."""
    payload = json.dumps({"type": event_type, **data}, default=str)
    return f"data: {payload}\n\n"


def _make_streaming_tool(
    tool_fn: Any,
    log: CitationLog,
    events: list[str],
) -> Any:
    """Wrap a tool with citation logging and event capture."""
    logged_fn = log.wrap(tool_fn)

    @functools.wraps(tool_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = logged_fn(*args, **kwargs)
        entry = log.entries[-1]
        events.append(
            _sse_event(
                "tool_call",
                {
                    "ref": entry.ref,
                    "tool": entry.tool,
                    "input": entry.input,
                    "result": entry.result,
                },
            )
        )
        return result

    return wrapper


def _build_sse_tools(
    log: CitationLog,
    events: list[str],
    answer_holder: dict[str, Any],
) -> list:
    """Build the full tool list with streaming wrappers."""
    wrapped = [_make_streaming_tool(t, log, events) for t in GRAPH_TOOLS]

    def finished_wrapper(answer: str) -> str:
        """Signal that the investigation is complete and deliver the final answer.

        Call this ONLY after you have made at least 3 tool calls and have
        sufficient graph evidence to fully support your answer.

        The answer must:
        - Cite every technique, mitigation, and case study with its ATLAS ID
        - Embed [Q1], [Q2]... markers after every factual claim
        - Note coverage gaps explicitly
        - Not contain any IDs not found in query results

        Args:
            answer: The complete, grounded, cited response.
        """
        answer_holder["answer"] = answer
        return answer

    finished_wrapper.__name__ = "finished"
    return wrapped + [finished_wrapper]


async def _run_agent_async(question: str, tools: list) -> str:
    """Run the ADK agent and return the final answer text."""
    agent = build_agent(tools=tools)
    session_service = InMemorySessionService()

    runner = Runner(
        agent=agent,
        app_name="atlas_reasoning",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="atlas_reasoning", user_id="local"
    )

    user_msg = types.Content(
        role="user", parts=[types.Part(text=question)]
    )

    final_text = ""
    async for event in runner.run_async(
        user_id="local",
        session_id=session.id,
        new_message=user_msg,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    final_text += part.text

    return final_text


@app.post("/query")
async def run_query(req: QueryRequest):
    """Stream tool calls and final answer as server-sent events."""

    async def event_stream():
        log = CitationLog()
        events: list[str] = []
        answer_holder: dict[str, Any] = {"answer": None}

        tools = _build_sse_tools(log, events, answer_holder)

        try:
            agent_result = await _run_agent_async(req.question, tools)
        except Exception as e:
            logger.exception("Agent failed")
            yield _sse_event("error", {"message": str(e)})
            return

        for event in events:
            yield event

        raw_answer = answer_holder.get("answer") or agent_result
        cited_answer = log.inject_citations(raw_answer)

        yield _sse_event(
            "final_answer",
            {
                "answer": cited_answer,
                "evidence": [
                    {
                        "ref": e.ref,
                        "tool": e.tool,
                        "input": e.input,
                        "result": e.result,
                    }
                    for e in log.entries
                ],
            },
        )

    return StreamingResponse(
        event_stream(), media_type="text/event-stream"
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
