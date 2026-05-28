"""
R71 Train B — test_r71_delivery_manifest_authority.py
Verify delivery manifest authority rules are enforced.

Delivery manifest is the authority for:
  - evidence_zip_sha256: inner ZIP SHA (must match inner ZIP file)
  - sidecar_sha256: sidecar FILE SHA (must differ from evidence_zip_sha256)
  - sidecar_claimed_sha: the SHA the sidecar records for the inner ZIP (= evidence_zip_sha256)
"""

import hashlib
import json
import pathlib
import pytest

LOCAL = pathlib.Path(".local")

INNER_ZIP_SHA = "1e600e73ab16b9917dd5476e3769e93669da75d7a780265310bde1b5f4984c64"
SIDECAR_FILE_SHA = "671f4f45b6593756fc72e5145d095a1399d1087bc186d839a3c992e297fcee0b"
OUTER_PKG_SHA = "0e6016b876863fe40b1ac9f69f11a2813e609b53a0f0fd285fab95ea51a7ec97"


def _check_manifest_authority(manifest: dict) -> list:
    """Check delivery manifest authority rules. Returns list of error strings."""
    errors = []
    evidence_sha = manifest.get("evidence_zip_sha256", "")
    sidecar_sha = manifest.get("sidecar_sha256", "")

    if not evidence_sha:
        errors.append("evidence_zip_sha256 missing from delivery manifest")
    if not sidecar_sha:
        errors.append("sidecar_sha256 missing from delivery manifest")

    if evidence_sha and sidecar_sha:
        if evidence_sha == sidecar_sha:
            errors.append(
                f"sidecar_sha256 == evidence_zip_sha256 == {evidence_sha[:16]}... "
                "These must be different: sidecar_sha256 = SHA of sidecar file, "
                "evidence_zip_sha256 = SHA of inner ZIP file."
            )

    return errors


def test_r70_manifest_sidecar_sha_differs_from_evidence_sha():
    """R70 delivery manifest must have sidecar_sha256 != evidence_zip_sha256."""
    manifest_path = LOCAL / "r70-delivery-manifest.json"
    if not manifest_path.exists():
        pytest.skip("r70-delivery-manifest.json not present (pre-build)")
    manifest = json.loads(manifest_path.read_bytes())
    errors = _check_manifest_authority(manifest)
    assert errors == [], f"R70 manifest authority violations: {errors}"


def test_r70_manifest_evidence_sha_matches_inner_zip():
    """R70 delivery manifest evidence_zip_sha256 must match actual inner ZIP."""
    manifest_path = LOCAL / "r70-delivery-manifest.json"
    inner_path = LOCAL / "r70-pass2-final.zip"
    if not manifest_path.exists() or not inner_path.exists():
        pytest.skip("Delivery artifacts not present")
    manifest = json.loads(manifest_path.read_bytes())
    actual_sha = hashlib.sha256(inner_path.read_bytes()).hexdigest()
    recorded = manifest.get("evidence_zip_sha256", "")
    assert recorded == actual_sha, f"evidence_zip_sha256={recorded} != actual={actual_sha}"


def test_r70_manifest_sidecar_sha_matches_sidecar_file():
    """R70 delivery manifest sidecar_sha256 must match actual sidecar file."""
    manifest_path = LOCAL / "r70-delivery-manifest.json"
    sidecar_path = LOCAL / "r70-pass2-final.sha256-proof.json"
    if not manifest_path.exists() or not sidecar_path.exists():
        pytest.skip("Delivery artifacts not present")
    manifest = json.loads(manifest_path.read_bytes())
    actual_sha = hashlib.sha256(sidecar_path.read_bytes()).hexdigest()
    recorded = manifest.get("sidecar_sha256", "")
    assert recorded == actual_sha, f"sidecar_sha256={recorded} != actual sidecar file SHA={actual_sha}"


def test_manifest_with_equal_shas_fails_check():
    """A manifest where sidecar_sha256 == evidence_zip_sha256 must fail authority check."""
    bad_manifest = {
        "evidence_zip_sha256": INNER_ZIP_SHA,
        "sidecar_sha256": INNER_ZIP_SHA,  # wrong — both same
    }
    errors = _check_manifest_authority(bad_manifest)
    assert len(errors) > 0, "Expected error for equal SHA fields"
    assert any("differ" in e.lower() or "different" in e.lower() or "==" in e for e in errors)


def test_manifest_with_distinct_shas_passes_check():
    """A manifest with distinct sidecar_sha256 and evidence_zip_sha256 must pass."""
    good_manifest = {
        "evidence_zip_sha256": INNER_ZIP_SHA,
        "sidecar_sha256": SIDECAR_FILE_SHA,
    }
    errors = _check_manifest_authority(good_manifest)
    assert errors == [], f"Expected no errors but got: {errors}"


def test_delivery_manifest_does_not_need_outer_package_sha():
    """Delivery manifest may omit outer delivery package SHA — it is external."""
    # The delivery manifest's job is sidecar + inner ZIP facts.
    # Outer package SHA is optional (computed after manifest is generated).
    manifest_path = LOCAL / "r70-delivery-manifest.json"
    if not manifest_path.exists():
        pytest.skip("r70-delivery-manifest.json not present")
    manifest = json.loads(manifest_path.read_bytes())
    # Just verify the authority fields are correct
    errors = _check_manifest_authority(manifest)
    assert errors == [], f"Manifest authority violations: {errors}"
