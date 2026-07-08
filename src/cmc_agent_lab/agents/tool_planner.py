"""Tool-planning agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.planning import build_tool_plan
from cmc_agent_lab.schema import AgentState


def plan_tools(state: AgentState) -> AgentState:
    if state.intent is None:
        raise ValueError("Intent must be scoped before tool planning.")
    state.tool_plan = build_tool_plan(state.scenario, state.intent)
    return record_event(
        state,
        step="tool_planning",
        summary=f"Selected {len(state.tool_plan)} tools for mode={state.scenario.mode}.",
        inputs=state.intent.model_dump(),
        outputs=[item.model_dump() for item in state.tool_plan],
    )
