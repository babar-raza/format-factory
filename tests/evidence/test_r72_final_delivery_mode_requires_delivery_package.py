"""
R72 Train D — test_r72_final_delivery_mode_requires_delivery_package.py

Verify that final-delivery mode requires a delivery package and is fail-closed
when DELIVERY_PACKAGE_UNDER_TEST is set but the file is missing.

R71 IV-R72-005 defect: R71 evidence tests replayed as 41 skipped from extracted bundle.
R72 repair: Delivery mode tests must not skip required checks when package is present.
"""
import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")
DELIVERY_PACKAGE_NAMES = ["r72-delivery-package.zip", "r71-delivery-package.zip"]


def _get_delivery_package() -> tuple:
    """Return (path, source) — source is 'env' or 'local'. Returns (None, None) if absent."""
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(
                f"DELIVERY_PACKAGE_UNDER_TEST={env_path!r} but file not found. "
                "Delivery-mode tests are fail-closed when the env var is set."
            )
        return p, "env"
    for name in DELIVERY_PACKAGE_NAMES:
        p = LOCAL / name
        if p.exists():
            return p, "local"
    return None, None


def test_env_var_respected():
    """DELIVERY_PACKAGE_UNDER_TEST must be respected — fail-closed if set and file absent."""
    env_val = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if not env_val:
        pytest.skip("DELIVERY_PACKAGE_UNDER_TEST not set — pre-delivery mode")
    p = pathlib.Path(env_val)
    assert p.exists(), (
        f"DELIVERY_PACKAGE_UNDER_TEST={env_val!r} is set but the file does not exist. "
        "Delivery mode is fail-closed — cannot proceed without the delivery package."
    )


def test_delivery_package_is_outer_zip():
    """When delivery package is available, it must be a valid ZIP (outer package)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    assert zipfile.is_zipfile(str(pkg_path)), f"{pkg_path} must be a valid ZIP file"


def test_delivery_package_has_three_required_members():
    """Delivery package must contain inner ZIP + sidecar + delivery manifest."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    inner_zips = [n for n in names if n.endswith(".zip")]
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    manifests = [n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"]
    assert len(inner_zips) >= 1, f"No inner ZIP found. Package members: {names}"
    assert len(sidecars) >= 1, f"No sidecar found. Package members: {names}"
    assert len(manifests) >= 1, f"No delivery manifest found. Package members: {names}"


def test_delivery_package_requires_delivery_not_inner_zip():
    """Delivery package must be the outer package, not the inner evidence ZIP directly.
    The inner ZIP must be nested inside the outer package."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    # A delivery package contains entries (inner ZIP as a member, sidecar, manifest)
    # An inner ZIP alone would not have a sidecar as a member
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert len(sidecars) >= 1, (
        f"No sidecar found in delivery package. If only inner ZIP was delivered "
        f"(not the outer delivery package), this test would fail. Package members: {names}"
    )


def test_local_fallback_picks_r72_before_r71():
    """Local fallback must prefer r72 over r71 delivery package."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available")
    if source != "local":
        pytest.skip("Not using local fallback — env var is set")
    # If both r72 and r71 exist, r72 should be picked
    r72 = LOCAL / "r72-delivery-package.zip"
    r71 = LOCAL / "r71-delivery-package.zip"
    if r72.exists() and r71.exists():
        assert pkg_path == r72, f"Should prefer r72 over r71, got {pkg_path}"
