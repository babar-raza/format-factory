"""
test_r53_sidecar_proof.py — R53 Lane 2B: External sidecar proof validation tests.

Sprint: FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001

Tests that check_sidecar_proof() correctly validates/rejects sidecar JSON files:

  test_sidecar_valid_sha_size_entries_passes
  test_sidecar_sha_mismatch_fails
  test_sidecar_size_mismatch_fails
  test_sidecar_entry_count_mismatch_fails
  test_sidecar_result_not_pass_fails
  test_sidecar_missing_file_fails
  test_sidecar_valid_partial_fields_passes
  test_write_sidecar_then_validate_roundtrip
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

import pytest

from tools.evidence.validate_evidence_bundle import check_sidecar_proof


def _make_bundle(content: bytes = b"fake bundle") -> str:
    """Write bytes to a temp file and return the path."""
    f = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    f.write(content)
    f.close()
    return f.name


def _real_bundle_sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_sidecar(data: dict) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8")
    json.dump(data, f)
    f.close()
    return f.name


def test_sidecar_valid_sha_size_entries_passes():
    """Matching SHA, size, entries → no errors."""
    # Create a real zip with known content
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "hello")
        zf.writestr("b.txt", "world")

    sha = _real_bundle_sha(bundle)
    size = os.path.getsize(bundle)
    with zipfile.ZipFile(bundle) as zf:
        entries = len(zf.namelist())

    sidecar_data = {
        "sha256": sha,
        "size_bytes": size,
        "entry_count": entries,
        "validation_result": "PASS",
    }
    sidecar = _write_sidecar(sidecar_data)
    try:
        errors = check_sidecar_proof(bundle, sidecar)
        assert errors == [], f"Expected no errors, got: {errors}"
    finally:
        os.unlink(bundle)
        os.unlink(sidecar)


def test_sidecar_sha_mismatch_fails():
    """SHA mismatch must produce SIDECAR_PROOF_SHA_MISMATCH error."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "content")

    size = os.path.getsize(bundle)
    with zipfile.ZipFile(bundle) as zf:
        entries = len(zf.namelist())

    sidecar_data = {
        "sha256": "a" * 64,  # wrong SHA
        "size_bytes": size,
        "entry_count": entries,
        "validation_result": "PASS",
    }
    sidecar = _write_sidecar(sidecar_data)
    try:
        errors = check_sidecar_proof(bundle, sidecar)
        assert any("SIDECAR_PROOF_SHA_MISMATCH" in e for e in errors), (
            f"Expected SHA mismatch error, got: {errors}"
        )
    finally:
        os.unlink(bundle)
        os.unlink(sidecar)


def test_sidecar_size_mismatch_fails():
    """Size mismatch must produce SIDECAR_PROOF_SIZE_MISMATCH error."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "content")

    sha = _real_bundle_sha(bundle)
    with zipfile.ZipFile(bundle) as zf:
        entries = len(zf.namelist())

    sidecar_data = {
        "sha256": sha,
        "size_bytes": 9999999,  # wrong size
        "entry_count": entries,
        "validation_result": "PASS",
    }
    sidecar = _write_sidecar(sidecar_data)
    try:
        errors = check_sidecar_proof(bundle, sidecar)
        assert any("SIDECAR_PROOF_SIZE_MISMATCH" in e for e in errors), (
            f"Expected size mismatch error, got: {errors}"
        )
    finally:
        os.unlink(bundle)
        os.unlink(sidecar)


def test_sidecar_entry_count_mismatch_fails():
    """Entry count mismatch must produce SIDECAR_PROOF_ENTRY_COUNT_MISMATCH error."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "content")

    sha = _real_bundle_sha(bundle)
    size = os.path.getsize(bundle)

    sidecar_data = {
        "sha256": sha,
        "size_bytes": size,
        "entry_count": 999,  # wrong entry count
        "validation_result": "PASS",
    }
    sidecar = _write_sidecar(sidecar_data)
    try:
        errors = check_sidecar_proof(bundle, sidecar)
        assert any("SIDECAR_PROOF_ENTRY_COUNT_MISMATCH" in e for e in errors), (
            f"Expected entry count mismatch error, got: {errors}"
        )
    finally:
        os.unlink(bundle)
        os.unlink(sidecar)


def test_sidecar_result_not_pass_fails():
    """Sidecar with validation_result != PASS must fail."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "content")

    sha = _real_bundle_sha(bundle)
    size = os.path.getsize(bundle)
    with zipfile.ZipFile(bundle) as zf:
        entries = len(zf.namelist())

    sidecar_data = {
        "sha256": sha,
        "size_bytes": size,
        "entry_count": entries,
        "validation_result": "FAIL",
    }
    sidecar = _write_sidecar(sidecar_data)
    try:
        errors = check_sidecar_proof(bundle, sidecar)
        assert any("SIDECAR_PROOF_RESULT_NOT_PASS" in e for e in errors), (
            f"Expected result-not-pass error, got: {errors}"
        )
    finally:
        os.unlink(bundle)
        os.unlink(sidecar)


def test_sidecar_missing_file_fails():
    """Non-existent sidecar file must return a readable error."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "content")

    try:
        errors = check_sidecar_proof(bundle, "/nonexistent/path/sidecar.json")
        assert any("SIDECAR_PROOF" in e for e in errors), (
            f"Expected sidecar error for missing file, got: {errors}"
        )
    finally:
        os.unlink(bundle)


def test_sidecar_valid_partial_fields_passes():
    """Sidecar with only SHA and result (no size/entries) still passes if SHA matches."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle = tmp.name
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("a.txt", "content")

    sha = _real_bundle_sha(bundle)

    # Only include SHA and result — size/entries are optional
    sidecar_data = {
        "sha256": sha,
        "validation_result": "PASS",
        # no size_bytes, no entry_count
    }
    sidecar = _write_sidecar(sidecar_data)
    try:
        errors = check_sidecar_proof(bundle, sidecar)
        assert errors == [], f"Expected no errors for partial sidecar, got: {errors}"
    finally:
        os.unlink(bundle)
        os.unlink(sidecar)


def test_write_sidecar_then_validate_roundtrip():
    """Full round-trip: write_sidecar_proof -> check_sidecar_proof passes."""
    from tools.evidence.write_sidecar_proof import build_sidecar, write_sidecar

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        bundle_path = tmp.name
    with zipfile.ZipFile(bundle_path, "w") as zf:
        zf.writestr("bundle-metadata/test.txt", "test content")
        zf.writestr("repo/some-file.py", "# code")

    sidecar_out = bundle_path + ".sha256-proof.json"
    try:
        sidecar = build_sidecar(
            bundle_path=Path(bundle_path),
            contract_path="tools/evidence/contracts/test.yaml",
            run_number="R53",
            validation_result="PASS",
        )
        write_sidecar(sidecar, Path(sidecar_out))

        errors = check_sidecar_proof(bundle_path, sidecar_out)
        assert errors == [], f"Round-trip sidecar validation failed: {errors}"
    finally:
        os.unlink(bundle_path)
        if os.path.exists(sidecar_out):
            os.unlink(sidecar_out)
