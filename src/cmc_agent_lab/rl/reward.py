"""Reward model for simulator-backed CMC experiment campaigns."""

from __future__ import annotations

from dataclasses import dataclass

from cmc_agent_lab.schema import Scenario
from cmc_agent_lab.simulators.builtin import (
    run_arrhenius_stability,
    run_batch_reactor,
    run_crystallization_moments,
    run_noyes_whitney_dissolution,
    scenario_with_candidate,
)


@dataclass(frozen=True)
class CandidateEvaluation:
    """Model-backed score for a proposed process experiment."""

    variables: dict[str, float]
    metrics: dict[str, float]
    objective_score: float
    constraint_penalty: float

    @property
    def reward_score(self) -> float:
        return self.objective_score - self.constraint_penalty


def evaluate_candidate(scenario: Scenario, variables: dict[str, float]) -> CandidateEvaluation:
    """Run built-in mechanistic models and compute a bounded CQA reward."""

    candidate_scenario = scenario_with_candidate(scenario, variables)
    stability = run_arrhenius_stability(candidate_scenario)
    reaction = run_batch_reactor(candidate_scenario)
    crystallization = run_crystallization_moments(candidate_scenario)
    dissolution = run_noyes_whitney_dissolution(candidate_scenario)

    metrics = {}
    for result in [stability, reaction, crystallization, dissolution]:
        metrics.update(result.metrics)

    objective = weighted_cqa_score(scenario, metrics)
    penalty = constraint_penalty(scenario, metrics)
    return CandidateEvaluation(
        variables={key: float(value) for key, value in variables.items()},
        metrics=metrics,
        objective_score=round(objective, 4),
        constraint_penalty=round(penalty, 4),
    )


def weighted_cqa_score(scenario: Scenario, metrics: dict[str, float]) -> float:
    """Score candidate quality on a 0-100 scale using declared CQA weights."""

    weights = {cqa.name: cqa.weight for cqa in scenario.critical_quality_attributes}
    purity = min(100.0, metrics.get("purity_remaining_pct", 0.0))
    dissolution = min(100.0, metrics.get("dissolution_30min_pct", 0.0))
    particle_size = metrics.get("particle_size_d50_um", 120.0)
    particle = max(0.0, 100.0 - abs(particle_size - 57.5) * 2.0)
    isolated_yield = min(100.0, metrics.get("isolated_yield_proxy_pct", 0.0))
    impurity = max(0.0, 100.0 - metrics.get("impurity_proxy_pct", 10.0) * 15.0)

    score = (
        weights.get("purity", 0.3) * purity
        + weights.get("dissolution_30min", 0.25) * dissolution
        + weights.get("particle_size_d50_um", 0.2) * particle
        + weights.get("isolated_yield", 0.15) * isolated_yield
        + weights.get("impurity_burden", 0.1) * impurity
    )
    weight_total = sum(
        weights.get(name, 0.0)
        for name in [
            "purity",
            "dissolution_30min",
            "particle_size_d50_um",
            "isolated_yield",
            "impurity_burden",
        ]
    )
    return max(0.0, min(100.0, score / max(weight_total, 1e-6)))


def constraint_penalty(scenario: Scenario, metrics: dict[str, float]) -> float:
    """Penalize candidates that violate explicit development thresholds."""

    purity_threshold = float(scenario.constraints.get("purity_threshold_pct", 98.0))
    dissolution_threshold = float(scenario.constraints.get("dissolution_threshold_pct", 85.0))
    impurity_threshold = float(scenario.constraints.get("impurity_threshold_pct", 1.0))

    purity_gap = max(0.0, purity_threshold - metrics.get("purity_remaining_pct", 0.0))
    dissolution_gap = max(0.0, dissolution_threshold - metrics.get("dissolution_30min_pct", 0.0))
    impurity_gap = max(0.0, metrics.get("impurity_proxy_pct", 0.0) - impurity_threshold)
    particle_size = metrics.get("particle_size_d50_um", 0.0)
    particle_gap = 0.0
    if particle_size < 35.0:
        particle_gap = 35.0 - particle_size
    elif particle_size > 80.0:
        particle_gap = particle_size - 80.0

    return 0.4 * purity_gap + 0.25 * dissolution_gap + 0.6 * impurity_gap + 0.1 * particle_gap
