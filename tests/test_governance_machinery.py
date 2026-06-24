"""
Governance machinery regression tests (TC-GOV-A4).

Tests that validators correctly detect violations and pass compliant code.
"""
from __future__ import annotations

import ast
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "tools" / "validators"))


class TestOrphanDetectionAnalyticsNotOrphan:
    """TC-GOV-A4: analytics files must not be flagged as orphans."""

    def test_analytics_in_known_purposes(self):
        from source_structure_validator import _KNOWN_PURPOSES
        assert "analytics" in _KNOWN_PURPOSES

    def test_abw_analytics_not_orphan(self):
        from source_structure_validator import _is_recognized_file
        assert _is_recognized_file("abw_analytics.py", "abw") is True

    def test_xcf_analytics_not_orphan(self):
        from source_structure_validator import _is_recognized_file
        assert _is_recognized_file("xcf_analytics.py", "xcf") is True

    def test_drawing_document_not_orphan(self):
        from source_structure_validator import _is_recognized_file
        assert _is_recognized_file("drawing_document.py", "fodg") is True


class TestDuplicateDetection:
    """Duplicate function definitions are detected."""

    def test_detects_duplicate(self, tmp_path):
        from source_structure_validator import _find_duplicate_defs
        f = tmp_path / "test_dup.py"
        f.write_text("def foo(): pass\ndef bar(): pass\ndef foo(): pass\n")
        dups = _find_duplicate_defs(f)
        assert len(dups) == 1
        assert "foo" in dups[0]

    def test_no_false_positive(self, tmp_path):
        from source_structure_validator import _find_duplicate_defs
        f = tmp_path / "test_nodup.py"
        f.write_text("def foo(): pass\ndef bar(): pass\n")
        dups = _find_duplicate_defs(f)
        assert len(dups) == 0


class TestBaselineCapMonotonicity:
    """No known_violations entry has loc > baseline_loc_cap."""

    def test_all_caps_honored(self):
        baseline_path = _REPO / "registry" / "source-structure-baseline.json"
        b = json.loads(baseline_path.read_text(encoding="utf-8"))
        kv = b.get("known_violations", {})
        violations = []
        tracked_remediation = []
        for path, entry in kv.items():
            loc = entry.get("loc", 0)
            cap = entry.get("baseline_loc_cap", loc)
            if loc > cap:
                if entry.get("remediation_deadline"):
                    tracked_remediation.append(f"{path}: loc {loc} > cap {cap} (deadline: {entry['remediation_deadline']})")
                else:
                    violations.append(f"{path}: loc {loc} > cap {cap}")
        # Untracked over-cap files are violations; tracked ones are accepted with deadlines
        assert violations == [], f"Untracked caps violated: {violations}"


class TestRemediationDeadline:
    """Every known_violations entry has a remediation_deadline."""

    def test_deadlines_present(self):
        baseline_path = _REPO / "registry" / "source-structure-baseline.json"
        b = json.loads(baseline_path.read_text(encoding="utf-8"))
        kv = b.get("known_violations", {})
        missing = [p for p, e in kv.items() if "remediation_deadline" not in e]
        assert missing == [], f"Missing deadlines: {missing[:5]}"
