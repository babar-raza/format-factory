"""Tests for detect_product_progress.py v2/v3 — R100 Train H + R101 Train I."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from detect_product_progress import (
    build_snapshot,
    detect_no_progress,
    category_progress,
    classify_progress_type,
)


def _matrix(*products, group="foss_reduced_products"):
    return {group: products}


def _product(fmt, **statuses):
    return {"format": fmt, "python_status": statuses}


def test_category_progress_load():
    m = _matrix(_product("fods", load_fods="DONE", parse_fods="DONE", save_fods="NOT_IMPLEMENTED"))
    counts = category_progress(m)
    assert counts["load"]["done"] == 2
    assert counts["load"]["total"] == 2
    assert counts["save"]["done"] == 0
    assert counts["save"]["total"] == 1


def test_category_progress_export():
    m = _matrix(_product("fods", export_to_csv="DONE", export_to_html="PARTIAL"))
    counts = category_progress(m)
    assert counts["export"]["done"] == 1
    assert counts["export"]["total"] == 2


def test_category_progress_dogfood():
    m = _matrix(_product("fods", dogfood="DONE"))
    counts = category_progress(m)
    assert counts["dogfood"]["done"] == 1


def test_category_progress_other():
    m = _matrix(_product("fods", some_misc="DONE", another_misc="NOT_STARTED"))
    counts = category_progress(m)
    assert counts["other"]["total"] == 2
    assert counts["other"]["done"] == 1


def test_category_progress_empty():
    counts = category_progress({})
    for cat in counts.values():
        assert cat["done"] == 0
        assert cat["total"] == 0


def test_build_snapshot_deterministic():
    ledger = {"entries": [{"entry_id": "e1"}, {"entry_id": "e2"}]}
    m = _matrix(_product("fods", load="DONE"))
    s1 = build_snapshot(ledger, m, captured_at="2026-01-01T00:00:00Z")
    s2 = build_snapshot(ledger, m, captured_at="2026-01-01T00:00:00Z")
    assert s1["fingerprint"] == s2["fingerprint"]


def test_detect_no_progress_stagnant():
    s = {"fingerprint": "abc"}
    result = detect_no_progress([s, s, s], threshold=2)
    assert result["no_progress"] is True
    assert result["stagnant_intervals"] >= 2


def test_detect_no_progress_changing():
    result = detect_no_progress(
        [{"fingerprint": "a"}, {"fingerprint": "b"}, {"fingerprint": "c"}],
        threshold=2,
    )
    assert result["no_progress"] is False


# --- v3 (R101): classify_progress_type tests ---


def test_classify_product_progress():
    """Positive: product caps done + product lanes -> PRODUCT_PROGRESS."""
    counts = {"load": {"done": 2, "total": 3}, "save": {"done": 0, "total": 1}, "other": {"done": 0, "total": 0}}
    ledger = {"lanes": [
        {"status": "completed", "stream_id": "mainstream"},
    ]}
    result = classify_progress_type(counts, ledger)
    assert result["progress_type"] == "PRODUCT_PROGRESS"
    assert result["capabilities_done"] == 2


def test_classify_tooling_progress():
    """Positive: only tooling lanes, no product caps -> TOOLING_PROGRESS."""
    counts = {"load": {"done": 0, "total": 0}, "other": {"done": 0, "total": 0}}
    ledger = {"lanes": [
        {"status": "completed", "stream_id": "acceleration"},
        {"status": "completed", "stream_id": "supervisor"},
    ]}
    result = classify_progress_type(counts, ledger)
    assert result["progress_type"] == "TOOLING_PROGRESS"
    assert result["tooling_lanes"] == 2


def test_classify_evidence_only():
    """Positive: completed lanes but no caps done and not tooling -> EVIDENCE_ONLY."""
    counts = {"load": {"done": 0, "total": 3}, "other": {"done": 0, "total": 0}}
    ledger = {"lanes": [
        {"status": "completed", "stream_id": "mainstream"},
    ]}
    result = classify_progress_type(counts, ledger)
    assert result["progress_type"] == "EVIDENCE_ONLY"


def test_classify_blocked_with_reason():
    """Positive: blockers present -> BLOCKED_WITH_REASON."""
    counts = {"load": {"done": 0, "total": 0}, "other": {"done": 0, "total": 0}}
    result = classify_progress_type(counts, blockers=["Gate 11 approval needed"])
    assert result["progress_type"] == "BLOCKED_WITH_REASON"
    assert "Gate 11" in result["reason"]


def test_classify_no_progress():
    """Positive: no lanes, no caps -> NO_PROGRESS."""
    counts = {"load": {"done": 0, "total": 0}, "other": {"done": 0, "total": 0}}
    result = classify_progress_type(counts)
    assert result["progress_type"] == "NO_PROGRESS"


def test_classify_blocked_takes_priority():
    """Negative: blockers override even if product progress exists."""
    counts = {"load": {"done": 5, "total": 5}, "other": {"done": 0, "total": 0}}
    ledger = {"lanes": [{"status": "completed", "stream_id": "mainstream"}]}
    result = classify_progress_type(counts, ledger, blockers=["blocked"])
    assert result["progress_type"] == "BLOCKED_WITH_REASON"


def test_classify_no_ledger():
    """Negative: None ledger should not crash."""
    counts = {"load": {"done": 0, "total": 0}, "other": {"done": 0, "total": 0}}
    result = classify_progress_type(counts, None)
    assert result["progress_type"] == "NO_PROGRESS"
