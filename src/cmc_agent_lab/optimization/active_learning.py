"""Experiment recommendation with surrogate-aware acquisition scoring."""

from __future__ import annotations

import math

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel

from cmc_agent_lab.schema import ExperimentRecommendation, Scenario


def recommend_experiments(scenario: Scenario, n: int | None = None) -> list[ExperimentRecommendation]:
    """Rank candidate experiments using historical data when available."""

    n = n or scenario.max_experiments
    candidates = _candidate_grid(scenario, size=max(80, n * 20))
    if len(scenario.historical_experiments) >= 3:
        scores, uncertainty = _gp_acquisition(scenario, candidates)
    else:
        scores = np.array([_heuristic_score(scenario, candidate) for candidate in candidates])
        uncertainty = np.array([_space_filling_bonus(scenario, candidate) for candidate in candidates])

    acquisition = scores + 0.35 * uncertainty
    order = np.argsort(acquisition)[::-1]
    recommendations: list[ExperimentRecommendation] = []
    seen: list[dict[str, float]] = []
    for index in order:
        candidate = candidates[index]
        if _too_close(candidate, seen):
            continue
        seen.append(candidate)
        rank = len(recommendations) + 1
        recommendations.append(
            ExperimentRecommendation(
                rank=rank,
                variables={key: round(value, 4) for key, value in candidate.items()},
                expected_score=round(float(scores[index]), 3),
                information_gain=round(float(uncertainty[index]), 3),
                rationale=_rationale(candidate, scenario, float(scores[index]), float(uncertainty[index])),
                constraints_checked=[
                    "within declared design-space bounds",
                    "ranked by expected CQA improvement and information gain",
                    "requires scientist approval before wet-lab execution",
                ],
            )
        )
        if len(recommendations) >= n:
            break
    return recommendations


def _candidate_grid(scenario: Scenario, size: int) -> list[dict[str, float]]:
    rng = np.random.default_rng(7)
    candidates: list[dict[str, float]] = []
    for _ in range(size):
        candidate = {}
        for variable in scenario.design_space:
            candidate[variable.name] = float(rng.uniform(variable.low, variable.high))
        candidates.append(candidate)
    for fraction in [0.2, 0.5, 0.8]:
        candidate = {
            variable.name: variable.low + fraction * (variable.high - variable.low)
            for variable in scenario.design_space
        }
        candidates.append(candidate)
    return candidates


def _gp_acquisition(
    scenario: Scenario, candidates: list[dict[str, float]]
) -> tuple[np.ndarray, np.ndarray]:
    variable_names = [variable.name for variable in scenario.design_space]
    x_train = []
    y_train = []
    for row in scenario.historical_experiments:
        if "objective_score" not in row:
            continue
        x_train.append([float(row.get(name, _midpoint(scenario, name))) for name in variable_names])
        y_train.append(float(row["objective_score"]))
    if len(x_train) < 3:
        scores = np.array([_heuristic_score(scenario, candidate) for candidate in candidates])
        uncertainty = np.array([_space_filling_bonus(scenario, candidate) for candidate in candidates])
        return scores, uncertainty

    x = np.array(x_train)
    y = np.array(y_train)
    x_candidates = np.array([[candidate[name] for name in variable_names] for candidate in candidates])
    x_scaled, x_candidate_scaled = _scale_features(scenario, x, x_candidates)
    kernel = Matern(length_scale=np.ones(x_scaled.shape[1]), nu=2.5) + WhiteKernel(noise_level=1.0)
    model = GaussianProcessRegressor(kernel=kernel, normalize_y=True, random_state=7)
    model.fit(x_scaled, y)
    mean, std = model.predict(x_candidate_scaled, return_std=True)
    heuristic = np.array([_heuristic_score(scenario, candidate) for candidate in candidates])
    scores = 0.65 * mean + 0.35 * heuristic
    return scores, std


def _scale_features(
    scenario: Scenario, x: np.ndarray, x_candidates: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    lows = np.array([variable.low for variable in scenario.design_space])
    highs = np.array([variable.high for variable in scenario.design_space])
    width = np.maximum(highs - lows, 1e-6)
    return (x - lows) / width, (x_candidates - lows) / width


def _heuristic_score(scenario: Scenario, candidate: dict[str, float]) -> float:
    temp = candidate.get("temperature_c", 40.0)
    cooling = candidate.get("cooling_rate_c_min", 0.6)
    antisolvent = candidate.get("antisolvent_fraction", 0.25)
    residence = candidate.get("residence_time_min", 90.0)
    ph = candidate.get("ph", 6.0)

    reaction_score = 100.0 * (1.0 - math.exp(-residence / 85.0)) - max(temp - 45.0, 0.0) * 0.7
    crystal_score = 88.0 - abs(cooling - 0.55) * 18.0 - abs(antisolvent - 0.27) * 45.0
    dissolution_score = 82.0 + 10.0 * math.exp(-((ph - 6.6) ** 2) / 2.0) - antisolvent * 9.0
    stability_score = 97.0 - max(temp - 35.0, 0.0) * 0.45

    weights = {cqa.name: cqa.weight for cqa in scenario.critical_quality_attributes}
    return (
        weights.get("isolated_yield", 0.15) * reaction_score
        + weights.get("particle_size_d50_um", 0.2) * crystal_score
        + weights.get("dissolution_30min", 0.25) * dissolution_score
        + weights.get("purity", 0.3) * stability_score
        + weights.get("impurity_burden", 0.1) * (100.0 - max(temp - 45.0, 0.0))
    )


def _space_filling_bonus(scenario: Scenario, candidate: dict[str, float]) -> float:
    if not scenario.historical_experiments:
        return 4.0
    variable_names = [variable.name for variable in scenario.design_space]
    distances = []
    for row in scenario.historical_experiments:
        squared = 0.0
        for variable in scenario.design_space:
            width = max(variable.high - variable.low, 1e-6)
            squared += ((candidate[variable.name] - float(row.get(variable.name, variable.midpoint))) / width) ** 2
        distances.append(math.sqrt(squared / max(len(variable_names), 1)))
    return min(10.0, 20.0 * min(distances))


def _too_close(candidate: dict[str, float], selected: list[dict[str, float]]) -> bool:
    for existing in selected:
        total = sum(abs(candidate[key] - existing.get(key, candidate[key])) for key in candidate)
        if total < 1e-6:
            return True
    return False


def _midpoint(scenario: Scenario, variable_name: str) -> float:
    for variable in scenario.design_space:
        if variable.name == variable_name:
            return variable.midpoint
    return 0.0


def _rationale(
    candidate: dict[str, float], scenario: Scenario, score: float, uncertainty: float
) -> str:
    variables = ", ".join(f"{key}={value:.3g}" for key, value in candidate.items())
    history = "uses GP uncertainty from historical experiments" if scenario.historical_experiments else "uses space-filling uncertainty"
    return f"{variables}; expected score {score:.1f}; {history}; information gain {uncertainty:.2f}."
