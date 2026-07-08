# Thermo/Chemicals Solvent Property Screen

## Executive Summary

CMC Agent Lab translated the development question into a tool-routed, auditable screen workflow for small_molecule_tablet.

## Objective

Screen a water/ethanol solvent system for a poorly soluble API using an open-source thermodynamic property package before deciding whether to run dissolution and crystallization experiments.

## Selected Tools

- `external.thermo_chemicals` (property_package, available): Maps to phase_equilibrium, properties, mixtures; available. Thermodynamic and chemical-property libraries for Python.
- `risk.qbd_fmea` (risk, available): Always include CQA/CPP risk framing for regulated development decisions.

## Model and Simulator Results

### external.thermo_chemicals

- property_temperature_k: 298.150
- api_molecular_weight_g_mol: 151.163
- api_melting_point_k: 442.950
- api_boiling_point_k: 773.150
- api_vapor_pressure_pa: 0.153
- api_density_kg_m3: 1142.074
- api_solubility_parameter_mpa05: 24.469
- solvent_density_kg_m3: 903.914
- solvent_viscosity_pa_s: 0.002
- solvent_surface_tension_n_m: 0.039
- solubility_parameter_gap_mpa05: 10.752
- Warning: acetaminophen is predicted as solid at the screening temperature.
- Assumptions: Thermo/Chemicals properties are used as an open-source screening property package.; Solubility-parameter mismatch is a proxy for solvent compatibility, not a validated solubility model.; Mixture properties are used for early CMC screening and require experimental confirmation.


## QbD Risk Register

- RPN 40: `temperature_c` -> `purity`. temperature_c variability may move purity outside target >= 98.0% Mitigation: Add stability-indicating method and impurity trend review.
- RPN 32: `ph` -> `dissolution_30min`. ph variability may move dissolution_30min outside target >= 85.0% Mitigation: Confirm discriminatory dissolution method and pH/formulation range.
- RPN 27: `cooling_rate_c_min` -> `particle_size_d50_um`. cooling_rate_c_min variability may move particle_size_d50_um outside target 35-80 um Mitigation: Use PAT particle-size monitoring during crystallization.

## Audit Controls

- Human review required: True
- Audit events recorded: 6
- objective_scoping: ok - Parsed workflow mode, unit operations, CQAs, and constraints into structured intent.
- tool_planning: ok - Selected 2 tools for mode=screen.
- mechanistic_simulation: ok - Executed or evaluated 1 simulator selections.
- experiment_design: ok - Skipped experiment generation for mode=screen.
- qbd_risk_review: ok - Created 3 CQA/CPP risk items.
- audit_verification: ok - Audit trail complete.

## Intended Use Boundary

This is a process-development decision-support workflow. It proposes model-backed experiments for scientist review; it does not release, validate, or manufacture a drug product.
