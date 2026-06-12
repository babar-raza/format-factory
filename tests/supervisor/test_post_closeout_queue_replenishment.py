"""
tests/supervisor/test_post_closeout_queue_replenishment.py

Lane 3 — Sprint FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

Tests that after a sprint closes out with an exhausted queue, the system
correctly seeds a QUEUE_HEALTH_CHECK item and writes fresh continuation files.

Addresses AF-002 (stale active-continuation.json) and AF-003 (empty post-closeout queue).
"""

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from evidence_continuation import (
    seed_post_closeout_queue_item,
    apply_post_closeout_continuation,
    generate_post_closeout_next_action,
)


# ---------------------------------------------------------------------------
# seed_post_closeout_queue_item — unit tests
# ---------------------------------------------------------------------------

class TestSeedPostCloseoutQueueItem:
    """seed_post_closeout_queue_item seeds a QUEUE_HEALTH_CHECK when queue exhausted."""

    def _write_queue(self, tmp_path: Path, items: list) -> Path:
        q = tmp_path / "action-queue.jsonl"
        with q.open("w") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")
        return q

    def test_seeds_when_all_done(self, monkeypatch, tmp_path):
        """When all items are done, seed returns SEEDED."""
        q = self._write_queue(tmp_path, [
            {"action_id": "a1", "action_type": "X", "status": "done"},
            {"action_id": "a2", "action_type": "Y", "status": "done"},
        ])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="TEST-SPRINT-001")
        assert result["status"] == "SEEDED"
        assert result["seeded"] is True

    def test_seeded_item_is_queue_health_check(self, monkeypatch, tmp_path):
        """Seeded item must have action_type=QUEUE_HEALTH_CHECK."""
        q = self._write_queue(tmp_path, [
            {"action_id": "a1", "status": "done"},
        ])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        seed_post_closeout_queue_item(sprint_id="TEST-SPRINT-001")
        items = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        pending = [i for i in items if i.get("status", "pending") != "done"]
        assert len(pending) == 1
        assert pending[0]["action_type"] == "QUEUE_HEALTH_CHECK"

    def test_seeded_item_is_not_external_gate(self, monkeypatch, tmp_path):
        """QUEUE_HEALTH_CHECK must not be an external gate."""
        q = self._write_queue(tmp_path, [
            {"action_id": "a1", "status": "done"},
        ])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        seed_post_closeout_queue_item(sprint_id="TEST-SPRINT-001")
        items = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        seeded = next(i for i in items if i.get("status", "pending") != "done")
        assert seeded.get("external_gate") is False

    def test_seeded_item_has_post_closeout_flag(self, monkeypatch, tmp_path):
        """Seeded item must carry post_closeout=True."""
        q = self._write_queue(tmp_path, [
            {"action_id": "a1", "status": "done"},
        ])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        seed_post_closeout_queue_item(sprint_id="MY-SPRINT")
        items = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        seeded = next(i for i in items if i.get("status", "pending") != "done")
        assert seeded.get("post_closeout") is True

    def test_seeded_item_carries_sprint_id(self, monkeypatch, tmp_path):
        """Seeded item must carry the sprint_id for traceability."""
        q = self._write_queue(tmp_path, [{"action_id": "a1", "status": "done"}])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        seed_post_closeout_queue_item(sprint_id="MY-SPRINT-XYZ")
        items = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        seeded = next(i for i in items if i.get("status", "pending") != "done")
        assert seeded.get("prior_sprint_id") == "MY-SPRINT-XYZ"

    def test_no_seed_when_pending_exists(self, monkeypatch, tmp_path):
        """If there is already a pending item, do NOT seed."""
        q = self._write_queue(tmp_path, [
            {"action_id": "a1", "status": "done"},
            {"action_id": "a2", "status": "pending"},
        ])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="TEST-SPRINT-001")
        assert result["status"] == "ALREADY_HAS_PENDING"
        assert result["seeded"] is False
        # Queue should be unchanged
        items = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        assert len(items) == 2

    def test_no_seed_when_no_status_field_is_pending(self, monkeypatch, tmp_path):
        """Items without status field default to pending — don't seed."""
        q = self._write_queue(tmp_path, [
            {"action_id": "a1"},  # no status = pending
        ])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="TEST-SPRINT-001")
        assert result["status"] == "ALREADY_HAS_PENDING"
        assert result["seeded"] is False

    def test_seed_on_empty_queue(self, monkeypatch, tmp_path):
        """If the queue is empty, seed a QUEUE_HEALTH_CHECK."""
        q = tmp_path / "action-queue.jsonl"
        q.write_text("")  # empty file
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="TEST-SPRINT-001")
        assert result["status"] == "SEEDED"
        assert result["seeded"] is True

    def test_seed_creates_queue_file_if_missing(self, monkeypatch, tmp_path):
        """If queue file doesn't exist, create it and seed."""
        q = tmp_path / "missing-queue.jsonl"
        assert not q.exists()
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="NEW-SPRINT")
        assert result["status"] == "SEEDED"
        assert q.exists()

    def test_seed_result_has_queue_path(self, monkeypatch, tmp_path):
        """Result dict must include queue_path."""
        q = self._write_queue(tmp_path, [{"action_id": "a1", "status": "done"}])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="TEST-SPRINT")
        assert "queue_path" in result

    def test_seed_result_has_queue_pending_count(self, monkeypatch, tmp_path):
        """Result dict must report queue_pending=1 after seeding."""
        q = self._write_queue(tmp_path, [{"action_id": "a1", "status": "done"}])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        result = seed_post_closeout_queue_item(sprint_id="TEST-SPRINT")
        assert result.get("queue_pending") == 1

    def test_seed_preferred_backend_is_local_deterministic(self, monkeypatch, tmp_path):
        """Seeded item must use LOCAL_DETERMINISTIC backend (no external deps)."""
        q = self._write_queue(tmp_path, [{"action_id": "a1", "status": "done"}])
        monkeypatch.setattr("evidence_continuation.ACTION_QUEUE_PATH", q)
        seed_post_closeout_queue_item(sprint_id="TEST-SPRINT")
        items = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        seeded = next(i for i in items if i.get("status", "pending") != "done")
        assert seeded.get("preferred_backend") == "LOCAL_DETERMINISTIC"


