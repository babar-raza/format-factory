"""
test_r65_delivery_package.py — R65 Train B: Delivery package protocol tests.

Tests:
- Delivery package contains evidence ZIP + sidecar + manifest
- Delivery manifest matches artifacts
- Inner evidence ZIP validates with sidecar
- Sidecar not inside inner ZIP
- Delivery package extraction and validation

R65 Sprint: FORMAT-FACTORY-R65-DELIVERY-PACKAGE-RC-REPLAY-AI-LIVE-WORKAHEAD-MEGA-TRAIN-001
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.build_delivery_package import (
    build_delivery_package,
    validate_delivery_package,
)

R65_CONTRACT = "tools/evidence/contracts/r65-delivery-package-rc-replay-ai-live-workahead.yaml"
R65_DELIVERY = PROJECT_ROOT / ".local" / "r65-delivery-package.zip"
R65_EVIDENCE = PROJECT_ROOT / ".local" / "r65-pass2-final.zip"
R65_SIDECAR = PROJECT_ROOT / ".local" / "r65-pass2-final.sha256-proof.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


class TestDeliveryPackageContents:
    """Delivery package must contain evidence ZIP + sidecar + manifest."""

    def test_delivery_package_exists(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        assert R65_DELIVERY.stat().st_size > 0

    def test_delivery_package_contains_evidence_zip(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with zipfile.ZipFile(R65_DELIVERY) as zf:
            entries = zf.namelist()
        zips = [e for e in entries if e.endswith(".zip")]
        assert len(zips) >= 1, f"No evidence ZIP in delivery package: {entries}"

    def test_delivery_package_contains_sidecar(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with zipfile.ZipFile(R65_DELIVERY) as zf:
            entries = zf.namelist()
        sidecars = [e for e in entries if e.endswith(".sha256-proof.json")]
        assert len(sidecars) >= 1, f"No sidecar in delivery package: {entries}"

    def test_delivery_package_contains_manifest(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with zipfile.ZipFile(R65_DELIVERY) as zf:
            entries = zf.namelist()
        manifests = [e for e in entries if "manifest" in e and e.endswith(".json")]
        assert len(manifests) >= 1, f"No manifest in delivery package: {entries}"

    def test_sidecar_not_inside_evidence_zip(self):
        if not R65_EVIDENCE.exists():
            pytest.skip("R65 evidence ZIP not yet built")
        with zipfile.ZipFile(R65_EVIDENCE) as zf:
            inner = zf.namelist()
        sidecars_inside = [e for e in inner if e.endswith(".sha256-proof.json")]
        assert not sidecars_inside, f"Sidecar found inside evidence ZIP: {sidecars_inside}"


class TestDeliveryManifestConsistency:
    """Manifest must match evidence ZIP and sidecar."""

    def test_manifest_evidence_sha_matches(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with zipfile.ZipFile(R65_DELIVERY) as zf:
            entries = zf.namelist()
            manifest_name = next((e for e in entries if "manifest" in e), None)
            if not manifest_name:
                pytest.fail("No manifest in delivery package")
            manifest = json.loads(zf.read(manifest_name))
            ez_name = next((e for e in entries if e.endswith(".zip")), None)
            if not ez_name:
                pytest.fail("No evidence ZIP in delivery package")
            with tempfile.TemporaryDirectory() as td:
                zf.extract(ez_name, td)
                actual_sha = _sha256(Path(td) / ez_name)
        assert manifest["evidence_zip_sha256"] == actual_sha

    def test_manifest_has_required_fields(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with zipfile.ZipFile(R65_DELIVERY) as zf:
            entries = zf.namelist()
            manifest_name = next((e for e in entries if "manifest" in e), None)
            manifest = json.loads(zf.read(manifest_name))
        required = [
            "evidence_zip_filename", "evidence_zip_sha256",
            "evidence_zip_size_bytes", "evidence_zip_entry_count",
            "sidecar_filename", "sidecar_sha256",
            "contract_path", "validation_command",
            "validation_result", "git_head",
        ]
        missing = [f for f in required if f not in manifest]
        assert not missing, f"Missing manifest fields: {missing}"

    def test_manifest_validation_result_pass(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with zipfile.ZipFile(R65_DELIVERY) as zf:
            entries = zf.namelist()
            manifest_name = next((e for e in entries if "manifest" in e), None)
            manifest = json.loads(zf.read(manifest_name))
        assert manifest["validation_result"] == "PASS"


class TestDeliveryPackageExtraction:
    """Delivery package must validate after extraction."""

    def test_extraction_validates(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with tempfile.TemporaryDirectory() as td:
            results = validate_delivery_package(R65_DELIVERY, Path(td))
        assert results["validation_result"] == "PASS", (
            f"Delivery package validation failed: {results['checks']}"
        )

    def test_sidecar_sha_matches_evidence_zip(self):
        if not R65_DELIVERY.exists():
            pytest.skip("R65 delivery package not yet built")
        with tempfile.TemporaryDirectory() as td:
            results = validate_delivery_package(R65_DELIVERY, Path(td))
        sha_check = next(
            (ok for name, ok in results["checks"] if name == "sidecar_sha_matches_evidence_zip"),
            None,
        )
        assert sha_check is True, "Sidecar SHA does not match evidence ZIP"


class TestSyntheticDeliveryPackage:
    """Unit tests using synthetic evidence."""

    def test_build_and_validate_synthetic(self, tmp_path):
        # Create a fake evidence ZIP
        ez = tmp_path / "test-evidence.zip"
        with zipfile.ZipFile(ez, "w") as zf:
            zf.writestr("repo/dummy.txt", "hello")
            zf.writestr("bundle-metadata/sprint-id.txt", "test")

        # Create a fake sidecar
        h = hashlib.sha256()
        with open(ez, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        sidecar_data = {
            "sha256": h.hexdigest(),
            "size_bytes": ez.stat().st_size,
            "entry_count": 2,
            "validation_result": "PASS",
            "git_head": "abc123",
        }
        sc = tmp_path / "test-evidence.sha256-proof.json"
        sc.write_text(json.dumps(sidecar_data))

        # Build delivery package
        out = tmp_path / "test-delivery.zip"
        manifest = build_delivery_package(
            evidence_zip=ez, sidecar=sc,
            contract_path="test-contract.yaml",
            output=out, git_head="abc123",
        )
        assert out.exists()
        assert manifest["validation_result"] == "PASS"

        # Validate extraction
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        results = validate_delivery_package(out, extract_dir)
        assert results["validation_result"] == "PASS"

    def test_synthetic_sidecar_not_inside_inner(self, tmp_path):
        ez = tmp_path / "inner.zip"
        with zipfile.ZipFile(ez, "w") as zf:
            zf.writestr("repo/test.py", "pass")

        h = hashlib.sha256()
        with open(ez, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        sc_data = {"sha256": h.hexdigest(), "size_bytes": ez.stat().st_size,
                   "entry_count": 1, "validation_result": "PASS", "git_head": "x"}
        sc = tmp_path / "inner.sha256-proof.json"
        sc.write_text(json.dumps(sc_data))

        out = tmp_path / "delivery.zip"
        build_delivery_package(ez, sc, "c.yaml", out)

        # Verify sidecar not inside inner
        with zipfile.ZipFile(ez) as zf:
            assert not any(e.endswith(".sha256-proof.json") for e in zf.namelist())
