"""
R70 Train E — test_r70_validator_rejects_pending_test_summary.py
Verify that python-tests-summary.txt with POST_BUNDLE_AUTHORITATIVE: PENDING
is detected as a defect.
"""

import pytest

DEFECTIVE_SUMMARY = """
Python Tests Summary — R69
Pre-bundle test run: 5172 passed, 10 failed, 31 skipped
POST_BUNDLE_AUTHORITATIVE: PENDING (to be updated after R69 bundle build)
"""

CORRECT_SUMMARY = """
Python Tests Summary — R69
Pre-bundle test run: 5172 passed, 10 failed, 31 skipped
POST_BUNDLE_AUTHORITATIVE: 5172 passed, 10 failed (all pre-existing), 31 skipped
"""


def _check_no_pending_test_summary(content):
    """Returns error if POST_BUNDLE_AUTHORITATIVE is still PENDING."""
    if "POST_BUNDLE_AUTHORITATIVE: PENDING" in content:
        return "python-tests-summary.txt has POST_BUNDLE_AUTHORITATIVE: PENDING — not filled after bundle build"
    if "PENDING (to be updated" in content:
        return "python-tests-summary.txt has unfilled PENDING placeholder"
    return None


def test_correct_summary_passes_check():
    """A summary with filled POST_BUNDLE_AUTHORITATIVE should pass."""
    err = _check_no_pending_test_summary(CORRECT_SUMMARY)
    assert err is None, f"Expected no error but got: {err}"


def test_defective_summary_fails_check():
    """A summary with POST_BUNDLE_AUTHORITATIVE: PENDING should fail."""
    err = _check_no_pending_test_summary(DEFECTIVE_SUMMARY)
    assert err is not None, "Expected error for PENDING POST_BUNDLE_AUTHORITATIVE"


def test_defective_summary_error_is_informative():
    """Error message must mention the POST_BUNDLE_AUTHORITATIVE field."""
    err = _check_no_pending_test_summary(DEFECTIVE_SUMMARY)
    assert "POST_BUNDLE_AUTHORITATIVE" in err, "Error should name the affected field"


def test_r69_actual_summary_not_pending():
    """After Train B repair, actual R69 python-tests-summary.txt must not be PENDING."""
    import pathlib
    f = pathlib.Path(".local/r69-metadata/python-tests-summary.txt")
    if not f.exists():
        pytest.skip("python-tests-summary.txt not present (pre-build)")
    content = f.read_text()
    err = _check_no_pending_test_summary(content)
    assert err is None, f"R69 python-tests-summary.txt still has PENDING: {err}"
