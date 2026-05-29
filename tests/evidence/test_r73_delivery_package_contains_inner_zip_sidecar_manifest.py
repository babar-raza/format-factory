"""
R73 Train B — test_r73_delivery_package_contains_inner_zip_sidecar_manifest.py

Verify that the R73 delivery package (or any current delivery package) contains:
  - inner evidence ZIP
  - sidecar JSON
  - delivery manifest
  - supervisor-readme (R73 addition)

IV-R73-002 fix: supervisor-readme.md must now be physically present in delivery package.
"""
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


def test_delivery_package_contains_inner_zip():
    """Delivery package must contain an inner evidence ZIP."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    inner_zips = [n for n in names if n.endswith(".zip")]
    assert inner_zips, f"No inner ZIP found. Package members: {names}"


def test_delivery_package_contains_sidecar():
    """Delivery package must contain sidecar JSON."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert sidecars, f"No sidecar JSON found. Package members: {names}"


def test_delivery_package_contains_manifest():
    """Delivery package must contain a delivery manifest JSON."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    manifests = [n for n in names if "manifest" in n.lower() and n.endswith(".json")]
    assert manifests, f"No delivery manifest JSON found. Package members: {names}"


def test_delivery_package_contains_supervisor_readme():
    """R73 delivery package must contain supervisor-readme (IV-R73-002 fix).

    Older packages (r72) may not have this; they are accepted with a warning.
    New packages (r73+) must have it.
    """
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    if "r73" not in pkg_path.name:
        pytest.skip(f"Older delivery package {pkg_path.name} — supervisor-readme required only for r73+")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    readmes = [n for n in names if "readme" in n.lower() or "supervisor" in n.lower()]
    assert readmes, (
        f"R73 delivery package must contain supervisor-readme (IV-R73-002 fix). "
        f"Package members: {names}"
    )


def test_delivery_package_has_four_members_for_r73():
    """R73 delivery package must have exactly 4 members: inner ZIP + sidecar + manifest + readme."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    if "r73" not in pkg_path.name:
        pytest.skip("4-member requirement only for r73+ packages")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    assert len(names) == 4, (
        f"R73 delivery package must have exactly 4 members. Got {len(names)}: {names}"
    )


def test_sidecar_not_inside_inner_zip():
    """Sidecar must NOT be inside the inner evidence ZIP (it proves from outside)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    import io
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        if not inner_name:
            pytest.skip("No inner ZIP in delivery package")
        inner_bytes = outer.read(inner_name)
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        inner_names = inner.namelist()
    sidecars_inside = [n for n in inner_names if n.endswith(".sha256-proof.json")]
    assert not sidecars_inside, (
        f"Sidecar must NOT be inside inner ZIP. Found: {sidecars_inside}"
    )
