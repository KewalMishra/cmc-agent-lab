"""Local mechanistic models used when external simulators are unavailable.

These models are intentionally compact and transparent. They are not validated process models;
they exist to demonstrate how an agent can route, execute, audit, and compare simulator outputs.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from cmc_agent_lab.schema import Scenario, SimulationResult

R_GAS = 8.314


def run_builtin_tool(tool_name: str, scenario: Scenario) -> SimulationResult:
    if tool_name == "builtin.arrhenius_stability":
        return run_arrhenius_stability(scenario)
    if tool_name == "builtin.batch_reactor_ode":
        return run_batch_reactor(scenario)
    if tool_name == "builtin.crystallization_moments":
        return run_crystallization_moments(scenario)
    if tool_name == "builtin.noyes_whitney_dissolution":
        return run_noyes_whitney_dissolution(scenario)
    raise ValueError(f"Unsupported built-in simulator: {tool_name}")


def run_arrhenius_stability(scenario: Scenario) -> SimulationResult:
    temperature_c = _value(scenario, "temperature_c", 40.0)
    shelf_life_months = float(scenario.qtp_profile.get("shelf_life_months", 24))
    time_days = shelf_life_months * 30.4375
    k_ref = float(scenario.constraints.get("degradation_k_25_per_day", 0.00005))
    ea = float(scenario.constraints.get("activation_energy_kj_mol", 60.0)) * 1000.0
    temperature_k = temperature_c + 273.15
    k = k_ref * math.exp((-ea / R_GAS) * ((1.0 / temperature_k) - (1.0 / 298.15)))
    purity_remaining = 100.0 * math.exp(-k * time_days)
    threshold = float(scenario.constraints.get("purity_threshold_pct", 98.0))
    warnings = []
    if purity_remaining < threshold:
        warnings.append("Predicted shelf-life purity is below threshold.")
    return SimulationResult(
        tool_name="builtin.arrhenius_stability",
        inputs={"temperature_c": temperature_c, "time_days": time_days, "k_ref": k_ref},
        metrics={
            "purity_remaining_pct": purity_remaining,
            "degradation_pct": 100.0 - purity_remaining,
            "degradation_rate_per_day": k,
        },
        assumptions=[
            "Single dominant first-order degradation pathway.",
            "Arrhenius temperature dependence around 25 C reference.",
        ],
        warnings=warnings,
    )


def run_batch_reactor(scenario: Scenario) -> SimulationResult:
    temperature_c = _value(scenario, "temperature_c", 40.0)
    residence_time_min = _value(scenario, "residence_time_min", 90.0)
    temperature_k = temperature_c + 273.15
    k_main = 0.035 * math.exp((-32_000.0 / R_GAS) * ((1.0 / temperature_k) - (1.0 / 313.15)))
    k_side = 0.004 * math.exp((-24_000.0 / R_GAS) * ((1.0 / temperature_k) - (1.0 / 313.15)))

    def rhs(_t: float, y: np.ndarray) -> list[float]:
        a, b, impurity = y
        return [-(k_main + k_side) * a, k_main * a, k_side * a + 0.0005 * b]

    solution = solve_ivp(rhs, (0.0, residence_time_min), [1.0, 0.0, 0.0], dense_output=False)
    a_end, b_end, impurity_end = solution.y[:, -1]
    conversion = (1.0 - a_end) * 100.0
    yield_pct = b_end * 100.0
    impurity_pct = impurity_end * 100.0
    warnings = []
    if impurity_pct > 1.0:
        warnings.append("Side-product burden exceeds a typical late-stage impurity threshold.")
    return SimulationResult(
        tool_name="builtin.batch_reactor_ode",
        inputs={"temperature_c": temperature_c, "residence_time_min": residence_time_min},
        metrics={
            "conversion_pct": conversion,
            "isolated_yield_proxy_pct": yield_pct,
            "impurity_proxy_pct": impurity_pct,
        },
        assumptions=[
            "Competitive first-order main and side reactions.",
            "Well-mixed batch or plug-flow-equivalent residence-time approximation.",
        ],
        warnings=warnings,
    )


def run_crystallization_moments(scenario: Scenario) -> SimulationResult:
    cooling_rate = _value(scenario, "cooling_rate_c_min", 0.5)
    antisolvent_fraction = _value(scenario, "antisolvent_fraction", 0.2)
    residence_time = _value(scenario, "residence_time_min", 90.0)
    start_temp_c = _value(scenario, "temperature_c", 45.0)
    c0 = 1.0
    kb = 0.08 * (1.0 + antisolvent_fraction)
    kg = 0.025 * (1.0 + 0.5 * antisolvent_fraction)

    def solubility(t: float) -> float:
        temp = max(5.0, start_temp_c - cooling_rate * t)
        return max(0.15, 0.25 + 0.014 * temp - 0.22 * antisolvent_fraction)

    def rhs(t: float, y: np.ndarray) -> list[float]:
        c, m0, m1, m2, m3 = y
        saturation = max(c / solubility(t) - 1.0, 0.0)
        nucleation = kb * saturation**2
        growth = kg * saturation
        dc = -0.018 * growth * max(m2, 1e-6) - 0.01 * nucleation
        return [
            dc,
            nucleation,
            growth * max(m0, 1e-6),
            2.0 * growth * max(m1, 1e-6),
            3.0 * growth * max(m2, 1e-6),
        ]

    solution = solve_ivp(
        rhs,
        (0.0, residence_time),
        [c0, 1e-4, 1e-4, 1e-4, 1e-4],
        max_step=max(residence_time / 100.0, 0.1),
    )
    c_end, m0, _m1, m2, m3 = solution.y[:, -1]
    yield_pct = max(0.0, min(100.0, (c0 - c_end) / c0 * 100.0))
    d50_um = max(5.0, min(250.0, (m3 / max(m2, 1e-6)) * 45.0))
    nucleation_density = max(0.0, m0)
    warnings = []
    if d50_um < 25 or d50_um > 120:
        warnings.append("Particle-size proxy is outside the preferred manufacturability band.")
    return SimulationResult(
        tool_name="builtin.crystallization_moments",
        inputs={
            "temperature_c": start_temp_c,
            "cooling_rate_c_min": cooling_rate,
            "antisolvent_fraction": antisolvent_fraction,
            "residence_time_min": residence_time,
        },
        metrics={
            "crystallization_yield_pct": yield_pct,
            "particle_size_d50_um": d50_um,
            "nucleation_density_proxy": nucleation_density,
        },
        assumptions=[
            "Moment-based population-balance approximation.",
            "Temperature-dependent solubility and antisolvent-driven supersaturation.",
        ],
        warnings=warnings,
    )


def run_noyes_whitney_dissolution(scenario: Scenario) -> SimulationResult:
    ph = _value(scenario, "ph", 6.0)
    antisolvent_fraction = _value(scenario, "antisolvent_fraction", 0.2)
    particle_size = 60.0
    surface_area_factor = 60.0 / particle_size
    ph_bonus = math.exp(-((ph - 6.5) ** 2) / 5.0)
    solubility_capacity = max(0.2, 1.05 * ph_bonus * (1.0 - 0.65 * antisolvent_fraction))
    k_dissolution = 0.065 * surface_area_factor
    concentration_30 = solubility_capacity * (1.0 - math.exp(-k_dissolution * 30.0))
    dissolved_pct = max(0.0, min(100.0, concentration_30 * 100.0))
    threshold = float(scenario.constraints.get("dissolution_threshold_pct", 85.0))
    warnings = []
    if dissolved_pct < threshold:
        warnings.append("Dissolution at 30 minutes is below target.")
    return SimulationResult(
        tool_name="builtin.noyes_whitney_dissolution",
        inputs={"ph": ph, "antisolvent_fraction": antisolvent_fraction},
        metrics={
            "dissolution_30min_pct": dissolved_pct,
            "relative_solubility_capacity": solubility_capacity,
        },
        assumptions=[
            "Noyes-Whitney dissolution with constant surface-area proxy.",
            "pH and antisolvent terms approximate formulation effects.",
        ],
        warnings=warnings,
    )


def _value(scenario: Scenario, name: str, default: float) -> float:
    for variable in scenario.design_space:
        if variable.name == name:
            return variable.midpoint
    return default


def scenario_with_candidate(scenario: Scenario, candidate: dict[str, float]) -> Scenario:
    """Return a scenario with design-variable ranges collapsed around a candidate."""

    data: dict[str, Any] = scenario.model_dump()
    variables = []
    for variable in scenario.design_space:
        value = float(candidate.get(variable.name, variable.midpoint))
        variables.append({"name": variable.name, "low": value, "high": value, "units": variable.units})
    data["design_space"] = variables
    return Scenario.model_validate(data)
