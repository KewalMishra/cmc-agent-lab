"""Simulator execution agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.schema import AgentState, SimulationResult
from cmc_agent_lab.simulators.builtin import run_builtin_tool
from cmc_agent_lab.simulators.thermo_chemicals import run_thermo_chemicals


def run_simulators(state: AgentState) -> AgentState:
    results: list[SimulationResult] = []
    for selection in state.tool_plan:
        if not selection.category.endswith("simulator") and selection.category != "property_package":
            continue
        if not selection.available:
            results.append(
                SimulationResult(
                    tool_name=selection.tool_name,
                    status="skipped",
                    warnings=["Optional external simulator dependency is not installed."],
                    assumptions=["Adapter boundary is documented; no local execution attempted."],
                )
            )
            continue
        if selection.tool_name.startswith("builtin."):
            results.append(run_builtin_tool(selection.tool_name, state.scenario))
        elif selection.tool_name == "external.thermo_chemicals":
            results.append(run_thermo_chemicals(state.scenario))
    state.simulations = results
    return record_event(
        state,
        step="mechanistic_simulation",
        summary=f"Executed or evaluated {len(results)} simulator selections.",
        inputs=[item.model_dump() for item in state.tool_plan],
        outputs=[item.model_dump() for item in results],
    )
