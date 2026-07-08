# Reinforcement Learning Integration

## Why RL Fits This Project

The strongest RL use case is not a chat agent. It is a **sequential experiment-selection
policy** trained against a simulator or digital twin. That matches the CMC problem: each
experiment is expensive, so the system should learn which experiment to run next under a fixed
budget.

## Current Implementation

The repository includes a dependency-free RL-lite baseline:

- `cmc_agent_lab.rl.env.CMCProcessEnv`
- `cmc_agent_lab.rl.reward.evaluate_candidate`
- `cmc_agent_lab.rl.policy.train_epsilon_greedy_policy`
- workflow mode: `learn`
- tool registry entry: `rl.epsilon_greedy_campaign`

The environment follows the familiar `reset()` / `step(action)` pattern, but does not require
Gymnasium as a hard dependency.

## RL Formulation

### State

The current state includes:

- remaining experiment budget
- best reward-adjusted score observed in the campaign
- fraction of candidate actions already selected

Future versions can add:

- posterior uncertainty from a Gaussian-process surrogate
- CQA gaps versus target
- simulator warnings
- risk register state
- scientist accept/reject feedback

### Action

An action is a proposed experiment from the candidate design space:

- temperature
- cooling rate
- antisolvent fraction
- residence time
- pH

The design space is bounded by the scenario YAML.

### Environment

The environment uses the built-in mechanistic models as a digital twin:

- Arrhenius stability model
- batch reaction ODE model
- crystallization moment model
- Noyes-Whitney dissolution model

Each action is evaluated by running those simulators at the chosen process conditions.

### Reward

The reward balances CQA improvement and process-development risk:

- positive score for purity, dissolution, particle-size fit, yield, and impurity control
- penalties for missing purity, dissolution, impurity, and particle-size thresholds
- repeated-action penalty
- experiment-budget awareness

This keeps RL aligned with process-development decisions instead of optimizing an abstract
agent score.

## How To Run

```bash
PYTHONPATH=src python -m cmc_agent_lab run examples/rl_experiment_policy.yaml
```

Or override any scenario:

```bash
PYTHONPATH=src python -m cmc_agent_lab run examples/small_molecule_process.yaml --mode learn
```

## Extension Path

### Phase 1: Current baseline

Use epsilon-greedy policy learning over simulator-generated candidate experiments. This is
simple, auditable, deterministic, and easy to explain in an interview.

### Phase 2: Contextual bandit

Add richer context:

- current CQA gaps
- posterior uncertainty
- similarity to historical experiments
- model-warning flags

Then compare against random search, DOE, and Bayesian optimization.

### Phase 3: Gymnasium adapter

Add an optional wrapper around `CMCProcessEnv` using the `rl` optional dependencies:

```bash
python -m pip install -e ".[rl]"
```

This enables PPO/SAC-style experiments through stable-baselines3 without changing the domain
reward or simulator contract.

### Phase 4: Agent-level RL

Move beyond choosing experiments. The policy can learn workflow decisions:

- simulate first or fit surrogate first
- ask for human review
- run stability-only analysis
- run full process optimization
- stop because uncertainty is low enough

The reward should include audit completeness, cost, recommendation quality, and scientist
acceptance.

## Interview Positioning

The credible framing is:

> The agent uses mechanistic simulators as a safe digital twin where reinforcement learning can
> learn experiment-selection policies before any wet-lab execution. The learned policy remains
> bounded by QbD risk controls and human approval.
