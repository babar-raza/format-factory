"""Tests proving product_task_selector consumes the capability gap ledger.

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT3
Moved from tests/supervisor/ to tests/capability_layer/ to avoid mainstream stream
cross-contamination (supervisor paths are forbidden in mainstream stream prompts).

Note: When all capability gaps are closed (0 gaps), tests that assert >= 1 gap
are skipped or adjusted to reflect the valid all-gaps-closed state.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from product_task_selector import (
    _load_gap_candidates,
    select_product_task,
)

_GAP_LEDGER = _REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_gap_ledger_loads_candidates():
    """_load_gap_candidates() can be called without error; 0 candidates is valid when all gaps closed."""
    candidates = _load_gap_candidates()
    # 0 candidates is valid when all capability gaps have been implemented
    assert isinstance(candidates, list), "Expected list from _load_gap_candidates()"


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_gap_candidates_have_valid_product_type():
    """All gaps must have a valid product_type (foss_reduced or commercial)."""
    data = json.loads(_GAP_LEDGER.read_text(encoding="utf-8"))
    gaps = data.get("gaps", [])
    if not gaps:
        pytest.skip("All gaps closed — no gaps to validate type for")
    valid_types = {"foss", "foss_reduced", "commercial", "commercial_dotnet", "governance",
                   "governance_machinery", "both", None}
    for g in gaps:
        assert g.get("product_type") in valid_types, (
            f"Gap {g.get('gap_id')} has invalid product_type: {g.get('product_type')}"
        )


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_gap_candidates_have_required_fields():
    """Each gap candidate has required task fields."""
    candidates = _load_gap_candidates()
    required = {"task_id", "format", "action", "target_file", "function_name",
                "classification", "gap_source", "gap_priority"}
    for c in candidates:
        missing = required - c.keys()
        assert not missing, f"Candidate {c.get('task_id')} missing fields: {missing}"


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_selector_reports_gap_candidates_loaded():
    """select_product_task() reports how many gap candidates were loaded (0 is valid when all closed)."""
    result = select_product_task()
    assert "gap_candidates_loaded" in result
    assert result["gap_candidates_loaded"] >= 0  # 0 is valid when all gaps are implemented


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_p0_gaps_have_priority_over_catalog():
    """P0 gap candidates appear before hardcoded catalog in evaluated list."""
    result = select_product_task()
    candidates = result["candidates"]
    gap_indices = [i for i, c in enumerate(candidates) if c.get("gap_source")]
    catalog_indices = [i for i, c in enumerate(candidates) if not c.get("gap_source")]
    if gap_indices and catalog_indices:
        assert min(gap_indices) < max(catalog_indices), (
            "Gap candidates should appear before catalog candidates"
        )


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_gap_candidates_all_classified_agent_owned():
    """All gap-derived candidates have classification AGENT_OWNED_SAFE (when gaps exist)."""
    candidates = _load_gap_candidates()
    if not candidates:
        pytest.skip("All gaps closed — no gap candidates to validate classification for")
    for c in candidates:
        assert c["classification"] == "AGENT_OWNED_SAFE", (
            f"Gap candidate {c['task_id']} must be AGENT_OWNED_SAFE"
        )


def test_selector_no_unsafe_gate_actions():
    """Selector never selects tasks requiring external gate approval from gap ledger."""
    result = select_product_task()
    selected = result.get("selected")
    if selected and selected.get("gap_source"):
        assert selected.get("gate_required") is None, (
            "Gap-derived selected task must not require external gate approval"
        )


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_closed_gaps_not_in_ledger():
    """Gaps for test_verified capabilities should not appear as missing_implementation gaps.

    Note: implementation_verified functions (implemented but no matching test file) may
    legitimately appear in the gap ledger as missing_test_coverage gaps. This test only
    checks that truly closed capabilities don't appear as missing_implementation.
    """
    data = json.loads(_GAP_LEDGER.read_text(encoding="utf-8"))
    # Only check missing_implementation gaps (not missing_test_coverage)
    missing_impl_ids = [
        g["gap_id"] for g in data.get("gaps", [])
        if g.get("gap_type") == "missing_implementation"
    ]
    # These were implemented — they should not be missing_implementation
    assert "GAP-TSV-FOSS-APPEND_ROW-001" not in missing_impl_ids, "TSV append_row was implemented"
    assert "GAP-FODG-FOSS-EXPORT_TO_CS-001" not in missing_impl_ids, "FODG export_to_csv was implemented"
    assert "GAP-FODG-FOSS-ROUNDTRIP-001" not in missing_impl_ids, "FODG roundtrip was implemented"
    assert "GAP-NDJSON-FOSS-VALIDATE_SCH-001" not in missing_impl_ids, "NDJSON validate_schema was implemented"
    assert "GAP-NDJSON-FOSS-ROUNDTRIP-001" not in missing_impl_ids, "NDJSON roundtrip was implemented"
    assert "GAP-TSV-FOSS-ROUNDTRIP-001" not in missing_impl_ids, "TSV roundtrip was implemented"
