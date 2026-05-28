"""
R72 Train D — test_r72_sidecar_file_sha_vs_bundle_sha.py

Verify the distinction between:
  - sidecar file SHA (SHA of the .sha256-proof.json file itself)
  - sidecar-claimed bundle SHA (the sha256 field inside the sidecar JSON = inner ZIP SHA)

These are two different values. Conflating them is the R70 IV-R70-001 defect.

Per the R71 layered proof model:
  - Layer 1: Inner ZIP = source + reports + inner validation
  - Layer 2: Sidecar (.sha256-proof.json) proves the inner ZIP (sidecar.sha256 = inner ZIP SHA)
  - Layer 3: Delivery manifest records sidecar_sha256 = SHA of sidecar FILE itself
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


def test_sidecar_file_sha_differs_from_sidecar_claimed_bundle_sha():
    """The SHA-256 of the sidecar FILE must differ from the sha256 field inside the sidecar.
    sidecar FILE sha = SHA of the JSON bytes.
    sidecar JSON sha256 field = SHA of the inner evidence ZIP.
    These are two different files with two different SHAs."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        assert sidecar_name is not None, f"No sidecar found. Members: {names}"
        sidecar_bytes = outer.read(sidecar_name)

    sidecar_file_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    sidecar_json = json.loads(sidecar_bytes.decode("utf-8"))
    sidecar_claimed_bundle_sha = sidecar_json.get("sha256", "")

    assert sidecar_claimed_bundle_sha, "Sidecar JSON must have 'sha256' field"
    assert sidecar_file_sha != sidecar_claimed_bundle_sha, (
        f"Sidecar file SHA ({sidecar_file_sha[:16]}...) == "
        f"sidecar-claimed bundle SHA ({sidecar_claimed_bundle_sha[:16]}...)\n"
        "These must differ:\n"
        "  - sidecar file SHA = SHA of the .sha256-proof.json file itself\n"
        "  - sidecar json sha256 = SHA of the inner evidence ZIP\n"
        "Conflating these is the R70 IV-R70-001 defect pattern."
    )


def test_sidecar_claimed_bundle_sha_matches_inner_zip():
    """Sidecar JSON sha256 field must match the actual inner ZIP SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        assert inner_name is not None, f"No inner ZIP. Members: {names}"
        assert sidecar_name is not None, f"No sidecar. Members: {names}"
        inner_bytes = outer.read(inner_name)
        sidecar_bytes = outer.read(sidecar_name)

    sidecar_json = json.loads(sidecar_bytes.decode("utf-8"))
    claimed_sha = sidecar_json.get("sha256", "")
    actual_sha = hashlib.sha256(inner_bytes).hexdigest()

    assert claimed_sha == actual_sha, (
        f"Sidecar claims inner ZIP SHA={claimed_sha[:16]}... "
        f"but actual inner ZIP SHA={actual_sha[:16]}...\n"
        "Sidecar must prove the inner evidence ZIP."
    )


def test_manifest_uses_sidecar_file_sha_not_bundle_sha():
    """manifest.sidecar_sha256 must be the sidecar FILE sha, not the bundle sha.
    The delivery manifest records the SHA of the sidecar JSON file (Layer 2 artifact)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert sidecar_name is not None
        assert manifest_name is not None
        sidecar_bytes = outer.read(sidecar_name)
        manifest = json.loads(outer.read(manifest_name))

    sidecar_file_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    manifest_sidecar_sha = manifest.get("sidecar_sha256", "")

    assert manifest_sidecar_sha == sidecar_file_sha, (
        f"manifest.sidecar_sha256={manifest_sidecar_sha[:16]}... "
        f"!= sidecar file SHA={sidecar_file_sha[:16]}...\n"
        "The manifest must record the SHA of the sidecar FILE, not the inner ZIP."
    )


def test_manifest_evidence_sha_is_not_sidecar_file_sha():
    """manifest.evidence_zip_sha256 must NOT equal the sidecar file SHA.
    evidence_zip_sha256 is the inner ZIP SHA; sidecar file SHA is the sidecar SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert sidecar_name is not None
        assert manifest_name is not None
        sidecar_bytes = outer.read(sidecar_name)
        manifest = json.loads(outer.read(manifest_name))

    sidecar_file_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    evidence_sha = manifest.get("evidence_zip_sha256", "")

    assert evidence_sha != sidecar_file_sha, (
        "manifest.evidence_zip_sha256 should be the inner ZIP SHA, not the sidecar file SHA."
    )
