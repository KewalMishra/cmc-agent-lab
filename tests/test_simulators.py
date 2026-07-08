from pathlib import Path

from cmc_agent_lab.simulators.builtin import run_arrhenius_stability, scenario_with_candidate
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
