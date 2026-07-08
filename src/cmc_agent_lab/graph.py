"""LangGraph assembly for production-style orchestration."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from cmc_agent_lab.agents.auditor import verify_auditability
from cmc_agent_lab.agents.experiment_designer import design_experiments
from cmc_agent_lab.agents.objective import scope_objective
from cmc_agent_lab.agents.reporter import render_report
from cmc_agent_lab.agents.rl_policy import learn_experiment_policy
from cmc_agent_lab.agents.risk import assess_risk
from cmc_agent_lab.agents.simulator import run_simulators
from cmc_agent_lab.agents.surrogate import assess_surrogate_readiness
from cmc_agent_lab.agents.tool_planner import plan_tools
from cmc_agent_lab.schema import AgentState


class GraphState(TypedDict):
    state: dict[str, Any]


def build_graph():
    """Build a LangGraph workflow.

    LangGraph is declared as a project dependency. This import is kept inside the function so
    the deterministic runner and tests remain usable before dependency installation.
    """

    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install the project dependencies to use LangGraph orchestration.") from exc

    builder = StateGraph(GraphState)
    builder.add_node("objective", _node(scope_objective))
    builder.add_node("planner", _node(plan_tools))
    builder.add_node("simulator", _node(run_simulators))
    builder.add_node("surrogate", _node(assess_surrogate_readiness))
    builder.add_node("experiment_designer", _node(design_experiments))
    builder.add_node("rl_policy", _node(learn_experiment_policy))
    builder.add_node("risk", _node(assess_risk))
    builder.add_node("auditor", _node(verify_auditability))
    builder.add_node("reporter", _node(render_report))

    builder.add_edge(START, "objective")
    builder.add_edge("objective", "planner")
    builder.add_conditional_edges(
        "planner", _route_after_planning, ["simulator", "surrogate", "rl_policy", "risk"]
    )
    builder.add_conditional_edges("simulator", _route_after_simulation, ["surrogate", "risk"])
    builder.add_edge("surrogate", "experiment_designer")
    builder.add_conditional_edges("experiment_designer", _route_after_experiment_design, ["rl_policy", "risk"])
    builder.add_edge("rl_policy", "risk")
    builder.add_edge("risk", "auditor")
    builder.add_edge("auditor", "reporter")
    builder.add_edge("reporter", END)
    return builder.compile()


def _node(func):
    def wrapped(graph_state: GraphState) -> GraphState:
        state = AgentState.model_validate(graph_state["state"])
        next_state = func(state)
        return {"state": next_state.to_jsonable()}

    return wrapped


def _route_after_planning(state: GraphState) -> Literal["simulator", "surrogate", "rl_policy", "risk"]:
    mode = state["state"]["scenario"]["mode"]
    if mode in {"simulate", "full", "screen"}:
        return "simulator"
    if mode == "optimize":
        return "surrogate"
    if mode == "learn":
        return "rl_policy"
    return "risk"


def _route_after_simulation(state: GraphState) -> Literal["surrogate", "risk"]:
    return "surrogate" if state["state"]["scenario"]["mode"] == "full" else "risk"


def _route_after_experiment_design(state: GraphState) -> Literal["rl_policy", "risk"]:
    constraints = state["state"]["scenario"].get("constraints", {})
    return "rl_policy" if constraints.get("enable_rl_policy", False) else "risk"
