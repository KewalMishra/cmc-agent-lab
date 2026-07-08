"""Tool registry for the agent planner."""

from __future__ import annotations

import importlib.util

from cmc_agent_lab.schema import ToolSpec


def default_tool_registry() -> list[ToolSpec]:
    """Return built-in and optional tool metadata."""

    return [
        ToolSpec(
            name="builtin.arrhenius_stability",
            category="mechanistic_simulator",
            fidelity="first_principles_simplified",
            activities=["simulate", "stability", "screen"],
            domains=["stability", "shelf_life", "degradation"],
            description="First-order Arrhenius degradation model for shelf-life sensitivity.",
        ),
        ToolSpec(
            name="builtin.batch_reactor_ode",
            category="mechanistic_simulator",
            fidelity="first_principles_simplified",
            activities=["simulate", "reaction", "screen"],
            domains=["reaction", "conversion", "impurity"],
            description="ODE model for main reaction conversion and side-product formation.",
        ),
        ToolSpec(
            name="builtin.crystallization_moments",
            category="mechanistic_simulator",
            fidelity="first_principles_simplified",
            activities=["simulate", "crystallization", "screen"],
            domains=["crystallization", "particle_size", "yield"],
            description="Moment-based population-balance approximation for crystallization.",
        ),
        ToolSpec(
            name="builtin.noyes_whitney_dissolution",
            category="mechanistic_simulator",
            fidelity="first_principles_simplified",
            activities=["simulate", "dissolution", "formulation", "screen"],
            domains=["dissolution", "solubility", "formulation"],
            description="Noyes-Whitney dissolution model with pH and antisolvent adjustments.",
        ),
        ToolSpec(
            name="optimizer.active_learning_batch",
            category="optimizer",
            fidelity="surrogate_model",
            activities=["optimize", "recommend_experiments"],
            domains=["design_of_experiments", "bayesian_optimization"],
            description="Candidate ranking with GP uncertainty when historical data is available.",
        ),
        ToolSpec(
            name="rl.epsilon_greedy_campaign",
            category="rl_policy",
            fidelity="simulator_trained_policy",
            activities=["learn", "reinforcement_learning", "recommend_experiments"],
            domains=["sequential_experimentation", "digital_twin", "policy_learning"],
            description=(
                "Sequential experiment-selection policy trained against the mechanistic simulator "
                "environment."
            ),
        ),
        ToolSpec(
            name="risk.qbd_fmea",
            category="risk",
            fidelity="rule_based",
            activities=["risk", "audit", "screen"],
            domains=["qbd", "cqa", "cpp", "fmea"],
            description="QbD/FMEA-style risk register linking CPPs to CQAs.",
        ),
        ToolSpec(
            name="external.pharmapy",
            category="process_simulator",
            fidelity="open_source_mechanistic",
            activities=["simulate", "flowsheet", "optimize"],
            domains=["drug_substance", "flowsheet", "crystallization", "drying"],
            optional_dependency="PharmaPy",
            estimated_runtime="minutes",
            description="Open-source pharmaceutical manufacturing flowsheet simulator.",
        ),
        ToolSpec(
            name="external.cantera",
            category="chemistry_simulator",
            fidelity="open_source_mechanistic",
            activities=["simulate", "reaction", "thermodynamics"],
            domains=["kinetics", "thermodynamics", "transport"],
            optional_dependency="cantera",
            estimated_runtime="seconds_to_minutes",
            description="Open-source chemical kinetics, thermodynamics, and transport toolkit.",
        ),
        ToolSpec(
            name="external.idaes_pyomo",
            category="process_simulator",
            fidelity="open_source_equation_oriented",
            activities=["simulate", "optimize", "control"],
            domains=["flowsheet", "dae", "optimization", "surrogate"],
            optional_dependency="idaes",
            estimated_runtime="minutes",
            description="IDAES/Pyomo process systems engineering modeling stack.",
        ),
        ToolSpec(
            name="external.dwsim",
            category="process_simulator",
            fidelity="open_source_flowsheet",
            activities=["simulate", "flowsheet"],
            domains=["steady_state", "dynamic_process", "property_packages"],
            optional_dependency="dwsim",
            estimated_runtime="minutes",
            description="Open-source process simulator with Python/.NET automation boundaries.",
        ),
        ToolSpec(
            name="external.thermo_chemicals",
            category="property_package",
            fidelity="open_source_property_model",
            activities=["simulate", "thermodynamics", "screen"],
            domains=["phase_equilibrium", "properties", "mixtures"],
            optional_dependency="thermo",
            estimated_runtime="seconds",
            description="Thermodynamic and chemical-property libraries for Python.",
        ),
    ]


def mark_availability(tools: list[ToolSpec]) -> dict[str, bool]:
    """Detect whether optional dependencies are importable."""

    availability: dict[str, bool] = {}
    for tool in tools:
        if tool.optional_dependency is None:
            availability[tool.name] = True
        else:
            availability[tool.name] = importlib.util.find_spec(tool.optional_dependency) is not None
    return availability
