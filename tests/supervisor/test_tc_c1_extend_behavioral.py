"""TC-C1-EXTEND-BEHAVIORAL-001: Behavioral tests for compiler invocation on non-mainstream streams.

Created: 2026-06-25 (velvet-hatching-lark v4.1 forensic plan)

BACKGROUND:
TC-C1-EXTEND-001 removed the stream restriction from generate_next_worker_prompt.py line 1026.
Previously: if effective_stream in ("mainstream","product",None) and _product_groups_allowed:
After fix: if _product_groups_allowed:  (stream check removed)

These tests verify the code-level invariants for C4 gate advancement (PL1 → PL3).
Note: _group_allowed and _product_groups_allowed are nested locals in build_next_work_items;
behavioral tests use source-code verification and integration through _run_capability_consumer.

See: plans/capability-fact-to-feature-production-plan.md G.5 TC-C1-EXTEND-BEHAVIORAL-001
See: plans/velvet-hatching-lark.md TC-C1-EXTEND-BEHAVIORAL-001
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

_SRC = _REPO / "tools" / "supervisor" / "generate_next_worker_prompt.py"


class TestC1ExtendBehavioral:
    """Behavioral tests: stream restriction removed; consumer fires for all streams."""

    def test_stream_restriction_removed_from_source(self):
        """
        Test 1: The old stream restriction is NOT in the source file.

        Verifies TC-C1-EXTEND-001 persists: no 'effective_stream in ("mainstream","product")'
        condition wraps the _run_capability_consumer call.
        """
        source = _SRC.read_text(encoding="utf-8")
        # The old restriction — must NOT be present
        old_guard = 'effective_stream in ("mainstream","product") and _product_groups_allowed'
        assert old_guard not in source, (
            f"TC-C1-EXTEND-001 REGRESSION: old stream restriction found in {_SRC.name}. "
            "The guard must be 'if _product_groups_allowed:' only."
        )

    def test_product_groups_allowed_guard_present(self):
        """
        Test 2: The product-groups guard exists and gates the consumer call.

        Verifies that _product_groups_allowed IS used (not removed entirely) and
        that _run_capability_consumer is called inside that conditional block.
        """
        source = _SRC.read_text(encoding="utf-8")
        assert "_product_groups_allowed" in source, "_product_groups_allowed guard must be present"
        assert "_run_capability_consumer(REPO_ROOT)" in source, (
            "_run_capability_consumer must be called in the source"
        )
        # The guard must precede the consumer call on adjacent lines
        lines = source.splitlines()
        guard_idx = next(
            (i for i, ln in enumerate(lines) if "if _product_groups_allowed:" in ln),
            None,
        )
        consumer_idx = next(
            (i for i, ln in enumerate(lines) if "_run_capability_consumer(REPO_ROOT)" in ln),
            None,
        )
        assert guard_idx is not None, "if _product_groups_allowed: not found"
        assert consumer_idx is not None, "_run_capability_consumer(REPO_ROOT) not found"
        assert consumer_idx > guard_idx, (
            "Consumer call must come after product_groups_allowed guard"
        )
        assert consumer_idx - guard_idx <= 3, (
            "Consumer call must be directly inside the product_groups_allowed block "
            f"(expected within 3 lines of guard; got {consumer_idx - guard_idx})"
        )

    def test_consumer_function_is_importable(self):
        """
        Test 3: _run_capability_consumer is importable and callable.

        Verifies the function exists at module level (it must be importable
        for the stream-agnostic call to work).
        """
        import generate_next_worker_prompt as gnwp
        assert hasattr(gnwp, "_run_capability_consumer"), (
            "_run_capability_consumer must exist at module level in generate_next_worker_prompt.py"
        )
        assert callable(gnwp._run_capability_consumer)

    def test_consumer_returns_list(self):
        """
        Test 4: _run_capability_consumer returns a list (not None, not dict).

        Verifies the return contract so the for-loop in build_next_work_items
        can iterate without error regardless of stream.
        """
        import generate_next_worker_prompt as gnwp
        # Call with a valid repo root — returns list of compiled taskcards (may be empty)
        with patch.object(gnwp, "_run_capability_consumer", wraps=gnwp._run_capability_consumer) as mock_fn:
            result = gnwp._run_capability_consumer(_REPO)
            mock_fn.assert_called_once()
        assert isinstance(result, list), (
            f"_run_capability_consumer must return a list; got {type(result).__name__}"
        )

    def test_no_stream_check_between_product_groups_guard_and_consumer(self):
        """
        Test 5: Between 'if _product_groups_allowed:' and '_run_capability_consumer(REPO_ROOT)',
        there is no 'effective_stream' check.

        This is the core invariant: once product groups are enabled, stream does NOT matter.
        """
        source = _SRC.read_text(encoding="utf-8")
        lines = source.splitlines()

        guard_idx = next(
            (i for i, ln in enumerate(lines) if "if _product_groups_allowed:" in ln),
            None,
        )
        consumer_idx = next(
            (i for i, ln in enumerate(lines) if "_run_capability_consumer(REPO_ROOT)" in ln),
            None,
        )
        assert guard_idx is not None and consumer_idx is not None

        # The lines between the guard and consumer must NOT contain effective_stream checks
        between_lines = "\n".join(lines[guard_idx:consumer_idx + 1])
        assert "effective_stream" not in between_lines, (
            "BEHAVIORAL FAILURE: 'effective_stream' check found between product_groups_allowed "
            f"guard and consumer call. Lines {guard_idx}-{consumer_idx}:\n{between_lines}"
        )
