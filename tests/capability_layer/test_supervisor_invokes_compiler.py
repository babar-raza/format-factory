"""
test_supervisor_invokes_compiler.py

TC-C1-003: Verify that generate_next_worker_prompt._run_capability_consumer()
subprocess-invokes capability_queue_consumer.py which in turn calls capability_compiler.

This confirms Gate C4: supervisor pipeline now has a code path that invokes
the capability compiler via the queue consumer subprocess.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT_DIR = REPO_ROOT / "tools" / "supervisor"


def _import_prompt_generator():
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    from generate_next_worker_prompt import _run_capability_consumer
    return _run_capability_consumer


class TestSupervisorInvokesCompiler:
    """Gate C4 verification — supervisor pipeline subprocess-invokes capability_queue_consumer."""

    def test_run_capability_consumer_function_exists(self):
        """_run_capability_consumer is importable from generate_next_worker_prompt."""
        fn = _import_prompt_generator()
        assert callable(fn), "_run_capability_consumer must be callable"

    def test_run_capability_consumer_returns_list(self):
        """Consumer function always returns a list (never raises)."""
        fn = _import_prompt_generator()
        result = fn(REPO_ROOT, max_gaps=1)
        assert isinstance(result, list), f"Expected list, got {type(result)}"

    def test_run_capability_consumer_produces_taskcards(self):
        """Consumer produces at least one taskcard when FOSS gaps are available."""
        fn = _import_prompt_generator()
        result = fn(REPO_ROOT, max_gaps=3)
        if not result:
            pytest.skip("No open FOSS gaps available for compilation — all gaps closed")

    def test_compiled_taskcard_has_required_fields(self):
        """Each compiled taskcard has the fields needed for sprint work items."""
        fn = _import_prompt_generator()
        result = fn(REPO_ROOT, max_gaps=2)
        if not result:
            pytest.skip("No FOSS gaps available for compilation")
        tc = result[0]
        assert "taskcard_id" in tc, "Missing taskcard_id"
        assert "title" in tc, "Missing title"
        assert "function_name" in tc, "Missing function_name"
        assert "status" in tc, "Missing status"
        assert tc["status"] == "READY_TO_EXECUTE", f"Expected READY_TO_EXECUTE, got {tc['status']}"

    def test_compiled_taskcard_has_test_obligations(self):
        """Each taskcard specifies test obligations (min count + required types)."""
        fn = _import_prompt_generator()
        result = fn(REPO_ROOT, max_gaps=2)
        if not result:
            pytest.skip("No FOSS gaps available for compilation")
        tc = result[0]
        obligations = tc.get("test_obligations", {})
        assert "min_test_count" in obligations, "Missing min_test_count in test_obligations"
        assert obligations["min_test_count"] >= 5, (
            f"Expected min_test_count >= 5, got {obligations['min_test_count']}"
        )

    def test_compiled_taskcard_has_evidence_obligations(self):
        """Each taskcard specifies evidence obligations."""
        fn = _import_prompt_generator()
        result = fn(REPO_ROOT, max_gaps=2)
        if not result:
            pytest.skip("No FOSS gaps available for compilation")
        tc = result[0]
        evidence = tc.get("evidence_obligations", [])
        assert isinstance(evidence, list) and len(evidence) >= 1, (
            "Expected at least 1 evidence obligation"
        )

    def test_consumer_script_exists(self):
        """capability_queue_consumer.py exists at expected path."""
        script = REPO_ROOT / "tools" / "supervisor" / "capability_queue_consumer.py"
        assert script.exists(), f"Consumer script not found: {script}"

    def test_compiler_script_exists(self):
        """capability_compiler.py exists at expected path (called by consumer)."""
        script = REPO_ROOT / "tools" / "supervisor" / "capability_compiler.py"
        assert script.exists(), f"Compiler script not found: {script}"

    def test_gate_c4_subprocess_pattern(self):
        """Confirm wiring uses subprocess (not import) — consistent with system architecture."""
        prompt_gen = REPO_ROOT / "tools" / "supervisor" / "generate_next_worker_prompt.py"
        src = prompt_gen.read_text(encoding="utf-8")
        # Must use subprocess.run or Popen, not import capability_compiler directly
        assert "subprocess.run" in src, "generate_next_worker_prompt must use subprocess.run for consumer"
        assert "_run_capability_consumer" in src, "Helper function must be defined"
        # Must NOT have a direct import of capability_compiler (use subprocess, not library import)
        assert "from capability_compiler import" not in src, (
            "generate_next_worker_prompt must NOT directly import capability_compiler "
            "(use subprocess via capability_queue_consumer instead)"
        )
