# Small Molecule Tablet Process Development

## Executive Summary

CMC Agent Lab translated the development question into a tool-routed, auditable full workflow for small_molecule_tablet.

## Objective

For a poorly soluble late-stage small molecule intended as an oral tablet, identify the minimum set of crystallization, reaction, dissolution, and stability experiments that should be run next to improve manufacturability, purity, dissolution, and 24-month shelf-life.

## Selected Tools

- `builtin.arrhenius_stability` (mechanistic_simulator, available): Maps to stability; available. First-order Arrhenius degradation model for shelf-life sensitivity.
- `builtin.batch_reactor_ode` (mechanistic_simulator, available): Maps to reaction; available. ODE model for main reaction conversion and side-product formation.
- `builtin.crystallization_moments` (mechanistic_simulator, available): Maps to crystallization; available. Moment-based population-balance approximation for crystallization.
- `builtin.noyes_whitney_dissolution` (mechanistic_simulator, available): Maps to dissolution; available. Noyes-Whitney dissolution model with pH and antisolvent adjustments.
- `optimizer.active_learning_batch` (optimizer, available): Maps to design_of_experiments, bayesian_optimization; available. Candidate ranking with GP uncertainty when historical data is available.
- `rl.epsilon_greedy_campaign` (rl_policy, available): Maps to sequential_experimentation, digital_twin, policy_learning; available. Sequential experiment-selection policy trained against the mechanistic simulator environment.
- `risk.qbd_fmea` (risk, available): Maps to qbd, cqa, cpp; available. QbD/FMEA-style risk register linking CPPs to CQAs.
- `external.thermo_chemicals` (property_package, available): Maps to phase_equilibrium, properties, mixtures; available. Thermodynamic and chemical-property libraries for Python.

## Model and Simulator Results

### builtin.arrhenius_stability

- purity_remaining_pct: 91.604
- degradation_pct: 8.396
- degradation_rate_per_day: 0.000
- Warning: Predicted shelf-life purity is below threshold.
- Assumptions: Single dominant first-order degradation pathway.; Arrhenius temperature dependence around 25 C reference.

### builtin.batch_reactor_ode

- conversion_pct: 98.888
- isolated_yield_proxy_pct: 88.965
- impurity_proxy_pct: 13.609
- Warning: Side-product burden exceeds a typical late-stage impurity threshold.
- Assumptions: Competitive first-order main and side reactions.; Well-mixed batch or plug-flow-equivalent residence-time approximation.

### builtin.crystallization_moments

- crystallization_yield_pct: 70.134
- particle_size_d50_um: 91.558
- nucleation_density_proxy: 16.091
- Assumptions: Moment-based population-balance approximation.; Temperature-dependent solubility and antisolvent-driven supersaturation.

### builtin.noyes_whitney_dissolution

- dissolution_30min_pct: 73.140
- relative_solubility_capacity: 0.853
- Warning: Dissolution at 30 minutes is below target.
- Assumptions: Noyes-Whitney dissolution with constant surface-area proxy.; pH and antisolvent terms approximate formulation effects.

### external.thermo_chemicals

- property_temperature_k: 315.650
- api_molecular_weight_g_mol: 151.163
- api_melting_point_k: 442.950
- api_boiling_point_k: 773.150
- api_vapor_pressure_pa: 1.044
- api_density_kg_m3: 1135.916
- api_solubility_parameter_mpa05: 23.932
- solvent_density_kg_m3: 890.372
- solvent_viscosity_pa_s: 0.002
- solvent_surface_tension_n_m: 0.037
- solubility_parameter_gap_mpa05: 10.588
- Warning: acetaminophen is predicted as solid at the screening temperature.
- Assumptions: Thermo/Chemicals properties are used as an open-source screening property package.; Solubility-parameter mismatch is a proxy for solvent compatibility, not a validated solubility model.; Mixture properties are used for early CMC screening and require experimental confirmation.

## Recommended Next Experiments

