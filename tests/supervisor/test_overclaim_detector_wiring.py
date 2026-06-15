"""Tests for SUP-RECT-003: Verify overclaim_detector is wired into autonomous_cycle.py.

Validates that autonomous_cycle.py imports and attempts to run the overclaim
detector after grading (Step 3c).
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


class TestOverclaimDetectorWiring:
    def test_autonomous_cycle_has_overclaim_import(self):
        """Verify that autonomous_cycle.py references overclaim_detector."""
        ac_path = _REPO / "tools" / "supervisor" / "autonomous_cycle.py"
        text = ac_path.read_text(encoding="utf-8")
        assert "overclaim_detector" in text, \
            "autonomous_cycle.py must import overclaim_detector (SUP-RECT-003)"
        assert "OverclaimDetector" in text
        assert "detect_all" in text

    def test_autonomous_cycle_step_3c_present(self):
        """Verify Step 3c overclaim detector section exists."""
        ac_path = _REPO / "tools" / "supervisor" / "autonomous_cycle.py"
        text = ac_path.read_text(encoding="utf-8")
        assert "STEP 3c" in text or "Step 3c" in text
        assert "OVERCLAIM DETECTOR" in text

    def test_overclaim_detector_module_exists(self):
        """Verify the overclaim_detector module exists."""
        oc_path = _REPO / "tools" / "requirements_authority" / "overclaim_detector.py"
        assert oc_path.exists(), "overclaim_detector.py must exist"

    def test_overclaim_detector_has_detect_all(self):
        """Verify OverclaimDetector.detect_all() method exists via source inspection."""
        oc_path = _REPO / "tools" / "requirements_authority" / "overclaim_detector.py"
        text = oc_path.read_text(encoding="utf-8")
        assert "def detect_all(self)" in text
        assert "class OverclaimDetector" in text

    def test_overclaim_report_has_to_dict(self):
        """Verify OverclaimReport.to_dict() method exists via source inspection."""
        oc_path = _REPO / "tools" / "requirements_authority" / "overclaim_detector.py"
        text = oc_path.read_text(encoding="utf-8")
        assert "class OverclaimReport" in text
        assert "def to_dict(self)" in text
        assert '"findings"' in text or "'findings'" in text
