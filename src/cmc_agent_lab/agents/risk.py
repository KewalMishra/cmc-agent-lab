"""QbD-style risk agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.schema import AgentState, RiskItem


CPP_BY_CQA = {
    "purity": ("temperature_c", "Add stability-indicating method and impurity trend review."),
    "dissolution_30min": ("ph", "Confirm discriminatory dissolution method and pH/formulation range."),
    "particle_size_d50_um": ("cooling_rate_c_min", "Use PAT particle-size monitoring during crystallization."),
    "isolated_yield": ("residence_time_min", "Run mass-balance reconciliation and yield sensitivity."),
    "impurity_burden": ("temperature_c", "Constrain high-temperature residence time and monitor side products."),
}


def assess_risk(state: AgentState) -> AgentState:
    risk_items: list[RiskItem] = []
    for cqa in state.scenario.critical_quality_attributes:
        cpp, mitigation = CPP_BY_CQA.get(
            cqa.name,
            ("process_parameter", "Define monitoring and scientist review before execution."),
        )
        occurrence = 4 if cqa.risk_severity >= 4 else 3
        detectability = 2 if cqa.name in {"purity", "dissolution_30min"} else 3
        rpn = cqa.risk_severity * occurrence * detectability
        risk_items.append(
            RiskItem(
                risk=f"{cpp} variability may move {cqa.name} outside target {cqa.target or ''}".strip(),
                cqa=cqa.name,
                cpp=cpp,
                severity=cqa.risk_severity,
                occurrence=occurrence,
                detectability=detectability,
                rpn=rpn,
                mitigation=mitigation,
            )
        )
    state.risk_register = sorted(risk_items, key=lambda item: item.rpn, reverse=True)
    state.human_review_required = bool(state.scenario.constraints.get("require_human_approval", True))
    return record_event(
        state,
        step="qbd_risk_review",
        summary=f"Created {len(state.risk_register)} CQA/CPP risk items.",
        inputs=[item.model_dump() for item in state.scenario.critical_quality_attributes],
        outputs=[item.model_dump() for item in state.risk_register],
    )
