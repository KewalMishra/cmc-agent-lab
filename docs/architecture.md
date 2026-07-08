# Architecture

## Core Pattern

CMC Agent Lab uses a higher-purpose supervisor pattern. The supervisor does not always run the
entire workflow. It decides which path is warranted by the user's requested mode, risk level,
available tools, and development objective.

## Agent Nodes

1. **Objective Scoping Agent**
   - Extracts workflow mode, product target, unit operations, CQAs, CPPs, and constraints.

2. **Tool Planner**
   - Selects tools from a registry.
   - Supports built-in local simulators and optional external tools.
   - Marks optional simulators as unavailable without failing the workflow.

3. **Mechanistic Simulator Agent**
   - Runs selected built-in first-principles-inspired models.
   - Skips unavailable optional tools with provenance.

4. **Surrogate Readiness Agent**
   - Checks historical experiment data.
   - Enables GP-based acquisition when enough prior data exists.

5. **Experiment Designer**
   - Generates candidate experiments inside design-space bounds.
   - Scores candidates using surrogate predictions, uncertainty, and heuristic CQA alignment.
   - Produces a top-N batch for scientist review.

6. **RL Policy Agent**
   - Trains a sequential experiment-selection policy against the simulator environment.
   - Uses reward shaped around CQA score, constraint penalties, repeated-action penalties, and
     experiment budget.
   - Produces an RL-selected experiment batch and compares against a random policy baseline.

7. **QbD Risk Agent**
   - Links CQAs to likely CPPs.
   - Creates an FMEA-style risk register with severity, occurrence, detectability, RPN, and
     mitigation.

8. **Auditor**
   - Verifies that intent, tool plan, simulations, recommendations, and risk artifacts are
     present when required by mode.

9. **Reporter**
   - Renders a process-development memo.

## LangGraph Role

The deterministic runner in `workflow.py` exists for easy local review. The LangGraph assembly in
`graph.py` wraps the same nodes for production-style orchestration:

- stateful graph execution
- conditional routing by workflow mode
- future persistence/checkpointing
- future human-in-the-loop interrupts
- future LangSmith trace/evaluation integration

## State Contract

The state is typed in `schema.py`:

- `Scenario`
- `Intent`
- `ToolSelection`
- `SimulationResult`
- `ExperimentRecommendation`
- `RLPolicyResult`
- `RiskItem`
- `AuditEvent`
- `AgentState`

The explicit state contract is intentional. In regulated workflows, hidden state is a liability.
