"""
Tests for tools/supervisor/evidence_continuation.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.evidence_continuation import (
    generate_post_closeout_next_action,
    write_post_closeout_next_action,
    write_post_closeout_active_continuation,
    repair_continuation_signal,
    apply_post_closeout_continuation,
    _is_advisory,
)


# ── Advisory detection ─────────────────────────────────────────────────────

@pytest.mark.parametrize("path, expected", [
    ("reports/supervisor/next-sprint.md", True),
    ("some/file.md", True),
    ("review/next-work-items.json", True),
    ("session-resume.md", True),
    (".local/supervisor/next-action.json", False),
    (".local/supervisor/active-continuation.json", False),
    ("reports/autonomous-system-acceptance/current-gap-analysis.json", False),
    ("", True),
])
def test_is_advisory(path, expected):
    assert _is_advisory(path) == expected, f"_is_advisory({path!r}) should be {expected}"


# ── Next action generation ─────────────────────────────────────────────────

def test_generate_post_closeout_action_has_schema():
    action = generate_post_closeout_next_action("TEST-SPRINT-001")
    assert action["schema_version"] == 1
    assert action["post_closeout"] is True
    assert action["external_gate"] is False
    assert action["preferred_backend"] == "LOCAL_DETERMINISTIC"


def test_generate_post_closeout_action_not_advisory():
    action = generate_post_closeout_next_action("TEST-SPRINT-001")
    assert not _is_advisory(action["target_path"])


def test_generate_post_closeout_action_preserves_sprint_id():
    action = generate_post_closeout_next_action("MY-SPRINT-XYZ")
    assert action["prior_sprint_id"] == "MY-SPRINT-XYZ"


def test_generate_post_closeout_action_preserves_run_id():
    action = generate_post_closeout_next_action("S-001", prior_run_id="run-abc")
    assert action["prior_run_id"] == "run-abc"


def test_generate_post_closeout_action_cycle_index():
    action = generate_post_closeout_next_action("S-001", cycle_index=5)
    assert action["cycle_index_after_closeout"] == 5


# ── Write next action ──────────────────────────────────────────────────────

def test_write_post_closeout_next_action(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    out = tmp_path / "next-action.json"
    monkeypatch.setattr(ec_mod, "NEXT_ACTION_PATH", out)
    result_path = write_post_closeout_next_action("TEST-SPRINT-001")
    assert result_path.exists()
    data = json.loads(result_path.read_text())
    assert data["post_closeout"] is True
    assert data["action_type"] is not None


def test_write_post_closeout_next_action_custom_path(tmp_path):
    out = tmp_path / "custom-next-action.json"
    write_post_closeout_next_action("S-001", output_path=out)
    assert out.exists()


# ── Write active continuation ──────────────────────────────────────────────

def test_write_post_closeout_active_continuation(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    ac_out = tmp_path / "active-continuation.json"
    monkeypatch.setattr(ec_mod, "ACTIVE_CONTINUATION_PATH", ac_out)
    na_path = tmp_path / "next-action.json"
    na_path.write_text("{}", encoding="utf-8")
    write_post_closeout_active_continuation("S-001", next_action_path=na_path)
    data = json.loads(ac_out.read_text())
    assert data["autonomous_continue"] is True
    assert data["advisory_prompt_executable"] is False
    assert data["post_closeout"] is True


def test_active_continuation_points_to_non_advisory(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    ac_out = tmp_path / "active-continuation.json"
    monkeypatch.setattr(ec_mod, "ACTIVE_CONTINUATION_PATH", ac_out)
    na_path = tmp_path / "next-action.json"
    na_path.write_text("{}", encoding="utf-8")
    write_post_closeout_active_continuation("S-001", next_action_path=na_path)
    data = json.loads(ac_out.read_text())
    assert not _is_advisory(data["next_action_path"])


# ── Repair continuation signal ─────────────────────────────────────────────

def test_repair_missing_signal(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    monkeypatch.setattr(ec_mod, "CONTINUATION_SIGNAL_PATH", tmp_path / "nonexistent.json")
    result = repair_continuation_signal("S-001")
    assert result["status"] == "NO_SIGNAL"
    assert result["repaired"] is False


def test_repair_advisory_signal(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    sig = tmp_path / "continuation-signal.json"
    sig.write_text(json.dumps({
        "autonomous_continue": True,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
    }), encoding="utf-8")
    monkeypatch.setattr(ec_mod, "CONTINUATION_SIGNAL_PATH", sig)
    monkeypatch.setattr(ec_mod, "NEXT_ACTION_PATH", tmp_path / "next-action.json")
    monkeypatch.setattr(ec_mod, "ACTIVE_CONTINUATION_PATH", tmp_path / "active-continuation.json")
    result = repair_continuation_signal("S-001")
    assert result["status"] == "REPAIRED"
    assert result["repaired"] is True
    assert (tmp_path / "next-action.json").exists()
    assert (tmp_path / "active-continuation.json").exists()


def test_repair_non_advisory_signal(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    sig = tmp_path / "continuation-signal.json"
    sig.write_text(json.dumps({
        "autonomous_continue": True,
        "next_sprint_path": ".local/supervisor/next-action.json",
    }), encoding="utf-8")
    monkeypatch.setattr(ec_mod, "CONTINUATION_SIGNAL_PATH", sig)
    result = repair_continuation_signal("S-001")
    assert result["status"] == "ALREADY_MACHINE_READABLE"
    assert result["repaired"] is False


def test_repair_continue_false_signal(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    sig = tmp_path / "continuation-signal.json"
    sig.write_text(json.dumps({
        "autonomous_continue": False,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
    }), encoding="utf-8")
    monkeypatch.setattr(ec_mod, "CONTINUATION_SIGNAL_PATH", sig)
    result = repair_continuation_signal("S-001")
    assert result["status"] == "CONTINUE_FALSE"
    assert result["repaired"] is False


# ── apply_post_closeout_continuation ──────────────────────────────────────

def test_apply_post_closeout_continuation(tmp_path, monkeypatch):
    import tools.supervisor.evidence_continuation as ec_mod
    monkeypatch.setattr(ec_mod, "NEXT_ACTION_PATH", tmp_path / "next-action.json")
    monkeypatch.setattr(ec_mod, "ACTIVE_CONTINUATION_PATH", tmp_path / "active-continuation.json")
    result = apply_post_closeout_continuation("S-001", run_id="run-xyz", cycle_index=3)
    assert result["status"] == "POST_CLOSEOUT_CONTINUATION_READY"
    assert Path(result["next_action_path"]).exists()
    assert Path(result["active_continuation_path"]).exists()
