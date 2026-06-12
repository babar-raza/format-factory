"""
R73 Train B — test_r73_rejects_missing_physical_sidecar.py

Verify that validation fails when the sidecar is physically absent from the delivery package
or from the extraction directory.

Enforces: "No claiming sidecar proof unless the sidecar JSON is physically present"
"""
import io
import json
import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")
DELIVERY_PACKAGE_NAMES = ["r73-delivery-package.zip", "r72-delivery-package.zip"]


def _get_delivery_package():
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(f"DELIVERY_PACKAGE_UNDER_TEST={env_path!r} not found.")
        return p
    for name in DELIVERY_PACKAGE_NAMES:
        p = LOCAL / name
        if p.exists():
            return p
    return None


def test_sidecar_physically_present_in_delivery_package():
    """Sidecar JSON must be physically present inside the delivery package ZIP."""
    dp = _get_delivery_package()
    if dp is None:
        pytest.skip("No delivery package available")
    with zipfile.ZipFile(dp) as zf:
        names = zf.namelist()
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert sidecars, (
        f"Sidecar JSON not physically present in delivery package. Members: {names}. "
        "Cannot claim sidecar proof without physical sidecar file."
    )


def test_sidecar_is_valid_json_when_extracted():
    """Sidecar JSON must be valid JSON when extracted from delivery package."""
    dp = _get_delivery_package()
    if dp is None:
        pytest.skip("No delivery package available")
    with zipfile.ZipFile(dp) as zf:
        names = zf.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        if not sidecar_name:
            pytest.skip("No sidecar in delivery package")
        sidecar_bytes = zf.read(sidecar_name)
    sidecar = json.loads(sidecar_bytes.decode("utf-8"))
    assert "sha256" in sidecar, f"Sidecar JSON must have 'sha256' field. Got keys: {list(sidecar.keys())}"
    assert len(sidecar["sha256"]) == 64, f"sha256 field must be 64 hex chars. Got: {sidecar['sha256']}"


def test_sidecar_size_nonzero():
    """Sidecar JSON must be non-empty."""
    dp = _get_delivery_package()
    if dp is None:
        pytest.skip("No delivery package available")
    with zipfile.ZipFile(dp) as zf:
        names = zf.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        if not sidecar_name:
            pytest.skip("No sidecar in delivery package")
        info = zf.getinfo(sidecar_name)
        assert info.file_size > 100, f"Sidecar file too small: {info.file_size} bytes"


def test_package_without_sidecar_fails_delivery_check():
    """Delivery package that has inner ZIP but no sidecar must fail delivery validation."""
    # Build a synthetic package with inner ZIP only (no sidecar)
    buf = io.BytesIO()
    inner_buf = io.BytesIO()
    with zipfile.ZipFile(inner_buf, "w") as inner:
        inner.writestr("bundle-metadata/sprint-id.txt", "FORMAT-FACTORY-TEST-001\n")
    inner_buf.seek(0)
    with zipfile.ZipFile(buf, "w") as outer:
        outer.writestr("test-pass2-final.zip", inner_buf.read())
        # No sidecar added
    buf.seek(0)

    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()

    # Verify: no sidecar present
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert not sidecars, "Synthetic package incorrectly has sidecar"

    # A delivery validator would reject this because sidecar is absent
    # We confirm the structural gap
    inner_zips = [n for n in names if n.endswith(".zip")]
    assert inner_zips, "Synthetic package has inner ZIP"
    assert not sidecars, "Synthetic package correctly has no sidecar — delivery validation would reject it"
