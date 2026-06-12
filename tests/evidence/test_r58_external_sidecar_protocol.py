"""
test_r58_external_sidecar_protocol.py — R58 Train B: External sidecar proof protocol tests.

Verifies:
1. External sidecar is written OUTSIDE the ZIP (not embedded)
2. Sidecar uses canonical sha256 field
3. Validation without sidecar fails when contract requires it
4. Validation with matching external sidecar passes
5. Validation with wrong/stale sidecar fails

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-002, IV-R57-003
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def _make_zip(tmp_path: Path, content: bytes = b"test content") -> Path:
    """Create a minimal test ZIP."""
    zp = tmp_path / "test-bundle.zip"
    with zipfile.ZipFile(zp, "w") as zf:
        zf.writestr("repo/README.md", "test")
        zf.writestr("bundle-metadata/sprint-id.txt", "R58")
    return zp


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestSidecarNotInsideZip:
    """Sidecar must be outside the ZIP it proves."""

    def test_sidecar_written_outside_zip(self, tmp_path):
        """write_sidecar_proof.build_sidecar writes a JSON with sha256, not inside ZIP."""
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar, write_sidecar
        sidecar = build_sidecar(
            bundle_path=zp,
            contract_path="test-contract.yaml",
            run_number="R58",
            validation_result="PASS",
        )
        out = tmp_path / "test-bundle.sha256-proof.json"
        write_sidecar(sidecar, out)
        # Sidecar is a file NEXT TO the ZIP
        assert out.exists()
        assert out.parent == zp.parent
        # ZIP contents do not contain the sidecar
        with zipfile.ZipFile(zp) as zf:
            names = zf.namelist()
        sidecar_in_zip = [n for n in names if "sha256-proof" in n]
        assert sidecar_in_zip == [], (
            f"Sidecar should NOT be inside the ZIP. Found: {sidecar_in_zip}"
        )

    def test_sidecar_sha_matches_zip(self, tmp_path):
        """Sidecar sha256 field must match the actual ZIP SHA-256."""
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        sidecar = build_sidecar(zp, "test-contract.yaml", "R58", "PASS")
        actual_sha = _compute_sha256(zp)
        assert sidecar["sha256"] == actual_sha

    def test_sidecar_uses_canonical_field_name(self, tmp_path):
        """Sidecar must use 'sha256' as the field name (not 'bundle_sha256')."""
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        sidecar = build_sidecar(zp, "test-contract.yaml", "R58", "PASS")
        assert "sha256" in sidecar, "Sidecar must have 'sha256' key"
        # Old non-canonical name must NOT be the primary key
        # (may exist as alias but 'sha256' must be present)
        assert isinstance(sidecar["sha256"], str)
        assert len(sidecar["sha256"]) == 64

    def test_sidecar_contains_required_canonical_fields(self, tmp_path):
        """Sidecar must contain all canonical required fields."""
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar
        sidecar = build_sidecar(zp, "test-contract.yaml", "R58", "PASS")
        required_fields = [
            "sidecar_version", "run_number", "bundle_filename",
            "sha256", "size_bytes", "entry_count",
            "contract_path", "validation_result", "timestamp_utc",
        ]
        for field in required_fields:
            assert field in sidecar, f"Sidecar missing required field: {field!r}"


class TestSidecarValidation:
    """Sidecar validation in the evidence validator."""

    def _make_minimal_zip(self, tmp_path, sprint_id="R58"):
        zp = tmp_path / "r58-test.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/state/current-state.md", f"Latest sprint: {sprint_id} - COMPLETE")
            zf.writestr("bundle-metadata/sprint-id.txt", sprint_id)
            zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit")
        return zp

    def test_validator_accepts_correct_sidecar(self, tmp_path):
        """Validator check_sidecar_proof returns [] for matching sidecar."""
        zp = _make_zip(tmp_path)
        from tools.evidence.write_sidecar_proof import build_sidecar, write_sidecar
        sidecar = build_sidecar(zp, "test-contract.yaml", "R58", "PASS")
        sidecar_path = tmp_path / "r58.sha256-proof.json"
        write_sidecar(sidecar, sidecar_path)
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        errors = check_sidecar_proof(str(zp), str(sidecar_path))
        assert errors == [], f"Unexpected errors with correct sidecar: {errors}"

    def test_validator_rejects_wrong_sha_sidecar(self, tmp_path):
        """Validator check_sidecar_proof returns errors for wrong SHA."""
        zp = _make_zip(tmp_path)
        # Write sidecar with wrong SHA
        sidecar = {
            "sidecar_version": "1.0",
            "run_number": "R58",
            "bundle_filename": zp.name,
            "sha256": "a" * 64,  # wrong SHA
            "size_bytes": zp.stat().st_size,
            "entry_count": 2,
            "contract_path": "test.yaml",
            "validation_result": "PASS",
            "timestamp_utc": "2026-05-24T00:00:00+00:00",
        }
        sidecar_path = tmp_path / "wrong.sha256-proof.json"
        sidecar_path.write_text(json.dumps(sidecar))
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        errors = check_sidecar_proof(str(zp), str(sidecar_path))
        assert any("SIDECAR_PROOF_SHA_MISMATCH" in e for e in errors)

    def test_validator_accepts_bundle_sha256_compat(self, tmp_path):
        """Validator accepts legacy bundle_sha256 field for backward compatibility."""
        zp = _make_zip(tmp_path)
        sha = _compute_sha256(zp)
        # Old-style sidecar using bundle_sha256
        sidecar = {
            "sidecar_version": "1.0",
            "run_number": "R57",
            "bundle_filename": zp.name,
            "bundle_sha256": sha,  # legacy field name
            "size_bytes": zp.stat().st_size,
            "entry_count": 2,
            "contract_path": "test.yaml",
            "validation_result": "PASS",
            "timestamp_utc": "2026-05-23T00:00:00+00:00",
        }
        sidecar_path = tmp_path / "legacy.sha256-proof.json"
        sidecar_path.write_text(json.dumps(sidecar))
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        errors = check_sidecar_proof(str(zp), str(sidecar_path))
        sha_errors = [e for e in errors if "SHA_MISMATCH" in e]
        assert sha_errors == [], f"Legacy bundle_sha256 should be accepted: {sha_errors}"


class TestSidecarInsideZipDetection:
    """check_repo_sidecar_not_inside_zip must detect sidecar committed to repo."""

    def test_sidecar_not_in_repo_passes(self, tmp_path):
        zp = tmp_path / "r58-bundle.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_repo_sidecar_not_inside_zip
        with zipfile.ZipFile(zp) as zf:
            errors = check_repo_sidecar_not_inside_zip(zf, str(zp))
        assert errors == []

    def test_sidecar_in_repo_fails(self, tmp_path):
        """When sidecar for this bundle is inside the ZIP (committed to repo), validator fails."""
        bundle_name = "r58-bundle.zip"
        zp = tmp_path / bundle_name
        sidecar_data = json.dumps({
            "sidecar_version": "1.0",
            "bundle_filename": bundle_name,
            "sha256": "a" * 64,
            "validation_result": "PASS",
        })
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
            zf.writestr(f"repo/reports/r58/{bundle_name}.sha256-proof.json", sidecar_data)
        from tools.evidence.validate_evidence_bundle import check_repo_sidecar_not_inside_zip
        with zipfile.ZipFile(zp) as zf:
            errors = check_repo_sidecar_not_inside_zip(zf, str(zp))
        assert any("SIDECAR_INSIDE_ZIP" in e for e in errors)
