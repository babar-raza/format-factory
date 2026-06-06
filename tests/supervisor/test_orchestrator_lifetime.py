"""
Tests for tools/supervisor/orchestrator_lifetime.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.orchestrator_lifetime import (
    is_resumable,
    get_resume_command,
    write_lifetime_stop,
    write_post_closeout_state,
    RESUMABLE_STOPS,
    EXTERNAL_AUTHORITY_STOPS,
    DIAGNOSIS_STOPS,
    STOP_TAXONOMY,
    STOP_TRUE_EXTERNAL_GATE,
    STOP_CREDENTIAL_REQUIRED,
    STOP_UNSAFE_WORKSPACE,
    STOP_REPEATED_FAILURE,
    STOP_NO_SAFE_ACTION,
    STOP_MAX_CYCLES_RESUMABLE,
    STOP_QUEUE_EMPTY,
    STOP_USER_STOPPED,
    STOP_EVIDENCE_PACKAGE_FAILED,
    STOP_ORCHESTRATOR_ERROR,
    STOP_LOCK_HELD,
    STOP_DRY_RUN,
    STOP_ADVISORY_PROMPT,
)


# ── Taxonomy completeness ──────────────────────────────────────────────────

def test_all_stop_codes_in_taxonomy():
    all_codes = [
        STOP_TRUE_EXTERNAL_GATE, STOP_CREDENTIAL_REQUIRED, STOP_UNSAFE_WORKSPACE,
        STOP_REPEATED_FAILURE, STOP_NO_SAFE_ACTION, STOP_MAX_CYCLES_RESUMABLE,
        STOP_QUEUE_EMPTY, STOP_USER_STOPPED, STOP_EVIDENCE_PACKAGE_FAILED,
        STOP_ORCHESTRATOR_ERROR, STOP_LOCK_HELD, STOP_DRY_RUN, STOP_ADVISORY_PROMPT,
    ]
    for code in all_codes:
        assert code in STOP_TAXONOMY, f"{code} missing from STOP_TAXONOMY"


def test_taxonomy_entries_have_required_fields():
    required_fields = {"description", "resumable", "requires", "resume_after"}
    for code, entry in STOP_TAXONOMY.items():
        for field in required_fields:
            assert field in entry, f"{code} missing field '{field}'"


# ── Resumability ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("stop_code", [
    STOP_MAX_CYCLES_RESUMABLE,
    STOP_QUEUE_EMPTY,
    STOP_LOCK_HELD,
    STOP_DRY_RUN,
    STOP_USER_STOPPED,
    STOP_REPEATED_FAILURE,
    STOP_ORCHESTRATOR_ERROR,
])
def test_resumable_stops_are_resumable(stop_code):
    assert is_resumable(stop_code), f"{stop_code} should be resumable"


@pytest.mark.parametrize("stop_code", [
    STOP_TRUE_EXTERNAL_GATE,
    STOP_CREDENTIAL_REQUIRED,
    STOP_UNSAFE_WORKSPACE,
])
def test_external_authority_stops_are_not_resumable(stop_code):
    assert not is_resumable(stop_code), f"{stop_code} should require external authority"


def test_external_authority_stops_set():
    for code in EXTERNAL_AUTHORITY_STOPS:
        assert not is_resumable(code)


# ── Resume command generation ──────────────────────────────────────────────

def test_resume_command_contains_python():
    cmd = get_resume_command(STOP_MAX_CYCLES_RESUMABLE)
    assert "python" in cmd.lower()


def test_resume_command_contains_resume_flag():
    cmd = get_resume_command(STOP_MAX_CYCLES_RESUMABLE)
    assert "--resume" in cmd


def test_resume_command_max_cycles():
    cmd = get_resume_command(STOP_MAX_CYCLES_RESUMABLE, max_cycles=5)
    assert "--max-cycles 5" in cmd


def test_resume_command_with_seed_action():
    cmd = get_resume_command(STOP_QUEUE_EMPTY, seed_action=".local/supervisor/next-action.json")
    assert "--seed-action" in cmd


# ── write_lifetime_stop ────────────────────────────────────────────────────

def test_write_lifetime_stop_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.supervisor.orchestrator_lifetime.STATE_DIR", tmp_path)
    write_lifetime_stop(
        run_id="test-run-001",
        stop_code=STOP_MAX_CYCLES_RESUMABLE,
        detail="Test stop",
        cycle_index=3,
    )
    p = tmp_path / "stop-reason.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["stop_code"] == STOP_MAX_CYCLES_RESUMABLE
    assert data["resumable"] is True
    assert data["cycle_index"] == 3


def test_write_lifetime_stop_external_gate(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.supervisor.orchestrator_lifetime.STATE_DIR", tmp_path)
    write_lifetime_stop(
        run_id="test-run-002",
        stop_code=STOP_TRUE_EXTERNAL_GATE,
        detail="Gate reached",
        cycle_index=1,
    )
    p = tmp_path / "stop-reason.json"
    data = json.loads(p.read_text())
    assert data["requires_external_authority"] is True
    assert data["resume_command"] == ""


def test_write_lifetime_stop_has_resume_command_for_resumable(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.supervisor.orchestrator_lifetime.STATE_DIR", tmp_path)
    write_lifetime_stop(
        run_id="test-run-003",
        stop_code=STOP_QUEUE_EMPTY,
        detail="Queue drained",
        cycle_index=2,
    )
    p = tmp_path / "stop-reason.json"
    data = json.loads(p.read_text())
    assert len(data["resume_command"]) > 0


# ── write_post_closeout_state ──────────────────────────────────────────────

def test_write_post_closeout_state_resumable(tmp_path, monkeypatch):
    out_path = tmp_path / "evidence-continuation" / "post-closeout-state.json"

    def fake_write(data, p):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Patch the output path
    import tools.supervisor.orchestrator_lifetime as lt_mod
    orig = lt_mod._repo_root
    monkeypatch.setattr(lt_mod, "_repo_root", tmp_path)
    # Create expected subdir
    (tmp_path / "reports" / "autonomous-system-acceptance" / "evidence-continuation").mkdir(parents=True, exist_ok=True)

    write_post_closeout_state(
        sprint_id="TEST-SPRINT-001",
        next_action_path=".local/supervisor/next-action.json",
        stop_code=STOP_MAX_CYCLES_RESUMABLE,
    )

    out = tmp_path / "reports" / "autonomous-system-acceptance" / "evidence-continuation" / "post-closeout-state.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["autonomous_continue"] is True
    assert data["post_closeout"] is True


def test_write_post_closeout_state_external_gate(tmp_path, monkeypatch):
    import tools.supervisor.orchestrator_lifetime as lt_mod
    monkeypatch.setattr(lt_mod, "_repo_root", tmp_path)
    (tmp_path / "reports" / "autonomous-system-acceptance" / "evidence-continuation").mkdir(parents=True, exist_ok=True)

    write_post_closeout_state(
        sprint_id="TEST-SPRINT-001",
        next_action_path=None,
        stop_code=STOP_TRUE_EXTERNAL_GATE,
    )

    out = tmp_path / "reports" / "autonomous-system-acceptance" / "evidence-continuation" / "post-closeout-state.json"
    data = json.loads(out.read_text())
    assert data["autonomous_continue"] is False
    assert data["next_action"] is None
