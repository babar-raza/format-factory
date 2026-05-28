"""
R71 Train E — test_r71_manifest_git_head_semantics.py
Verify that package-artifact-manifest.yaml and dotnet-nupkg-manifest.yaml
use the new unambiguous git-head field semantics introduced in R71 Train E.

Prior sprints (R67-R70) used `final_git_head` which was ambiguous:
  - Sometimes it was the HEAD when artifacts were built
  - Sometimes it was the HEAD when the manifest was written
  - Sometimes it was the HEAD of the delivery-seal sprint (not the build sprint)

R71 replaces `final_git_head` with explicit fields:
  - artifact_source_commit: SHA of commit where artifact source code was final
    (the commit from which wheels/nupkgs were actually built; often a prior sprint)
  - artifact_manifest_commit: SHA of commit where this manifest file was last modified
    (set to the current sprint's feat commit)

The builder still records the inner_evidence_git_head in the sidecar (git_head field).
"""

import pathlib
import re
import pytest

LOCAL = pathlib.Path(".local")
R71_META = LOCAL / "r71-metadata"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _load_yaml_simple(path: pathlib.Path) -> dict:
    """Minimal YAML loader for flat key: value lines (no full YAML parser needed)."""
    result = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def test_pam_has_artifact_source_commit():
    """package-artifact-manifest.yaml must have artifact_source_commit field."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present (.local/r71-metadata/ pre-build)")
    data = _load_yaml_simple(pam)
    assert "artifact_source_commit" in data, (
        "package-artifact-manifest.yaml missing 'artifact_source_commit'. "
        "R71 Train E requires explicit artifact source commit (commit that built the artifacts)."
    )


def test_pam_artifact_source_commit_is_valid_sha():
    """artifact_source_commit must be a full 40-char hex SHA."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    data = _load_yaml_simple(pam)
    commit = data.get("artifact_source_commit", "")
    assert SHA_PATTERN.match(commit), (
        f"artifact_source_commit={commit!r} is not a valid 40-char git SHA. "
        "This must be the commit at which the artifact source code was final."
    )


def test_pam_does_not_use_ambiguous_final_git_head():
    """package-artifact-manifest.yaml must NOT use the ambiguous `final_git_head` field.
    R71 Train E replaces this with artifact_source_commit + artifact_manifest_commit."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    content = pam.read_text(encoding="utf-8")
    assert "final_git_head:" not in content, (
        "package-artifact-manifest.yaml still uses 'final_git_head' — "
        "R71 Train E replaces this with 'artifact_source_commit' and 'artifact_manifest_commit'."
    )


def test_pam_has_artifact_manifest_commit_field():
    """package-artifact-manifest.yaml must have artifact_manifest_commit field."""
    pam = R71_META / "package-artifact-manifest.yaml"
    if not pam.exists():
        pytest.skip("R71 PAM not yet present")
    data = _load_yaml_simple(pam)
    assert "artifact_manifest_commit" in data, (
        "package-artifact-manifest.yaml missing 'artifact_manifest_commit'. "
        "This field records when the manifest itself was last modified."
    )


def test_dnm_has_artifact_source_commit():
    """dotnet-nupkg-manifest.yaml must have artifact_source_commit field."""
    dnm = R71_META / "dotnet-nupkg-manifest.yaml"
    if not dnm.exists():
        pytest.skip("R71 DNM not yet present (.local/r71-metadata/ pre-build)")
    data = _load_yaml_simple(dnm)
    assert "artifact_source_commit" in data, (
        "dotnet-nupkg-manifest.yaml missing 'artifact_source_commit'. "
        "R71 Train E requires explicit artifact source commit."
    )


def test_dnm_does_not_use_ambiguous_final_git_head():
    """dotnet-nupkg-manifest.yaml must NOT use the ambiguous `final_git_head` field."""
    dnm = R71_META / "dotnet-nupkg-manifest.yaml"
    if not dnm.exists():
        pytest.skip("R71 DNM not yet present")
    content = dnm.read_text(encoding="utf-8")
    assert "final_git_head:" not in content, (
        "dotnet-nupkg-manifest.yaml still uses 'final_git_head' — "
        "R71 Train E replaces this with 'artifact_source_commit' and 'artifact_manifest_commit'."
    )


def test_pam_artifact_source_commit_matches_dnm():
    """PAM and DNM artifact_source_commit must match (both built from the same source commit)."""
    pam = R71_META / "package-artifact-manifest.yaml"
    dnm = R71_META / "dotnet-nupkg-manifest.yaml"
    if not pam.exists() or not dnm.exists():
        pytest.skip("R71 PAM or DNM not yet present")
    pam_data = _load_yaml_simple(pam)
    dnm_data = _load_yaml_simple(dnm)
    pam_commit = pam_data.get("artifact_source_commit", "")
    dnm_commit = dnm_data.get("artifact_source_commit", "")
    assert pam_commit == dnm_commit, (
        f"PAM artifact_source_commit={pam_commit[:12]}... != "
        f"DNM artifact_source_commit={dnm_commit[:12]}... "
        "Both manifests describe artifacts built from the same source commit."
    )
