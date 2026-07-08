"""Simple RL policies for simulator-backed experiment selection."""

from __future__ import annotations

import numpy as np

from cmc_agent_lab.rl.env import CMCProcessEnv
from cmc_agent_lab.schema import ExperimentRecommendation, RLPolicyResult, RLPolicyStep, Scenario


def train_epsilon_greedy_policy(
    scenario: Scenario,
    *,
    episodes: int | None = None,
    budget: int | None = None,
    candidate_count: int | None = None,
    epsilon: float | None = None,
    seed: int = 23,
) -> RLPolicyResult:
    """Train a lightweight sequential experiment-selection policy.

    This is intentionally a transparent RL-lite baseline. It is easier to audit than a deep RL
    policy and provides a credible bridge to Gymnasium/stable-baselines3 later.
    """

    episodes = episodes or int(scenario.constraints.get("rl_episodes", 25))
    budget = budget or int(scenario.constraints.get("rl_budget", scenario.max_experiments))
    candidate_count = candidate_count or int(scenario.constraints.get("rl_candidate_count", 80))
    epsilon = epsilon if epsilon is not None else float(scenario.constraints.get("rl_epsilon", 0.2))

    rng = np.random.default_rng(seed)
    env = CMCProcessEnv(scenario, budget=budget, candidate_count=candidate_count, seed=seed)
    q_values = np.zeros(env.action_space.n)
    counts = np.zeros(env.action_space.n)
    trajectory: list[RLPolicyStep] = []
    best_reward_score = float("-inf")
    best_objective_score = float("-inf")
    best_variables: dict[str, float] = {}

    for episode in range(episodes):
        env.reset(seed=seed)
        done = False
        step = 0
        while not done:
            action = _choose_action(q_values, counts, env.action_mask(), epsilon, rng)
            _observation, reward, done, info = env.step(action)
            evaluation = info["evaluation"]
            counts[action] += 1.0
            q_values[action] += (reward - q_values[action]) / counts[action]
            if evaluation.reward_score > best_reward_score:
                best_reward_score = evaluation.reward_score
                best_objective_score = evaluation.objective_score
                best_variables = evaluation.variables
            trajectory.append(
                RLPolicyStep(
                    episode=episode + 1,
                    step=step + 1,
                    action_index=action,
                    variables={key: round(value, 4) for key, value in evaluation.variables.items()},
                    reward=round(float(reward), 4),
                    objective_score=round(float(evaluation.objective_score), 4),
                    done=done,
                )
            )
            step += 1

    baseline = _random_baseline(scenario, budget=budget, candidate_count=candidate_count, seed=seed + 101)
    recommendations = _policy_recommendations(env, q_values, counts, limit=budget)
    return RLPolicyResult(
        policy_name="epsilon_greedy_simulator_policy",
        episodes=episodes,
        budget=budget,
        candidate_count=env.action_space.n,
        best_reward=round(float(best_reward_score), 4),
        best_objective_score=round(float(best_objective_score), 4),
        best_variables={key: round(value, 4) for key, value in best_variables.items()},
        random_baseline_score=round(float(baseline), 4),
        improvement_over_random=round(float(best_reward_score - baseline), 4),
        trajectory=trajectory,
        recommendations=recommendations,
    )


def _choose_action(
    q_values: np.ndarray,
    counts: np.ndarray,
    action_mask: list[bool],
    epsilon: float,
    rng: np.random.Generator,
) -> int:
    available = np.array([index for index, allowed in enumerate(action_mask) if allowed])
    if len(available) == 0:
        return int(rng.integers(0, len(action_mask)))
    untried = available[counts[available] == 0]
    if len(untried) > 0:
        return int(rng.choice(untried))
    if rng.random() < epsilon:
        return int(rng.choice(available))
    best_available = available[np.argmax(q_values[available])]
    return int(best_available)


def _random_baseline(
    scenario: Scenario,
    *,
    budget: int,
    candidate_count: int,
    seed: int,
    episodes: int = 10,
) -> float:
    rng = np.random.default_rng(seed)
    best_scores = []
    for episode in range(episodes):
        env = CMCProcessEnv(scenario, budget=budget, candidate_count=candidate_count, seed=seed + episode)
        env.reset(seed=seed + episode)
        done = False
        best_episode_score = float("-inf")
        while not done:
            available = [index for index, allowed in enumerate(env.action_mask()) if allowed]
            action = int(rng.choice(available))
            _observation, _reward, done, info = env.step(action)
            evaluation = info["evaluation"]
            best_episode_score = max(best_episode_score, float(evaluation.reward_score))
        best_scores.append(best_episode_score)
    return float(np.mean(best_scores))


def _policy_recommendations(
    env: CMCProcessEnv,
    q_values: np.ndarray,
    counts: np.ndarray,
    *,
    limit: int,
) -> list[ExperimentRecommendation]:
    observed = np.array([index for index, count in enumerate(counts) if count > 0])
    if len(observed) == 0:
        observed = np.arange(env.action_space.n)
    ordered = observed[np.argsort(q_values[observed])[::-1]]
    recommendations: list[ExperimentRecommendation] = []
    for rank, action in enumerate(ordered[:limit], start=1):
        evaluation = env.evaluate_action(int(action))
        recommendations.append(
            ExperimentRecommendation(
                rank=rank,
                variables={key: round(value, 4) for key, value in evaluation.variables.items()},
                expected_score=round(float(evaluation.objective_score), 3),
                information_gain=round(float(max(q_values[action], 0.0)), 3),
                rationale=(
                    "Selected by simulator-trained epsilon-greedy policy; reward balances "
                    "CQA improvement, constraint penalties, and experiment budget."
                ),
                constraints_checked=[
                    "within declared design-space bounds",
                    "reward penalizes purity, dissolution, impurity, and particle-size failures",
                    "requires scientist approval before wet-lab execution",
                ],
            )
        )
    return recommendations
