"""
tests/python/test_gate4_contract.py

Gate 4 evidence contract tests.
Validates that the Gate 4 validator correctly accepts valid entries
and rejects invalid ones per the contract in docs/gate4-evidence-contract.yaml.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.gates.validate_gate4_evidence import validate_gate4

# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(fid: str, g4: dict) -> dict:
    return {"format_id": fid, "gates": {"gate_4": g4}}


def _has_error(errors: list[str], fragment: str) -> bool:
    return any(fragment in e for e in errors)


# ── STANDALONE_PROTOTYPE ──────────────────────────────────────────────────────

def test_standalone_prototype_accepted():
    fmt = _fmt("xpm", {
        "status": "passed",
        "evidence_type": "STANDALONE_PROTOTYPE",
        "prototype_path": "prototypes/by-format/xpm/",
        "tests": ["tests/skills/test_xpm_gate4_prototype.py"],
        "corpus": ["samples/by-format/xpm/"],
        "limitations": ["XPM3 only"],
    })
    errors = validate_gate4("xpm", fmt)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_standalone_prototype_missing_tests_rejected():
    fmt = _fmt("xpm", {
        "status": "passed",
        "evidence_type": "STANDALONE_PROTOTYPE",
        "prototype_path": "prototypes/by-format/xpm/",
        "corpus": ["samples/by-format/xpm/"],
    })
    errors = validate_gate4("xpm", fmt)
    assert _has_error(errors, "missing tests")


def test_standalone_prototype_missing_corpus_rejected():
    fmt = _fmt("xpm", {
        "status": "passed",
        "evidence_type": "STANDALONE_PROTOTYPE",
        "prototype_path": "prototypes/by-format/xpm/",
        "tests": ["tests/skills/test_xpm_gate4_prototype.py"],
    })
    errors = validate_gate4("xpm", fmt)
    assert _has_error(errors, "missing corpus")


def test_standalone_prototype_with_delegation_rejected():
    fmt = _fmt("xpm", {
        "status": "passed",
        "evidence_type": "STANDALONE_PROTOTYPE",
        "prototype_path": "prototypes/by-format/xpm/",
        "delegated_source_path": "src/python/xpm/xpm_parser.py",  # prohibited
        "tests": ["tests/skills/test_xpm_gate4_prototype.py"],
        "corpus": ["samples/by-format/xpm/"],
    })
    errors = validate_gate4("xpm", fmt)
    assert _has_error(errors, "INV-G4-006")


# ── EVIDENCE_WRAPPER ──────────────────────────────────────────────────────────

def test_valid_wrapper_accepted():
    fmt = _fmt("csv", {
        "status": "passed",
        "evidence_type": "EVIDENCE_WRAPPER",
        "prototype_path": "prototypes/by-format/csv/",
        "delegated_source_path": "src/python/csv/csv_parser.py",
        "delegated_symbols": ["parse_csv", "probe_csv"],
        "tests": ["tests/skills/test_csv_gate4_prototype.py"],
        "corpus": ["samples/by-format/csv/"],
    })
    errors = validate_gate4("csv", fmt)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_wrapper_missing_delegated_source_rejected():
    fmt = _fmt("csv", {
        "status": "passed",
        "evidence_type": "EVIDENCE_WRAPPER",
        "prototype_path": "prototypes/by-format/csv/",
        "tests": ["tests/skills/test_csv_gate4_prototype.py"],
        "corpus": ["samples/by-format/csv/"],
    })
    errors = validate_gate4("csv", fmt)
    assert _has_error(errors, "delegated_source_path")


# ── SOURCE_TRACK_EQUIVALENT ───────────────────────────────────────────────────

def test_source_track_equivalent_accepted():
    fmt = _fmt("ods", {
        "status": "passed",
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "delegated_source_path": "src/python/ods/ods_parser.py",
        "corpus": ["samples/by-format/ods/"],
        "tests": ["tests/python/ods/test_dogfood_ods_csv_pipeline.py"],
    })
    errors = validate_gate4("ods", fmt)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_source_track_missing_delegated_source_rejected():
    fmt = _fmt("ods", {
        "status": "passed",
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "corpus": ["samples/by-format/ods/"],
        "tests": ["tests/python/ods/test_dogfood_ods_csv_pipeline.py"],
    })
    errors = validate_gate4("ods", fmt)
    assert _has_error(errors, "delegated_source_path")


# ── BLOCKED_BEFORE_GATE4 ──────────────────────────────────────────────────────

def test_blocked_prerequisite_retained():
    fmt = _fmt("zpaq", {
        "status": "blocked",
        "evidence_type": "BLOCKED_BEFORE_GATE4",
        "reason": "gate3_prerequisite_incomplete",
        "blocker": "ZPAQL VM unavailable",
        "next_gate": "gate_3_recovery",
    })
    errors = validate_gate4("zpaq", fmt)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_blocked_missing_reason_rejected():
    fmt = _fmt("zpaq", {
        "status": "blocked",
        "evidence_type": "BLOCKED_BEFORE_GATE4",
        "blocker": "something",
        "next_gate": "gate_3_recovery",
    })
    errors = validate_gate4("zpaq", fmt)
    assert _has_error(errors, "reason")


def test_blocked_with_passed_status_rejected():
    fmt = _fmt("zpaq", {
        "status": "passed",  # MUST NOT be passed when blocked
        "evidence_type": "BLOCKED_BEFORE_GATE4",
        "reason": "gate3_prerequisite_incomplete",
        "blocker": "ZPAQL VM unavailable",
        "next_gate": "gate_3_recovery",
    })
    errors = validate_gate4("zpaq", fmt)
    assert _has_error(errors, "INV-G4-005")


# ── ABSENT gate_4 ──────────────────────────────────────────────────────────────

def test_missing_gate4_disposition_rejected():
    fmt = {"format_id": "unknown_fmt", "gates": {}}
    errors = validate_gate4("unknown_fmt", fmt)
    assert _has_error(errors, "ABSENT")


# ── Missing evidence_type ──────────────────────────────────────────────────────

def test_path_only_evidence_rejected():
    fmt = _fmt("csv", {
        "status": "passed",
        # No evidence_type — PROHIBITED-004
        "prototype_path": "prototypes/by-format/csv/",
    })
    errors = validate_gate4("csv", fmt)
    assert _has_error(errors, "PROHIBITED-004") or _has_error(errors, "evidence_type")


# ── NOT_APPLICABLE ────────────────────────────────────────────────────────────

def test_not_applicable_format_skipped():
    fmt = {"format_id": "odf-shared", "gates": {}}
    errors = validate_gate4("odf-shared", fmt)
    assert errors == []
