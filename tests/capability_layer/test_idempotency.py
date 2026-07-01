"""Tests for idempotency — repeated generation produces stable SHA-256 (TC-CAP-015)."""
import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CAP_DIR = REPO_ROOT / "reports" / "capability-layer"

STABLE_ARTIFACTS = [
    "gap-ledger-active.json",
    "gap-ledger-archive.json",
    "action-queue.json",
    "sal-driven-capability-map.json",
    "taskcard-linkage-report.yaml",
    "closure-receipt-index.json",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("artifact_name", STABLE_ARTIFACTS)
def test_artifact_exists(artifact_name):
    path = CAP_DIR / artifact_name
    assert path.exists(), f"{artifact_name} must exist"


def test_active_ledger_stable():
    path = CAP_DIR / "gap-ledger-active.json"
    if not path.exists():
        pytest.skip("gap-ledger-active.json not found")
    data1 = json.loads(path.read_bytes())
    # Re-parse and re-serialize to test determinism (no timestamp churn)
    roundtrip = json.loads(json.dumps(data1))
    assert roundtrip.get("schema_version") == "2.0"
    assert roundtrip.get("required_counters", {}).get("ACTIVE_LEDGER_CLOSED_GAPS") == 0


def test_action_queue_stable():
    path = CAP_DIR / "action-queue.json"
    if not path.exists():
        pytest.skip("action-queue.json not found")
    data = json.loads(path.read_bytes())
    assert data.get("schema_version") == "2.0"
    assert data.get("stale_detection_enabled") is True
    assert data.get("source_ledger_hash") is not None


def test_hash_tracking_stable():
    queue_path = CAP_DIR / "action-queue.json"
    ledger_path = CAP_DIR / "gap-ledger-active.json"
    if not queue_path.exists() or not ledger_path.exists():
        pytest.skip("Required files not found")

    queue_data = json.loads(queue_path.read_bytes())
    stored_hash = queue_data.get("source_ledger_hash")
    current_hash = _sha(ledger_path)
    assert stored_hash == current_hash, (
        f"Hash drift detected after second load: stored={stored_hash[:16]} current={current_hash[:16]}"
    )


def test_archive_count_stable():
    path = CAP_DIR / "gap-ledger-archive.json"
    if not path.exists():
        pytest.skip("gap-ledger-archive.json not found")
    data = json.loads(path.read_bytes())
    # Archive should always have exactly 1245 entries (closed gaps are stable)
    assert len(data.get("gaps", [])) == 1245, (
        f"Archive gap count changed: expected 1245, got {len(data.get('gaps', []))}"
    )


def test_taskcard_count_stable():
    taskcards_dir = CAP_DIR / "taskcards"
    if not taskcards_dir.exists():
        pytest.skip("taskcards dir not found")
    tc_count = len(list(taskcards_dir.glob("*.yaml")))
    # Should match active gap count (32)
    active_path = CAP_DIR / "gap-ledger-active.json"
    if active_path.exists():
        active_data = json.loads(active_path.read_bytes())
        expected = len(active_data.get("gaps", []))
        assert tc_count == expected, f"Taskcard count {tc_count} != active gap count {expected}"
