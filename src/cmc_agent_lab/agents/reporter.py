"""Technical memo renderer."""

from __future__ import annotations

from cmc_agent_lab.audit import record_event
from cmc_agent_lab.schema import AgentState


def render_report(state: AgentState) -> AgentState:
    scenario = state.scenario
    lines = [
        f"# {scenario.project_name}",
        "",
        "## Executive Summary",
        "",
        (
            "CMC Agent Lab translated the development question into a tool-routed, auditable "
            f"{scenario.mode} workflow for {scenario.product_type}."
        ),
        "",
        "## Objective",
        "",
        scenario.question.strip(),
        "",
        "## Selected Tools",
        "",
    ]
    for item in state.tool_plan:
        availability = "available" if item.available else "not installed"
        lines.append(f"- `{item.tool_name}` ({item.category}, {availability}): {item.reason}")

    if state.simulations:
        lines.extend(["", "## Model and Simulator Results", ""])
        for result in state.simulations:
            lines.append(f"### {result.tool_name}")
            lines.append("")
            if result.status != "ok":
                lines.append(f"- Status: {result.status}")
            for key, value in result.metrics.items():
                lines.append(f"- {key}: {value:.3f}")
            for warning in result.warnings:
                lines.append(f"- Warning: {warning}")
            if result.assumptions:
                lines.append(f"- Assumptions: {'; '.join(result.assumptions)}")
            lines.append("")

    if state.recommendations:
        lines.extend(["## Recommended Next Experiments", ""])
        for rec in state.recommendations:
            variables = ", ".join(f"{key}={value}" for key, value in rec.variables.items())
            lines.append(
                f"{rec.rank}. {variables} | expected score={rec.expected_score} | "
                f"information gain={rec.information_gain}"
            )
            lines.append(f"   Rationale: {rec.rationale}")

    if state.rl_policy:
        lines.extend(["", "## Reinforcement Learning Policy", ""])
        lines.append(f"- Policy: `{state.rl_policy.policy_name}`")
        lines.append(f"- Episodes: {state.rl_policy.episodes}")
        lines.append(f"- Experiment budget: {state.rl_policy.budget}")
        lines.append(f"- Candidate experiments: {state.rl_policy.candidate_count}")
        lines.append(f"- Best objective score: {state.rl_policy.best_objective_score:.3f}")
        lines.append(f"- Best reward-adjusted score: {state.rl_policy.best_reward:.3f}")
        lines.append(f"- Random baseline reward-adjusted score: {state.rl_policy.random_baseline_score:.3f}")
        lines.append(f"- Improvement over random: {state.rl_policy.improvement_over_random:.3f}")
        if state.rl_policy.best_variables:
            variables = ", ".join(
                f"{key}={value}" for key, value in state.rl_policy.best_variables.items()
            )
            lines.append(f"- Best learned experiment: {variables}")
        if state.rl_policy.recommendations:
            lines.extend(["", "### RL-Selected Experiment Batch", ""])
            for rec in state.rl_policy.recommendations:
                variables = ", ".join(f"{key}={value}" for key, value in rec.variables.items())
                lines.append(
                    f"{rec.rank}. {variables} | simulator score={rec.expected_score} | "
                    f"learned value={rec.information_gain}"
                )

    if state.risk_register:
        lines.extend(["", "## QbD Risk Register", ""])
        for item in state.risk_register:
            lines.append(
                f"- RPN {item.rpn}: `{item.cpp}` -> `{item.cqa}`. "
                f"{item.risk} Mitigation: {item.mitigation}"
            )

    lines.extend(
        [
            "",
            "## Audit Controls",
            "",
            f"- Human review required: {state.human_review_required}",
            f"- Audit events recorded: {len(state.audit_events)}",
        ]
    )
    for event in state.audit_events:
        lines.append(f"- {event.step}: {event.status} - {event.summary}")

    lines.extend(
        [
            "",
            "## Intended Use Boundary",
            "",
            (
                "This is a process-development decision-support workflow. It proposes model-backed "
                "experiments for scientist review; it does not release, validate, or manufacture a drug product."
            ),
        ]
    )
    state.report = "\n".join(lines) + "\n"
    return record_event(
        state,
        step="report_rendering",
        summary="Rendered technical development memo.",
        inputs=state.to_jsonable(),
        outputs={"characters": len(state.report)},
    )
