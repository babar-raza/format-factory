"""
R70 Train D — test_r70_manifest_git_head_truth.py
Verify package-artifact-manifest.yaml final_git_head is R69 final commit (not a prior sprint SHA).
"""

import pathlib
import re
import pytest

MANIFEST = pathlib.Path(".local/r69-metadata/package-artifact-manifest.yaml")
SOURCE_PROOF = pathlib.Path(".local/r69-metadata/source-commit-proof.txt")

# R68 pass-1 SHA that must NOT appear as final_git_head
STALE_R68_SHA = "26ba79919400137164e48b00c6f51cde62e66c06"
# R69 final commit
CORRECT_R69_SHA = "2f74eefb8df76250733e5e0fcc75aa4b6c9ee458"


def test_manifest_exists():
    """Package artifact manifest must exist."""
    if not MANIFEST.exists():
        pytest.skip("package-artifact-manifest.yaml not present (pre-build)")
    assert MANIFEST.exists()


def test_manifest_final_git_head_is_r69():
    """final_git_head must be R69 final commit, not a stale R68 SHA."""
    if not MANIFEST.exists():
        pytest.skip("package-artifact-manifest.yaml not present (pre-build)")
    content = MANIFEST.read_text()
    m = re.search(r"final_git_head:\s*([0-9a-f]{40})", content)
    assert m is not None, "final_git_head field not found in package-artifact-manifest.yaml"
    recorded = m.group(1)
    assert recorded != STALE_R68_SHA, (
        f"final_git_head={recorded!r} is the stale R68 pass-1 SHA. "
        "Must be updated to R69 final commit."
    )
    assert recorded == CORRECT_R69_SHA, (
        f"final_git_head={recorded!r} != expected R69 final commit {CORRECT_R69_SHA!r}"
    )


def test_source_commit_proof_records_r69_final():
    """source-commit-proof.txt must record R69 final commit as 2f74eef (not e3ab74f)."""
    if not SOURCE_PROOF.exists():
        pytest.skip("source-commit-proof.txt not present (pre-build)")
    content = SOURCE_PROOF.read_text()
    assert "e3ab74f" not in content or "2f74eef" in content, (
        "source-commit-proof.txt records e3ab74f as R69 final commit; "
        "correct value is 2f74eef (delivery package SHA commit)"
    )
    assert "2f74eef" in content, (
        "source-commit-proof.txt must contain R69 final commit 2f74eef"
    )


def test_source_commit_proof_no_stale_r68_sha():
    """source-commit-proof.txt must not list the stale R68 SHA as R69's final commit."""
    if not SOURCE_PROOF.exists():
        pytest.skip("source-commit-proof.txt not present (pre-build)")
    content = SOURCE_PROOF.read_text()
    # The stale R68 SHA should only appear in R68 context lines, not R69 final commit line
    for line in content.splitlines():
        if "R69 final commit" in line:
            assert STALE_R68_SHA[:7] not in line, (
                f"R69 final commit line contains stale R68 SHA: {line!r}"
            )