# ---------------------------------------------------------------------------
# apply_post_closeout_continuation — integration tests
# ---------------------------------------------------------------------------

class TestApplyPostCloseoutContinuation:
    """apply_post_closeout_continuation writes fresh next-action.json and active-continuation.json."""

    def test_returns_dict_with_expected_keys(self, tmp_path):
        """Result dict must include status, next_action_path, active_continuation_path."""
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-001",
            run_id="abc12345",
            cycle_index=1,
        )
        assert "status" in result
        assert "next_action_path" in result
        assert "active_continuation_path" in result

    def test_status_is_post_closeout_continuation_ready(self, tmp_path):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-001",
            run_id="abc12345",
        )
        assert result["status"] == "POST_CLOSEOUT_CONTINUATION_READY"

    def test_next_action_path_is_string(self, tmp_path):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-001",
            run_id="def67890",
        )
        assert isinstance(result["next_action_path"], str)
        assert len(result["next_action_path"]) > 0

    def test_next_action_path_file_exists(self, tmp_path):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-002",
            run_id="abc12345",
        )
        path = Path(result["next_action_path"])
        assert path.exists(), f"next_action.json not written to {path}"

    def test_active_continuation_path_file_exists(self, tmp_path):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-002",
            run_id="abc12345",
        )
        path = Path(result["active_continuation_path"])
        assert path.exists(), f"active-continuation.json not written to {path}"

    def test_active_continuation_contains_sprint_id(self):
        sprint = "FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001"
        result = apply_post_closeout_continuation(sprint_id=sprint, run_id="test99")
        cont_path = Path(result["active_continuation_path"])
        cont = json.loads(cont_path.read_text(encoding="utf-8"))
        assert cont.get("sprint_id") == sprint

    def test_active_continuation_advisory_prompt_not_executable(self):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-003",
            run_id="xyz",
        )
        cont_path = Path(result["active_continuation_path"])
        cont = json.loads(cont_path.read_text(encoding="utf-8"))
        # advisory_prompt_executable must NOT be True (that's the whole point of this fix)
        assert cont.get("advisory_prompt_executable") is False

    def test_active_continuation_autonomous_continue_true(self):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-003",
            run_id="xyz",
        )
        cont_path = Path(result["active_continuation_path"])
        cont = json.loads(cont_path.read_text(encoding="utf-8"))
        assert cont.get("autonomous_continue") is True

    def test_next_action_json_has_action_type(self):
        result = apply_post_closeout_continuation(
            sprint_id="TEST-SPRINT-004",
            run_id="zzz",
        )
        action_path = Path(result["next_action_path"])
        action = json.loads(action_path.read_text(encoding="utf-8"))
        assert "action_type" in action
        assert action["action_type"]  # non-empty


# ---------------------------------------------------------------------------
# generate_post_closeout_next_action — unit tests
# ---------------------------------------------------------------------------

class TestGeneratePostCloseoutNextAction:
    """generate_post_closeout_next_action returns a well-formed next-action dict."""

    def test_returns_dict(self):
        result = generate_post_closeout_next_action(
            sprint_id="TEST-SPRINT",
            prior_run_id="abc",
        )
        assert isinstance(result, dict)

    def test_has_action_type(self):
        result = generate_post_closeout_next_action(sprint_id="TEST-SPRINT")
        assert "action_type" in result
        assert result["action_type"]

    def test_has_action_id(self):
        result = generate_post_closeout_next_action(sprint_id="FORMAT-FACTORY-TEST-SPRINT-001")
        assert "action_id" in result
        assert result["action_id"]  # non-empty

    def test_not_external_gate(self):
        """Post-closeout action must not require human authorization."""
        result = generate_post_closeout_next_action(sprint_id="TEST-SPRINT")
        assert result.get("external_gate") is False

    def test_has_target_or_objective(self):
        """Must have either a target or objective field."""
        result = generate_post_closeout_next_action(sprint_id="TEST-SPRINT")
        has_target = "target" in result or "objective" in result
        assert has_target, f"Missing target/objective in {list(result.keys())}"
