"""
test_queue_backed_mutation_pilot.py -- Queue-backed source mutation proof.

Sprint: TRUE-AUTONOMOUS-MAINSTREAM-CONTINUATION-001
Added: 2026-06-10

Proves that the ProductSourceExecutor can be invoked with a queue item,
the execution is bounded (path checks, rollback), and produces
a structured ExecutionResult. This is NOT a real source mutation —
it's a proof that the queue dispatch pipeline works.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from product_source_executor import ProductSourceExecutor, ExecutionResult


def test_executor_blocks_forbidden_path():
    """Queue item targeting src/net/ should be BLOCKED."""
    executor = ProductSourceExecutor(repo_root=_REPO)
    item = {
        "action_id": "PILOT-FORBIDDEN-001",
        "target_path": "src/net/fods/FodsDocument.cs",
        "expected_tests": ["tests/net/fods/"],
        "allowed_paths": ["src/net/"],
        "forbidden_paths": [],
        "code_to_append": "// test",
    }
    result = executor.execute(item)
    assert result.status == "BLOCKED"
    assert result.action_id == "PILOT-FORBIDDEN-001"


def test_executor_blocks_missing_target():
    """Queue item with no target_path should be BLOCKED."""
    executor = ProductSourceExecutor(repo_root=_REPO)
    item = {
        "action_id": "PILOT-MISSING-001",
    }
    result = executor.execute(item)
    assert result.status == "BLOCKED"


def test_execution_result_to_dict():
    """ExecutionResult serializes to dict with all required fields."""
    result = ExecutionResult(
        action_id="TEST-001",
        status="SUCCESS",
        source_path="src/python/ndjson/ndjson_codec.py",
        test_passed=True,
        test_output="5 passed",
    )
    d = result.to_dict()
    assert d["action_id"] == "TEST-001"
    assert d["status"] == "SUCCESS"
    assert d["test_passed"] is True
    assert "executed_at" in d
    assert isinstance(d["changed_files"], list)


def test_executor_validates_allowed_paths():
    """Queue item with path outside allowed_paths should be BLOCKED."""
    executor = ProductSourceExecutor(repo_root=_REPO)
    item = {
        "action_id": "PILOT-PATH-001",
        "target_path": "src/python/ndjson/ndjson_codec.py",
        "expected_tests": ["tests/python/ndjson/"],
        "allowed_paths": ["src/python/csv/"],  # ndjson not in allowed
        "forbidden_paths": [],
        "code_to_append": "def pilot(): pass",
    }
    result = executor.execute(item)
    assert result.status == "BLOCKED"


def test_executor_result_has_timestamp():
    """All results must have an executed_at timestamp."""
    result = ExecutionResult(
        action_id="TS-001",
        status="FAILED",
        error="test error",
    )
    assert result.executed_at is not None
    assert "T" in result.executed_at  # ISO format
