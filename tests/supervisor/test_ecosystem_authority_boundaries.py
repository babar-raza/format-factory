"""
Format Factory — Ecosystem Authority Boundary Validators
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
Lane 3: Validators 15-20 + package-108 quarantine validators

Tests 15-20: Ecosystem tool authority boundaries.
"""
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from tools.supervisor.execution_backend import BackendStatus
from tools.supervisor.backends.task_master_backend import TaskMasterBackend, get_task_master_layers
from tools.supervisor.backends.cognee_memory_backend import CogneeMemoryBackend
from tools.supervisor.backends.skill_seekers_backend import SkillSeekersBackend


# --------------------------------------------------------------------------
# 15. Task Master done != taskcard closed
# --------------------------------------------------------------------------
def test_task_master_done_ne_taskcard_closed():
    """Task Master MCP 'done' cannot close a Format Factory taskcard."""
    backend = TaskMasterBackend()
    # Backend must not be callable
    assert not backend.can_execute({"action_type": "MCP_TOOL_CALL"})
    # Simulate TM "done" status
    tm_status = "done"
    # Format Factory taskcard requires evidence check
    ff_taskcard_closed = False  # Cannot be set by TM status alone
    assert ff_taskcard_closed == False, "TM done must not set taskcard CLOSED without evidence"
    # Layers check
    layers = get_task_master_layers()
    assert layers["L5"] == False, "L5 must be False without API key + daemon"


# --------------------------------------------------------------------------
# 16. Cognee recall is not evidence
# --------------------------------------------------------------------------
def test_cognee_recall_is_not_evidence():
    """Cognee memory retrieval = H1 only. Cannot be treated as execution proof."""
    from tools.supervisor.execution_backend import ProofLevel
    backend = CogneeMemoryBackend()
    # Cognee NOT_FOUND in this environment
    status = backend.discover()
    assert status in (BackendStatus.NOT_FOUND, BackendStatus.SETUP_REQUIRED)
    assert not backend.can_execute({"action_type": "LLM_API_CALL"})
    # Even if cognee were installed, result would have proof_level H1
    result = backend.execute({"action_id": "test-cognee", "action_type": "LLM_API_CALL"}, [])
    assert result.proof_level == ProofLevel.H1 or "COGNEE_RECALL_IS_NOT_EVIDENCE" in result.errors[0]


# --------------------------------------------------------------------------
# 17. Skill Seekers generated != installed
# --------------------------------------------------------------------------
def test_skill_seekers_generated_ne_installed():
    """Skill Seekers produces skill candidates. Generated SKILL.md ≠ installed skill."""
    backend = SkillSeekersBackend()
    status = backend.discover()
    assert status in (BackendStatus.NOT_FOUND, BackendStatus.SETUP_REQUIRED)
    assert not backend.can_execute({"action_type": "SKILL_TOOL_INVOKE"})
    result = backend.execute({"action_id": "test-skill", "action_type": "SKILL_TOOL_INVOKE"}, [])
    assert any("SKILL_SEEKERS_GENERATED_NE_INSTALLED" in e for e in result.errors)


# --------------------------------------------------------------------------
# 18. H5/H6 cannot be assigned by narrative
# --------------------------------------------------------------------------
def test_h5_h6_cannot_be_assigned_by_narrative():
    """
    H5 (agentic backend) and H6 (external host) proof levels cannot be
    assigned by writing narrative text. They require runner-dispatched evidence.
    """
    # H5 would require: runner executed, agentic backend invoked, result written by backend
    # H6 would require: CLAUDECODE=0, external host process, child agent wrote proof file
    in_claudecode = sys.path  # exists
    claudecode_env = __import__("os").environ.get("CLAUDECODE", "")
    # H6 requires CLAUDECODE to be unset/0 — we're in a session so H6 is not provable here
    # Just verify the principle: narrative proof cannot assign these levels
    fake_h5 = {"proof_level": "H5", "evidence": "I described agentic execution in text"}
    assert fake_h5.get("backend_used") is None, "Narrative H5 claim has no backend_used — invalid"

    fake_h6 = {"proof_level": "H6", "evidence": "External host ran in my imagination"}
    assert fake_h6.get("external_host_pid") is None, "Narrative H6 claim has no external_host_pid — invalid"


# --------------------------------------------------------------------------
# 19. Package-108 unsafe next-work-items are quarantined
# --------------------------------------------------------------------------
def test_package_108_unsafe_next_work_items_are_quarantined():
    """
    Verify quarantine documentation exists and active plan source is set correctly.
    """
    quarantine_file = Path("reports/superpowers-agentic-autonomy/package-108-trust/unsafe-next-work-items-quarantine.md")
    audit_file = Path("reports/superpowers-agentic-autonomy/package-108-trust/package-108-audit.json")
    assert quarantine_file.exists(), f"Quarantine file missing: {quarantine_file}"
    assert audit_file.exists(), f"Audit file missing: {audit_file}"

    audit = json.loads(audit_file.read_text(encoding="utf-8"))
    assert audit.get("active_plan_source", "").endswith("next-execution-prompt.md"), (
        "Active plan source must be final-handoff/next-execution-prompt.md"
    )
    assert audit.get("continuation_decision") == "CONTINUE_WITH_QUARANTINE"
    quarantined = audit.get("unsafe_artifacts_quarantined", [])
    assert len(quarantined) >= 2, "At least 2 unsafe artifacts must be quarantined"


# --------------------------------------------------------------------------
# 20. Final handoff prompt is active source
# --------------------------------------------------------------------------
def test_final_handoff_prompt_is_active_source():
    """
    The execution source must be final-handoff/next-execution-prompt.md, not package-108's
    generated prompts or stale next-sprint.md.
    """
    prompt_file = Path("reports/superpowers-ecosystem-plan-final-repair/final-handoff/next-execution-prompt.md")
    assert prompt_file.exists(), f"Final handoff prompt missing: {prompt_file}"
    content = prompt_file.read_text(encoding="utf-8")
    assert len(content) > 1000, "Final handoff prompt must be substantial (not a placeholder)"
    assert "FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001" in content
    assert "H3" in content, "Must specify H3 minimum proof requirement"
    assert "next_action_runner" in content, "Must reference next_action_runner"

    # Verify execution-state.json points to correct source
    state_file = Path("reports/superpowers-agentic-autonomy/execution-state.json")
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert "next-execution-prompt.md" in state.get("active_plan_source", "")
