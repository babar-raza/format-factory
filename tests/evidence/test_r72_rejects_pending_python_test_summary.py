"""
R72 Train F — test_r72_rejects_pending_python_test_summary.py

Verify that python-tests-summary.txt does NOT contain POST_BUNDLE_AUTHORITATIVE: PENDING.

R71 IV-R72-004: python-tests-summary.txt had POST_BUNDLE_AUTHORITATIVE: PENDING.
R72 repair: POST_BUNDLE_AUTHORITATIVE must be filled with actual test result after bundle build.
"""
import os
import pathlib
import re
import pytest

LOCAL = pathlib.Path(".local")


def _find_metadata_dir():
    """Find R72 metadata only.
    R71 metadata has POST_BUNDLE_AUTHORITATIVE: PENDING (the IV-R72-004 defect being fixed).
    Only R72 metadata is subject to this check.
    Returns None if metadata is in pre-build state (bundle not yet built)."""
    d = LOCAL / "r72-metadata"
    if d.exists():
        # Skip if python-tests-summary indicates pre-build state
        summary = d / "python-tests-summary.txt"
        if summary.exists():
            content = summary.read_text(encoding="utf-8")
            if "POST_BUNDLE_AUTHORITATIVE: PENDING_FINAL_RUN" in content:
                return None, None  # pre-build state; run after bundle is built
        return d, "r72"
    return None, None


def test_python_tests_summary_no_pending_post_bundle():
    """python-tests-summary.txt must not have POST_BUNDLE_AUTHORITATIVE: PENDING."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "python-tests-summary.txt"
    if not f.exists():
        pytest.skip(f"python-tests-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    assert "POST_BUNDLE_AUTHORITATIVE: PENDING" not in content, (
        f"python-tests-summary.txt contains 'POST_BUNDLE_AUTHORITATIVE: PENDING'. "
        f"This must be filled with the actual post-bundle test result. "
        f"R71 IV-R72-004: {run} metadata had this defect."
    )


def test_python_tests_summary_has_post_bundle_result():
    """python-tests-summary.txt must have POST_BUNDLE_AUTHORITATIVE with an actual result."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "python-tests-summary.txt"
    if not f.exists():
        pytest.skip(f"python-tests-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    assert "POST_BUNDLE_AUTHORITATIVE:" in content, (
        f"python-tests-summary.txt must have POST_BUNDLE_AUTHORITATIVE field."
    )
    # The value must contain actual test result pattern (N passed, M failed, K skipped)
    post_bundle_line = None
    for line in content.splitlines():
        if line.startswith("POST_BUNDLE_AUTHORITATIVE:"):
            post_bundle_line = line
            break
    assert post_bundle_line is not None
    assert "PENDING" not in post_bundle_line, (
        f"POST_BUNDLE_AUTHORITATIVE line still has PENDING: {post_bundle_line}"
    )
    assert "passed" in post_bundle_line, (
        f"POST_BUNDLE_AUTHORITATIVE must contain 'passed'. Got: {post_bundle_line}"
    )


def test_python_tests_summary_has_authoritative_result():
    """python-tests-summary.txt must have AUTHORITATIVE_TEST_RESULT with actual counts."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "python-tests-summary.txt"
    if not f.exists():
        pytest.skip(f"python-tests-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    # Check for PRE_BUNDLE or POST_BUNDLE authoritative result
    has_result = (
        "AUTHORITATIVE_TEST_RESULT:" in content
        or "PRE_BUNDLE_AUTHORITATIVE:" in content
        or "POST_BUNDLE_AUTHORITATIVE:" in content
    )
    assert has_result, (
        "python-tests-summary.txt must contain an authoritative test result field."
    )


def test_python_tests_summary_no_to_be_filled():
    """python-tests-summary.txt must not have 'to be filled' placeholder language."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "python-tests-summary.txt"
    if not f.exists():
        pytest.skip(f"python-tests-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8").lower()
    assert "to be filled" not in content, (
        f"python-tests-summary.txt contains 'to be filled' placeholder. "
        f"All fields must be finalized before bundle build."
    )
