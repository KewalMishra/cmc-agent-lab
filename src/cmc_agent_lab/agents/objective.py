"""Objective scoping agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.planning import infer_intent
from cmc_agent_lab.schema import AgentState


def scope_objective(state: AgentState) -> AgentState:
    state.intent = infer_intent(state.scenario)
    return record_event(
        state,
        step="objective_scoping",
        summary="Parsed workflow mode, unit operations, CQAs, and constraints into structured intent.",
        inputs=state.scenario.model_dump(),
        outputs=state.intent.model_dump(),
    )
