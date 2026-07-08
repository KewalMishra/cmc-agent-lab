from pathlib import Path

from cmc_agent_lab.optimization.active_learning import recommend_experiments
from cmc_agent_lab.workflow import load_scenario


ROOT = Path(__file__).resolve().parents[1]


def test_recommendations_respect_design_space_and_budget():
    scenario = load_scenario(ROOT / "examples" / "small_molecule_process.yaml")
    recommendations = recommend_experiments(scenario)
    bounds = {variable.name: (variable.low, variable.high) for variable in scenario.design_space}

    assert len(recommendations) == scenario.max_experiments
    for rec in recommendations:
        for name, value in rec.variables.items():
            low, high = bounds[name]
            assert low <= value <= high
