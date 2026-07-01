"""Tests for taskcard linkage — ready gaps get taskcards, closed gaps don't (TC-CAP-015)."""
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACTIVE_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-active.json"
ARCHIVE_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger-archive.json"
TASKCARDS_DIR = REPO_ROOT / "reports" / "capability-layer" / "taskcards"
LINKAGE_REPORT = REPO_ROOT / "reports" / "capability-layer" / "taskcard-linkage-report.yaml"


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


def test_taskcards_dir_exists():
    assert TASKCARDS_DIR.exists() and TASKCARDS_DIR.is_dir()


def test_linkage_report_exists():
    assert LINKAGE_REPORT.exists()


def test_required_counters_in_linkage_report():
    import yaml
    data = yaml.safe_load(LINKAGE_REPORT.read_text(encoding="utf-8"))
    counters = data.get("required_counters", {})
    assert counters.get("READY_OPEN_GAPS_WITHOUT_TASKCARDS") == 0
    assert counters.get("CLOSED_GAPS_WITH_ACTIVE_TASKCARDS") == 0


def test_all_active_gaps_have_taskcard_file(active_data):
    missing = []
    for g in active_data.get("gaps", []):
        tc_ids = g.get("taskcard_ids", [])
        if tc_ids:
            tc_file = TASKCARDS_DIR / f"{g['gap_id']}.yaml"
            if not tc_file.exists():
                missing.append(g["gap_id"])
    assert missing == [], f"Gaps with taskcard_ids but no file: {missing[:5]}"


def test_no_active_taskcard_for_closed_gaps(archive_data):
    archive_ids = {g["gap_id"] for g in archive_data.get("gaps", [])}
    active_tc_files = {f.stem for f in TASKCARDS_DIR.glob("*.yaml")}
    # Taskcard file names match gap_ids; no closed gap should have a taskcard file
    closed_with_tc = archive_ids & active_tc_files
    assert closed_with_tc == set(), f"CLOSED_GAPS_WITH_ACTIVE_TASKCARDS: {list(closed_with_tc)[:5]}"


def test_taskcard_files_have_gap_id(active_data):
    active_gap_ids = {g["gap_id"] for g in active_data.get("gaps", [])}
    for tc_file in TASKCARDS_DIR.glob("*.yaml"):
        content = tc_file.read_text(encoding="utf-8")
        assert "gap_id:" in content, f"{tc_file.name} missing gap_id field"
        assert "taskcard_status:" in content, f"{tc_file.name} missing taskcard_status field"


def test_taskcard_count_matches_active_gaps(active_data):
    tc_count = len(list(TASKCARDS_DIR.glob("*.yaml")))
    gap_count = len(active_data.get("gaps", []))
    assert tc_count == gap_count, f"Taskcard count ({tc_count}) != active gap count ({gap_count})"
