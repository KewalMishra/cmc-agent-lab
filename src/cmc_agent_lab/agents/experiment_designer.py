"""Experiment recommendation agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.optimization.active_learning import recommend_experiments
from cmc_agent_lab.schema import AgentState


def design_experiments(state: AgentState) -> AgentState:
    if state.scenario.mode in {"scope", "screen", "learn", "risk", "audit"}:
        return record_event(
            state,
            step="experiment_design",
            summary=f"Skipped experiment generation for mode={state.scenario.mode}.",
            inputs=state.scenario.mode,
            outputs=[],
        )
    state.recommendations = recommend_experiments(state.scenario, state.scenario.max_experiments)
    return record_event(
        state,
        step="experiment_design",
        summary=f"Recommended top {len(state.recommendations)} next experiments.",
        inputs=state.scenario.model_dump(),
        outputs=[item.model_dump() for item in state.recommendations],
    )
