"""
R72 Train D — test_r72_inner_zip_validates_from_delivery_package.py

Verify that the inner evidence ZIP can be validated using only the delivery package:
- Extract inner ZIP and sidecar from delivery package
- Verify inner ZIP SHA matches sidecar-claimed SHA
- Verify inner ZIP can be opened as a valid ZIP
- Verify inner ZIP contains bundle-metadata directory

This proves the delivery package is self-contained for verification.
R71 IV-R72-005: Tests skipped because .local/ fallback was missing from extracted bundle.
R72 repair: All validation uses extracted delivery package contents directly.
"""
import hashlib
import json
import io
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


def test_inner_zip_sha_matches_sidecar_claim():
    """Inner ZIP extracted from delivery package must have SHA matching sidecar-claimed SHA."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        assert inner_name, f"No inner ZIP found. Members: {names}"
        assert sidecar_name, f"No sidecar found. Members: {names}"
        inner_bytes = outer.read(inner_name)
        sidecar_bytes = outer.read(sidecar_name)

    sidecar = json.loads(sidecar_bytes.decode("utf-8"))
    claimed_sha = sidecar.get("sha256", "")
    actual_sha = hashlib.sha256(inner_bytes).hexdigest()

    assert claimed_sha == actual_sha, (
        f"Inner ZIP SHA mismatch.\n"
        f"  Sidecar claims: {claimed_sha}\n"
        f"  Actual inner ZIP SHA: {actual_sha}\n"
        "The delivery package is corrupt or tampered."
    )


def test_inner_zip_is_valid_zip_from_delivery_package():
    """Inner ZIP extracted from delivery package must be a valid ZIP file."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name, f"No inner ZIP found. Members: {names}"
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner_zf:
        inner_names = inner_zf.namelist()

    assert len(inner_names) > 100, (
        f"Inner ZIP has only {len(inner_names)} entries — expected a full evidence bundle."
    )


def test_inner_zip_contains_bundle_metadata():
    """Inner ZIP must contain bundle-metadata directory."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner_zf:
        inner_names = inner_zf.namelist()

    bm = [n for n in inner_names if n.startswith("bundle-metadata/")]
    assert len(bm) >= 10, (
        f"Inner ZIP must have >= 10 bundle-metadata entries, found {len(bm)}."
    )


def test_inner_zip_contains_sprint_id():
    """Inner ZIP must contain bundle-metadata/sprint-id.txt."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner_zf:
        inner_names = inner_zf.namelist()
        sprint_ids = [n for n in inner_names if n.endswith("sprint-id.txt")]
        assert sprint_ids, "Inner ZIP must contain bundle-metadata/sprint-id.txt"
        sprint_id_content = inner_zf.read(sprint_ids[0]).decode("utf-8")

    assert "FORMAT-FACTORY" in sprint_id_content, (
        f"sprint-id.txt must contain FORMAT-FACTORY. Got: {sprint_id_content[:100]}"
    )


def test_inner_zip_contains_package_artifacts():
    """Inner ZIP must contain package artifacts (wheels/sdists/nupkgs)."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner_zf:
        inner_names = inner_zf.namelist()

    wheels = [n for n in inner_names if n.endswith(".whl")]
    nupkgs = [n for n in inner_names if n.endswith(".nupkg")]

    assert len(wheels) >= 10, f"Expected >= 10 wheels, found {len(wheels)}"
    assert len(nupkgs) >= 2, f"Expected >= 2 nupkgs, found {len(nupkgs)}"
