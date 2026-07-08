"""
Tests that queue accounting is accurate — action-queue.jsonl is authoritative source of truth.
Sprint: FORMAT-FACTORY-H6-QUEUE-DRIVEN-PRODUCT-SOURCE-PILOT-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.state_dependent

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

QUEUE_PATH = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"

if not QUEUE_PATH.exists():
    pytest.skip(
        "action-queue.jsonl not present (gitignored, CI skip)",
        allow_module_level=True,
    )

CONSUMPTION_RESULT_PATH = (
    _repo_root
    / "reports"
    / "h6-queue-product-loop"
    / "host-run"
    / "queue-consumption-result.json"
)
ACCOUNTING_FIX_PATH = (
    _repo_root
    / "reports"
    / "h6-product-source-pilot"
    / "queue"
    / "queue-accounting-fix.json"
)


def _load_queue():
    if not QUEUE_PATH.exists():
        return []
    lines = QUEUE_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lines if l.strip()]


def test_queue_has_no_null_action_types():
    """After quarantine fix, action-queue.jsonl must have no items missing both action_type and item_type."""
    items = _load_queue()
    null_items = [i for i in items if i.get("action_type") is None and i.get("item_type") is None]
    assert null_items == [], f"Corrupt items with neither action_type nor item_type: {null_items}"


def test_queue_done_items_at_least_four():
    """Prior sprint consumed at least 4 items; queue must reflect this."""
    items = _load_queue()
    done = [i for i in items if i.get("status") == "done"]
    assert len(done) >= 4, f"Expected >=4 done items, got {len(done)}"


def test_h6q_product_001_done():
    """h6q-product-001 (product-safe pilot) must be done."""
    items = _load_queue()
    match = [i for i in items if i.get("action_id") == "h6q-product-001"]
    assert match, "h6q-product-001 not found in queue"
    assert match[0]["status"] == "done", f"Expected done, got {match[0]['status']}"


def test_accounting_fix_document_exists():
    """queue-accounting-fix.json must exist documenting the inconsistency."""
    assert ACCOUNTING_FIX_PATH.exists(), "queue-accounting-fix.json not found"


def test_accounting_fix_correct_count():
    """Accounting fix must declare correct_consumed_count=4."""
    if not ACCOUNTING_FIX_PATH.exists():
        pytest.skip("accounting fix not present")
    data = json.loads(ACCOUNTING_FIX_PATH.read_text())
    assert data.get("correct_consumed_count") == 4


def test_h6_q_002_in_done_set():
    """h6-q-002 (RUN_MD_NONEMPTY_CHECK) must be done in queue (was missing from prior result)."""
    items = _load_queue()
    match = [i for i in items if i.get("action_id") == "h6-q-002"]
    assert match, "h6-q-002 not found in queue"
    assert match[0]["status"] == "done"


def test_queue_path_exists():
    """action-queue.jsonl must exist."""
    assert QUEUE_PATH.exists()


def test_all_queue_items_have_action_type():
    """Every queue item must have a non-null action_type or item_type."""
    items = _load_queue()
    for item in items:
        has_type = item.get("action_type") is not None or item.get("item_type") is not None
        assert has_type, f"Missing both action_type and item_type: {item}"
