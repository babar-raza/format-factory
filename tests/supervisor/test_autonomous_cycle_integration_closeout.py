"""Integration tests proving closeout gate and watchdog are wired into autonomous_cycle.py.

Validates SHRP-003: autonomous_cycle.py imports and invokes validate_closeout_gate,
validate_no_stop_watchdog, and passes declared_scope to run_all_checks.
"""

import ast
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_CYCLE_PATH = _REPO / "tools" / "supervisor" / "autonomous_cycle.py"


class TestCloseoutWatchdogIntegration:
    """Prove that autonomous_cycle.py integrates closeout gate and watchdog."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        self.source = _CYCLE_PATH.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_syntax_valid(self):
        """autonomous_cycle.py parses without syntax errors."""
        # If ast.parse succeeded in fixture, this passes
        assert self.tree is not None

    def test_imports_closeout_gate(self):
        """Source contains import of run_closeout_gate from validate_closeout_gate."""
        assert "from validate_closeout_gate import run_closeout_gate" in self.source

    def test_imports_no_stop_watchdog(self):
        """Source contains import of run_no_stop_watchdog from validate_no_stop_watchdog."""
        assert "from validate_no_stop_watchdog import run_no_stop_watchdog" in self.source

    def test_invokes_closeout_gate(self):
        """Source calls run_closeout_gate(evidence_root_path)."""
        assert "run_closeout_gate(evidence_root_path)" in self.source

    def test_invokes_watchdog(self):
        """Source calls run_no_stop_watchdog(evidence_root_path)."""
        assert "run_no_stop_watchdog(evidence_root_path)" in self.source

    def test_stores_closeout_verdict_in_review(self):
        """Closeout gate result is stored in review dict."""
        assert 'review["closeout_gate_verdict"]' in self.source

    def test_stores_watchdog_verdict_in_review(self):
        """Watchdog result is stored in review dict."""
        assert 'review["watchdog_verdict"]' in self.source

    def test_declared_scope_passed_to_anti_skip(self):
        """run_all_checks is called with declared_scope parameter."""
        assert "declared_scope=_declared_item_types" in self.source

    def test_declared_scope_reads_planned_work_items(self):
        """declared_scope is extracted from planned_work_items, not work_items."""
        assert 'decl.get("planned_work_items", [])' in self.source

    def test_closeout_gate_section_comment(self):
        """The integration section has the R-CLOSEOUT marker."""
        assert "R-CLOSEOUT" in self.source


class TestCloseoutGateExecutable:
    """Prove the closeout gate validator is importable and executable."""

    def test_importable(self):
        sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
        try:
            from validate_closeout_gate import run_closeout_gate, ALL_GATES
            assert callable(run_closeout_gate)
            assert len(ALL_GATES) >= 5
        finally:
            sys.path.pop(0)

    def test_runs_on_empty_dir(self, tmp_path):
        sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
        try:
            from validate_closeout_gate import run_closeout_gate
            result = run_closeout_gate(tmp_path)
            assert "verdict" in result
            assert "gates" in result
        finally:
            sys.path.pop(0)


class TestNoStopWatchdogExecutable:
    """Prove the no-stop watchdog is importable and executable."""

    def test_importable(self):
        sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
        try:
            from validate_no_stop_watchdog import run_no_stop_watchdog, ALL_CHECKS
            assert callable(run_no_stop_watchdog)
            assert len(ALL_CHECKS) >= 3
        finally:
            sys.path.pop(0)

    def test_runs_on_empty_dir(self, tmp_path):
        sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
        try:
            from validate_no_stop_watchdog import run_no_stop_watchdog
            result = run_no_stop_watchdog(tmp_path)
            assert "verdict" in result
            assert result["verdict"] in ("ALLOW_STOP", "BLOCK_STOP")
        finally:
            sys.path.pop(0)
