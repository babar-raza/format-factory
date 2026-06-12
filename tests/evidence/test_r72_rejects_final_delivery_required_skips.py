"""
R72 Train F — test_r72_rejects_final_delivery_required_skips.py

Verify that R72 evidence tests do NOT skip required checks when the delivery package
is present. Required skips in delivery mode are a blocker.

R71 IV-R72-005: R71 tests replayed as 9 passed, 41 skipped from extracted bundle.
R72 repair: No required skip when delivery package is available.

A "required skip" is a skip that occurs because the delivery package is missing
and the test cannot proceed. When the package IS present, required checks must run.
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


def test_sidecar_check_does_not_skip():
    """When delivery package is present, sidecar check must not skip."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar = next((n for n in names if n.endswith(".sha256-proof.json")), None)

    # If we reached here, the package is present — this check must NOT skip
    assert sidecar is not None, (
        "Sidecar not found in delivery package. Required check must not be skipped."
    )


def test_manifest_check_does_not_skip():
    """When delivery package is present, manifest check must not skip."""
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
        "Delivery manifest not found. Required check must not be skipped."
    )


def test_sha_validation_does_not_skip():
    """When delivery package is present, SHA validation must not skip."""
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
    # This check must run — no skip
    assert sidecar.get("sha256") == actual_sha, (
        "SHA validation failed — inner ZIP SHA does not match sidecar claim."
    )


def test_proof_model_check_does_not_skip():
    """When delivery package is present, proof model check (Layer 1-3 integrity) must not skip."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        assert manifest_name is not None
        assert sidecar_name is not None
        manifest = json.loads(outer.read(manifest_name))
        sidecar_bytes = outer.read(sidecar_name)

    sidecar_file_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    manifest_sidecar_sha = manifest.get("sidecar_sha256", "")
    manifest_evidence_sha = manifest.get("evidence_zip_sha256", "")

    # Layer 2 → Layer 3 check: sidecar file SHA in manifest
    assert manifest_sidecar_sha == sidecar_file_sha, (
        "Layer 3 integrity: manifest.sidecar_sha256 != actual sidecar file SHA"
    )
    # Layer 1 ≠ Layer 2 SHA check
    assert manifest_evidence_sha != manifest_sidecar_sha, (
        "Proof model: evidence_zip_sha256 and sidecar_sha256 must differ."
    )


def test_sprint_id_check_does_not_skip():
    """When delivery package is present, sprint ID check must not skip."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        inner_names = inner.namelist()
        sprint_ids = [n for n in inner_names if n.endswith("sprint-id.txt")]
        assert sprint_ids, "bundle-metadata/sprint-id.txt not found in inner ZIP"
        sprint_id_content = inner.read(sprint_ids[0]).decode("utf-8", errors="replace")

    assert "FORMAT-FACTORY" in sprint_id_content, (
        f"sprint-id.txt does not contain FORMAT-FACTORY. Got: {sprint_id_content[:100]}"
    )
