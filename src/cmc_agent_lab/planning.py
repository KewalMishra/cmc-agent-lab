"""Flexible planning policy for CMC agent workflows."""

from __future__ import annotations

from cmc_agent_lab.registry import default_tool_registry, mark_availability
from cmc_agent_lab.schema import Intent, Scenario, ToolSelection


def infer_intent(scenario: Scenario) -> Intent:
    """Infer the requested scientific activities from scenario metadata."""

    text = " ".join(
        [scenario.question, scenario.product_type, " ".join(scenario.unit_operations)]
    ).lower()
    activities: list[str] = []
    for keyword, activity in [
        ("stability", "stability"),
        ("shelf", "stability"),
        ("reaction", "reaction"),
        ("conversion", "reaction"),
        ("crystall", "crystallization"),
        ("particle", "crystallization"),
        ("dissolution", "dissolution"),
        ("solub", "dissolution"),
        ("formulation", "formulation"),
        ("experiment", "recommend_experiments"),
        ("optimiz", "optimize"),
        ("reinforcement", "reinforcement_learning"),
        ("policy", "learn"),
        ("learn", "learn"),
        ("sequential", "learn"),
        ("risk", "risk"),
        ("audit", "audit"),
    ]:
        if keyword in text and activity not in activities:
            activities.append(activity)

    mode_activity_map = {
        "scope": ["scope"],
        "screen": ["screen", "risk"],
        "simulate": ["simulate"],
        "optimize": ["optimize", "recommend_experiments"],
        "learn": ["learn", "reinforcement_learning", "recommend_experiments"],
        "risk": ["risk"],
        "audit": ["audit"],
        "full": ["simulate", "optimize", "recommend_experiments", "risk", "audit"],
    }
    for activity in mode_activity_map[scenario.mode]:
        if activity not in activities:
            activities.append(activity)
    if scenario.constraints.get("enable_rl_policy", False):
        for activity in ["learn", "reinforcement_learning"]:
            if activity not in activities:
                activities.append(activity)

    entities = scenario.unit_operations + [cqa.name for cqa in scenario.critical_quality_attributes]
    constraints = [f"{key}={value}" for key, value in scenario.constraints.items()]
    return Intent(
        activities=activities,
        entities=entities,
        constraints=constraints,
        rationale=(
            "Intent derived from workflow mode, process unit operations, CQAs, and question terms."
        ),
    )


def build_tool_plan(scenario: Scenario, intent: Intent) -> list[ToolSelection]:
    """Choose tools based on requested activities, availability, and disabled tools."""

    registry = default_tool_registry()
    availability = mark_availability(registry)
    disabled = set(scenario.disabled_tools) | set(scenario.constraints.get("disabled_tools", []))
    requested = set(scenario.requested_tools)

    if scenario.mode == "scope":
        allowed_categories = {"risk"}
    elif scenario.mode == "screen":
        allowed_categories = {"mechanistic_simulator", "property_package", "risk"}
    elif scenario.mode == "risk":
        allowed_categories = {"risk"}
    elif scenario.mode == "audit":
        allowed_categories = {"risk"}
    elif scenario.mode == "optimize":
        allowed_categories = {"optimizer", "risk"}
    elif scenario.mode == "learn":
        allowed_categories = {"rl_policy", "risk"}
    else:
        allowed_categories = {
            "mechanistic_simulator",
            "property_package",
            "optimizer",
            "rl_policy",
            "risk",
            "process_simulator",
            "chemistry_simulator",
        }

    selections: list[ToolSelection] = []
    for tool in registry:
        if tool.name in disabled:
            continue
        if tool.category not in allowed_categories:
            continue
        if requested and tool.name not in requested:
            continue
        if not _matches_intent(tool.activities + tool.domains, intent.activities):
            continue
        available = availability[tool.name]
        if tool.name.startswith("external.") and not available and tool.name not in requested:
            continue
        required = not tool.name.startswith("external.")
        selections.append(
            ToolSelection(
                tool_name=tool.name,
                category=tool.category,
                reason=_reason(tool, intent.activities, available),
                required=required,
                available=available,
            )
        )

    if not any(item.tool_name == "risk.qbd_fmea" for item in selections):
        selections.append(
            ToolSelection(
                tool_name="risk.qbd_fmea",
                category="risk",
                reason="Always include CQA/CPP risk framing for regulated development decisions.",
                required=True,
                available=True,
            )
        )
    return selections


def _matches_intent(tool_labels: list[str], activities: list[str]) -> bool:
    if "simulate" in activities and any(label in tool_labels for label in ["simulate", "screen"]):
        return True
    return any(activity in tool_labels for activity in activities)


def _reason(tool, activities: list[str], available: bool) -> str:
    status = "available" if available else "declared but optional dependency is not installed"
    matched = [label for label in tool.domains if label in activities]
    if not matched:
        matched = tool.domains[:3]
    return f"Maps to {', '.join(matched)}; {status}. {tool.description}"
