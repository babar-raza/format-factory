"""Tests for product_deepening_gate.py — TC-HEAL-PD-007."""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import json
import pytest
import yaml

from product_deepening_gate import (
    load_ledger,
    check_product_readiness,
    check_formats_in_gaps,
    emit_continuation_signal_gates,
)
from governance_validators_ext import validate_expansion_fallback_refs


# ── Group 1: Format gate logic (uses real ledger) ──


def test_seeded_format_not_allowed():
    """Seeded formats (e.g. abw) must be blocked with qname_gate=FAIL."""
    r = check_product_readiness("abw")
    assert r["allowed"] is False
    assert r["qname_gate"] == "FAIL"


def test_implementing_format_not_allowed():
    """Implementing formats (e.g. ndjson) must be blocked."""
    r = check_product_readiness("ndjson")
    assert r["allowed"] is False
    # implementing gets PASS on qname_gate but still blocked by other gates
    assert r["qname_gate"] == "PASS"


def test_fods_oversized_not_allowed():
    """FODS has qname=verified but src_layout=oversized — must be blocked."""
    r = check_product_readiness("fods")
    assert r["allowed"] is False
    assert r["src_layout_gate"] == "FAIL"
    assert r["qname_gate"] == "PASS"


def test_all_20_formats_return_result():
    """load_ledger() returns 20 entries; check_product_readiness works for each."""
    ledger = load_ledger()
    assert len(ledger) == 20, f"Expected 20, got {len(ledger)}"
    for fmt in ledger:
        r = check_product_readiness(fmt)
        assert "format" in r
        assert "allowed" in r
        assert r["allowed"] is False  # all 20 blocked at launch


# ── Group 2: Error handling and bootstrap tolerance ──


def test_missing_ledger_returns_false_gracefully():
    """Non-existent ledger path -> allowed=False, reason=ledger_missing, no exception."""
    r = check_product_readiness("fods", ledger_path=Path("/nonexistent/ledger.yaml"))
    assert r["allowed"] is False
    assert r["reason"] == "ledger_missing"


def test_missing_format_entry_returns_false():
    """Unknown format not in ledger -> allowed=False, reason=no_ledger_entry."""
    r = check_product_readiness("unknown_xyz_format_zzz_999")
    assert r["allowed"] is False
    assert r["reason"] == "no_ledger_entry"


def test_empty_selected_gaps_returns_empty_results():
    """check_formats_in_gaps([]) returns empty list, not error."""
    result = check_formats_in_gaps([])
    assert result == []


def test_emit_signal_gates_structure():
    """emit_continuation_signal_gates([]) returns dict with expected keys."""
    sig = emit_continuation_signal_gates([])
    assert "evaluated_formats" in sig
    assert "all_allowed" in sig
    assert "blocked_formats" in sig
    assert "gate_results" in sig
    assert sig["evaluated_formats"] == []
    assert sig["blocked_formats"] == []


# ── Group 3: Check 9 integration ──


def test_check9_blocks_when_format_not_allowed(tmp_path):
    """Check 9 blocks when ledger has a blocked format in selected gaps."""
    # Create a minimal ledger
    ledger_data = [{
        "product_id": "TEST-PYTHON",
        "format": "testfmt",
        "runtime": "python",
        "qname_schema_version": "1.0",
        "qname_compliance_status": "seeded",
        "spec_hierarchy_mapping": "missing",
        "src_layout_status": "unknown",
        "forbidden_bucket_scan_status": "unknown",
        "sal_fact_linkage": "unknown",
        "sal_fact_count": 0,
        "continuation_allowed": False,
        "last_verified_at": "2026-06-23",
        "ledger_entry_hash": "",
    }]
    ledger_path = tmp_path / "product-deepening-ledger.yaml"
    ledger_path.write_text(yaml.dump(ledger_data), encoding="utf-8")

    # Test check_formats_in_gaps with this ledger
    gaps = [{"format": "testfmt", "gap_id": "GAP-TEST-001"}]
    results = check_formats_in_gaps(gaps, ledger_path=ledger_path)
    assert len(results) == 1
    assert results[0]["allowed"] is False
    assert results[0]["format"] == "testfmt"


def test_check9_passes_when_no_gaps_selected():
    """Empty selected_gaps list -> Check 9 skipped -> no block."""
    results = check_formats_in_gaps([])
    assert results == []  # No formats evaluated = no block


def test_check9_bootstrap_tolerance_when_ledger_absent():
    """Missing ledger -> check_product_readiness returns allowed=False gracefully."""
    r = check_product_readiness("fods", ledger_path=Path("/tmp/nonexistent/ledger.yaml"))
    assert r["allowed"] is False
    assert r["reason"] == "ledger_missing"


def test_check9_does_not_block_when_no_gaps_file():
    """When selected_gaps is empty, no formats are evaluated."""
    sig = emit_continuation_signal_gates([])
    assert sig["all_allowed"] is True  # vacuously true
    assert sig["blocked_formats"] == []


# ── Group 4: V58 validator ──


def test_v58_warns_on_expansion_fallback():
    """EXPANSION-FALLBACK ref -> result=WARN, blocks_sprint=False."""
    decl = {
        "planned_work_items": [{
            "item_type": "PRODUCT_SOURCE",
            "item_id": "X-001",
            "gap_ledger_ref": "EXPANSION-FALLBACK-FODS-some_fn",
        }]
    }
    r = validate_expansion_fallback_refs(decl)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False
    assert r["fallback_count"] == 1


def test_v58_passes_on_real_gap_ref():
    """Real GAP ref -> result=PASS."""
    decl = {
        "planned_work_items": [{
            "item_type": "PRODUCT_SOURCE",
            "item_id": "Y-001",
            "gap_ledger_ref": "GAP-FODS-LOAD-001",
        }]
    }
    r = validate_expansion_fallback_refs(decl)
    assert r["result"] == "PASS"
    assert r["fallback_count"] == 0


def test_v58_passes_on_empty_declaration():
    """Empty declaration -> PASS, blocks_sprint=False."""
    r = validate_expansion_fallback_refs({})
    assert r["result"] == "PASS"
    assert r["blocks_sprint"] is False


def test_v58_blocks_sprint_is_always_false():
    """Even with multiple violations, blocks_sprint must be False."""
    decl = {
        "planned_work_items": [
            {"item_type": "PRODUCT_SOURCE", "item_id": f"ITEM-{i}",
             "gap_ledger_ref": f"EXPANSION-FALLBACK-FMT-fn{i}"}
            for i in range(10)
        ]
    }
    r = validate_expansion_fallback_refs(decl)
    assert r["result"] == "WARN"
    assert r["blocks_sprint"] is False
    assert r["fallback_count"] == 10


def test_v58_skips_governance_taskcard():
    """GOVERNANCE_TASKCARD items are not in CHECKED set -> not flagged."""
    decl = {
        "planned_work_items": [{
            "item_type": "GOVERNANCE_TASKCARD",
            "item_id": "TC-001",
            "gap_ledger_ref": "EXPANSION-FALLBACK-FODS-something",
        }]
    }
    r = validate_expansion_fallback_refs(decl)
    assert r["result"] == "PASS"
    assert r["total_checked"] == 0
    assert r["fallback_count"] == 0
