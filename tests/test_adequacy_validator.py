"""Focused proof tests for sprint_executor_validate.py adequacy validator.

Original: RC-5 evidence (fslay01)
Updated: TC-FSLAY02-ENF-001 — adequacy now returns (errors, warnings) tuple.
Product items trigger ERROR, non-product items trigger WARN (until escalation date).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "supervisor"))
from sprint_executor_validate import _check_test_layer_adequacy


def test_adequacy_warns_on_governance_change_with_low_layer():
    """test_layer=1 on a tools/supervisor/ change (non-product) must produce a warning."""
    doc = {"test_layer": 1, "changed_files": ["tools/supervisor/foo.py"]}
    errors, warnings = _check_test_layer_adequacy(doc)
    assert len(errors) == 0, f"Non-product items should not produce errors: {errors}"
    assert len(warnings) == 1
    assert "WARN[adequacy]" in warnings[0]
    assert "min_layer=3" in warnings[0]


def test_adequacy_no_warning_on_adequate_layer():
    """test_layer=3 on a tools/supervisor/ change must produce no warning."""
    doc = {"test_layer": 3, "changed_files": ["tools/supervisor/foo.py"]}
    errors, warnings = _check_test_layer_adequacy(doc)
    assert len(errors) == 0
    assert all("WARN[adequacy]" not in w for w in warnings)


def test_adequacy_skips_when_no_test_layer_declared():
    """If test_layer is absent, adequacy check must return no errors or warnings."""
    doc = {"changed_files": ["tools/supervisor/foo.py"]}
    errors, warnings = _check_test_layer_adequacy(doc)
    assert len(errors) == 0
    assert all("WARN[adequacy]" not in w for w in warnings)


def test_adequacy_skips_when_no_changed_files():
    """If changed_files is absent, adequacy check must return no errors or warnings."""
    doc = {"test_layer": 1}
    errors, warnings = _check_test_layer_adequacy(doc)
    assert len(errors) == 0
    assert all("WARN[adequacy]" not in w for w in warnings)


# --- TC-FSLAY02-ENF-001: Product item enforcement tests ---

def test_adequacy_errors_on_product_source_with_low_layer():
    """PRODUCT_SOURCE item with test_layer=0 on a src/python/ change must produce ERROR."""
    doc = {
        "test_layer": 0,
        "changed_files": ["src/python/ndjson/ndjson_parser.py"],
        "planned_work_items": [
            {"item_id": "TEST-001", "title": "Add parser fn", "status": "completed",
             "item_type": "PRODUCT_SOURCE"},
        ],
    }
    errors, warnings = _check_test_layer_adequacy(doc)
    assert len(errors) == 1, f"Expected 1 error for product item, got: {errors}"
    assert "ERROR[adequacy]" in errors[0]
    assert "PRODUCT item enforcement active" in errors[0]
    assert len(warnings) == 0


def test_adequacy_warns_on_non_product_with_low_layer():
    """GOVERNANCE_TASKCARD item with test_layer=1 on supervisor change must WARN, not ERROR."""
    doc = {
        "test_layer": 1,
        "changed_files": ["tools/supervisor/foo.py"],
        "planned_work_items": [
            {"item_id": "GOV-001", "title": "Update validator", "status": "completed",
             "item_type": "GOVERNANCE_TASKCARD"},
        ],
    }
    errors, warnings = _check_test_layer_adequacy(doc)
    assert len(errors) == 0, f"Non-product items should not produce errors: {errors}"
    assert any("WARN[adequacy]" in w for w in warnings)
