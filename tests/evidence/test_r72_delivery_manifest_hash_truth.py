"""
R72 Train D — test_r72_delivery_manifest_hash_truth.py

Verify delivery manifest hash fields are truthful:
- evidence_zip_sha256 must match actual inner ZIP SHA
- sidecar_sha256 must match actual sidecar file SHA
- These two values must differ (R70 IV-R70-001 pattern)

R71 IV-R72-002: delivery-package-validation-summary.txt had PENDING_PASS_2_SHA.
R72 repair: All manifest SHA fields must be actual computed values.
"""
import hashlib
import json
import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")
DELIVERY_PACKAGE_NAMES = ["r72-delivery-package.zip", "r71-delivery-package.zip"]


def _get_delivery_package() -> tuple:
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(f"DELIVERY_PACKAGE_UNDER_TEST={env_path!r} not found.")
        return p, "env"
    for name in DELIVERY_PACKAGE_NAMES:
        p = LOCAL / name
        if p.exists():
            return p, "local"
    return None, None


def _load_package_members(pkg_path: pathlib.Path) -> dict:
    """Return dict of {role: (name, bytes)} for inner_zip, sidecar, manifest."""
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        result = {}
        if inner_name:
            result["inner_zip"] = (inner_name, outer.read(inner_name))
        if sidecar_name:
            result["sidecar"] = (sidecar_name, outer.read(sidecar_name))
        if manifest_name:
            result["manifest"] = (manifest_name, outer.read(manifest_name))
    return result


def test_manifest_evidence_sha_matches_inner_zip():
    """manifest.evidence_zip_sha256 must equal the actual SHA-256 of the inner ZIP."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    members = _load_package_members(pkg_path)
    assert "inner_zip" in members, "No inner ZIP found in delivery package"
    assert "manifest" in members, "No delivery manifest found in delivery package"

    inner_bytes = members["inner_zip"][1]
    manifest = json.loads(members["manifest"][1])

    actual_sha = hashlib.sha256(inner_bytes).hexdigest()
    recorded_sha = manifest.get("evidence_zip_sha256", "")

    assert recorded_sha, "manifest.evidence_zip_sha256 must not be empty"
    assert actual_sha == recorded_sha, (
        f"manifest.evidence_zip_sha256={recorded_sha[:16]}... "
        f"!= actual inner ZIP SHA {actual_sha[:16]}...\n"
        "The delivery manifest hash truth check failed."
    )


def test_manifest_sidecar_sha_matches_sidecar_file():
    """manifest.sidecar_sha256 must equal the actual SHA-256 of the sidecar file.
    Per R70 lesson: sidecar_sha256 = SHA of .sha256-proof.json, NOT the inner ZIP SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    members = _load_package_members(pkg_path)
    assert "sidecar" in members, "No sidecar found in delivery package"
    assert "manifest" in members, "No delivery manifest found in delivery package"

    sidecar_bytes = members["sidecar"][1]
    manifest = json.loads(members["manifest"][1])

    actual_sidecar_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    recorded_sidecar_sha = manifest.get("sidecar_sha256", "")

    assert recorded_sidecar_sha, "manifest.sidecar_sha256 must not be empty"
    assert actual_sidecar_sha == recorded_sidecar_sha, (
        f"manifest.sidecar_sha256={recorded_sidecar_sha[:16]}... "
        f"!= actual sidecar file SHA {actual_sidecar_sha[:16]}...\n"
        "manifest.sidecar_sha256 must be the SHA of the sidecar JSON file, not the inner ZIP."
    )


def test_manifest_sha_fields_are_different():
    """evidence_zip_sha256 and sidecar_sha256 must differ — they are different files.
    Equal values indicate the R70 IV-R70-001 defect: sidecar_sha256 was set to inner ZIP SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    members = _load_package_members(pkg_path)
    assert "manifest" in members, "No delivery manifest found in delivery package"
    manifest = json.loads(members["manifest"][1])

    evidence_sha = manifest.get("evidence_zip_sha256", "")
    sidecar_sha = manifest.get("sidecar_sha256", "")
    assert evidence_sha != sidecar_sha, (
        f"manifest.evidence_zip_sha256 == manifest.sidecar_sha256 == {evidence_sha[:16]}...\n"
        "These are SHAs of different files and MUST differ. "
        "Equal values indicate the R70 IV-R70-001 defect pattern."
    )


def test_manifest_sha_fields_are_64char_hex():
    """Both manifest SHA fields must be valid 64-char SHA-256 hex strings."""
    import re
    hex64 = re.compile(r"^[0-9a-f]{64}$")
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    members = _load_package_members(pkg_path)
    assert "manifest" in members
    manifest = json.loads(members["manifest"][1])

    evidence_sha = manifest.get("evidence_zip_sha256", "")
    sidecar_sha = manifest.get("sidecar_sha256", "")
    assert hex64.match(evidence_sha), f"evidence_zip_sha256={evidence_sha!r} is not valid SHA-256 hex"
    assert hex64.match(sidecar_sha), f"sidecar_sha256={sidecar_sha!r} is not valid SHA-256 hex"


def test_manifest_git_head_present():
    """Delivery manifest must include git_head field."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    members = _load_package_members(pkg_path)
    assert "manifest" in members
    manifest = json.loads(members["manifest"][1])
    assert manifest.get("git_head"), "manifest must have non-empty git_head field"
