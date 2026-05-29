"""
R73 Train B — test_r73_rejects_inner_zip_only_delivery.py

Verify that an inner evidence ZIP alone fails delivery package validation.
A valid delivery package must be an outer ZIP containing inner ZIP + sidecar + manifest.

IV-R73-001: supervisor uploaded inner ZIP only; outer delivery package not used.
"""
import hashlib
import io
import json
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")


def _inner_zip_path():
    for name in ["r73-pass2-final.zip", "r72-pass2-final.zip"]:
        p = LOCAL / name
        if p.exists():
            return p
    return None


def _delivery_package_path():
    for name in ["r73-delivery-package.zip", "r72-delivery-package.zip"]:
        p = LOCAL / name
        if p.exists():
            return p
    return None


def test_inner_zip_missing_sidecar():
    """Inner evidence ZIP has no sidecar as a member — delivery requires outer package."""
    inner = _inner_zip_path()
    if inner is None:
        pytest.skip("No inner ZIP available")
    with zipfile.ZipFile(inner) as zf:
        names = zf.namelist()
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert not sidecars, (
        f"Inner evidence ZIP should NOT contain a sidecar as a member. "
        f"Found: {sidecars}. The sidecar must be in the outer delivery package."
    )


def test_inner_zip_missing_delivery_manifest():
    """Inner evidence ZIP has no delivery manifest — delivery requires outer package."""
    inner = _inner_zip_path()
    if inner is None:
        pytest.skip("No inner ZIP available")
    with zipfile.ZipFile(inner) as zf:
        names = zf.namelist()
    manifests = [n for n in names if n.endswith("-delivery-manifest.json")]
    assert not manifests, (
        f"Inner evidence ZIP should NOT contain a delivery manifest as a member. "
        f"Found: {manifests}. The manifest must be in the outer delivery package."
    )


def test_delivery_package_is_outer_not_inner():
    """Delivery package must be the outer ZIP (contains inner ZIP + sidecar + manifest)."""
    dp = _delivery_package_path()
    if dp is None:
        pytest.skip("No delivery package available")
    with zipfile.ZipFile(dp) as zf:
        names = zf.namelist()
    # Outer package contains inner ZIP as a member
    inner_zips = [n for n in names if n.endswith(".zip")]
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert inner_zips, f"Outer delivery package must contain inner ZIP. Members: {names}"
    assert sidecars, f"Outer delivery package must contain sidecar. Members: {names}"


def test_inner_zip_alone_rejects_validation():
    """Delivery package validation must reject inner ZIP alone (missing sidecar in members)."""
    inner = _inner_zip_path()
    dp = _delivery_package_path()
    if inner is None or dp is None:
        pytest.skip("Need both inner ZIP and delivery package")

    # Simulate: check if inner ZIP alone would pass delivery package validation
    with zipfile.ZipFile(inner) as zf:
        inner_names = zf.namelist()

    # Inner ZIP has no sidecar as member — delivery package validation would fail
    sidecars_in_inner = [n for n in inner_names if n.endswith(".sha256-proof.json")]
    manifests_in_inner = [n for n in inner_names if n.endswith("-delivery-manifest.json")]

    assert not sidecars_in_inner, "Inner ZIP must not contain sidecar"
    assert not manifests_in_inner, "Inner ZIP must not contain delivery manifest"
    # Therefore delivery package validation (which checks for sidecar presence) would reject it
    # This test confirms the structural gap that makes inner-ZIP-only uploads detectable


def test_outer_delivery_package_sha_differs_from_inner_zip_sha():
    """Outer delivery package SHA must differ from inner ZIP SHA (they are different files)."""
    inner = _inner_zip_path()
    dp = _delivery_package_path()
    if inner is None or dp is None:
        pytest.skip("Need both inner ZIP and delivery package")

    inner_sha = hashlib.sha256(inner.read_bytes()).hexdigest()
    dp_sha = hashlib.sha256(dp.read_bytes()).hexdigest()

    assert inner_sha != dp_sha, (
        "Outer delivery package SHA and inner ZIP SHA must differ. "
        "If they match, the wrong file is being used as the delivery package."
    )
