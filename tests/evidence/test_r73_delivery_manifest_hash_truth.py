"""
R73 Train B — test_r73_delivery_manifest_hash_truth.py

Verify that R73 delivery manifest contains correct SHA truth for all fields.
Extends R72 manifest tests with additional fields added in R73:
  - sidecar_claimed_bundle_sha256
  - delivery_package_sha256_note (new field explaining circular dependency)
"""
import hashlib
import json
import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")
DELIVERY_PACKAGE_NAMES = ["r73-delivery-package.zip", "r72-delivery-package.zip"]


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


def _load_from_package(pkg_path):
    """Extract inner bytes, sidecar, and manifest from delivery package."""
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        manifest_name = next((n for n in names if "manifest" in n.lower() and n.endswith(".json")), None)
        inner_bytes = zf.read(inner_name) if inner_name else None
        sidecar_bytes = zf.read(sidecar_name) if sidecar_name else None
        manifest_bytes = zf.read(manifest_name) if manifest_name else None
    return inner_bytes, sidecar_bytes, manifest_bytes


def test_manifest_evidence_sha_matches_inner_zip():
    """Manifest evidence_zip_sha256 must match actual inner ZIP SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    inner_bytes, _, manifest_bytes = _load_from_package(pkg_path)
    assert inner_bytes and manifest_bytes
    actual = hashlib.sha256(inner_bytes).hexdigest()
    manifest = json.loads(manifest_bytes)
    recorded = manifest.get("evidence_zip_sha256", "")
    assert actual == recorded, f"Manifest evidence SHA mismatch.\nActual: {actual}\nRecorded: {recorded}"


def test_manifest_sidecar_sha_matches_sidecar_file():
    """Manifest sidecar_sha256 must match actual sidecar file SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    _, sidecar_bytes, manifest_bytes = _load_from_package(pkg_path)
    assert sidecar_bytes and manifest_bytes
    actual = hashlib.sha256(sidecar_bytes).hexdigest()
    manifest = json.loads(manifest_bytes)
    recorded = manifest.get("sidecar_sha256", "")
    assert actual == recorded, f"Manifest sidecar SHA mismatch.\nActual: {actual}\nRecorded: {recorded}"


def test_manifest_sha_fields_are_different():
    """evidence_zip_sha256 and sidecar_sha256 in manifest must differ (they are different files)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    _, _, manifest_bytes = _load_from_package(pkg_path)
    assert manifest_bytes
    manifest = json.loads(manifest_bytes)
    ev_sha = manifest.get("evidence_zip_sha256", "")
    sc_sha = manifest.get("sidecar_sha256", "")
    assert ev_sha != sc_sha, (
        f"evidence_zip_sha256 and sidecar_sha256 must differ. Both: {ev_sha}"
    )


def test_manifest_sidecar_claimed_bundle_sha_matches_inner_zip():
    """R73 manifest sidecar_claimed_bundle_sha256 must match actual inner ZIP SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    if "r73" not in pkg_path.name:
        pytest.skip("sidecar_claimed_bundle_sha256 field only required for r73+")
    inner_bytes, _, manifest_bytes = _load_from_package(pkg_path)
    assert inner_bytes and manifest_bytes
    actual = hashlib.sha256(inner_bytes).hexdigest()
    manifest = json.loads(manifest_bytes)
    claimed = manifest.get("sidecar_claimed_bundle_sha256", "")
    assert claimed, "Manifest must have sidecar_claimed_bundle_sha256 field"
    assert actual == claimed, f"Claimed bundle SHA mismatch.\nActual: {actual}\nClaimed: {claimed}"


def test_manifest_has_delivery_package_sha_note():
    """R73 manifest must explain why outer delivery package SHA is not in manifest."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    if "r73" not in pkg_path.name:
        pytest.skip("delivery_package_sha256_note field only required for r73+")
    _, _, manifest_bytes = _load_from_package(pkg_path)
    assert manifest_bytes
    manifest = json.loads(manifest_bytes)
    note = manifest.get("delivery_package_sha256_note", "")
    assert note, "R73 manifest must have delivery_package_sha256_note field"
    # Accept "circular" (R74+ builder) or "self-referential" (R73 builder — pre-fix wording)
    has_explanation = "circular" in note.lower() or "self-referential" in note.lower()
    assert has_explanation, f"Note must explain circular/self-referential dependency. Got: {note[:100]}"


def test_manifest_version_1_1_for_r73():
    """R73 delivery manifest must use version 1.1 (R73 updated format)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    if "r73" not in pkg_path.name:
        pytest.skip("Version 1.1 only required for r73+")
    _, _, manifest_bytes = _load_from_package(pkg_path)
    assert manifest_bytes
    manifest = json.loads(manifest_bytes)
    version = manifest.get("delivery_package_version", "")
    assert version == "1.1", f"R73 manifest must be version 1.1. Got: {version}"
