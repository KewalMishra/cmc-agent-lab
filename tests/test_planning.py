from pathlib import Path

from cmc_agent_lab.planning import build_tool_plan, infer_intent
from cmc_agent_lab.workflow import load_scenario


ROOT = Path(__file__).resolve().parents[1]


def test_full_mode_selects_simulation_optimizer_and_risk_tools():
    scenario = load_scenario(ROOT / "examples" / "small_molecule_process.yaml")
    intent = infer_intent(scenario)
    tools = build_tool_plan(scenario, intent)
    names = {tool.tool_name for tool in tools}

    assert "builtin.arrhenius_stability" in names
    assert "builtin.crystallization_moments" in names
    assert "optimizer.active_learning_batch" in names
    assert "risk.qbd_fmea" in names


def test_risk_mode_only_selects_risk_tool():
    scenario = load_scenario(ROOT / "examples" / "small_molecule_process.yaml", mode_override="risk")
    intent = infer_intent(scenario)
    tools = build_tool_plan(scenario, intent)

    assert {tool.category for tool in tools} == {"risk"}


def test_learn_mode_selects_rl_policy_and_risk_tools():
    scenario = load_scenario(ROOT / "examples" / "rl_experiment_policy.yaml")
    intent = infer_intent(scenario)
    tools = build_tool_plan(scenario, intent)
    names = {tool.tool_name for tool in tools}

    assert "rl.epsilon_greedy_campaign" in names
    assert "risk.qbd_fmea" in names
    assert {tool.category for tool in tools} == {"rl_policy", "risk"}
