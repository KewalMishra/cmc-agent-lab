from pathlib import Path

from cmc_agent_lab.workflow import run_workflow


ROOT = Path(__file__).resolve().parents[1]


def test_full_workflow_generates_auditable_recommendations():
    state = run_workflow(ROOT / "examples" / "small_molecule_process.yaml")

    assert state.intent is not None
    assert state.simulations
    assert len(state.recommendations) == 5
    assert state.risk_register
    assert state.audit_events
    assert state.human_review_required
    assert state.report is not None
    assert "Recommended Next Experiments" in state.report
    assert "QbD Risk Register" in state.report


def test_scope_mode_skips_simulation_and_experiment_generation():
    state = run_workflow(ROOT / "examples" / "small_molecule_process.yaml", mode_override="scope")

    assert state.scenario.mode == "scope"
    assert not state.simulations
    assert not state.recommendations
    assert state.risk_register
    assert "Skipped experiment generation" in " ".join(event.summary for event in state.audit_events)
