"""
R72 Train F — test_r72_requires_failing_test_ledger.py

Verify that a failing-test ledger exists whenever the final verdict claims failed tests.
"All pre-existing" is not acceptable without a ledger that names each failure.

R71 IV-R72-006: Final verdict said "10 failed (all pre-existing)" without naming them.
R71 IV-R72-007: 10 failing tests uninvestigated, unclassified, untaskcarded.
R72 repair: Failing-test ledger must exist and name each failure.
"""
import json
import os
import pathlib
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "reports"


def _find_latest_r7x_failing_ledger():
    """Find the most recent failing-test-ledger.json in reports/r7x/."""
    for run in ["r72", "r71"]:
        j = REPORTS_DIR / run / "failing-test-ledger.json"
        if j.exists():
            return j, run
        m = REPORTS_DIR / run / "failing-test-ledger.md"
        if m.exists():
            return m, run
    return None, None


def _read_latest_verdict(run: str) -> str:
    v = REPORTS_DIR / run / "final-verdict.md"
    if v.exists():
        return v.read_text(encoding="utf-8")
    return ""


def test_failing_test_ledger_exists_for_r72():
    """R72 must have a failing-test-ledger (.md or .json) in reports/r72/."""
    r72_reports = REPORTS_DIR / "r72"
    if not r72_reports.exists():
        pytest.skip("R72 reports directory not yet created")

    ledger_md = r72_reports / "failing-test-ledger.md"
    ledger_json = r72_reports / "failing-test-ledger.json"
    assert ledger_md.exists() or ledger_json.exists(), (
        "R72 must have a failing-test-ledger.md or failing-test-ledger.json. "
        "Every sprint that claims pre-existing failures must name them. "
        "R71 IV-R72-006: R71 verdict had '10 failed all pre-existing' without ledger."
    )


def test_failing_test_ledger_json_has_entries():
    """If failing-test-ledger.json exists, it must list the failing tests."""
    r72_ledger = REPORTS_DIR / "r72" / "failing-test-ledger.json"
    if not r72_ledger.exists():
        pytest.skip("failing-test-ledger.json not yet created")

    ledger = json.loads(r72_ledger.read_text(encoding="utf-8"))
    failures = ledger.get("failures", ledger.get("failing_tests", []))
    assert len(failures) > 0, (
        "failing-test-ledger.json has no entries. "
        "If there are zero failures, the ledger should still exist stating zero failures."
    )


def test_failing_test_ledger_classifies_each_failure():
    """Each entry in the ledger must have a classification."""
    r72_ledger = REPORTS_DIR / "r72" / "failing-test-ledger.json"
    if not r72_ledger.exists():
        pytest.skip("failing-test-ledger.json not yet created")

    ledger = json.loads(r72_ledger.read_text(encoding="utf-8"))
    failures = ledger.get("failures", ledger.get("failing_tests", []))

    valid_classifications = {
        "FIXED_IN_R72",
        "TRUE_PRE_EXISTING_WITH_EVIDENCE",
        "ENVIRONMENT_SPECIFIC",
        "TEST_BUG",
        "PRODUCT_BUG",
        "BLOCKED_BY_EXTERNAL_DEPENDENCY",
    }
    for entry in failures:
        classification = entry.get("classification", entry.get("status", ""))
        assert classification in valid_classifications, (
            f"Failure {entry.get('test_name', entry.get('name', '?'))!r} has "
            f"invalid classification {classification!r}. "
            f"Must be one of: {sorted(valid_classifications)}"
        )


def test_r72_verdict_zero_unnamed_failures():
    """R72 final verdict must not say 'X failed' without a named ledger entry for each."""
    import re
    verdict = _read_latest_verdict("r72")
    if not verdict:
        pytest.skip("R72 final-verdict.md not yet created")

    match = re.search(r"(\d+)\s+failed", verdict)
    if not match:
        return  # No failures mentioned
    n_failed = int(match.group(1))
    if n_failed == 0:
        return  # Zero failures is fine

    # If failures are claimed, the ledger must exist
    r72_ledger_json = REPORTS_DIR / "r72" / "failing-test-ledger.json"
    r72_ledger_md = REPORTS_DIR / "r72" / "failing-test-ledger.md"
    assert r72_ledger_json.exists() or r72_ledger_md.exists(), (
        f"R72 verdict claims {n_failed} failed tests but no failing-test ledger exists. "
        "Every failure must be named, reproduced, and classified."
    )
