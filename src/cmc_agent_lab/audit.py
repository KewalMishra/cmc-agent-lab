"""Audit helpers for traceable agent execution."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from cmc_agent_lab.schema import AgentState, AuditEvent


def digest(payload: Any) -> str:
    """Return a stable digest for an audit payload."""

    data = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


def record_event(
    state: AgentState,
    *,
    step: str,
    summary: str,
    status: str = "ok",
    inputs: Any | None = None,
    outputs: Any | None = None,
) -> AgentState:
    """Append an audit event to the state."""

    state.audit_events.append(
        AuditEvent(
            timestamp=datetime.now(timezone.utc),
            step=step,
            status=status,
            summary=summary,
            input_digest=digest(inputs) if inputs is not None else None,
            output_digest=digest(outputs) if outputs is not None else None,
        )
    )
    return state
