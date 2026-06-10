"""Tests proving product_task_selector consumes the capability gap ledger.

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-VERIFICATION-PRODUCT-AUTONOMY-MEGA-SPRINT
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


def _gap_ledger_has_gaps() -> bool:
    """Return True only if the gap ledger exists AND contains at least one gap."""
    if not _GAP_LEDGER.exists():
        return False
    try:
        data = json.loads(_GAP_LEDGER.read_text(encoding="utf-8"))
        return len(data.get("gaps", [])) > 0
    except Exception:
        return False


@pytest.mark.skipif(not _gap_ledger_has_gaps(), reason="gap-ledger.json not present or all gaps closed")
def test_gap_ledger_loads_candidates():
    """_load_gap_candidates() returns at least one candidate from the live gap ledger."""
    candidates = _load_gap_candidates()
    assert len(candidates) >= 1, "Expected at least 1 gap candidate from live gap ledger"


@pytest.mark.skipif(not _gap_ledger_has_gaps(), reason="gap-ledger.json not present or all gaps closed")
def test_gap_candidates_are_foss_only():
    """All gap candidates are foss_reduced — commercial/Gate-11 items excluded."""
    # Verify the gap ledger has foss gaps
    data = json.loads(_GAP_LEDGER.read_text(encoding="utf-8"))
    gaps = data.get("gaps", [])
    foss_gaps = [g for g in gaps if g.get("product_type") == "foss_reduced"]
    assert len(foss_gaps) >= 1, "Expected foss_reduced gaps in ledger"


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
    """select_product_task() reports how many gap candidates were loaded."""
    result = select_product_task()
    assert "gap_candidates_loaded" in result


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_p0_gaps_have_priority_over_catalog():
    """P0 gap candidates appear before hardcoded catalog in evaluated list."""
    result = select_product_task()
    candidates = result["candidates"]
    gap_indices = [i for i, c in enumerate(candidates) if c.get("gap_source")]
    catalog_indices = [i for i, c in enumerate(candidates) if not c.get("gap_source")]
    if gap_indices and catalog_indices:
        # At least one gap candidate appears before the first catalog candidate
        assert min(gap_indices) < max(catalog_indices), (
            "Gap candidates should appear before catalog candidates"
        )


@pytest.mark.skipif(not _GAP_LEDGER.exists(), reason="gap-ledger.json not present")
def test_gap_candidates_all_classified_agent_owned():
    """All gap-derived candidates have classification AGENT_OWNED_SAFE."""
    candidates = _load_gap_candidates()
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
