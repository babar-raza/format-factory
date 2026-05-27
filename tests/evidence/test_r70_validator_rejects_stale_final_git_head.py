"""
R70 Train E — test_r70_validator_rejects_stale_final_git_head.py
Verify that package-artifact-manifest.yaml with stale final_git_head (R68 SHA)
is detected, and that the correct R69 SHA is required.
"""

import re
import pytest

STALE_R68_SHA = "26ba79919400137164e48b00c6f51cde62e66c06"
CORRECT_R69_SHA = "2f74eefb8df76250733e5e0fcc75aa4b6c9ee458"

DEFECTIVE_MANIFEST = f"""
artifact_count: 22
artifact_source_commit: 8c79f05c6d1cde6424d09edd0d136afc10f08ee8
final_git_head: {STALE_R68_SHA}
run: r69
"""

CORRECT_MANIFEST = f"""
artifact_count: 22
artifact_source_commit: 8c79f05c6d1cde6424d09edd0d136afc10f08ee8
final_git_head: {CORRECT_R69_SHA}
run: r69
"""


def _check_final_git_head(content, expected_sha):
    """Returns error if final_git_head is not the expected SHA."""
    m = re.search(r"final_git_head:\s*([0-9a-f]{40})", content)
    if not m:
        return "final_git_head field not found"
    if m.group(1) == STALE_R68_SHA:
        return f"final_git_head is stale R68 SHA {STALE_R68_SHA!r} — must be R69 final {expected_sha!r}"
    if m.group(1) != expected_sha:
        return f"final_git_head={m.group(1)!r} != expected {expected_sha!r}"
    return None


def test_correct_manifest_passes_git_head_check():
    """A manifest with correct R69 final_git_head should pass."""
    err = _check_final_git_head(CORRECT_MANIFEST, CORRECT_R69_SHA)
    assert err is None, f"Expected no error but got: {err}"


def test_defective_manifest_fails_git_head_check():
    """A manifest with stale R68 final_git_head should fail."""
    err = _check_final_git_head(DEFECTIVE_MANIFEST, CORRECT_R69_SHA)
    assert err is not None, "Expected error for stale final_git_head"


def test_stale_sha_detected_in_error_message():
    """Error message must name the stale SHA."""
    err = _check_final_git_head(DEFECTIVE_MANIFEST, CORRECT_R69_SHA)
    assert STALE_R68_SHA in err or "stale" in err.lower(), \
        "Error should identify the stale SHA"


def test_r69_manifest_now_has_correct_git_head():
    """After Train C repair, actual R69 package-artifact-manifest.yaml must be correct."""
    import pathlib
    f = pathlib.Path(".local/r69-metadata/package-artifact-manifest.yaml")
    if not f.exists():
        pytest.skip("package-artifact-manifest.yaml not present (pre-build)")
    content = f.read_text()
    err = _check_final_git_head(content, CORRECT_R69_SHA)
    assert err is None, f"R69 package-artifact-manifest.yaml still has stale git_head: {err}"
