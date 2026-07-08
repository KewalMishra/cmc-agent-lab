"""Audit-control agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.schema import AgentState


def verify_auditability(state: AgentState) -> AgentState:
    missing = []
    if state.intent is None:
        missing.append("intent")
    if not state.tool_plan:
        missing.append("tool_plan")
    if state.scenario.mode in {"simulate", "full"} and not state.simulations:
        missing.append("simulations")
    if state.scenario.mode in {"optimize", "full"} and not state.recommendations:
        missing.append("recommendations")
    if (
        state.scenario.mode == "learn" or state.scenario.constraints.get("enable_rl_policy", False)
    ) and state.rl_policy is None:
        missing.append("rl_policy")
    if not state.risk_register:
        missing.append("risk_register")
    status = "warn" if missing else "ok"
    summary = "Audit trail complete." if not missing else f"Audit gaps: {', '.join(missing)}."
    return record_event(
        state,
        step="audit_verification",
        status=status,
        summary=summary,
        inputs=state.to_jsonable(),
        outputs={"missing": missing},
    )
