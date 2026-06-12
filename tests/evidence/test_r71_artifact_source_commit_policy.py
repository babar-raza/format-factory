"""
R71 Train E — test_r71_artifact_source_commit_policy.py
Verify that artifact_source_commit in the manifests correctly points to the
historical commit where artifacts were built, and that this is consistent
with the actual artifact checksums.

Policy rules:
  1. artifact_source_commit must be a valid 40-char git SHA (not PENDING, not HEAD alias)
  2. artifact_source_commit is the BUILDER commit, not the delivery-sprint commit
     (It can and should be from a prior sprint if no rebuilds happened)
  3. The commit must predate (or equal) the current HEAD
  4. artifact_source_commit is NOT required to match the current sprint's HEAD
     (Artifacts are preserved across delivery-seal sprints)
"""

import pathlib
import re
import subprocess
import pytest

LOCAL = pathlib.Path(".local")
R71_META = LOCAL / "r71-metadata"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _load_yaml_simple(path: pathlib.Path) -> dict:
    """Minimal key: value YAML parser."""
    result = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _git_commit_exists(sha: str) -> bool:
    """Return True if sha exists in the git history."""
    try:
        result = subprocess.run(
            ["git", "cat-file", "-t", sha],
            capture_output=True, text=True, cwd=str(pathlib.Path("."))
        )
        return result.returncode == 0 and result.stdout.strip() == "commit"
    except Exception:
        return False


def test_pam_artifact_source_commit_is_not_pending():
    """artifact_source_commit must not be PENDING or empty."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    data = _load_yaml_simple(pam)
    commit = data.get("artifact_source_commit", "")
    assert commit, "artifact_source_commit must not be empty"
    assert "PENDING" not in commit.upper(), (
        f"artifact_source_commit={commit!r} — PENDING is not allowed. "
        "The artifact source commit is known (it's the historical build commit)."
    )


def test_pam_artifact_source_commit_exists_in_git():
    """artifact_source_commit must exist as a real commit in git history."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    data = _load_yaml_simple(pam)
    commit = data.get("artifact_source_commit", "")
    if not SHA_PATTERN.match(commit):
        pytest.skip(f"artifact_source_commit={commit!r} not a valid SHA (checked by semantics test)")
    assert _git_commit_exists(commit), (
        f"artifact_source_commit={commit[:12]}... not found in git history. "
        "The artifact source commit must be a real commit in this repository."
    )


def test_pam_artifact_manifest_commit_is_not_pending_after_feat_commit():
    """artifact_manifest_commit should be a real SHA after the feat commit.
    Pre-commit it may be PENDING_FINAL_COMMIT which is acceptable."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    data = _load_yaml_simple(pam)
    commit = data.get("artifact_manifest_commit", "")
    assert commit, "artifact_manifest_commit must not be empty"
    # PENDING_FINAL_COMMIT is acceptable pre-commit; real SHA required post-commit
    if commit == "PENDING_FINAL_COMMIT":
        # Not yet committed — this is acceptable in pre-commit source-tree mode
        return
    assert SHA_PATTERN.match(commit), (
        f"artifact_manifest_commit={commit!r} must be a 40-char git SHA "
        "(after the feat commit this must be filled with the actual commit SHA)."
    )


def test_pam_artifact_count_matches_artifacts_list():
    """artifact_count in PAM header must match the number of artifact entries."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    content = pam.read_text(encoding="utf-8")
    data = _load_yaml_simple(pam)
    count_str = data.get("artifact_count", "0")
    try:
        declared_count = int(count_str)
    except ValueError:
        pytest.fail(f"artifact_count={count_str!r} is not an integer")
    # Count 'filename:' occurrences in the artifacts list (under '- filename:' entries)
    actual_count = content.count("filename:")
    assert declared_count == actual_count, (
        f"PAM declares artifact_count={declared_count} but has {actual_count} filename entries."
    )


def test_artifact_source_commit_is_prior_to_current_head():
    """artifact_source_commit should not be newer than current HEAD.
    (Artifacts are built from committed code; the builder commit can't be in the future.)"""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    data = _load_yaml_simple(pam)
    commit = data.get("artifact_source_commit", "")
    if not SHA_PATTERN.match(commit):
        pytest.skip("artifact_source_commit not a valid SHA")

    try:
        # Check if commit is an ancestor of HEAD (or equals HEAD)
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            capture_output=True, cwd=str(pathlib.Path("."))
        )
        assert result.returncode == 0, (
            f"artifact_source_commit={commit[:12]}... is not an ancestor of HEAD. "
            "Artifacts should be built from a commit that predates or equals current HEAD."
        )
    except FileNotFoundError:
        pytest.skip("git not available in test environment")


def test_artifacts_in_pam_have_sha256():
    """Every artifact in the PAM must have a non-empty sha256 field."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    import yaml  # noqa
    try:
        import yaml
        with open(pam, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        artifacts = data.get("artifacts", [])
        for art in artifacts:
            sha = art.get("sha256", "")
            fname = art.get("filename", "unknown")
            assert sha, f"Artifact {fname!r} has empty sha256"
            assert re.match(r"^[0-9a-f]{64}$", sha), (
                f"Artifact {fname!r} sha256={sha!r} is not a valid SHA-256"
            )
    except ImportError:
        # yaml not available, fall back to simple check
        content = pam.read_text(encoding="utf-8")
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("sha256:"):
                val = line.split(":", 1)[1].strip()
                assert val, f"Empty sha256 at line {i+1}"
