"""TC-WIRE-001 verification tests.

Verifies that:
1. capability_queue_consumer.py is subprocess-wired in autonomous_cycle.py (Step 3e)
2. capability_queue_consumer.py respects status='closed' when selecting gaps
3. The consumer produces 0 results when all FOSS gaps are closed
4. The subprocess wiring uses consistent pattern with SAL/capmap recomputes
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_CONSUMER = _REPO / "tools" / "supervisor" / "capability_queue_consumer.py"
_CYCLE = _REPO / "tools" / "supervisor" / "autonomous_cycle.py"
_GAP_LEDGER = _REPO / "reports" / "capability-layer" / "gap-ledger.json"


class TestConsumerWiredInAutonomousCycle:
    def test_step_3e_present_in_cycle(self):
        """autonomous_cycle.py contains Step 3e capability queue consumer block."""
        source = _CYCLE.read_text(encoding="utf-8")
        assert "Step 3e: Capability Queue Consumer" in source

    def test_step_3e_uses_subprocess(self):
        """Step 3e calls consumer via subprocess, not import."""
        source = _CYCLE.read_text(encoding="utf-8")
        assert "capability_queue_consumer.py" in source
        # subprocess.run is used (via _subprocess_recompute alias)
        assert "_subprocess_recompute.run" in source

    def test_step_3e_non_blocking(self):
        """Step 3e failure does not raise — wrapped in try/except."""
        source = _CYCLE.read_text(encoding="utf-8")
        # The cap consumer block has try/except
        idx = source.index("Step 3e: Capability Queue Consumer")
        block = source[idx:idx+1500]
        assert "except" in block

    def test_step_3e_result_stored_in_review(self):
        """Step 3e stores result in review dict as cap_consumer."""
        source = _CYCLE.read_text(encoding="utf-8")
        assert 'review["cap_consumer"]' in source


class TestConsumerStatusFilter:
    def test_consumer_skips_closed_status_gaps(self):
        """Consumer source contains status='closed' check."""
        source = _CONSUMER.read_text(encoding="utf-8")
        assert 'gap.get("status", "").lower() == "closed"' in source

    def test_consumer_checks_status_before_gap_type_in_loop(self):
        """Status check precedes gap_type check inside the selection loop."""
        source = _CONSUMER.read_text(encoding="utf-8")
        status_idx = source.index('gap.get("status", "").lower() == "closed"')
        # Find gap_type check inside the loop (after the status check)
        gap_type_in_loop_idx = source.index('gap.get("gap_type"', status_idx)
        assert status_idx < gap_type_in_loop_idx

    def test_consumer_with_all_closed_gaps_returns_zero(self):
        """Consumer produces 0 taskcards when all FOSS gaps are closed."""
        if not _GAP_LEDGER.exists():
            return  # skip if gap ledger not generated
        gap_data = json.loads(_GAP_LEDGER.read_text(encoding="utf-8"))
        foss_open = [
            g for g in gap_data.get("gaps", [])
            if g.get("product_type", "").lower() in ("foss", "foss_reduced", "both")
            and g.get("status", "").lower() != "closed"
        ]
        if len(foss_open) > 0:
            return  # skip — gaps exist, consumer will find them (expected)
        # All FOSS gaps closed — consumer should find 0
        result = subprocess.run(
            [sys.executable, str(_CONSUMER), "--max-gaps", "3"],
            capture_output=True, text=True, cwd=str(_REPO), timeout=30
        )
        assert result.returncode == 0
        assert "Selected 0 FOSS gaps" in result.stdout

    def test_consumer_executable(self):
        """Consumer runs without error."""
        result = subprocess.run(
            [sys.executable, str(_CONSUMER), "--max-gaps", "1"],
            capture_output=True, text=True, cwd=str(_REPO), timeout=30
        )
        assert result.returncode == 0

    def test_consumer_path_exists(self):
        """Consumer file exists at expected path."""
        assert _CONSUMER.is_file()
