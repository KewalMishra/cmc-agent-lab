# Product Plan

## Product Concept

**Agentic Process Development Copilot**

A process scientist enters a development question, product target, current design space, and
available historical experiments. The system chooses the smallest useful workflow, runs
scientific tools when needed, and returns an auditable recommendation package.

## Primary User

Late-stage pharmaceutical development scientists and process engineers working on small-molecule
or formulation process development.

## Main Demo Workflow

1. User asks for the minimum next experiments to improve purity, dissolution, particle size,
   yield, and shelf-life.
2. Agent extracts QTPP/CQAs/CPPs.
3. Agent selects stability, reaction, crystallization, dissolution, optimizer, and risk tools.
4. Built-in mechanistic models run locally.
5. Historical experiments feed a Gaussian-process acquisition function.
6. Optional RL mode trains a simulator-backed sequential experiment policy.
7. Agent recommends five experiments.
8. Agent generates a QbD risk register and audit trail.
9. Agent renders a technical development memo.

## Why It Stands Out

- It targets a real late-stage pharma workflow rather than a generic chatbot.
- It combines mechanistic simulation and surrogate ML.
- It makes sparse-data experiment planning central.
- It shows product judgment: flexible modes, user control, auditability, and human approval.
- It creates a credible bridge from AI engineering to product management in HCLS/CMC.

## Milestones

### v0.1

- Deterministic local workflow.
- Built-in mechanistic models.
- Active-learning recommendation.
- RL-lite sequential experiment policy.
- QbD risk register.
- Markdown technical memo.

### v0.2

- Streamlit or FastAPI UI.
- LangGraph checkpointing and human approval interrupt.
- LangSmith or local trace viewer.
- PharmaPy adapter for one crystallization flowsheet.
- Gymnasium wrapper around the simulator-backed RL environment.

### v0.3

- Thermo/Chemicals property backend.
- IDAES/Pyomo optimization example.
- Evaluation dashboard for route correctness, simulator provenance, recommendation quality, and
  audit completeness.

### v1.0

- Full portfolio demo with hosted docs, screenshots, benchmark report, and updated personal
  website case study.
