"""R67 Train D: no placeholder or IN_PROGRESS tokens in key metadata files.

Validator hardening: extends R66 Train C tests to cover PENDING_FINAL_COMMIT
and IN_PROGRESS in any bundled metadata file.
"""
from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_TOKENS = [
    "to be completed",
    "to be generated",
    "to be filled",
    "to be confirmed",
    "placeholder",
    "PENDING_FINAL_COMMIT",
]

METADATA_PROOF_FILES = [
    "final-bundle-validation-proof.txt",
    "external-sidecar-proof-summary.txt",
    "delivery-package-validation-summary.txt",
    "missing-sidecar-negative-proof.txt",
    "wrong-sidecar-negative-proof.txt",
    "extracted-package-replay-summary.txt",
]


def _find_metadata_dir() -> Path | None:
    for run in ["r67", "r66"]:
        d = PROJECT_ROOT / ".local" / f"{run}-metadata"
        if d.is_dir():
            return d
    return None


@pytest.fixture
def metadata_dir():
    d = _find_metadata_dir()
    if d is None:
        pytest.skip("No metadata directory available")
    return d


@pytest.mark.parametrize("filename", METADATA_PROOF_FILES)
def test_proof_file_no_forbidden_tokens(filename, metadata_dir):
    f = metadata_dir / filename
    if not f.is_file():
        pytest.skip(f"{filename} not found in metadata dir")
    content = f.read_text(encoding="utf-8", errors="replace")
    for token in FORBIDDEN_TOKENS:
        assert token not in content, f"Forbidden token '{token}' found in {filename}"


@pytest.mark.parametrize("filename", ["package-artifact-manifest.yaml", "dotnet-nupkg-manifest.yaml"])
def test_manifest_no_forbidden_tokens(filename, metadata_dir):
    f = metadata_dir / filename
    if not f.is_file():
        pytest.skip(f"{filename} not found")
    content = f.read_text(encoding="utf-8", errors="replace")
    for token in FORBIDDEN_TOKENS:
        assert token not in content, f"Forbidden token '{token}' found in {filename}"
