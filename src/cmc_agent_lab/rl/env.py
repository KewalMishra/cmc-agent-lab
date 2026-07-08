"""Simulator-backed experiment campaign environment.

The API intentionally mirrors Gymnasium's reset/step pattern without requiring Gymnasium as a
hard dependency. Optional Gymnasium wrappers can be added later without changing the reward
or policy code.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cmc_agent_lab.rl.reward import CandidateEvaluation, evaluate_candidate
from cmc_agent_lab.schema import Scenario


@dataclass
class DiscreteActionSpace:
    """Small dependency-free stand-in for a discrete action space."""

    n: int

    def sample(self, rng: np.random.Generator | None = None) -> int:
        generator = rng or np.random.default_rng()
        return int(generator.integers(0, self.n))


class CMCProcessEnv:
    """Sequential experiment-selection environment for CMC process development."""

    def __init__(
        self,
        scenario: Scenario,
        *,
        budget: int | None = None,
        candidate_count: int = 80,
        seed: int = 17,
    ) -> None:
        self.scenario = scenario
        self.budget = budget or scenario.max_experiments
        self.candidate_count = candidate_count
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.candidates = self._generate_candidates(candidate_count)
        self.action_space = DiscreteActionSpace(len(self.candidates))
        self.current_step = 0
        self.best_score = self._historical_best()
        self.selected_actions: set[int] = set()

    def reset(self, *, seed: int | None = None) -> dict[str, float]:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.current_step = 0
        self.best_score = self._historical_best()
        self.selected_actions = set()
        return self._observation()

    def step(self, action_index: int) -> tuple[dict[str, float], float, bool, dict[str, object]]:
        if action_index < 0 or action_index >= len(self.candidates):
            raise ValueError(f"Action index {action_index} is outside the candidate set.")

        candidate = self.candidates[action_index]
        evaluation = evaluate_candidate(self.scenario, candidate)
        repeated_penalty = 4.0 if action_index in self.selected_actions else 0.0
        prior_best = self.best_score
        self.best_score = max(self.best_score, evaluation.reward_score)
        self.selected_actions.add(action_index)
        self.current_step += 1

        improvement = max(0.0, evaluation.reward_score - prior_best)
        reward = improvement + 0.08 * evaluation.objective_score - repeated_penalty
        done = self.current_step >= self.budget
        info = {
            "candidate": candidate,
            "evaluation": evaluation,
            "prior_best": prior_best,
            "best_score": self.best_score,
            "repeated": repeated_penalty > 0.0,
        }
        return self._observation(), round(float(reward), 4), done, info

    def action_mask(self) -> list[bool]:
        """Return True for actions that have not been selected in the current episode."""

        return [index not in self.selected_actions for index in range(len(self.candidates))]

    def evaluate_action(self, action_index: int) -> CandidateEvaluation:
        return evaluate_candidate(self.scenario, self.candidates[action_index])

    def _observation(self) -> dict[str, float]:
        return {
            "remaining_budget": float(max(self.budget - self.current_step, 0)),
            "best_score": float(self.best_score),
            "selected_fraction": float(len(self.selected_actions) / max(len(self.candidates), 1)),
        }

    def _generate_candidates(self, size: int) -> list[dict[str, float]]:
        candidates: list[dict[str, float]] = []
        for _ in range(size):
            candidate = {}
            for variable in self.scenario.design_space:
                candidate[variable.name] = float(self.rng.uniform(variable.low, variable.high))
            candidates.append(candidate)

        for fraction in [0.2, 0.5, 0.8]:
            candidates.append(
                {
                    variable.name: variable.low + fraction * (variable.high - variable.low)
                    for variable in self.scenario.design_space
                }
            )
        return candidates

    def _historical_best(self) -> float:
        scores = [
            float(row["objective_score"])
            for row in self.scenario.historical_experiments
            if "objective_score" in row
        ]
        return max(scores) if scores else 0.0
