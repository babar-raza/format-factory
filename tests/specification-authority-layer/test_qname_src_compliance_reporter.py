"""
Tests for tools/specification-authority-layer/qname_src_compliance_reporter.py
TC-QNAME-VALIDATOR-001
"""
import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).parents[2]
_REPORTER = _REPO / "tools" / "specification-authority-layer" / "qname_src_compliance_reporter.py"
_spec = importlib.util.spec_from_file_location("qname_src_compliance_reporter", _REPORTER)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
run_compliance_check = _mod.run_compliance_check


def test_reporter_runs_and_returns_dict():
    report = run_compliance_check()
    assert isinstance(report, dict)


def test_report_has_required_keys():
    report = run_compliance_check()
    assert "total_classes" in report
    assert "summary" in report
    assert "classes" in report


def test_total_classes_positive():
    report = run_compliance_check()
    assert report["total_classes"] > 0


def test_summary_counts_sum_to_total():
    report = run_compliance_check()
    s = report["summary"]
    total = s["implemented"] + s["stub_only"] + s["facade_only"] + s["missing"]
    assert total == report["total_classes"]


def test_all_classes_have_canonical_field():
    report = run_compliance_check()
    for cls in report["classes"]:
        assert "canonical" in cls
        assert isinstance(cls["canonical"], str)
        assert len(cls["canonical"]) > 0


def test_all_classes_have_compliance_status():
    report = run_compliance_check()
    valid_statuses = {"implemented", "stub_only", "facade_only", "missing"}
    for cls in report["classes"]:
        assert cls["compliance_status"] in valid_statuses


def test_all_classes_have_qname():
    report = run_compliance_check()
    for cls in report["classes"]:
        assert "qname" in cls


def test_fodt_spec_stubs_detected():
    """FODT Spec/ files (Text.Paragraph etc.) must appear as stub_only (not missing)."""
    report = run_compliance_check()
    fodt_spec_class = next(
        (c for c in report["classes"] if c["canonical"] == "Text.Paragraph"), None
    )
    assert fodt_spec_class is not None
    assert fodt_spec_class["compliance_status"] in {"stub_only", "implemented"}


def test_missing_count_less_than_total():
    """Some classes should be more than missing (stubs exist for FODT)."""
    report = run_compliance_check()
    assert report["summary"]["missing"] < report["total_classes"]


def test_no_implemented_classes():
    """All canonical classes are currently stubs or missing — none fully implemented."""
    report = run_compliance_check()
    assert report["summary"]["implemented"] == 0
