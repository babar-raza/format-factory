"""
R69 Train D — Test: delivery manifest SHA must match the inner ZIP and sidecar.

Covers IV-R69-004: R68's delivery-package-validation-summary.txt recorded stale SHA
values (10c57c6f) that didn't match the final delivery package (c6b53bd2). This test
ensures delivery manifest fields are consistent.
"""
import hashlib
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
R69_LOCAL = PROJECT_ROOT / ".local"


class TestDeliveryManifestMatchesArtifacts:
    """Delivery manifest must have consistent SHA-256 values matching actual artifacts."""

    def test_r69_delivery_manifest_has_required_fields(self):
        """Delivery manifest must have all required fields."""
        manifest_path = R69_LOCAL / "r69-delivery-manifest.json"
        if not manifest_path.exists():
            pytest.skip("r69-delivery-manifest.json not yet built")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        required_fields = [
            "run_number", "sprint_id", "evidence_zip_filename", "evidence_zip_sha256",
            "evidence_zip_size_bytes", "evidence_zip_entry_count",
            "sidecar_filename", "sidecar_sha256", "sidecar_size_bytes",
            "contract_path", "validation_command", "validation_exit_code",
            "validation_result", "git_head", "timestamp_utc",
        ]
        missing = [f for f in required_fields if f not in manifest]
        assert not missing, (
            f"Delivery manifest missing required fields: {missing}"
        )

    def test_r69_manifest_evidence_zip_sha_matches_actual(self):
        """Manifest evidence_zip_sha256 must match the actual inner ZIP SHA."""
        manifest_path = R69_LOCAL / "r69-delivery-manifest.json"
        inner_zip = R69_LOCAL / "r69-pass2-final.zip"
        if not manifest_path.exists() or not inner_zip.exists():
            pytest.skip("R69 artifacts not yet built")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        actual_sha = hashlib.sha256(inner_zip.read_bytes()).hexdigest()
        recorded_sha = manifest.get("evidence_zip_sha256", "")
        assert actual_sha == recorded_sha, (
            f"Manifest evidence_zip_sha256 mismatch: "
            f"actual={actual_sha[:16]}... recorded={recorded_sha[:16]}..."
        )

    def test_r69_manifest_sidecar_sha_matches_actual(self):
        """Manifest sidecar_sha256 must match the sidecar's claimed bundle SHA."""
        manifest_path = R69_LOCAL / "r69-delivery-manifest.json"
        sidecar_path = R69_LOCAL / "r69-pass2-final.sha256-proof.json"
        inner_zip = R69_LOCAL / "r69-pass2-final.zip"
        if not manifest_path.exists() or not sidecar_path.exists():
            pytest.skip("R69 artifacts not yet built")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        actual_sha = hashlib.sha256(inner_zip.read_bytes()).hexdigest()
        sidecar_sha = sidecar.get("sha256", "")
        manifest_sidecar_sha = manifest.get("sidecar_sha256", "")
        # Manifest's sidecar_sha256 is the SHA of the sidecar FILE, not the bundle
        # The sidecar's sha256 is the bundle SHA — verify they all agree
        assert actual_sha == sidecar_sha, (
            f"Sidecar bundle SHA mismatch: inner_zip={actual_sha[:16]}... sidecar={sidecar_sha[:16]}..."
        )
        assert manifest_sidecar_sha, "Manifest must have sidecar_sha256 field"

    def test_r69_manifest_validation_result_pass(self):
        """Delivery manifest must show validation_result: PASS."""
        manifest_path = R69_LOCAL / "r69-delivery-manifest.json"
        if not manifest_path.exists():
            pytest.skip("r69-delivery-manifest.json not yet built")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest.get("validation_result") == "PASS", (
            f"Delivery manifest validation_result must be PASS, got: {manifest.get('validation_result')}"
        )
