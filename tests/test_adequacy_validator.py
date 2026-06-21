"""Focused proof tests for sprint_executor_validate.py adequacy validator (RC-5 evidence)."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "supervisor"))
from sprint_executor_validate import _check_test_layer_adequacy


def test_adequacy_warns_on_governance_change_with_low_layer():
    """test_layer=1 on a tools/supervisor/ change must produce a warning."""
    doc = {"test_layer": 1, "changed_files": ["tools/supervisor/foo.py"]}
    warnings = _check_test_layer_adequacy(doc)
    assert len(warnings) == 1
    assert "WARN[adequacy]" in warnings[0]
    assert "min_layer=3" in warnings[0]


def test_adequacy_no_warning_on_adequate_layer():
    """test_layer=3 on a tools/supervisor/ change must produce no warning."""
    doc = {"test_layer": 3, "changed_files": ["tools/supervisor/foo.py"]}
    warnings = _check_test_layer_adequacy(doc)
    assert all("WARN[adequacy]" not in w for w in warnings)


def test_adequacy_skips_when_no_test_layer_declared():
    """If test_layer is absent, adequacy check must return no warnings."""
    doc = {"changed_files": ["tools/supervisor/foo.py"]}
    warnings = _check_test_layer_adequacy(doc)
    assert all("WARN[adequacy]" not in w for w in warnings)


def test_adequacy_skips_when_no_changed_files():
    """If changed_files is absent, adequacy check must return no warnings."""
    doc = {"test_layer": 1}
    warnings = _check_test_layer_adequacy(doc)
    assert all("WARN[adequacy]" not in w for w in warnings)
