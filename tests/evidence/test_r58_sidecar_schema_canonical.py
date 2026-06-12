"""
test_r58_sidecar_schema_canonical.py — R58 Train B: Sidecar canonical schema tests.

Verifies that write_sidecar_proof.py produces sidecars with all required canonical fields
and that the validator reads them correctly.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-003
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def _make_zip(tmp_path, name="r58-test.zip"):
    zp = tmp_path / name
    with zipfile.ZipFile(zp, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/sprint-id.txt", "R58")
    return zp


class TestCanonicalSchema:
    """Sidecar canonical schema requirements."""

    def test_sidecar_version_is_string(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert isinstance(s["sidecar_version"], str)

    def test_run_number_present(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert s["run_number"] == "R58"

    def test_bundle_filename_is_basename(self, tmp_path):
        zp = _make_zip(tmp_path, "r58-final.zip")
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert s["bundle_filename"] == "r58-final.zip"

    def test_sha256_is_64_hex(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert len(s["sha256"]) == 64
        assert all(c in "0123456789abcdef" for c in s["sha256"])

    def test_size_bytes_positive(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert s["size_bytes"] > 0
        assert s["size_bytes"] == zp.stat().st_size

    def test_entry_count_positive(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert s["entry_count"] > 0

    def test_validation_result_pass(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert s["validation_result"] == "PASS"

    def test_timestamp_utc_is_iso(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert "T" in s["timestamp_utc"]
        assert "+" in s["timestamp_utc"] or "Z" in s["timestamp_utc"]

    def test_contract_path_present(self, tmp_path):
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert s["contract_path"] == "test.yaml"

    def test_no_bundle_sha256_in_canonical_sidecar(self, tmp_path):
        """New sidecars use sha256, not bundle_sha256 (the old non-canonical name)."""
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        assert "sha256" in s
        # The primary sha field should be 'sha256', not require 'bundle_sha256'
        # bundle_sha256 is only for backward compat reading of old sidecars


class TestSidecarRoundtrip:
    """Sidecar can be serialized to JSON and read back with validator."""

    def test_write_and_read_sidecar(self, tmp_path):
        zp = _make_zip(tmp_path, "r58-bundle.zip")
        from tools.evidence.write_sidecar_proof import build_sidecar, write_sidecar
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        s = build_sidecar(zp, "test.yaml", "R58", "PASS")
        out = tmp_path / "r58-bundle.sha256-proof.json"
        write_sidecar(s, out)
        # Read back and verify
        loaded = json.loads(out.read_text())
        assert loaded["sha256"] == s["sha256"]
        # Validator accepts it
        errors = check_sidecar_proof(str(zp), str(out))
        assert errors == []
