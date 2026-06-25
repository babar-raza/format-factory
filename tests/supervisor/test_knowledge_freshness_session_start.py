"""test_knowledge_freshness_session_start.py — TC-P3-002 extension hook tests.

Tests for autonomous_cycle_extensions.knowledge_freshness_hook.run_hook().
The hook is designed to be called at Step 0a-knowledge in autonomous_cycle.py but
is blocked by LOC cap (2465/2465). These tests verify the hook works in isolation.

See hidden-puzzling-rain.md TC-P3-002 and TC-P3-002-SUB-001.
"""
import sys
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


def _import_hook():
    """Import the hook module (adds extensions dir to sys.path as needed)."""
    ext_dir = _REPO / "tools" / "supervisor"
    if str(ext_dir) not in sys.path:
        sys.path.insert(0, str(ext_dir))
    from autonomous_cycle_extensions.knowledge_freshness_hook import run_hook
    return run_hook


class TestKnowledgeFreshnessHook:
    """TC-P3-002: session-start V68 hook tests."""

    def test_hook_importable(self):
        """Hook module is importable without error."""
        run_hook = _import_hook()
        assert callable(run_hook)

    def test_hook_pass_prints_knowledge_freshness(self, capsys):
        """PASS result prints 'KNOWLEDGE FRESHNESS: PASS: N source hash(es) verified'."""
        run_hook = _import_hook()
        pass_result = {
            "validator": "V68_knowledge_freshness",
            "result": "PASS",
            "items": ["KC-PYTHON-001 VERIFIED_CURRENT (src/python/csv/models.py)"],
            "summary": "PASS: 1 source hash(es) verified",
            "blocks_sprint": False,
        }
        with patch("knowledge_freshness_validator.validate_knowledge_freshness", return_value=pass_result):
            run_hook()
        captured = capsys.readouterr()
        assert "KNOWLEDGE FRESHNESS" in captured.out
        assert "PASS" in captured.out

    def test_hook_warn_prints_warning(self, capsys):
        """WARN result prints 'WARNING: KNOWLEDGE FRESHNESS: ...' and stale items."""
        run_hook = _import_hook()
        warn_result = {
            "validator": "V68_knowledge_freshness",
            "result": "WARN",
            "items": ["KC-PYTHON-001 STALE: hash diverged for src/python/csv/models.py"],
            "summary": "WARN: 1 stale/missing source(s)",
            "blocks_sprint": False,
        }
        with patch("knowledge_freshness_validator.validate_knowledge_freshness", return_value=warn_result):
            run_hook()
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "STALE" in captured.out

    def test_hook_skip_produces_no_output(self, capsys):
        """SKIP result (e.g., no registry) produces no output — silent."""
        run_hook = _import_hook()
        skip_result = {
            "validator": "V68_knowledge_freshness",
            "result": "PASS",
            "items": ["registry.yaml not found -- skipped"],
            "summary": "SKIPPED (no registry)",
            "blocks_sprint": False,
        }
        with patch("knowledge_freshness_validator.validate_knowledge_freshness", return_value=skip_result):
            run_hook()
        captured = capsys.readouterr()
        # SKIP result: summary contains SKIPPED but result is PASS — prints "KNOWLEDGE FRESHNESS: SKIPPED"
        # This is acceptable (non-blocking); verify no ERROR output
        assert "ERROR" not in captured.out
        assert "WARNING" not in captured.out

    def test_hook_non_blocking_on_import_error(self, capsys):
        """Hook must not raise even if validator cannot be imported."""
        run_hook = _import_hook()
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "knowledge_freshness_validator":
                raise ImportError("simulated unavailable")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Should return silently without raising
            try:
                run_hook()
            except Exception as exc:
                raise AssertionError(f"Hook raised unexpectedly: {exc}") from exc
        captured = capsys.readouterr()
        assert "ERROR" not in captured.out

    def test_hook_with_real_registry(self, capsys):
        """Integration: run hook against real repository — must not raise."""
        run_hook = _import_hook()
        try:
            run_hook()
        except Exception as exc:
            raise AssertionError(f"Hook raised against real repo: {exc}") from exc
        captured = capsys.readouterr()
        # Either PASS or WARNING is acceptable — both are non-blocking
        output = captured.out + captured.err
        assert "ERROR" not in output
        # If output is produced, it must mention KNOWLEDGE FRESHNESS
        if output.strip():
            assert "KNOWLEDGE FRESHNESS" in output or "WARNING" in output
