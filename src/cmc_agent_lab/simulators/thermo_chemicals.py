"""Thermo/Chemicals property-package adapter.

This adapter is the first real open-source scientific tool integration in the project. It uses
the `thermo` package, backed by `chemicals` and `fluids`, to calculate pure-component and
mixture properties for a CMC solvent/formulation screening question.
"""

from __future__ import annotations

import math
from typing import Any

from cmc_agent_lab.schema import Scenario, SimulationResult


def run_thermo_chemicals(scenario: Scenario) -> SimulationResult:
    """Run a property-package calculation for API and solvent-system screening."""

    try:
        from thermo import Chemical, Mixture
    except ImportError:
        return SimulationResult(
            tool_name="external.thermo_chemicals",
            status="skipped",
            warnings=["Install optional dependency with `python -m pip install -e '.[property]'`."],
            assumptions=["Thermo/Chemicals adapter was selected but package import failed."],
        )

    config = _property_config(scenario)
    temperature_c = _float_config(config, "temperature_c", _value(scenario, "temperature_c", 25.0))
    temperature_k = temperature_c + 273.15
    pressure_pa = _float_config(config, "pressure_pa", 101325.0)
    api_name = str(config.get("active_ingredient", "acetaminophen"))
    solvent_entries = _solvent_entries(config.get("solvents"))
    solvent_names = [str(item["name"]) for item in solvent_entries]
    mole_fractions = _normalize([float(item.get("mole_fraction", 0.0)) for item in solvent_entries])

    inputs = {
        "active_ingredient": api_name,
        "solvents": solvent_entries,
        "temperature_k": temperature_k,
        "pressure_pa": pressure_pa,
    }
    try:
        api = Chemical(api_name, T=temperature_k, P=pressure_pa)
        mixture = Mixture(solvent_names, zs=mole_fractions, T=temperature_k, P=pressure_pa)
    except Exception as exc:
        return SimulationResult(
            tool_name="external.thermo_chemicals",
            status="error",
            inputs=inputs,
            warnings=[f"Thermo/Chemicals execution failed: {exc}"],
            assumptions=["Adapter failures are surfaced as tool results so the graph remains auditable."],
        )

    api_delta = _safe_float(getattr(api, "solubility_parameter", None))
    mixture_delta = _volume_weighted_solubility_parameter(solvent_names, mole_fractions, temperature_k, pressure_pa)
    delta_gap = abs(api_delta - mixture_delta) if api_delta is not None and mixture_delta is not None else None

    metrics = {
        "property_temperature_k": temperature_k,
        "api_molecular_weight_g_mol": _safe_float(getattr(api, "MW", None)),
        "api_melting_point_k": _safe_float(getattr(api, "Tm", None)),
        "api_boiling_point_k": _safe_float(getattr(api, "Tb", None)),
        "api_vapor_pressure_pa": _safe_float(getattr(api, "Psat", None)),
        "api_density_kg_m3": _safe_float(getattr(api, "rho", None)),
        "api_solubility_parameter_mpa05": _to_mpa05(api_delta),
        "solvent_density_kg_m3": _safe_float(getattr(mixture, "rho", None)),
        "solvent_viscosity_pa_s": _safe_float(getattr(mixture, "mul", None)),
        "solvent_surface_tension_n_m": _safe_float(getattr(mixture, "sigma", None)),
        "solubility_parameter_gap_mpa05": _to_mpa05(delta_gap),
    }
    metrics = {key: value for key, value in metrics.items() if value is not None}
    warnings = _warnings(api_name, api, mixture, metrics)

    return SimulationResult(
        tool_name="external.thermo_chemicals",
        inputs=inputs,
        metrics=metrics,
        assumptions=[
            "Thermo/Chemicals properties are used as an open-source screening property package.",
            "Solubility-parameter mismatch is a proxy for solvent compatibility, not a validated solubility model.",
            "Mixture properties are used for early CMC screening and require experimental confirmation.",
        ],
        warnings=warnings,
    )


def _property_config(scenario: Scenario) -> dict[str, Any]:
    config = scenario.constraints.get("property_package", {})
    return config if isinstance(config, dict) else {}


def _default_solvents() -> list[dict[str, float | str]]:
    return [
        {"name": "water", "mole_fraction": 0.7},
        {"name": "ethanol", "mole_fraction": 0.3},
    ]


def _float_config(config: dict[str, Any], key: str, default: float) -> float:
    value = _safe_float(config.get(key, default))
    return value if value is not None else default


def _solvent_entries(raw_value: Any) -> list[dict[str, float | str]]:
    if not isinstance(raw_value, list) or not raw_value:
        return _default_solvents()

    entries: list[dict[str, float | str]] = []
    for item in raw_value:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        mole_fraction = _safe_float(item.get("mole_fraction", 0.0))
        entries.append(
            {
                "name": str(item["name"]),
                "mole_fraction": mole_fraction if mole_fraction is not None else 0.0,
            }
        )
    return entries or _default_solvents()


def _normalize(values: list[float]) -> list[float]:
    total = sum(max(value, 0.0) for value in values)
    if total <= 0:
        return [1.0 / len(values)] * len(values)
    return [max(value, 0.0) / total for value in values]


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _to_mpa05(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 1000.0


def _volume_weighted_solubility_parameter(
    solvent_names: list[str],
    mole_fractions: list[float],
    temperature_k: float,
    pressure_pa: float,
) -> float | None:
    try:
        from thermo import Chemical
    except ImportError:
        return None

    weighted = 0.0
    total_weight = 0.0
    for name, z in zip(solvent_names, mole_fractions):
        solvent = Chemical(name, T=temperature_k, P=pressure_pa)
        delta = _safe_float(getattr(solvent, "solubility_parameter", None))
        molar_volume = _safe_float(getattr(solvent, "Vml", None))
        if delta is None or molar_volume is None:
            continue
        weight = max(z * molar_volume, 0.0)
        weighted += weight * delta
        total_weight += weight
    return weighted / total_weight if total_weight > 0 else None


def _warnings(api_name: str, api: Any, mixture: Any, metrics: dict[str, float]) -> list[str]:
    warnings = []
    phase = getattr(api, "phase", None)
    mixture_phase = getattr(mixture, "phase", None)
    if phase == "s":
        warnings.append(f"{api_name} is predicted as solid at the screening temperature.")
    if mixture_phase and mixture_phase != "l":
        warnings.append(f"Solvent system phase is predicted as `{mixture_phase}`.")
    if metrics.get("solubility_parameter_gap_mpa05", 0.0) > 12.0:
        warnings.append("Large solubility-parameter mismatch; solvent compatibility may be poor.")
    return warnings


def _value(scenario: Scenario, name: str, default: float) -> float:
    for variable in scenario.design_space:
        if variable.name == name:
            return variable.midpoint
    return default
