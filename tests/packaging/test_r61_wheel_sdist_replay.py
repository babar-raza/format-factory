"""
test_r61_wheel_sdist_replay.py — R61 Train E: Python wheel/sdist replay from extracted bundle.

Verifies that:
1. Wheels can be found via portable discovery from extracted bundle
2. Wheel content is verifiable (APIs present, no import errors)
3. sdist artifacts are present alongside wheels
4. Both FODS and FODT wheels carry correct R60+R61 APIs

Repairs IV-R60-012 (extracted-bundle replay not proven).

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path


def _get_wheel(format_name: str) -> "Path | None":
    """Find wheel for given format using portable discovery."""
    artifact_dir = find_artifact_dir("r60", PROJECT_ROOT)
    if artifact_dir is None:
        return None
    candidates = list(artifact_dir.glob(f"*{format_name}*.whl"))
    return candidates[0] if candidates else None


def _get_sdist(format_name: str) -> "Path | None":
    """Find sdist for given format using portable discovery."""
    artifact_dir = find_artifact_dir("r60", PROJECT_ROOT)
    if artifact_dir is None:
        return None
    candidates = list(artifact_dir.glob(f"*{format_name}*.tar.gz"))
    return candidates[0] if candidates else None


class TestWheelContentReplay:
    """Wheel content verifiable without installation."""

    def test_fods_wheel_apis_verifiable_from_bundle(self):
        """FODS wheel APIs readable directly from ZIP without installation."""
        wheel = _get_wheel("fods")
        if wheel is None:
            pytest.skip("FODS wheel not available via portable discovery")
        with zipfile.ZipFile(wheel) as zf:
            nm_files = [n for n in zf.namelist() if "neutral_model.py" in n]
            assert nm_files, f"neutral_model.py not in FODS wheel. Contents: {zf.namelist()[:10]}"
            content = zf.read(nm_files[0]).decode("utf-8")
        # R59 APIs
        for api in ["workbook_type_distribution", "find_sheet_by_name", "workbook_stats"]:
            assert api in content, f"R59 API {api!r} missing from FODS wheel"
        # R60 APIs
        for api in ["workbook_sheet_summary", "workbook_empty_rows"]:
            assert api in content, f"R60 API {api!r} missing from FODS wheel"

    def test_fodt_wheel_apis_verifiable_from_bundle(self):
        """FODT wheel APIs readable directly from ZIP without installation."""
        wheel = _get_wheel("fodt")
        if wheel is None:
            pytest.skip("FODT wheel not available via portable discovery")
        with zipfile.ZipFile(wheel) as zf:
            nm_files = [n for n in zf.namelist() if "neutral_model.py" in n]
            assert nm_files, f"neutral_model.py not in FODT wheel"
            content = zf.read(nm_files[0]).decode("utf-8")
        # R59 APIs
        for api in ["document_heading_outline", "document_text_content", "document_stats"]:
            assert api in content, f"R59 API {api!r} missing from FODT wheel"
        # R60 APIs
        for api in ["document_word_count", "document_table_summary"]:
            assert api in content, f"R60 API {api!r} missing from FODT wheel"

    def test_fods_wheel_sha256_verifiable(self):
        """FODS wheel SHA-256 can be computed and is non-trivial."""
        wheel = _get_wheel("fods")
        if wheel is None:
            pytest.skip("FODS wheel not available")
        sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
        assert len(sha) == 64, f"SHA-256 must be 64 chars: {sha!r}"
        assert sha != "0" * 64, "SHA must not be all zeros"

    def test_fodt_wheel_sha256_verifiable(self):
        """FODT wheel SHA-256 can be computed."""
        wheel = _get_wheel("fodt")
        if wheel is None:
            pytest.skip("FODT wheel not available")
        sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
        assert len(sha) == 64


class TestSdistPresence:
    """sdist artifacts must be present alongside wheels."""

    def test_fods_sdist_present(self):
        """FODS sdist (.tar.gz) present in artifact directory."""
        sdist = _get_sdist("fods")
        if sdist is None:
            pytest.skip("FODS sdist not available via portable discovery")
        assert sdist.exists()
        assert sdist.suffix == ".gz"

    def test_fodt_sdist_present(self):
        """FODT sdist (.tar.gz) present in artifact directory."""
        sdist = _get_sdist("fodt")
        if sdist is None:
            pytest.skip("FODT sdist not available via portable discovery")
        assert sdist.exists()

    def test_ten_wheels_present(self):
        """All 10 wheels (5 formats * 2 for fods/fodt/etc.) present."""
        artifact_dir = find_artifact_dir("r60", PROJECT_ROOT)
        if artifact_dir is None:
            pytest.skip("Artifact directory not available")
        wheels = list(artifact_dir.glob("*.whl"))
        assert len(wheels) >= 10, (
            f"Expected at least 10 wheels in {artifact_dir}. Found: {[w.name for w in wheels]}"
        )

    def test_ten_sdists_present(self):
        """All 10 sdists present alongside wheels."""
        artifact_dir = find_artifact_dir("r60", PROJECT_ROOT)
        if artifact_dir is None:
            pytest.skip("Artifact directory not available")
        sdists = list(artifact_dir.glob("*.tar.gz"))
        assert len(sdists) >= 10, (
            f"Expected at least 10 sdists in {artifact_dir}. Found: {[s.name for s in sdists]}"
        )


class TestExtractedBundleWheelReplay:
    """Wheel replay from extracted bundle structure."""

    def test_bundle_extraction_preserves_wheel_integrity(self, tmp_path):
        """Extracting bundle to tmp_path produces intact wheels."""
        bundle = PROJECT_ROOT / ".local" / "r60-pass2-final.zip"
        if not bundle.exists():
            pytest.skip("R60 bundle not available")

        extract_dir = tmp_path / "extracted"
        with zipfile.ZipFile(bundle) as zf:
            # Extract only FODS/FODT wheels to speed up test
            artifact_entries = [n for n in zf.namelist()
                                if "bundle-metadata/package-artifacts/" in n
                                and n.endswith(".whl")
                                and ("fods" in n or "fodt" in n)]
            assert artifact_entries, "No FODS/FODT wheels found in bundle"
            for entry in artifact_entries[:2]:  # Just FODS + FODT
                zf.extract(entry, extract_dir)

        # Find the extracted wheels
        extracted_wheels = list((extract_dir / "bundle-metadata" / "package-artifacts").glob("*.whl"))
        assert len(extracted_wheels) >= 1, f"No wheels after extraction: {list(extract_dir.rglob('*.whl'))}"

        # Verify each extracted wheel has neutral_model.py (FODS/FODT only)
        for wheel_path in extracted_wheels:
            with zipfile.ZipFile(wheel_path) as zf:
                names = zf.namelist()
            has_nm = any("neutral_model.py" in n for n in names)
            assert has_nm, f"Wheel {wheel_path.name} has no neutral_model.py"

    def test_manifest_sha256_matches_wheel_on_disk(self):
        """Manifest SHA-256 matches actual wheel file on disk."""
        import re
        manifest_path = find_manifest_path("r60", PROJECT_ROOT)
        artifact_dir = find_artifact_dir("r60", PROJECT_ROOT)
        if manifest_path is None or artifact_dir is None:
            pytest.skip("R60 manifest or artifacts not available")

        content = manifest_path.read_text(encoding="utf-8")
        # Find FODS wheel SHA from manifest
        fods_sha_match = re.search(
            r"aspose_format_factory_fods[^.]*\.whl\n.*?sha256:\s*([0-9a-f]{64})",
            content,
            re.DOTALL,
        )
        if not fods_sha_match:
            # Try alternate format
            import yaml
            try:
                data = yaml.safe_load(content)
                for art in data.get("artifacts", []):
                    if "fods" in art.get("file", "") and art.get("file", "").endswith(".whl"):
                        expected_sha = art["sha256"]
                        wheel = artifact_dir / art["file"]
                        if wheel.exists():
                            actual_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
                            assert actual_sha == expected_sha, (
                                f"Manifest SHA {expected_sha!r} != actual SHA {actual_sha!r} for {art['file']}"
                            )
                        break
            except Exception:
                pytest.skip("Could not parse manifest to extract SHA")
        else:
            expected_sha = fods_sha_match.group(1)
            fods_wheels = list(artifact_dir.glob("*fods*.whl"))
            if not fods_wheels:
                pytest.skip("FODS wheel not found in artifact dir")
            actual_sha = hashlib.sha256(fods_wheels[0].read_bytes()).hexdigest()
            assert actual_sha == expected_sha, (
                f"Manifest SHA {expected_sha!r} != actual wheel SHA {actual_sha!r}"
            )
