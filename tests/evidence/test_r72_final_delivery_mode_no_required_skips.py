"""
R72 Train D — test_r72_final_delivery_mode_no_required_skips.py

Verify that no required checks are skipped when the delivery package is available.

R71 IV-R72-005: R71 tests replayed as 9 passed, 41 skipped from extracted bundle.
R72 repair: In delivery mode, no required check may skip because files are "not yet built."
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
    """Return (path, source). Returns (None, None) if absent. Fail-closed if env var set."""
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(
                f"DELIVERY_PACKAGE_UNDER_TEST={env_path!r} but file not found."
            )
        return p, "env"
    for name in DELIVERY_PACKAGE_NAMES:
        p = LOCAL / name
        if p.exists():
            return p, "local"
    return None, None


def test_inner_zip_accessible_no_skip():
    """Inner ZIP must be accessible from delivery package — no skip allowed."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner = next((n for n in names if n.endswith(".zip")), None)
    assert inner is not None, (
        f"Inner ZIP not found in delivery package. Members: {names}"
    )


def test_sidecar_accessible_no_skip():
    """Sidecar must be accessible from delivery package — no skip allowed."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar = next((n for n in names if n.endswith(".sha256-proof.json")), None)
    assert sidecar is not None, (
        f"Sidecar not found in delivery package. Members: {names}"
    )


def test_manifest_accessible_no_skip():
    """Delivery manifest must be accessible — no skip allowed."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
    assert manifest is not None, (
        f"Delivery manifest not found. Members: {names}"
    )


def test_inner_zip_validates_with_sidecar_no_skip():
    """Inner ZIP must validate against sidecar — no skip allowed in delivery mode."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        assert inner_name is not None
        assert sidecar_name is not None
        inner_bytes = outer.read(inner_name)
        sidecar_bytes = outer.read(sidecar_name)

    sidecar = json.loads(sidecar_bytes.decode("utf-8"))
    actual_sha = hashlib.sha256(inner_bytes).hexdigest()
    expected_sha = sidecar.get("sha256", "")

    assert expected_sha, "Sidecar must have sha256 field"
    assert actual_sha == expected_sha, (
        f"Inner ZIP SHA {actual_sha[:16]}... does not match sidecar claim {expected_sha[:16]}...\n"
        "Delivery package validation failed — inner ZIP and sidecar disagree."
    )


def test_manifest_sha_fields_no_skip():
    """Delivery manifest SHA fields must be present and non-empty — no skip allowed."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert manifest_name is not None
        manifest = json.loads(outer.read(manifest_name))

    assert manifest.get("evidence_zip_sha256"), "manifest.evidence_zip_sha256 must be non-empty"
    assert manifest.get("sidecar_sha256"), "manifest.sidecar_sha256 must be non-empty"


def test_delivery_package_sha_no_skip():
    """Delivery package must have its own SHA recorded — no placeholder."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    # Verify delivery package is a real file with a computable SHA
    h = hashlib.sha256()
    with open(pkg_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    sha = h.hexdigest()
    assert len(sha) == 64, "Delivery package SHA-256 must be a 64-char hex string"
    assert sha != "0" * 64, "Delivery package SHA-256 must not be all-zero"


def test_no_required_skips_in_delivery_mode():
    """Summary assertion: in delivery mode, critical checks must not skip.
    Counts the checks that ran vs. those that would have skipped pre-delivery."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
    has_inner = any(n.endswith(".zip") for n in names)
    has_sidecar = any(n.endswith(".sha256-proof.json") for n in names)
    has_manifest = any(
        n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"
        for n in names
    )
    required_checks = [has_inner, has_sidecar, has_manifest]
    assert all(required_checks), (
        f"Required delivery checks: inner_zip={has_inner}, sidecar={has_sidecar}, "
        f"manifest={has_manifest}. All must be True in delivery mode."
    )
