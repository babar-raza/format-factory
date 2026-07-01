"""Tests for action queue — hash staleness, closed-gap exclusion, priority (TC-CAP-015)."""
import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
QUEUE_PATH = REPO_ROOT / "reports" / "capability-layer" / "action-queue.json"
ACTIVE_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-active.json"
ARCHIVE_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-archive.json"


@pytest.fixture(scope="module")
def queue_data():
    if not QUEUE_PATH.exists():
        pytest.skip("action-queue.json not found")
    return json.loads(QUEUE_PATH.read_bytes())


@pytest.fixture(scope="module")
def active_ids():
    if not ACTIVE_PATH.exists():
        return set()
    data = json.loads(ACTIVE_PATH.read_bytes())
    return {g["gap_id"] for g in data.get("gaps", [])}


@pytest.fixture(scope="module")
def archive_ids():
    if not ARCHIVE_PATH.exists():
        return set()
    data = json.loads(ARCHIVE_PATH.read_bytes())
    return {g["gap_id"] for g in data.get("gaps", [])}


def test_queue_schema_version(queue_data):
    assert queue_data.get("schema_version") == "2.0"


def test_stale_detection_enabled(queue_data):
    assert queue_data.get("stale_detection_enabled") is True


def test_source_ledger_hash_present(queue_data):
    assert queue_data.get("source_ledger_hash"), "source_ledger_hash must be non-empty"


def test_source_taskcard_hash_present(queue_data):
    assert queue_data.get("source_taskcard_hash"), "source_taskcard_hash must be non-empty"


def test_queue_hash_matches_active_ledger(queue_data):
    if not ACTIVE_PATH.exists():
        pytest.skip("gap-ledger-active.json not found")
    current = hashlib.sha256(ACTIVE_PATH.read_bytes()).hexdigest()
    stored = queue_data.get("source_ledger_hash")
    assert current == stored, (
        f"VAL-013 ACTION_QUEUE_STALE: stored={stored[:16]}... != current={current[:16]}..."
    )


def test_no_closed_gaps_in_queue(queue_data, archive_ids):
    actions = queue_data.get("actions", [])
    closed_in_queue = [a for a in actions if a.get("gap_id") in archive_ids]
    assert closed_in_queue == [], (
        f"CLOSED_GAPS_IN_ACTION_QUEUE={len(closed_in_queue)}: {[a['gap_id'] for a in closed_in_queue[:3]]}"
    )


def test_all_actions_have_taskcard_id(queue_data):
    actions = queue_data.get("actions", [])
    missing = [a.get("action_id") for a in actions if not a.get("taskcard_id")]
    assert missing == [], f"QUEUE_ITEMS_WITHOUT_TASKCARDS: {missing}"


def test_required_counters(queue_data):
    counters = queue_data.get("required_counters", {})
    assert counters.get("CLOSED_GAPS_IN_ACTION_QUEUE") == 0
    assert counters.get("QUEUE_ITEMS_WITHOUT_TASKCARDS") == 0
    assert counters.get("ACTION_QUEUE_STALE_RELATIVE_TO_LEDGER") is False


def test_root_advisory_only_is_false(queue_data):
    # Root-level advisory_only=False is required by check_system_healing_gate.py Lane 2
    assert queue_data.get("advisory_only") is False


def test_all_actions_have_required_skill(queue_data):
    actions = queue_data.get("actions", [])
    missing = [a.get("action_id") for a in actions if not a.get("required_skill")]
    assert missing == [], f"Actions without required_skill: {missing}"
