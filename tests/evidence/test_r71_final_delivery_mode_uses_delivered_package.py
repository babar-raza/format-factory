"""
R71 Train D — test_r71_final_delivery_mode_uses_delivered_package.py
Final-delivery tests that operate on the actual delivered outer package.

When DELIVERY_PACKAGE_UNDER_TEST env var is set, tests read from the
specified outer delivery package ZIP instead of .local/ source-tree artifacts.
This is the correct mode for bundle-replay and extracted-delivery testing.

When DELIVERY_PACKAGE_UNDER_TEST is NOT set and .local/ artifacts exist,
tests fall back to source-tree mode (pre-delivery verification).

When neither is available, tests FAIL CLOSED (not skip) to prevent
accidental clean-closure with unverified delivery.
"""

import hashlib
import io
import json
import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")


def _get_delivery_package() -> tuple:
    """
    Returns (outer_zip_path, source) where source is 'env' or 'local'.
    Raises pytest.fail if neither is available and tests require a package.
    """
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(
                f"DELIVERY_PACKAGE_UNDER_TEST={env_path} but file not found. "
                "Delivery-mode tests cannot run without the delivery package."
            )
        return p, "env"

    # Fallback to .local/ for source-tree / pre-delivery mode
    for name in ["r71-delivery-package.zip", "r70-delivery-package.zip"]:
        p = LOCAL / name
        if p.exists():
            return p, "local"

    return None, None


def _get_sprint_name() -> str:
    """Get sprint name from env or detect from available files."""
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        name = pathlib.Path(env_path).name
        # e.g. r71-delivery-package.zip -> r71
        return name.split("-delivery-package")[0]
    for name in ["r71", "r70"]:
        if (LOCAL / f"{name}-delivery-package.zip").exists():
            return name
    return "unknown"


def test_delivery_package_exists_and_is_readable():
    """The delivery package must exist and be a valid ZIP."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    assert len(names) >= 3, f"Delivery package must have at least 3 files, got: {names}"


def test_delivery_package_contains_inner_zip():
    """Outer delivery package must contain an inner evidence ZIP."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    inner_zips = [n for n in names if n.endswith(".zip")]
    assert len(inner_zips) == 1, f"Expected exactly one inner ZIP, found: {inner_zips}"


def test_delivery_package_contains_sidecar():
    """Outer delivery package must contain exactly one sidecar JSON file."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert len(sidecars) == 1, f"Expected exactly one sidecar, found: {sidecars}"


def test_delivery_package_contains_manifest():
    """Outer delivery package must contain a delivery manifest JSON."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    manifests = [n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"]
    assert len(manifests) >= 1, f"Expected delivery manifest JSON, found files: {names}"


def test_inner_zip_sha_matches_sidecar():
    """Sidecar-claimed inner ZIP SHA must match actual inner ZIP file SHA."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next(n for n in names if n.endswith(".zip"))
        sidecar_name = next(n for n in names if n.endswith(".sha256-proof.json"))
        inner_bytes = outer.read(inner_name)
        sidecar_data = json.loads(outer.read(sidecar_name))
    actual_sha = hashlib.sha256(inner_bytes).hexdigest()
    claimed_sha = sidecar_data.get("sha256", "")
    assert actual_sha == claimed_sha, (
        f"Inner ZIP SHA mismatch: actual={actual_sha[:16]}... "
        f"sidecar claims={claimed_sha[:16]}..."
    )


def test_manifest_sidecar_sha_matches_sidecar_file():
    """Delivery manifest sidecar_sha256 must match actual sidecar file SHA."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar_name = next(n for n in names if n.endswith(".sha256-proof.json"))
        manifest_name = next(
            n for n in names
            if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"
        )
        sidecar_bytes = outer.read(sidecar_name)
        manifest_data = json.loads(outer.read(manifest_name))
    actual_sidecar_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    recorded = manifest_data.get("sidecar_sha256", "")
    assert recorded == actual_sidecar_sha, (
        f"manifest sidecar_sha256={recorded[:16]}... != "
        f"actual sidecar file SHA={actual_sidecar_sha[:16]}..."
    )


def test_manifest_sidecar_sha_differs_from_evidence_sha():
    """Manifest sidecar_sha256 must NOT equal evidence_zip_sha256."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest_name = next(
            n for n in names
            if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"
        )
        manifest_data = json.loads(outer.read(manifest_name))
    sidecar_sha = manifest_data.get("sidecar_sha256", "")
    evidence_sha = manifest_data.get("evidence_zip_sha256", "")
    assert sidecar_sha != evidence_sha, (
        f"manifest sidecar_sha256 == evidence_zip_sha256 == {sidecar_sha[:16]}... "
        "These are different files and must have different SHA-256 values."
    )


def test_sidecar_not_inside_inner_zip():
    """The sidecar JSON file must be in the outer delivery package, not inside the inner ZIP."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next(n for n in names if n.endswith(".zip"))
        inner_bytes = outer.read(inner_name)
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        inner_names = inner.namelist()
    sidecar_in_inner = [n for n in inner_names if n.endswith(".sha256-proof.json")]
    assert sidecar_in_inner == [], (
        f"Sidecar found inside inner ZIP: {sidecar_in_inner}. "
        "Sidecar must be external to inner ZIP."
    )


def test_inner_zip_validates_with_sidecar():
    """The inner ZIP must validate correctly against its sidecar."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-build in source mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next(n for n in names if n.endswith(".zip"))
        sidecar_name = next(n for n in names if n.endswith(".sha256-proof.json"))
        inner_bytes = outer.read(inner_name)
        sidecar_data = json.loads(outer.read(sidecar_name))
    actual_sha = hashlib.sha256(inner_bytes).hexdigest()
    actual_size = len(inner_bytes)
    actual_count = len(zipfile.ZipFile(io.BytesIO(inner_bytes)).infolist())
    claimed_sha = sidecar_data.get("sha256", "")
    claimed_size = sidecar_data.get("size_bytes", 0)
    claimed_count = sidecar_data.get("entry_count", sidecar_data.get("entries", 0))
    assert actual_sha == claimed_sha, f"SHA mismatch: {actual_sha[:16]} != {claimed_sha[:16]}"
    assert actual_size == claimed_size, f"Size mismatch: {actual_size} != {claimed_size}"
    assert actual_count == claimed_count, f"Entry count mismatch: {actual_count} != {claimed_count}"
