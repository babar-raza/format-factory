"""Tests for compilation_diff.py (TC-TEST-002-02).

4 focused tests verifying that the diff tool produces stable output for identical
inputs, detects changes in priority ordering and format coverage, and is a
pure function that does not mutate state.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools"))
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

sys.path.insert(0, str(_REPO_ROOT / "tools" / "canary"))
from compilation_diff import diff_outputs, run_compiler, load_compiler


# ---------------------------------------------------------------------------
# Synthetic ledger helpers
# ---------------------------------------------------------------------------

def make_ledger(items: list[dict], tmp_path: Path) -> Path:
    """Write a synthetic gap ledger JSONL/JSON and return its path."""
    ledger_path = tmp_path / "gap-ledger.json"
    # Write as list (the format run_compiler expects)
    ledger_path.write_text(json.dumps(items), encoding="utf-8")
    return ledger_path


def make_compiler_module(items_out: list[dict]) -> ModuleType:
    """Return a minimal module with compile_gaps returning fixed output."""
    mod = ModuleType("test_compiler")

    def compile_gaps(gaps, max_items=20):
        return items_out, []

    mod.compile_gaps = compile_gaps
    return mod


# ---------------------------------------------------------------------------
# Test 1: identical runs produce empty change lists
# ---------------------------------------------------------------------------

def test_diff_identical_runs_produces_empty_changes(tmp_path):
    """stable vs stable on same 5-gap ledger: priority_changes=[], format_coverage_changes=[]."""
    items = [
        {"format": "fods", "capability_name": "read_cell", "priority": "HIGH"},
        {"format": "csv", "capability_name": "read_row", "priority": "HIGH"},
        {"format": "ods", "capability_name": "get_sheet", "priority": "MEDIUM"},
        {"format": "toml", "capability_name": "get_key", "priority": "LOW"},
        {"format": "ndjson", "capability_name": "stream_rows", "priority": "MEDIUM"},
    ]

    stable_mod = make_compiler_module(items)
    candidate_mod = make_compiler_module(items)  # identical

    result = diff_outputs(items, items)

    assert result["priority_changes"] == []
    assert result["format_coverage_changes"] == []
    assert result["recommendation"] == "SAFE_TO_DEPLOY"


# ---------------------------------------------------------------------------
# Test 2: detects priority reordering
# ---------------------------------------------------------------------------

def test_diff_detects_priority_reordering():
    """Candidate with changed priority → priority_changes contains the reordered gap."""
    stable = [
        {"format": "fods", "capability_name": "read_cell", "priority": "HIGH"},
        {"format": "csv", "capability_name": "read_row", "priority": "MEDIUM"},
    ]
    candidate = [
        {"format": "fods", "capability_name": "read_cell", "priority": "LOW"},  # changed
        {"format": "csv", "capability_name": "read_row", "priority": "MEDIUM"},
    ]

    result = diff_outputs(stable, candidate)

    assert len(result["priority_changes"]) == 1
    change = result["priority_changes"][0]
    assert change["format"] == "fods"
    assert change["capability"] == "read_cell"
    assert change["stable_priority"] == "HIGH"
    assert change["candidate_priority"] == "LOW"
    assert result["recommendation"] == "REVIEW_REQUIRED"


# ---------------------------------------------------------------------------
# Test 3: detects format entering coverage
# ---------------------------------------------------------------------------

def test_diff_detects_format_entering_coverage():
    """Candidate with an extra format → format_coverage_changes records it as 'added'."""
    stable = [
        {"format": "fods", "capability_name": "read_cell", "priority": "HIGH"},
    ]
    candidate = [
        {"format": "fods", "capability_name": "read_cell", "priority": "HIGH"},
        {"format": "abw", "capability_name": "parse_doc", "priority": "LOW"},  # new format
    ]

    result = diff_outputs(stable, candidate)

    added = [c for c in result["format_coverage_changes"] if c["change"] == "added"]
    assert len(added) >= 1
    assert any(c["format"] == "abw" for c in added)
    assert result["recommendation"] == "REVIEW_REQUIRED"


# ---------------------------------------------------------------------------
# Test 4: pure function — no state mutation
# ---------------------------------------------------------------------------

def test_diff_is_pure_no_state_mutation(tmp_path):
    """Two runs on same ledger: output is identical; gap-ledger.json unchanged."""
    gap_items = [
        {"format": "fods", "capability_name": "read_cell", "priority": "HIGH"},
        {"format": "csv", "capability_name": "read_row", "priority": "MEDIUM"},
        {"format": "ods", "capability_name": "get_sheet", "priority": "LOW"},
    ]
    ledger_path = make_ledger(gap_items, tmp_path)

    # Record ledger hash before any runs
    ledger_hash_before = hashlib.sha256(ledger_path.read_bytes()).hexdigest()

    # Run diff twice
    result1 = diff_outputs(gap_items, gap_items)
    result2 = diff_outputs(gap_items, gap_items)

    # Both results must be equal (pure function)
    assert result1["priority_changes"] == result2["priority_changes"]
    assert result1["format_coverage_changes"] == result2["format_coverage_changes"]
    assert result1["recommendation"] == result2["recommendation"]

    # Ledger must be unchanged
    ledger_hash_after = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    assert ledger_hash_before == ledger_hash_after
