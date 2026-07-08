"""Typed contracts for CMC Agent Lab."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

WorkflowMode = Literal["scope", "screen", "simulate", "optimize", "learn", "risk", "audit", "full"]


class CriticalQualityAttribute(BaseModel):
    """Critical quality attribute defined from the target product profile."""

    name: str
    target: str | None = None
    weight: float = 1.0
    risk_severity: int = Field(default=3, ge=1, le=5)


class DesignVariable(BaseModel):
    """Controllable process variable in the experimental design space."""

    name: str
    low: float
    high: float
    units: str | None = None

    @property
    def midpoint(self) -> float:
        return (self.low + self.high) / 2.0


class Scenario(BaseModel):
    """Scenario loaded from YAML."""

    project_name: str
    question: str
    mode: WorkflowMode = "full"
    product_type: str = "small_molecule"
    route: str | None = None
    unit_operations: list[str] = Field(default_factory=list)
    qtp_profile: dict[str, Any] = Field(default_factory=dict)
    critical_quality_attributes: list[CriticalQualityAttribute] = Field(default_factory=list)
    design_space: list[DesignVariable] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    historical_experiments: list[dict[str, Any]] = Field(default_factory=list)
    disabled_tools: list[str] = Field(default_factory=list)
    requested_tools: list[str] = Field(default_factory=list)

    @property
    def max_experiments(self) -> int:
        return int(self.constraints.get("max_experiments", 5))


class Intent(BaseModel):
    """Structured interpretation of the user/scientist request."""

    activities: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    rationale: str = ""


class ToolSpec(BaseModel):
    """Tool metadata used by the planner."""

    name: str
    category: str
    fidelity: str
    activities: list[str]
    domains: list[str]
    optional_dependency: str | None = None
    estimated_runtime: str = "seconds"
    description: str


class ToolSelection(BaseModel):
    """Planner-selected tool and reason."""

    tool_name: str
    category: str
    reason: str
    required: bool = True
    available: bool = True


class SimulationResult(BaseModel):
    """Normalized output from a mechanistic or simulator-backed model."""

    tool_name: str
    status: str = "ok"
    inputs: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ExperimentRecommendation(BaseModel):
    """Recommended next experiment."""

    rank: int
    variables: dict[str, float]
    expected_score: float
    information_gain: float
    rationale: str
    constraints_checked: list[str] = Field(default_factory=list)


class RLPolicyStep(BaseModel):
    """One interaction between the policy and the simulator environment."""

    episode: int
    step: int
    action_index: int
    variables: dict[str, float]
    reward: float
    objective_score: float
    done: bool


class RLPolicyResult(BaseModel):
    """Summary of an RL experiment-selection policy run."""

    policy_name: str
    episodes: int
    budget: int
    candidate_count: int
    best_reward: float
    best_objective_score: float
    best_variables: dict[str, float]
    random_baseline_score: float
    improvement_over_random: float
    trajectory: list[RLPolicyStep] = Field(default_factory=list)
    recommendations: list[ExperimentRecommendation] = Field(default_factory=list)


class RiskItem(BaseModel):
    """QbD/FMEA-style risk register item."""

    risk: str
    cqa: str
    cpp: str
    severity: int = Field(ge=1, le=5)
    occurrence: int = Field(ge=1, le=5)
    detectability: int = Field(ge=1, le=5)
    rpn: int
    mitigation: str


class AuditEvent(BaseModel):
    """Execution provenance event."""

    timestamp: datetime
    step: str
    status: str
    summary: str
    input_digest: str | None = None
    output_digest: str | None = None


class AgentState(BaseModel):
    """Complete workflow state."""

    scenario: Scenario
    intent: Intent | None = None
    tool_plan: list[ToolSelection] = Field(default_factory=list)
    simulations: list[SimulationResult] = Field(default_factory=list)
    recommendations: list[ExperimentRecommendation] = Field(default_factory=list)
    rl_policy: RLPolicyResult | None = None
    risk_register: list[RiskItem] = Field(default_factory=list)
    audit_events: list[AuditEvent] = Field(default_factory=list)
    human_review_required: bool = False
    report: str | None = None

    def to_jsonable(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
