from pathlib import Path

import pytest

from cmc_agent_lab.simulators.builtin import run_arrhenius_stability, scenario_with_candidate
from cmc_agent_lab.simulators.thermo_chemicals import run_thermo_chemicals
from cmc_agent_lab.workflow import load_scenario


ROOT = Path(__file__).resolve().parents[1]


def test_stability_model_penalizes_higher_temperature():
    scenario = load_scenario(ROOT / "examples" / "small_molecule_process.yaml")
    low_temp = scenario_with_candidate(scenario, {"temperature_c": 25})
    high_temp = scenario_with_candidate(scenario, {"temperature_c": 55})

    low = run_arrhenius_stability(low_temp)
    high = run_arrhenius_stability(high_temp)

    assert low.metrics["purity_remaining_pct"] > high.metrics["purity_remaining_pct"]


def test_candidate_override_collapses_design_variable():
    scenario = load_scenario(ROOT / "examples" / "small_molecule_process.yaml")
    candidate = scenario_with_candidate(scenario, {"ph": 7.1})

    ph = next(variable for variable in candidate.design_space if variable.name == "ph")
    assert ph.low == 7.1
    assert ph.high == 7.1


def test_thermo_chemicals_adapter_returns_real_property_metrics():
    pytest.importorskip("thermo")
    scenario = load_scenario(ROOT / "examples" / "property_package_screen.yaml")

    result = run_thermo_chemicals(scenario)

    assert result.status == "ok"
    assert result.tool_name == "external.thermo_chemicals"
    assert result.metrics["api_molecular_weight_g_mol"] > 100
    assert result.metrics["solvent_density_kg_m3"] > 500
    assert result.metrics["solubility_parameter_gap_mpa05"] >= 0
    assert result.inputs["active_ingredient"] == "acetaminophen"


def test_thermo_chemicals_adapter_defaults_empty_solvent_config():
    pytest.importorskip("thermo")
    scenario = load_scenario(ROOT / "examples" / "property_package_screen.yaml")
    scenario.constraints["property_package"]["solvents"] = []

    result = run_thermo_chemicals(scenario)

    assert result.status == "ok"
    assert result.inputs["solvents"][0]["name"] == "water"
