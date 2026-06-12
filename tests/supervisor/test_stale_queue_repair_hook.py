"""
Integration tests for stale_queue_repair_hook.py — the bridge that wires
rework_orchestrator into the real supervisor/autonomous rework path.

Tests:
  - Hook callable from supervisor_loop CLI path
  - Stale items detected and repaired
  - Capability gap stops safely
  - Idempotent second run
  - No product source mutation during stale repair
  - No global continuation signal corruption

Sprint: FORMAT-FACTORY-SELF-HEALING-PRODUCT-DEEPENING-RNEXT
Run ID: format-factory-self-healing-product-deepening-rnext-20260611-2000
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_TOOLS_SUP = _REPO / "tools" / "supervisor"

if str(_TOOLS_SUP) not in sys.path:
    sys.path.insert(0, str(_TOOLS_SUP))

from stale_queue_repair_hook import run_stale_repair  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

STALE_QUEUE = json.dumps(
    {"action_id": "test-stale-001", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
     "status": "pending", "target_path": "src/python/abw/abw_codec.py",
     "function_name": "search_text"}  # search_text exists in source → stale
) + "\n"

GAP_QUEUE = json.dumps(
    {"action_id": "test-gap-001", "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
     "status": "pending", "target_path": "src/python/abw/abw_codec.py",
     "function_name": "nonexistent_function_xyz_totally_missing"}
) + "\n"

MIXED_QUEUE = STALE_QUEUE + GAP_QUEUE


def _write_queue(tmp_path, content: str):
    queue = tmp_path / ".local" / "supervisor"
    queue.mkdir(parents=True)
    (queue / "action-queue.jsonl").write_text(content, encoding="utf-8")


def _write_source(tmp_path, rel_path: str, content: str):
    """Write a source file into the tmp_path repo."""
    p = tmp_path / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# Minimal ABW codec with search_text present (for stale detection)
_ABW_WITH_SEARCH_TEXT = """
def search_text(model, query):
    return [i for i, p in enumerate(model.get('paragraphs', [])) if query in p]
"""

# Minimal ABW codec WITHOUT search_text (for gap detection)
_ABW_WITHOUT_SEARCH_TEXT = """
def load(path):
    return {}
"""


@pytest.fixture
def stale_repo(tmp_path):
    """Repo with one stale queue item (function already exists in source)."""
    _write_queue(tmp_path, STALE_QUEUE)
    _write_source(tmp_path, "src/python/abw/abw_codec.py", _ABW_WITH_SEARCH_TEXT)
    return tmp_path


@pytest.fixture
def gap_repo(tmp_path):
    """Repo with one genuine capability gap (function missing from source)."""
    _write_queue(tmp_path, GAP_QUEUE)
    _write_source(tmp_path, "src/python/abw/abw_codec.py", _ABW_WITHOUT_SEARCH_TEXT)
    return tmp_path


@pytest.fixture
def empty_queue_repo(tmp_path):
    _write_queue(tmp_path, "")
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_hook_importable():
    """Hook is importable from supervisor_loop CLI path."""
    from stale_queue_repair_hook import run_stale_repair as fn
    assert callable(fn)


def test_hook_returns_ok_empty_queue(empty_queue_repo):
    result = run_stale_repair(repo_root=empty_queue_repo, dry_run=True)
    assert result["status"] == "OK"
    assert result["stale_repaired"] == 0
    assert result["capability_gaps"] == 0


def test_hook_detects_stale_item(stale_repo):
    result = run_stale_repair(repo_root=stale_repo, dry_run=True)
    assert result["status"] == "OK"
    cycle = result["cycle_summary"]
    assert cycle.get("stale_detected", 0) >= 1 or cycle.get("defects_detected", 0) >= 1


def test_hook_dry_run_does_not_mutate_queue(stale_repo):
    queue_path = stale_repo / ".local" / "supervisor" / "action-queue.jsonl"
    before = queue_path.read_text(encoding="utf-8")
    run_stale_repair(repo_root=stale_repo, dry_run=True)
    after = queue_path.read_text(encoding="utf-8")
    assert before == after, "Dry-run must not mutate the queue"


def test_hook_repairs_stale_item(stale_repo):
    result = run_stale_repair(repo_root=stale_repo, dry_run=False)
    assert result["status"] == "OK"
    # After repair, stale items should be marked done
    queue_path = stale_repo / ".local" / "supervisor" / "action-queue.jsonl"
    lines = [l for l in queue_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    items = [json.loads(l) for l in lines]
    pending = [i for i in items if i.get("status") == "pending"]
    assert len(pending) == 0, "No pending stale items should remain after repair"


def test_hook_idempotent_second_run(stale_repo):
    run_stale_repair(repo_root=stale_repo, dry_run=False)
    result2 = run_stale_repair(repo_root=stale_repo, dry_run=False)
    assert result2["status"] == "OK"
    assert result2["stale_repaired"] == 0, "Second run must find 0 stale items (idempotent)"


def test_hook_stops_on_capability_gap(gap_repo):
    result = run_stale_repair(repo_root=gap_repo, dry_run=False)
    assert result["status"] == "CAPABILITY_GAP_STOP"
    assert result["capability_gaps"] >= 1


def test_hook_no_product_source_mutation(stale_repo):
    source_file = stale_repo / "src" / "python" / "abw" / "abw_codec.py"
    before = source_file.read_bytes()
    run_stale_repair(repo_root=stale_repo, dry_run=False)
    after = source_file.read_bytes()
    assert before == after, "Stale queue repair must not mutate product source files"


def test_hook_writes_log_file(tmp_path, stale_repo):
    log_path = tmp_path / "test-repair-log.json"
    run_stale_repair(repo_root=stale_repo, dry_run=True, log_path=log_path)
    assert log_path.exists()
    data = json.loads(log_path.read_text(encoding="utf-8"))
    assert "status" in data
    assert "run_at" in data


def test_hook_reachable_from_supervisor_loop_module():
    """Verify supervisor_loop has stale-repair in CANONICAL_COMMANDS."""
    import importlib
    if str(_TOOLS_SUP) not in sys.path:
        sys.path.insert(0, str(_TOOLS_SUP))
    loop = importlib.import_module("supervisor_loop")
    assert "stale-repair" in loop.CANONICAL_COMMANDS


def test_hook_result_no_continuation_signal_corruption(stale_repo):
    """Ensure no .local/supervisor/continuation-signal.json is created/modified by hook."""
    signal_path = stale_repo / ".local" / "supervisor" / "continuation-signal.json"
    assert not signal_path.exists(), "Signal should not exist before test"
    run_stale_repair(repo_root=stale_repo, dry_run=False)
    assert not signal_path.exists(), "Hook must not create continuation-signal.json"
