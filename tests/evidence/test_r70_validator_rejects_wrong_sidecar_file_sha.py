"""
R70 Train E — test_r70_validator_rejects_wrong_sidecar_file_sha.py
Verify that a delivery manifest with sidecar_sha256 = inner ZIP SHA (not sidecar file SHA)
is detected as a defect.
"""

import json
import pytest

INNER_ZIP_SHA = "3e02c171fe2c188d4331a885eb1abbfa4261e3475d87766c998bd913157fda22"
ACTUAL_SIDECAR_FILE_SHA = "6a08df047d0b841a62b3d995fa6aae40167873629c79dfa471f4e5ddb78a184e"

# Manifest with the R69 IV-R70-001 defect (sidecar_sha256 = inner ZIP SHA)
DEFECTIVE_MANIFEST = {
    "evidence_zip_sha256": INNER_ZIP_SHA,
    "sidecar_sha256": INNER_ZIP_SHA,  # WRONG: same as inner ZIP
    "sidecar_filename": "r69-pass2-final.sha256-proof.json",
}

# Correct manifest
CORRECT_MANIFEST = {
    "evidence_zip_sha256": INNER_ZIP_SHA,
    "sidecar_sha256": ACTUAL_SIDECAR_FILE_SHA,  # CORRECT: actual sidecar file SHA
    "sidecar_filename": "r69-pass2-final.sha256-proof.json",
}


def _check_sidecar_sha_not_same_as_inner_zip(manifest):
    """Returns error if sidecar_sha256 == evidence_zip_sha256."""
    if manifest.get("sidecar_sha256") == manifest.get("evidence_zip_sha256"):
        return "sidecar_sha256 equals evidence_zip_sha256 — sidecar file SHA must differ from inner ZIP SHA"
    return None


def test_correct_manifest_passes_sidecar_check():
    """A manifest with distinct sidecar_sha256 should pass."""
    err = _check_sidecar_sha_not_same_as_inner_zip(CORRECT_MANIFEST)
    assert err is None, f"Expected no error but got: {err}"


def test_defective_manifest_fails_sidecar_check():
    """A manifest where sidecar_sha256 == evidence_zip_sha256 should fail."""
    err = _check_sidecar_sha_not_same_as_inner_zip(DEFECTIVE_MANIFEST)
    assert err is not None, "Expected error for sidecar_sha256 == evidence_zip_sha256"


def test_defective_manifest_error_message_is_informative():
    """Error message must explain the sidecar/inner-zip distinction."""
    err = _check_sidecar_sha_not_same_as_inner_zip(DEFECTIVE_MANIFEST)
    assert "sidecar" in err.lower(), "Error should mention 'sidecar'"
    assert "inner" in err.lower() or "zip" in err.lower(), "Error should mention inner ZIP"


def test_r69_manifest_now_has_correct_sidecar_sha():
    """After Train B repair, the R69 manifest must have the correct sidecar file SHA."""
    import pathlib
    manifest_path = pathlib.Path(".local/r69-delivery-manifest.json")
    if not manifest_path.exists():
        pytest.skip("r69-delivery-manifest.json not present (pre-build)")
    manifest = json.loads(manifest_path.read_bytes())
    sidecar_sha = manifest.get("sidecar_sha256", "")
    evidence_sha = manifest.get("evidence_zip_sha256", "")
    assert sidecar_sha != evidence_sha, (
        "R69 manifest still has sidecar_sha256 == evidence_zip_sha256 (IV-R70-001 not repaired)"
    )
    assert sidecar_sha == ACTUAL_SIDECAR_FILE_SHA, (
        f"R69 manifest sidecar_sha256={sidecar_sha!r} != expected {ACTUAL_SIDECAR_FILE_SHA!r}"
    )
