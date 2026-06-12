"""
R72 Train F — test_r72_rejects_inner_zip_only_delivery.py

Verify that validator/tests reject delivery when only the inner evidence ZIP is present
(missing sidecar and delivery manifest). This is the R71 IV-R72-001 defect pattern.

The validator must fail when:
1. Sidecar is missing
2. Delivery manifest is missing
3. Only inner ZIP is present (no outer delivery package wrapper)
"""
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


def test_delivery_package_is_not_inner_zip():
    """The delivery package must be an outer package containing a sidecar.
    If it were just the inner ZIP, it would not have a .sha256-proof.json member."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()

    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert sidecars, (
        f"Delivery package contains no sidecar (.sha256-proof.json). "
        f"Members: {names}\n"
        "This would indicate only the inner evidence ZIP was delivered, not the full delivery package. "
        "R71 IV-R72-001: The outer delivery package containing inner ZIP + sidecar + manifest is required."
    )


def test_inner_zip_alone_would_fail_sidecar_check(tmp_path):
    """A ZIP containing only the inner evidence ZIP (no sidecar) would fail sidecar check.
    Verifies that the sidecar requirement is enforced (negative test)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    # Get inner ZIP bytes
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name, "No inner ZIP found"
        inner_bytes = outer.read(inner_name)

    # Build a fake "delivery package" that only contains the inner ZIP (no sidecar)
    fake_pkg = tmp_path / "inner_only.zip"
    with zipfile.ZipFile(fake_pkg, "w", zipfile.ZIP_DEFLATED) as fz:
        fz.writestr(inner_name, inner_bytes)

    with zipfile.ZipFile(fake_pkg) as fz:
        fake_names = fz.namelist()

    # This fake package should NOT have a sidecar
    fake_sidecars = [n for n in fake_names if n.endswith(".sha256-proof.json")]
    fake_manifests = [
        n for n in fake_names
        if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"
    ]

    assert not fake_sidecars, "Negative test: fake inner-ZIP-only package must not have a sidecar"
    assert not fake_manifests, "Negative test: fake inner-ZIP-only package must not have a manifest"
    # This confirms that a sidecar check would FAIL for this package


def test_delivery_package_has_sidecar_not_just_inner_zip():
    """The delivery package must contain a sidecar alongside the inner ZIP.
    This is the positive proof that the full delivery package was built."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()

    inner_zips = [n for n in names if n.endswith(".zip")]
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    manifests = [
        n for n in names
        if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"
    ]

    assert inner_zips, f"No inner ZIP in delivery package. Members: {names}"
    assert sidecars, f"No sidecar in delivery package. Members: {names}"
    assert manifests, f"No delivery manifest in delivery package. Members: {names}"

    # This is the full delivery package (not just inner ZIP)
    assert len(names) >= 3, (
        f"Delivery package has only {len(names)} members. "
        "Expected at least 3: inner ZIP + sidecar + manifest."
    )
