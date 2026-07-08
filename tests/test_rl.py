from pathlib import Path

from cmc_agent_lab.rl.env import CMCProcessEnv
from cmc_agent_lab.rl.policy import train_epsilon_greedy_policy
from cmc_agent_lab.schema import Scenario
from cmc_agent_lab.workflow import load_scenario, run_workflow


ROOT = Path(__file__).resolve().parents[1]


def _small_rl_scenario() -> Scenario:
    scenario = load_scenario(ROOT / "examples" / "rl_experiment_policy.yaml")
    data = scenario.model_dump()
    data["constraints"]["rl_episodes"] = 6
    data["constraints"]["rl_budget"] = 3
    data["constraints"]["rl_candidate_count"] = 12
    return Scenario.model_validate(data)


def test_cmc_process_env_step_returns_reward_and_metrics():
    scenario = _small_rl_scenario()
    env = CMCProcessEnv(scenario, budget=2, candidate_count=8, seed=3)

    observation = env.reset(seed=3)
    next_observation, reward, done, info = env.step(0)

    assert observation["remaining_budget"] == 2.0
    assert next_observation["remaining_budget"] == 1.0
    assert isinstance(reward, float)
    assert done is False
    assert info["evaluation"].objective_score > 0
    assert "purity_remaining_pct" in info["evaluation"].metrics


def test_epsilon_greedy_policy_produces_recommendations():
    scenario = _small_rl_scenario()
    result = train_epsilon_greedy_policy(scenario)
    bounds = {variable.name: (variable.low, variable.high) for variable in scenario.design_space}

    assert result.policy_name == "epsilon_greedy_simulator_policy"
    assert result.episodes == 6
    assert result.budget == 3
    assert len(result.trajectory) == 18
    assert len(result.recommendations) == 3
    assert result.best_objective_score > 0
    for rec in result.recommendations:
        for name, value in rec.variables.items():
            low, high = bounds[name]
            assert low <= value <= high


def test_learn_workflow_renders_rl_policy_section():
    state = run_workflow(_small_rl_scenario())

    assert state.rl_policy is not None
    assert not state.recommendations
    assert "Reinforcement Learning Policy" in (state.report or "")
    assert any(event.step == "rl_policy_learning" for event in state.audit_events)
