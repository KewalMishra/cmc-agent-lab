"""Surrogate-model readiness agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.schema import AgentState


def assess_surrogate_readiness(state: AgentState) -> AgentState:
    count = len([row for row in state.scenario.historical_experiments if "objective_score" in row])
    status = "ready" if count >= 3 else "limited"
    return record_event(
        state,
        step="surrogate_readiness",
        summary=f"Historical experiment count={count}; surrogate status={status}.",
        inputs=state.scenario.historical_experiments,
        outputs={"status": status, "count": count},
    )