1. temperature_c=40.1321, cooling_rate_c_min=0.6203, antisolvent_fraction=0.2616, residence_time_min=172.1848, ph=7.1672 | expected score=78.494 | information gain=4.948
   Rationale: temperature_c=40.1, cooling_rate_c_min=0.62, antisolvent_fraction=0.262, residence_time_min=172, ph=7.17; expected score 78.5; uses GP uncertainty from historical experiments; information gain 4.95.
2. temperature_c=33.1689, cooling_rate_c_min=0.5101, antisolvent_fraction=0.1938, residence_time_min=179.8588, ph=5.5577 | expected score=78.438 | information gain=4.948
   Rationale: temperature_c=33.2, cooling_rate_c_min=0.51, antisolvent_fraction=0.194, residence_time_min=180, ph=5.56; expected score 78.4; uses GP uncertainty from historical experiments; information gain 4.95.
3. temperature_c=28.5877, cooling_rate_c_min=0.4727, antisolvent_fraction=0.2413, residence_time_min=142.2497, ph=7.1898 | expected score=78.378 | information gain=4.948
   Rationale: temperature_c=28.6, cooling_rate_c_min=0.473, antisolvent_fraction=0.241, residence_time_min=142, ph=7.19; expected score 78.4; uses GP uncertainty from historical experiments; information gain 4.95.
4. temperature_c=24.3311, cooling_rate_c_min=1.0257, antisolvent_fraction=0.2844, residence_time_min=153.5828, ph=6.9105 | expected score=78.108 | information gain=4.948
   Rationale: temperature_c=24.3, cooling_rate_c_min=1.03, antisolvent_fraction=0.284, residence_time_min=154, ph=6.91; expected score 78.1; uses GP uncertainty from historical experiments; information gain 4.95.
5. temperature_c=37.1263, cooling_rate_c_min=0.2872, antisolvent_fraction=0.2981, residence_time_min=154.5829, ph=5.6306 | expected score=77.945 | information gain=4.948
   Rationale: temperature_c=37.1, cooling_rate_c_min=0.287, antisolvent_fraction=0.298, residence_time_min=155, ph=5.63; expected score 77.9; uses GP uncertainty from historical experiments; information gain 4.95.

## QbD Risk Register

- RPN 48: `temperature_c` -> `impurity_burden`. temperature_c variability may move impurity_burden outside target <= 1.0% Mitigation: Constrain high-temperature residence time and monitor side products.
- RPN 40: `temperature_c` -> `purity`. temperature_c variability may move purity outside target >= 98.0% Mitigation: Add stability-indicating method and impurity trend review.
- RPN 32: `ph` -> `dissolution_30min`. ph variability may move dissolution_30min outside target >= 85.0% Mitigation: Confirm discriminatory dissolution method and pH/formulation range.
- RPN 27: `cooling_rate_c_min` -> `particle_size_d50_um`. cooling_rate_c_min variability may move particle_size_d50_um outside target 35-80 um Mitigation: Use PAT particle-size monitoring during crystallization.
- RPN 27: `residence_time_min` -> `isolated_yield`. residence_time_min variability may move isolated_yield outside target >= 82.0% Mitigation: Run mass-balance reconciliation and yield sensitivity.

## Audit Controls

- Human review required: True
- Audit events recorded: 7
- objective_scoping: ok - Parsed workflow mode, unit operations, CQAs, and constraints into structured intent.
- tool_planning: ok - Selected 8 tools for mode=full.
- mechanistic_simulation: ok - Executed or evaluated 5 simulator selections.
- surrogate_readiness: ok - Historical experiment count=4; surrogate status=ready.
- experiment_design: ok - Recommended top 5 next experiments.
- qbd_risk_review: ok - Created 5 CQA/CPP risk items.
- audit_verification: ok - Audit trail complete.

## Intended Use Boundary

This is a process-development decision-support workflow. It proposes model-backed experiments for scientist review; it does not release, validate, or manufacture a drug product.
