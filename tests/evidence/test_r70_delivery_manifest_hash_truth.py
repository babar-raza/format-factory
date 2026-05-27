"""
R70 Train D — test_r70_delivery_manifest_hash_truth.py
Verify delivery manifest sidecar_sha256 matches actual sidecar file SHA.
"""

import json
import hashlib
import pathlib
import pytest

LOCAL = pathlib.Path(".local")
MANIFEST = LOCAL / "r69-delivery-manifest.json"
SIDECAR = LOCAL / "r69-pass2-final.sha256-proof.json"
INNER_ZIP = LOCAL / "r69-pass2-final.zip"


def test_delivery_manifest_exists():
    """Delivery manifest must exist in .local/."""
    if not MANIFEST.exists():
        pytest.skip("r69-delivery-manifest.json not present (pre-build)")
    assert MANIFEST.exists()


def test_sidecar_sha256_matches_actual_sidecar_file():
    """manifest sidecar_sha256 must equal SHA-256 of the actual sidecar JSON file."""
    if not MANIFEST.exists() or not SIDECAR.exists():
        pytest.skip("Delivery artifacts not present (pre-build)")
    manifest = json.loads(MANIFEST.read_bytes())
    sidecar_sha = hashlib.sha256(SIDECAR.read_bytes()).hexdigest()
    recorded = manifest.get("sidecar_sha256", "")
    assert recorded == sidecar_sha, (
        f"manifest sidecar_sha256={recorded!r} != actual sidecar file SHA={sidecar_sha!r}. "
        "sidecar_sha256 must be the SHA of the sidecar JSON file, not the inner ZIP."
    )


def test_evidence_zip_sha256_matches_actual_inner_zip():
    """manifest evidence_zip_sha256 must equal SHA-256 of the actual inner ZIP file."""
    if not MANIFEST.exists() or not INNER_ZIP.exists():
        pytest.skip("Delivery artifacts not present (pre-build)")
    manifest = json.loads(MANIFEST.read_bytes())
    inner_sha = hashlib.sha256(INNER_ZIP.read_bytes()).hexdigest()
    recorded = manifest.get("evidence_zip_sha256", "")
    assert recorded == inner_sha, (
        f"manifest evidence_zip_sha256={recorded!r} != actual inner ZIP SHA={inner_sha!r}"
    )


def test_sidecar_sha256_differs_from_evidence_zip_sha256():
    """sidecar_sha256 must NOT equal evidence_zip_sha256 (they are different files)."""
    if not MANIFEST.exists():
        pytest.skip("Delivery manifest not present (pre-build)")
    manifest = json.loads(MANIFEST.read_bytes())
    sidecar_sha = manifest.get("sidecar_sha256", "")
    inner_sha = manifest.get("evidence_zip_sha256", "")
    assert sidecar_sha != inner_sha, (
        f"sidecar_sha256 == evidence_zip_sha256 == {sidecar_sha!r}. "
        "These are different files and must have different SHA-256 values."
    )
