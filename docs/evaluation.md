# Evaluation Strategy

## Why Evaluation Matters

For this project, evaluation should not be limited to "the answer sounds good." The system makes
scientific process-development recommendations, so evaluation must cover routing, simulator
execution, recommendation quality, and audit completeness.

## Evaluation Dimensions

1. **Intent extraction**
   - Did the agent identify the right workflow mode, unit operations, CQAs, CPPs, and constraints?

2. **Tool-routing correctness**
   - Did the agent select relevant tools?
   - Did it avoid expensive or irrelevant tools when the user asked for a subset?
   - Did it record unavailable optional tools without failing?

3. **Simulator execution**
   - Are required inputs present?
   - Are outputs in the expected schema?
   - Are assumptions and warnings attached?

4. **Experiment recommendation quality**
   - Are recommended experiments inside the design space?
   - Do they balance expected performance with information gain?
   - Are they sufficiently diverse?
   - Do they respect the experiment budget?

5. **RL policy quality**
   - Does the policy beat a random experiment-selection baseline?
   - Are selected actions inside the declared design space?
   - Does the reward penalize CQA and constraint failures?
   - Is the learned policy reported separately from wet-lab-ready recommendations?

6. **Risk and control strategy**
   - Are high-severity CQAs linked to plausible CPPs?
   - Are mitigations actionable?
   - Is human review required for wet-lab recommendations?

7. **Audit completeness**
   - Does every major step record inputs, outputs, status, and digest?
   - Can the final memo be traced back to selected tools and model outputs?

## Initial Automated Tests

The current tests check:

- workflow execution
- planner flexibility by mode
- simulator behavior
- top-N experiment recommendation bounds
- RL environment and policy output
- audit and report generation

## Future Benchmark

Add YAML scenarios with expected properties:

- "scope-only" should select no simulator tools.
- "stability-only" should select stability and risk tools.
- "full CMC optimization" should produce five experiments and at least one simulation warning.
- "learn" should produce an RL policy result, random baseline comparison, and RL-selected
  experiment batch.
- "optional external simulator unavailable" should be skipped with provenance, not crash.
