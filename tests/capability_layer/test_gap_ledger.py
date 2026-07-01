"""Tests for gap ledger reconciliation — active/archive split (TC-CAP-015)."""
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACTIVE_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-active.json"
ARCHIVE_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-archive.json"
FULL_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"


@pytest.fixture(scope="module")
def active_data():
    if not ACTIVE_PATH.exists():
        pytest.skip("gap-ledger-active.json not found")
    return json.loads(ACTIVE_PATH.read_bytes())


@pytest.fixture(scope="module")
def archive_data():
    if not ARCHIVE_PATH.exists():
        pytest.skip("gap-ledger-archive.json not found")
    return json.loads(ARCHIVE_PATH.read_bytes())


def test_active_ledger_exists():
    assert ACTIVE_PATH.exists()


def test_archive_ledger_exists():
    assert ARCHIVE_PATH.exists()


def test_active_has_no_closed_gaps(active_data):
    closed_statuses = {"closed", "CLOSED", "CLOSED_VERIFIED", "CLOSED_SUPERSEDED"}
    closed_in_active = [
        g["gap_id"] for g in active_data.get("gaps", [])
        if g.get("status") in closed_statuses
    ]
    assert closed_in_active == [], f"ACTIVE_LEDGER_CLOSED_GAPS={len(closed_in_active)}: {closed_in_active[:5]}"


def test_active_required_counters(active_data):
    counters = active_data.get("required_counters", {})
    assert counters.get("ACTIVE_LEDGER_CLOSED_GAPS") == 0
    assert counters.get("OPEN_GAPS_WITHOUT_EXACT_NEXT_ACTION") == 0


def test_all_active_gaps_have_exact_next_action(active_data):
    no_action = [g["gap_id"] for g in active_data.get("gaps", []) if not g.get("exact_next_action")]
    assert no_action == [], f"Gaps without exact_next_action: {no_action}"


def test_all_active_gaps_have_taskcard_ids(active_data):
    no_tc = [g["gap_id"] for g in active_data.get("gaps", []) if not g.get("taskcard_ids")]
    assert no_tc == [], f"Gaps without taskcard_ids: {no_tc}"


def test_no_cross_contamination(active_data, archive_data):
    active_ids = {g["gap_id"] for g in active_data.get("gaps", [])}
    archive_ids = {g["gap_id"] for g in archive_data.get("gaps", [])}
    overlap = active_ids & archive_ids
    assert overlap == set(), f"CROSS_CONTAMINATION: {overlap}"


def test_total_gaps_preserved(active_data, archive_data):
    total_active = len(active_data.get("gaps", []))
    total_archive = len(archive_data.get("gaps", []))
    # Should add up to the original 1277 gaps
    assert total_active + total_archive == 1277, (
        f"Total gap count mismatch: {total_active} active + {total_archive} archive = {total_active + total_archive} (expected 1277)"
    )


def test_archive_all_closed(archive_data):
    non_closed = [
        g["gap_id"] for g in archive_data.get("gaps", [])
        if g.get("status") not in {"closed", "CLOSED"}
    ]
    assert non_closed == [], f"Archive contains non-closed gaps: {non_closed[:5]}"


def test_active_schema_version(active_data):
    assert active_data.get("schema_version") == "2.0"
