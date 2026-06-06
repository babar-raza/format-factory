"""
Tests that the orchestrator consumes the action queue when --queue-first is used.
Sprint: FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

STATE_DIR = _repo_root / ".local" / "supervisor"
QUEUE_AFTER = _repo_root / "reports" / "h6-queue-product-loop" / "queue" / "queue-after.json"
QUEUE_BEFORE = _repo_root / "reports" / "h6-queue-product-loop" / "queue" / "queue-before.json"
CONSUMPTION_RESULT = _repo_root / "reports" / "h6-queue-product-loop" / "host-run" / "queue-consumption-result.json"
PRODUCT_PILOT = _repo_root / "reports" / "h6-queue-product-loop" / "product-pilot" / "product-gap-classification.json"


def test_queue_before_had_all_pending():
    """Prior to this sprint, all queue items were pending."""
    if not QUEUE_BEFORE.exists():
        pytest.skip("queue-before.json not present")
    data = json.loads(QUEUE_BEFORE.read_text())
    items = data.get("items", [])
    assert len(items) >= 1, "queue-before must have items"
    for item in items:
        assert item.get("status") == "pending", f"Item {item.get('action_id')} was not pending: {item.get('status')}"


def test_queue_after_has_consumed_items():
    """After orchestrator run, at least 3 queue items are done."""
    if not QUEUE_AFTER.exists():
        pytest.skip("queue-after.json not present")
    data = json.loads(QUEUE_AFTER.read_text())
    done_count = data.get("done_count", 0)
    assert done_count >= 3, f"Expected at least 3 done items, got {done_count}"


def test_product_item_consumed():
    """h6q-product-001 (PRODUCT_GAP_CLASSIFICATION_READONLY) was consumed."""
    if not QUEUE_AFTER.exists():
        pytest.skip("queue-after.json not present")
    data = json.loads(QUEUE_AFTER.read_text())
    items = data.get("items", [])
    product_items = [i for i in items if i.get("action_id") == "h6q-product-001"]
    assert len(product_items) == 1, "h6q-product-001 must exist in queue"
    assert product_items[0]["status"] == "done", f"h6q-product-001 must be done, got {product_items[0]['status']}"


def test_product_pilot_result_exists():
    """Product pilot result file was written by the orchestrator."""
    assert PRODUCT_PILOT.exists(), f"Product pilot result not found: {PRODUCT_PILOT}"
    data = json.loads(PRODUCT_PILOT.read_text())
    assert data.get("status") == "SUCCESS"
    assert data.get("action_type") == "PRODUCT_GAP_CLASSIFICATION_READONLY"
    assert data.get("product_source_mutated") is False
    assert data.get("poc_targets_mutated") is False


def test_no_product_source_mutated():
    """Product source was NOT mutated during queue consumption."""
    if not CONSUMPTION_RESULT.exists():
        pytest.skip("queue-consumption-result.json not present")
    data = json.loads(CONSUMPTION_RESULT.read_text())
    assert data.get("no_product_source_mutated") is True


def test_no_advisory_prompt_executed():
    """No advisory prompt was executed during queue consumption."""
    if not CONSUMPTION_RESULT.exists():
        pytest.skip("queue-consumption-result.json not present")
    data = json.loads(CONSUMPTION_RESULT.read_text())
    assert data.get("no_advisory_prompt_executed") is True


def test_queue_consumption_verdict():
    """Consumption result has a valid verdict."""
    if not CONSUMPTION_RESULT.exists():
        pytest.skip("queue-consumption-result.json not present")
    data = json.loads(CONSUMPTION_RESULT.read_text())
    verdict = data.get("verdict", "")
    valid_verdicts = {
        "QUEUE_DRIVEN_H6_MULTI_ACTION_PROVEN",
        "QUEUE_DRIVEN_H6_PRODUCT_SAFE_PILOT_PROVEN",
    }
    assert verdict in valid_verdicts, f"Invalid verdict: {verdict}"


def test_orchestrator_queue_first_flag_works():
    """Orchestrator accepts --queue-first flag without error."""
    from tools.supervisor.autonomous_orchestrator import _build_parser
    parser = _build_parser()
    args = parser.parse_args(["--max-cycles", "1", "--backend", "local", "--queue-first"])
    assert args.queue_first is True


def test_queue_item_result_path_populated():
    """Consumed queue items have result_path populated."""
    if not QUEUE_AFTER.exists():
        pytest.skip("queue-after.json not present")
    data = json.loads(QUEUE_AFTER.read_text())
    items = data.get("items", [])
    done_items = [i for i in items if i.get("status") == "done"]
    assert len(done_items) >= 1
    for item in done_items:
        assert item.get("result_path"), f"Done item {item.get('action_id')} has no result_path"
