"""Tests for dynamic target writer unblocking in select_poc_gaps.py.

Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001
Updated: FORMAT-FACTORY-DOTNET-TARGET-WRITER-READINESS-HARDENING-AND-POC-RECONCILIATION-001

Validates (v4 — original):
  - detect_target_writer_status() returns empty when all writers exist on disk
  - detect_target_writer_status() correctly re-blocks a gap when writer is absent
  - BLOCKED_GAP_IDS at import is empty (writers are now present)
  - _ARCHITECTURE_BLOCKED_SEED still contains all 4 canonical gap IDs
  - _GAP_WRITER_SOURCE maps all 4 gaps to actual source files
  - The four writer source files exist on disk

Validates (v5 — hardening, proof-backed):
  - all_four_writers_ready_when_source_project_tests_logs_outputs_exist
  - source_only_does_not_create_full_ready_status
  - missing_raw_log_downgrades_readiness
  - missing_sample_output_downgrades_readiness
  - missing_project_downgrades_readiness
  - missing_tests_downgrades_readiness
  - ready_writer_unblocks_gap_for_routing
  - not_ready_writer_remains_blocked
  - gap_selector_never_marks_accepted_for_poc_from_source_only
  - generated_registry_contains_all_four_writer_gaps
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure tools/supervisor is importable
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from select_poc_gaps import (  # noqa: E402
    BLOCKED_GAP_IDS,
    _ARCHITECTURE_BLOCKED_SEED,
    _GAP_WRITER_SOURCE,
    _GAP_WRITER_PROOF,
    detect_target_writer_status,
    detect_target_writer_readiness,
    READINESS_READY,
    READINESS_MISSING_PROJECT,
    READINESS_MISSING_TESTS,
    READINESS_MISSING_SAMPLE_OUTPUT,
    READINESS_SOURCE_PRESENT_TESTS_REQUIRED,
)

EXPECTED_GAP_IDS = frozenset({
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet",
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet",
})

EXPECTED_WRITERS = {
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet": "src/net/csv/CsvWriter.cs",
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet": "src/net/html/HtmlWriter.cs",
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet": "src/net/markdown/MarkdownWriter.cs",
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet": "src/net/txt/TxtWriter.cs",
}


# ---------------------------------------------------------------------------
# T1: Seed contains all 4 canonical gap IDs
# ---------------------------------------------------------------------------
def test_architecture_blocked_seed_has_all_four_gaps():
    assert _ARCHITECTURE_BLOCKED_SEED == EXPECTED_GAP_IDS, (
        f"Seed mismatch: {_ARCHITECTURE_BLOCKED_SEED} != {EXPECTED_GAP_IDS}"
    )


# ---------------------------------------------------------------------------
# T2: Writer source map contains all 4 entries
# ---------------------------------------------------------------------------
def test_gap_writer_source_has_all_four_mappings():
    for gap_id, expected_path in EXPECTED_WRITERS.items():
        assert gap_id in _GAP_WRITER_SOURCE, f"{gap_id} missing from _GAP_WRITER_SOURCE"
        assert _GAP_WRITER_SOURCE[gap_id] == expected_path, (
            f"{gap_id}: expected path {expected_path!r}, got {_GAP_WRITER_SOURCE[gap_id]!r}"
        )


# ---------------------------------------------------------------------------
# T3: All four writer source files exist on disk
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("gap_id,rel_path", list(EXPECTED_WRITERS.items()))
def test_writer_source_file_exists(gap_id, rel_path):
    abs_path = REPO_ROOT / rel_path
    assert abs_path.exists(), (
        f"Writer source file missing for {gap_id}: {abs_path}"
    )


# ---------------------------------------------------------------------------
# T4: detect_target_writer_status returns empty set (all writers present)
# ---------------------------------------------------------------------------
def test_detect_target_writer_status_returns_empty_when_all_present():
    result = detect_target_writer_status(REPO_ROOT)
    assert result == frozenset(), (
        f"Expected no blocked gaps after writers built, got: {sorted(result)}"
    )


# ---------------------------------------------------------------------------
# T5: BLOCKED_GAP_IDS at import time is empty (dynamic probe)
# ---------------------------------------------------------------------------
def test_blocked_gap_ids_at_import_is_empty():
    assert BLOCKED_GAP_IDS == frozenset(), (
        f"BLOCKED_GAP_IDS should be empty after writers built, got: {sorted(BLOCKED_GAP_IDS)}"
    )


# ---------------------------------------------------------------------------
# T6: detect_target_writer_status re-blocks if a writer source is absent (simulate)
# ---------------------------------------------------------------------------
def test_detect_target_writer_status_reblocks_when_writer_source_absent(tmp_path):
    """Simulate a repo root where one writer source is missing; that gap should be re-blocked."""
    # Build full proof tree for 3 gaps; leave txt absent entirely
    for gap_id in _ARCHITECTURE_BLOCKED_SEED:
        if "txt" not in gap_id:
            proof = _GAP_WRITER_PROOF[gap_id]
            for key in ("source_path", "project_path", "test_project_path"):
                f = tmp_path / proof[key]
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("// stub", encoding="utf-8")
            log = tmp_path / proof["raw_log_path"]
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text("Passed!  - Failed:     0", encoding="utf-8")
            sample = tmp_path / proof["sample_output_path"]
            sample.parent.mkdir(parents=True, exist_ok=True)
            sample.write_text("sample", encoding="utf-8")
    # txt gap: source absent → must stay blocked
    result = detect_target_writer_status(tmp_path)
    assert "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet" in result, (
        f"Expected txt gap to remain blocked, got: {sorted(result)}"
    )


# ---------------------------------------------------------------------------
# T7: detect_target_writer_status re-blocks ALL when no writers present
# ---------------------------------------------------------------------------
def test_detect_target_writer_status_all_blocked_when_no_writers(tmp_path):
    """Empty repo root → all 4 gaps remain blocked."""
    result = detect_target_writer_status(tmp_path)
    assert result == EXPECTED_GAP_IDS, (
        f"Expected all 4 gaps blocked in empty repo, got: {sorted(result)}"
    )


# ---------------------------------------------------------------------------
# T8: detect_target_writer_status returns empty when full proof tree exists
# ---------------------------------------------------------------------------
def test_detect_target_writer_status_empty_when_full_proof_tree_present(tmp_path):
    """v5: all 5 conditions must be met for status=READY → BLOCKED_GAP_IDS empty."""
    for gap_id in _ARCHITECTURE_BLOCKED_SEED:
        proof = _GAP_WRITER_PROOF[gap_id]
        for key in ("source_path", "project_path", "test_project_path"):
            f = tmp_path / proof[key]
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("// stub", encoding="utf-8")
        log = tmp_path / proof["raw_log_path"]
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("Passed!  - Failed:     0, Passed:    15", encoding="utf-8")
        sample = tmp_path / proof["sample_output_path"]
        sample.parent.mkdir(parents=True, exist_ok=True)
        sample.write_text("sample output", encoding="utf-8")

    result = detect_target_writer_status(tmp_path)
    assert result == frozenset(), (
        f"Expected empty set when full proof tree present, got: {sorted(result)}"
    )


# ===========================================================================
# v5 HARDENING TESTS (proof-backed readiness — Phase B)
# ===========================================================================

SAMPLE_GAP = "commercial-net-fods-dogfood-status-fods-to-csv-dotnet"


def _make_full_proof_tree(tmp_path: Path, gap_id: str = SAMPLE_GAP) -> None:
    """Create all five proof artifacts for a gap in tmp_path."""
    proof = _GAP_WRITER_PROOF[gap_id]
    for key in ("source_path", "project_path", "test_project_path"):
        f = tmp_path / proof[key]
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("// stub", encoding="utf-8")
    log = tmp_path / proof["raw_log_path"]
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("Passed!  - Failed:     0, Passed:    15", encoding="utf-8")
    sample = tmp_path / proof["sample_output_path"]
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text("a,b,c\n1,2,3\n", encoding="utf-8")


# T9: All four writers READY when full proof tree exists
def test_all_four_writers_ready_when_full_proof_tree(tmp_path):
    for gap_id in _ARCHITECTURE_BLOCKED_SEED:
        _make_full_proof_tree(tmp_path, gap_id)
    for gap_id in _ARCHITECTURE_BLOCKED_SEED:
        r = detect_target_writer_readiness(tmp_path, gap_id)
        assert r["status"] == READINESS_READY, f"{gap_id}: expected READY, got {r['status']}"
        assert r["accepted_for_poc"] is True


# T10: Source only does not create full READY status
def test_source_only_does_not_produce_ready_status(tmp_path):
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    src = tmp_path / proof["source_path"]
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("// stub", encoding="utf-8")
    r = detect_target_writer_readiness(tmp_path, SAMPLE_GAP)
    assert r["status"] != READINESS_READY, f"Source-only should not be READY, got {r['status']}"
    assert r["accepted_for_poc"] is False


# T11: Missing raw log downgrades readiness to SOURCE_PRESENT_TESTS_REQUIRED
def test_missing_raw_log_downgrades_readiness(tmp_path):
    _make_full_proof_tree(tmp_path)
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    log = tmp_path / proof["raw_log_path"]
    log.unlink()
    r = detect_target_writer_readiness(tmp_path, SAMPLE_GAP)
    assert r["status"] == READINESS_SOURCE_PRESENT_TESTS_REQUIRED, (
        f"Missing log should give SOURCE_PRESENT_TESTS_REQUIRED, got {r['status']}"
    )
    assert r["accepted_for_poc"] is False


# T12: Missing sample output downgrades readiness
def test_missing_sample_output_downgrades_readiness(tmp_path):
    _make_full_proof_tree(tmp_path)
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    sample = tmp_path / proof["sample_output_path"]
    sample.unlink()
    r = detect_target_writer_readiness(tmp_path, SAMPLE_GAP)
    assert r["status"] == READINESS_MISSING_SAMPLE_OUTPUT, (
        f"Missing sample should give MISSING_SAMPLE_OUTPUT, got {r['status']}"
    )
    assert r["accepted_for_poc"] is False


# T13: Missing project file downgrades readiness
def test_missing_project_downgrades_readiness(tmp_path):
    _make_full_proof_tree(tmp_path)
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    (tmp_path / proof["project_path"]).unlink()
    r = detect_target_writer_readiness(tmp_path, SAMPLE_GAP)
    assert r["status"] == READINESS_MISSING_PROJECT, (
        f"Missing project should give MISSING_PROJECT, got {r['status']}"
    )
    assert r["accepted_for_poc"] is False


# T14: Missing test project downgrades readiness
def test_missing_tests_downgrades_readiness(tmp_path):
    _make_full_proof_tree(tmp_path)
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    (tmp_path / proof["test_project_path"]).unlink()
    r = detect_target_writer_readiness(tmp_path, SAMPLE_GAP)
    assert r["status"] == READINESS_MISSING_TESTS, (
        f"Missing tests should give MISSING_TESTS, got {r['status']}"
    )
    assert r["accepted_for_poc"] is False


# T15: READY writer unblocks gap (not in BLOCKED_GAP_IDS)
def test_ready_writer_unblocks_gap_for_routing(tmp_path):
    for gap_id in _ARCHITECTURE_BLOCKED_SEED:
        _make_full_proof_tree(tmp_path, gap_id)
    result = detect_target_writer_status(tmp_path)
    assert result == frozenset(), f"READY writers should leave no blocked gaps, got {sorted(result)}"


# T16: NOT-READY writer keeps gap in BLOCKED_GAP_IDS
def test_not_ready_writer_remains_blocked(tmp_path):
    # Only source present — NOT READY
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    src = tmp_path / proof["source_path"]
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("// stub", encoding="utf-8")
    result = detect_target_writer_status(tmp_path)
    assert SAMPLE_GAP in result, (
        f"NOT-READY gap should be in blocked set, but got {sorted(result)}"
    )


# T17: accepted_for_poc is never True from source-only
def test_gap_selector_never_marks_accepted_for_poc_from_source_only(tmp_path):
    proof = _GAP_WRITER_PROOF[SAMPLE_GAP]
    src = tmp_path / proof["source_path"]
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("// stub", encoding="utf-8")
    r = detect_target_writer_readiness(tmp_path, SAMPLE_GAP)
    assert r["accepted_for_poc"] is False, (
        "Source-only must never set accepted_for_poc=True"
    )
    assert r["status"] != READINESS_READY


# T18: Readiness registry JSON contains all four writer gaps
def test_generated_registry_contains_all_four_writer_gaps():
    registry_path = REPO_ROOT / "reports" / "dotnet-target-writer-readiness-hardening" / "target-writer-readiness-registry.json"
    assert registry_path.exists(), f"Registry not found: {registry_path}"
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    writers = data.get("writers", [])
    gap_ids = {w["gap_id"] for w in writers}
    assert len(writers) == 4, f"Expected 4 writers, got {len(writers)}"
    assert gap_ids == _ARCHITECTURE_BLOCKED_SEED, f"Gap ID mismatch: {gap_ids}"
    for w in writers:
        assert w["status"] == READINESS_READY, f"{w['gap_id']}: expected READY, got {w['status']}"
        assert w["accepted_for_poc"] is True
