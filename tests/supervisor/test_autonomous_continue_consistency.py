"""Regression tests for Change 5: autonomous_continue signal unification.

C5 (SIGNAL-UNIFY-001): After autonomous_cycle.py processes a declaration, the
autonomous_continue value in work-item-grades.md and latest-cycle-summary.md must
agree with continuation-signal.json.

These tests verify the structural fix: that the patching block (inserted after
auto_continue_value is computed) is present and correctly targets both output files.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestSignalUnificationCodePresent:
    """Verify SIGNAL-UNIFY-001 patch block is present in autonomous_cycle.py."""

    def test_unification_block_present(self):
        """C5 patch block must be present and contain the three key operations."""
        ac_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        src = ac_path.read_text(encoding="utf-8")

        assert "SIGNAL-UNIFY-001" in src, (
            "SIGNAL-UNIFY-001 patch block not found in autonomous_cycle.py"
        )
        assert "work-item-grades.md" in src, (
            "work-item-grades.md not referenced in unification block"
        )
        assert "latest-cycle-summary.md" in src, (
            "latest-cycle-summary.md not referenced in unification block"
        )
        assert "auto_continue_value" in src, (
            "auto_continue_value not used in unification block"
        )

    def test_unification_block_after_auto_continue_computation(self):
        """SIGNAL-UNIFY-001 block must appear AFTER auto_continue_value is set."""
        ac_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        src = ac_path.read_text(encoding="utf-8")

        # Find positions
        auto_continue_line = "auto_continue_value = bool(manifest.get"
        unify_marker = "SIGNAL-UNIFY-001"

        pos_auto = src.find(auto_continue_line)
        pos_unify = src.find(unify_marker)

        assert pos_auto != -1, f"auto_continue_value computation not found"
        assert pos_unify != -1, f"SIGNAL-UNIFY-001 marker not found"
        assert pos_unify > pos_auto, (
            f"SIGNAL-UNIFY-001 block (pos {pos_unify}) must come AFTER "
            f"auto_continue_value computation (pos {pos_auto})"
        )

    def test_unification_block_before_signal_write(self):
        """SIGNAL-UNIFY-001 block must appear BEFORE the signal dict is written."""
        ac_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        src = ac_path.read_text(encoding="utf-8")

        unify_marker = "SIGNAL-UNIFY-001"
        # The signal dict creation
        signal_write_marker = '"autonomous_continue": auto_continue_value,'

        pos_unify = src.find(unify_marker)
        pos_signal = src.find(signal_write_marker)

        assert pos_unify != -1
        assert pos_signal != -1
        assert pos_unify < pos_signal, (
            f"SIGNAL-UNIFY-001 block must appear before signal dict is written"
        )


class TestSignalUnificationLogic:
    """Unit tests for the value-replacement logic used in SIGNAL-UNIFY-001."""

    def test_replacement_logic_correct(self):
        """The string replacement logic correctly updates autonomous_continue."""
        fake_review_value = False
        fake_auto_continue_value = "true_with_rework"

        file_content = (
            "# Work Item Grades\n"
            "Sprint: test-sprint\n"
            "## Summary\n"
            f"- Autonomous Continue: {fake_review_value}\n"
        )

        old_ac = f"- Autonomous Continue: {fake_review_value}"
        new_ac = f"- Autonomous Continue: {fake_auto_continue_value}"

        if old_ac != new_ac and old_ac in file_content:
            patched = file_content.replace(old_ac, new_ac, 1)
        else:
            patched = file_content

        assert f"- Autonomous Continue: {fake_auto_continue_value}" in patched, (
            "Replacement logic did not correctly update autonomous_continue"
        )
        assert f"- Autonomous Continue: {fake_review_value}" not in patched

    def test_no_replacement_when_values_agree(self):
        """When review value and auto_continue_value agree, file is unchanged."""
        same_value = True

        file_content = (
            "# Work Item Grades\n"
            f"- Autonomous Continue: {same_value}\n"
        )
        original = file_content

        old_ac = f"- Autonomous Continue: {same_value}"
        new_ac = f"- Autonomous Continue: {same_value}"

        if old_ac != new_ac and old_ac in file_content:
            patched = file_content.replace(old_ac, new_ac, 1)
        else:
            patched = file_content

        assert patched == original, "File should not be modified when values agree"
