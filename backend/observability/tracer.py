"""Structured execution tracing.

Emits one JSON-lines event per pipeline step to stdout: easy to grep, and
parseable by log collectors (or the React UI, via SSE later).
"""

import json
import time


def trace_execution(step_name: str, payload: dict):
    """Emit a structured trace event for an agent/pipeline step."""
    event = {"ts": round(time.time(), 3), "step": step_name, "payload": payload}
    print(f"[TRACE] {json.dumps(event)}", flush=True)
