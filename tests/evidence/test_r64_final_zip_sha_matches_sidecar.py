"""
test_r64_final_zip_sha_matches_sidecar.py — R64 Train B: ZIP SHA must match sidecar.

Closes:
- IV-R63-004: SHA mismatch between verdict and ZIP

Tests:
- Sidecar SHA matches actual ZIP SHA-256
- Sidecar entry_count matches actual ZIP entry count
- Sidecar size_bytes matches actual ZIP size
- Final verdict SIDECAR_SHA matches sidecar file SHA

R64 Sprint: FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
IV-R63-004
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_sidecar() -> dict | None:
    sidecar_path = PROJECT_ROOT / ".local" / "r64-pass2-final.sha256-proof.json"
    if not sidecar_path.exists():
        return None
    return json.loads(sidecar_path.read_text(encoding="utf-8"))


class TestR64ZipSidecarConsistency:
    """ZIP and sidecar must agree on SHA, size, and entries."""

    def test_sidecar_sha_matches_zip(self):
        zip_path = PROJECT_ROOT / ".local" / "r64-pass2-final.zip"
        if not zip_path.exists():
            pytest.skip("R64 bundle not yet built")
        sidecar = _load_sidecar()
        if sidecar is None:
            pytest.skip("R64 sidecar not yet generated")
        actual_sha = _compute_sha256(zip_path)
        assert sidecar["sha256"] == actual_sha, (
            f"Sidecar SHA {sidecar['sha256'][:16]}... != actual ZIP SHA {actual_sha[:16]}..."
        )

    def test_sidecar_size_matches_zip(self):
        zip_path = PROJECT_ROOT / ".local" / "r64-pass2-final.zip"
        if not zip_path.exists():
            pytest.skip("R64 bundle not yet built")
        sidecar = _load_sidecar()
        if sidecar is None:
            pytest.skip("R64 sidecar not yet generated")
        actual_size = zip_path.stat().st_size
        assert sidecar["size_bytes"] == actual_size

    def test_sidecar_entries_match_zip(self):
        zip_path = PROJECT_ROOT / ".local" / "r64-pass2-final.zip"
        if not zip_path.exists():
            pytest.skip("R64 bundle not yet built")
        sidecar = _load_sidecar()
        if sidecar is None:
            pytest.skip("R64 sidecar not yet generated")
        with zipfile.ZipFile(str(zip_path)) as zf:
            actual_entries = len(zf.namelist())
        assert sidecar["entry_count"] == actual_entries

    def test_sidecar_validation_result_pass(self):
        sidecar = _load_sidecar()
        if sidecar is None:
            pytest.skip("R64 sidecar not yet generated")
        assert sidecar["validation_result"] == "PASS"

    def test_verdict_sidecar_sha_matches(self):
        verdict_path = PROJECT_ROOT / "reports" / "r64" / "final-verdict.md"
        if not verdict_path.exists():
            pytest.skip("R64 final-verdict not yet written")
        sidecar = _load_sidecar()
        if sidecar is None:
            pytest.skip("R64 sidecar not yet generated")
        content = verdict_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("SIDECAR_SHA:"):
                verdict_sha = line.split(":", 1)[1].strip()
                assert verdict_sha == sidecar["sha256"], (
                    f"Verdict SIDECAR_SHA {verdict_sha[:16]}... != sidecar {sidecar['sha256'][:16]}..."
                )
                return
        pytest.skip("SIDECAR_SHA not found in verdict")
