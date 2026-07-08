# RL-Guided CMC Experiment Campaign

## Executive Summary

CMC Agent Lab translated the development question into a tool-routed, auditable learn workflow for small_molecule_tablet.

## Objective

Learn a sequential experiment-selection policy for a late-stage small molecule process. The policy should use mechanistic simulator feedback to choose experiments that improve purity, dissolution, particle size, yield, and impurity burden within a five-experiment budget.

## Selected Tools

- `rl.epsilon_greedy_campaign` (rl_policy, available): Maps to sequential_experimentation, digital_twin, policy_learning; available. Sequential experiment-selection policy trained against the mechanistic simulator environment.
- `risk.qbd_fmea` (risk, available): Always include CQA/CPP risk framing for regulated development decisions.

## Reinforcement Learning Policy

- Policy: `epsilon_greedy_simulator_policy`
- Episodes: 25
- Experiment budget: 5
- Candidate experiments: 83
- Best objective score: 78.358
- Best reward-adjusted score: 68.866
- Random baseline reward-adjusted score: 56.245
- Improvement over random: 12.621
- Best learned experiment: temperature_c=42.5995, cooling_rate_c_min=0.6341, antisolvent_fraction=0.0181, residence_time_min=83.9555, ph=6.5313

### RL-Selected Experiment Batch

1. temperature_c=42.5995, cooling_rate_c_min=0.6341, antisolvent_fraction=0.0181, residence_time_min=83.9555, ph=6.5313 | simulator score=78.358 | learned value=6.269
2. temperature_c=28.5348, cooling_rate_c_min=0.3956, antisolvent_fraction=0.2607, residence_time_min=54.2121, ph=5.9458 | simulator score=75.513 | learned value=6.041
3. temperature_c=37.3926, cooling_rate_c_min=1.469, antisolvent_fraction=0.026, residence_time_min=68.027, ph=6.6463 | simulator score=74.308 | learned value=5.945
4. temperature_c=58.4056, cooling_rate_c_min=0.3825, antisolvent_fraction=0.0981, residence_time_min=137.4877, ph=5.9121 | simulator score=73.847 | learned value=5.908
5. temperature_c=29.0, cooling_rate_c_min=0.38, antisolvent_fraction=0.09, residence_time_min=60.0, ph=5.1 | simulator score=72.578 | learned value=5.806

## QbD Risk Register

- RPN 48: `temperature_c` -> `impurity_burden`. temperature_c variability may move impurity_burden outside target <= 1.0% Mitigation: Constrain high-temperature residence time and monitor side products.
- RPN 40: `temperature_c` -> `purity`. temperature_c variability may move purity outside target >= 98.0% Mitigation: Add stability-indicating method and impurity trend review.
- RPN 32: `ph` -> `dissolution_30min`. ph variability may move dissolution_30min outside target >= 85.0% Mitigation: Confirm discriminatory dissolution method and pH/formulation range.
- RPN 27: `cooling_rate_c_min` -> `particle_size_d50_um`. cooling_rate_c_min variability may move particle_size_d50_um outside target 35-80 um Mitigation: Use PAT particle-size monitoring during crystallization.
- RPN 27: `residence_time_min` -> `isolated_yield`. residence_time_min variability may move isolated_yield outside target >= 82.0% Mitigation: Run mass-balance reconciliation and yield sensitivity.

## Audit Controls

- Human review required: True
- Audit events recorded: 6
- objective_scoping: ok - Parsed workflow mode, unit operations, CQAs, and constraints into structured intent.
- tool_planning: ok - Selected 2 tools for mode=learn.
- experiment_design: ok - Skipped experiment generation for mode=learn.
- rl_policy_learning: ok - Trained epsilon_greedy_simulator_policy for 25 episodes over 83 candidate experiments.
- qbd_risk_review: ok - Created 5 CQA/CPP risk items.
- audit_verification: ok - Audit trail complete.

## Intended Use Boundary

This is a process-development decision-support workflow. It proposes model-backed experiments for scientist review; it does not release, validate, or manufacture a drug product.
