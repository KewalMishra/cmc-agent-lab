"""Offline deterministic workflow runner.

This runner lets the project be reviewed without API keys or external simulator installs. The
LangGraph assembly in graph.py wraps these same agent nodes for stateful orchestration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from cmc_agent_lab.agents.auditor import verify_auditability
from cmc_agent_lab.agents.experiment_designer import design_experiments
from cmc_agent_lab.agents.objective import scope_objective
from cmc_agent_lab.agents.reporter import render_report
from cmc_agent_lab.agents.rl_policy import learn_experiment_policy
from cmc_agent_lab.agents.risk import assess_risk
from cmc_agent_lab.agents.simulator import run_simulators
from cmc_agent_lab.agents.surrogate import assess_surrogate_readiness
from cmc_agent_lab.agents.tool_planner import plan_tools
from cmc_agent_lab.schema import AgentState, Scenario, WorkflowMode


def load_scenario(path: str | Path, mode_override: WorkflowMode | None = None) -> Scenario:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if isinstance(data.get("design_space"), dict):
        data["design_space"] = data["design_space"].get("variables", [])
    if mode_override is not None:
        data["mode"] = mode_override
    constraints = data.setdefault("constraints", {})
    data["disabled_tools"] = list(set(data.get("disabled_tools", []) + constraints.get("disabled_tools", [])))
    return Scenario.model_validate(data)


def run_workflow(path_or_scenario: str | Path | Scenario, mode_override: WorkflowMode | None = None) -> AgentState:
    scenario = (
        load_scenario(path_or_scenario, mode_override=mode_override)
        if not isinstance(path_or_scenario, Scenario)
        else _override(path_or_scenario, mode_override)
    )
    state = AgentState(scenario=scenario)
    state = scope_objective(state)
    state = plan_tools(state)
    if scenario.mode in {"simulate", "full", "screen"}:
        state = run_simulators(state)
    if scenario.mode in {"optimize", "full"}:
        state = assess_surrogate_readiness(state)
        state = design_experiments(state)
    elif scenario.mode in {"scope", "screen", "learn", "risk", "audit"}:
        state = design_experiments(state)
    if scenario.mode == "learn" or scenario.constraints.get("enable_rl_policy", False):
        state = learn_experiment_policy(state)
    state = assess_risk(state)
    state = verify_auditability(state)
    state = render_report(state)
    return state


def _override(scenario: Scenario, mode_override: WorkflowMode | None) -> Scenario:
    if mode_override is None:
        return scenario
    data: dict[str, Any] = scenario.model_dump()
    data["mode"] = mode_override
    return Scenario.model_validate(data)
