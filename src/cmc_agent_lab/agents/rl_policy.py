"""RL policy agent."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.rl.policy import train_epsilon_greedy_policy
from cmc_agent_lab.schema import AgentState


def learn_experiment_policy(state: AgentState) -> AgentState:
    state.rl_policy = train_epsilon_greedy_policy(state.scenario)
    return record_event(
        state,
        step="rl_policy_learning",
        summary=(
            f"Trained {state.rl_policy.policy_name} for {state.rl_policy.episodes} episodes "
            f"over {state.rl_policy.candidate_count} candidate experiments."
        ),
        inputs={
            "mode": state.scenario.mode,
            "constraints": state.scenario.constraints,
            "design_space": [item.model_dump() for item in state.scenario.design_space],
        },
        outputs=state.rl_policy.model_dump(),
    )
