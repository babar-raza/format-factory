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
    """Seeded formats (e.g. fodg) must be blocked."""
    r = check_product_readiness("fodg")
    assert r["allowed"] is False


def test_implementing_format_not_allowed():
    """Implementing formats (e.g. ndjson) must be blocked."""
    r = check_product_readiness("ndjson")
    assert r["allowed"] is False


def test_fods_returns_result():
    """FODS check_product_readiness returns a structured result."""
    r = check_product_readiness("fods")
    assert "allowed" in r
    assert "qname_gate" in r
    assert "src_layout_gate" in r


def test_all_formats_return_result():
    """load_ledger() returns entries; check_product_readiness works for each."""
    ledger = load_ledger()
    assert len(ledger) >= 20, f"Expected at least 20, got {len(ledger)}"
    for fmt in ledger:
        r = check_product_readiness(fmt)
        assert "format" in r
        assert "allowed" in r
        assert isinstance(r["allowed"], bool)
        assert "qname_gate" in r


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


# ── Group 5: Check 9 real integration (calls check_continuation.check() directly) ──
# These tests advance proof from PROOF_LEVEL_2 (unit) to PROOF_LEVEL_3 (integration).


def _make_minimal_signal(tmp_path: Path, *, autonomous_continue: bool = True) -> Path:
    """Write a minimal continuation signal sufficient to reach Check 9."""
    signal = {
        "continuation_state": "YES_CONTINUE",
        "autonomous_continue": autonomous_continue,
        "stop_reason": None,
        "iteration": 0,
        "max_iterations": 5,
        "rework_items": [],
        "hard_stops": [],
    }
    sig_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
    sig_path.parent.mkdir(parents=True, exist_ok=True)
    sig_path.write_text(json.dumps(signal), encoding="utf-8")
    return sig_path


def _make_gates_file(tmp_path: Path) -> None:
    """Write approval-gates.md that satisfies Check 6."""
    gates_dir = tmp_path / "reports" / "supervisor"
    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "approval-gates.md").write_text(
        "AUTONOMOUS_CONTINUE: YES\n", encoding="utf-8"
    )


def _make_work_items(tmp_path: Path) -> None:
    """Write next-work-items.json to satisfy Check 7."""
    wi_dir = tmp_path / ".local" / "supervisor"
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "next-work-items.json").write_text(
        json.dumps({"stream": "product", "work_items": []}), encoding="utf-8"
    )


def _make_plan_lock(tmp_path: Path) -> None:
    """Ensure no active plan lock files exist so POST_PLAN_TERMINAL is not triggered.

    check_continuation Check M6 fires on TERMINAL_CLOSED locks. Integration tests
    pass an empty plan-locks directory so the plan lock checks are bypassed cleanly.
    """
    plan_locks_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
    plan_locks_dir.mkdir(parents=True, exist_ok=True)
    # Active plan lock absent -> no TERMINAL_CLOSED trigger
    active_lock = tmp_path / ".local" / "supervisor" / "active-plan-lock.json"
    if active_lock.exists():
        active_lock.unlink()


def test_check9_real_check_call_blocks_on_blocked_format(tmp_path):
    """PROOF_LEVEL_3: check() returns STOP when selected gaps contain a blocked format.

    This test calls check_continuation.check() directly with a synthesized repo
    layout, exercising Check 9 through the real continuation orchestration path.
    """
    from check_continuation import check

    # Write a single-entry ledger where 'testfmt' is blocked
    ledger_data = [{
        "product_id": "TEST-PYTHON",
        "format": "testfmt",
        "runtime": "python",
        "qname_schema_version": "1.0",
        "qname_compliance_status": "seeded",
        "spec_hierarchy_mapping": "missing",
        "src_layout_status": "mixed_model",
        "forbidden_bucket_scan_status": "clean",
        "sal_fact_linkage": "present",
        "sal_fact_count": 10,
        "continuation_allowed": False,
        "continuation_reason": "qname_status_not_verified",
        "blockers": ["qname_compliance_gate: FAIL"],
        "next_required_action": "Heal qname registry",
        "last_verified_at": "2026-06-24",
        "ledger_entry_hash": "abcd1234abcd1234",
    }]
    ledger_path = tmp_path / "registry" / "product-deepening-ledger.yaml"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(yaml.dump(ledger_data), encoding="utf-8")

    # Write selected-product-gaps.json containing the blocked format
    gaps_path = tmp_path / ".local" / "supervisor" / "selected-product-gaps.json"
    gaps_path.parent.mkdir(parents=True, exist_ok=True)
    gaps_path.write_text(json.dumps({
        "selected_gaps": [{"format": "testfmt", "gap_id": "GAP-TEST-001"}]
    }), encoding="utf-8")

    # Scaffold the other required files so earlier checks pass
    _make_minimal_signal(tmp_path)
    _make_gates_file(tmp_path)
    _make_work_items(tmp_path)
    _make_plan_lock(tmp_path)

    result = check(tmp_path, session_id="test-session-check9")

    assert result["verdict"] == "STOP", (
        f"Expected STOP from Check 9 but got: {result}"
    )
    assert result["reason"] == "product_deepening_architecture_gate", (
        f"Wrong stop reason: {result['reason']}"
    )
    assert "testfmt" in result.get("blocked_formats", []), (
        f"Expected testfmt in blocked_formats: {result}"
    )


def test_check9_real_check_call_continues_when_no_gaps(tmp_path):
    """PROOF_LEVEL_3: check() reaches CONTINUE when selected-product-gaps.json is absent.

    Bootstrap tolerance: if gaps file is missing, Check 9 is silently skipped.
    The test verifies the check() passes through to a CONTINUE verdict when no gaps are selected.
    """
    from check_continuation import check

    # Write real ledger (all blocked)
    ledger_path = tmp_path / "registry" / "product-deepening-ledger.yaml"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_data = [{
        "product_id": "TEST-PYTHON",
        "format": "testfmt",
        "runtime": "python",
        "qname_schema_version": "1.0",
        "qname_compliance_status": "seeded",
        "spec_hierarchy_mapping": "missing",
        "src_layout_status": "mixed_model",
        "forbidden_bucket_scan_status": "clean",
        "sal_fact_linkage": "present",
        "sal_fact_count": 0,
        "continuation_allowed": False,
        "continuation_reason": "qname_status_not_verified",
        "blockers": [],
        "next_required_action": "Heal qname registry",
        "last_verified_at": "2026-06-24",
        "ledger_entry_hash": "abcd1234abcd1234",
    }]
    ledger_path.write_text(yaml.dump(ledger_data), encoding="utf-8")

    # No gaps file written — Check 9 should be skipped (bootstrap tolerance)
    _make_minimal_signal(tmp_path)
    _make_gates_file(tmp_path)
    _make_work_items(tmp_path)
    _make_plan_lock(tmp_path)

    result = check(tmp_path, session_id="test-session-check9-bt")

    # Check 9 was skipped → should reach CONTINUE
    assert result["verdict"] == "CONTINUE", (
        f"Expected CONTINUE (Check 9 bootstrap) but got: {result}"
    )
