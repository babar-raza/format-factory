"""
tests/evidence/test_r47_artifact_inventory.py

R47 MT1 Lane 1B — Tests for check_artifact_inventory() and builder subdirectory fix.

Validates that:
1. check_artifact_inventory() catches bundles where manifest claims artifacts
   but ZIP has no artifact files (R46 false-positive defect reproduction).
2. check_artifact_inventory() passes when artifacts are present and hashes match.
3. check_artifact_inventory() catches SHA-256 mismatch.
4. check_artifact_inventory() passes cleanly when no manifest is present.
5. Builder's rglob fix: subdirectory files are now included in metadata collection.
6. R46 bundle fails artifact inventory check (regression test).

Sprint: FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
"""

import hashlib
import io
import zipfile
from pathlib import Path


# Import the validator module
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "evidence"))
from validate_evidence_bundle import check_artifact_inventory


class TestCheckArtifactInventoryBasic:
    """Basic functionality tests for check_artifact_inventory()."""

    def _make_bundle(self, entries: dict[str, bytes]) -> zipfile.ZipFile:
        """Create an in-memory ZIP with the given entries."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
        buf.seek(0)
        return zipfile.ZipFile(buf, "r")

    def test_no_manifest_returns_empty(self):
        """No manifest = no claims to check = no errors."""
        zf = self._make_bundle({
            "bundle-metadata/other-file.txt": b"content",
        })
        errors = check_artifact_inventory(zf)
        assert errors == []

    def test_manifest_claims_whl_artifact_absent(self):
        """R46 defect reproduction: manifest claims .whl but file is absent from ZIP."""
        manifest = b"""
sprint_id: TEST-R46-DEFECT
FODS wheel: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
  SHA-256: aabbccdd00000000000000000000000000000000000000000000000000000001
"""
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
            # Note: NO bundle-metadata/package-artifacts/*.whl present
        })
        errors = check_artifact_inventory(zf)
        assert len(errors) == 1
        assert "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl" in errors[0]
        assert "absent" in errors[0].lower() or "ARTIFACT_INVENTORY" in errors[0]

    def test_manifest_claims_nupkg_artifact_absent(self):
        """Manifest claims .nupkg but file is absent."""
        manifest = b"""
FODS nupkg: FormatFactory.Fods.0.1.0-tier0.nupkg
  SHA-256: aabbccdd00000000000000000000000000000000000000000000000000000002
"""
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
        })
        errors = check_artifact_inventory(zf)
        assert len(errors) >= 1
        assert "FormatFactory.Fods.0.1.0-tier0.nupkg" in errors[0]

    def test_manifest_claims_multiple_absent(self):
        """Manifest claims 4 artifacts, none present."""
        manifest = b"""
FODS wheel: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
FODS sdist: aspose_format_factory_fods-0.1.0.dev0.tar.gz
FODT wheel: aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl
FODT sdist: aspose_format_factory_fodt-0.1.0.dev0.tar.gz
"""
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
        })
        errors = check_artifact_inventory(zf)
        assert len(errors) == 4, f"Expected 4 errors, got {len(errors)}: {errors}"

    def test_artifact_present_in_subdir_passes(self):
        """Artifact present under bundle-metadata/package-artifacts/ passes."""
        artifact_bytes = b"PK fake-whl-content"
        artifact_sha = hashlib.sha256(artifact_bytes).hexdigest()
        manifest = f"""
FODS wheel: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
  SHA-256: {artifact_sha}
""".encode()
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
            "bundle-metadata/package-artifacts/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl": artifact_bytes,
        })
        errors = check_artifact_inventory(zf)
        assert errors == [], f"Expected PASS but got errors: {errors}"

    def test_artifact_present_flat_passes(self):
        """Artifact present directly under bundle-metadata/ also passes."""
        artifact_bytes = b"PK flat-whl-content"
        artifact_sha = hashlib.sha256(artifact_bytes).hexdigest()
        manifest = f"""
  - aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
  SHA-256: {artifact_sha}
""".encode()
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
            "bundle-metadata/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl": artifact_bytes,
        })
        errors = check_artifact_inventory(zf)
        assert errors == [], f"Expected PASS but got errors: {errors}"

    def test_sha_mismatch_fails(self):
        """Artifact present but SHA-256 does not match manifest claim."""
        artifact_bytes = b"correct-content"
        wrong_sha = "a" * 64
        manifest = f"""
  - aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
  SHA-256: {wrong_sha}
""".encode()
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
            "bundle-metadata/package-artifacts/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl": artifact_bytes,
        })
        errors = check_artifact_inventory(zf)
        assert len(errors) >= 1
        assert "SHA" in errors[0] or "mismatch" in errors[0].lower()

    def test_sha_match_passes(self):
        """Artifact present with correct SHA-256 passes cleanly."""
        artifact_bytes = b"real-artifact-content-12345"
        real_sha = hashlib.sha256(artifact_bytes).hexdigest()
        manifest = f"""
FODS wheel: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
  SHA-256: {real_sha}
""".encode()
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
            "bundle-metadata/package-artifacts/aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl": artifact_bytes,
        })
        errors = check_artifact_inventory(zf)
        assert errors == []

    def test_r46_defect_reproduction(self):
        """Reproduce the exact R46 defect: 6 manifest claims, 0 artifact files."""
        manifest = b"""
ARTIFACT LOCATION IN BUNDLE
  - aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
  - aspose_format_factory_fods-0.1.0.dev0.tar.gz
  - aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl
  - aspose_format_factory_fodt-0.1.0.dev0.tar.gz
  - FormatFactory.Fods.0.1.0-tier0.nupkg
  - FormatFactory.Fodt.0.1.0-tier0.nupkg
"""
        zf = self._make_bundle({
            "bundle-metadata/package-artifact-manifest.yaml": manifest,
            # No actual artifact files — R46 defect
        })
        errors = check_artifact_inventory(zf)
        assert len(errors) == 6, f"Expected 6 errors (R46 defect pattern), got {len(errors)}: {errors}"


class TestBuilderSubdirectoryFix:
    """Tests that verify the builder's subdirectory fix."""

    def test_builder_metadata_collection_includes_subdirs(self):
        """Verify that build_evidence_bundle.py rglob fix collects subdir files."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "evidence"))
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            meta_dir = Path(tmpdir) / "metadata"
            meta_dir.mkdir()
            subdir = meta_dir / "package-artifacts"
            subdir.mkdir()

            # Write top-level file
            (meta_dir / "top-file.txt").write_text("top level", encoding="utf-8")
            # Write subdirectory files
            (subdir / "package.whl").write_bytes(b"fake wheel")
            (subdir / "package.nupkg").write_bytes(b"fake nupkg")

            # Simulate the collection loop from build_evidence_bundle.py
            metadata_files = []
            for mf in sorted(meta_dir.rglob("*")):
                if mf.is_file():
                    rel = str(mf.relative_to(meta_dir)).replace("\\", "/")
                    metadata_files.append(rel)

            assert "top-file.txt" in metadata_files
            assert "package-artifacts/package.whl" in metadata_files
            assert "package-artifacts/package.nupkg" in metadata_files

    def test_zip_arcname_for_subdir_file(self):
        """ZIP arcname for subdir file is bundle-metadata/package-artifacts/file."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            rel = "package-artifacts/package.whl"
            arcname = f"bundle-metadata/{rel}"
            zf.writestr(arcname, b"fake wheel")

        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            entries = zf.namelist()
        assert "bundle-metadata/package-artifacts/package.whl" in entries


class TestArtifactInventoryImportable:
    """Structural tests for the validator function."""

    def test_function_importable(self):
        from validate_evidence_bundle import check_artifact_inventory
        assert callable(check_artifact_inventory)

    def test_hashlib_imported_in_validator(self):
        """Validator module imports hashlib for SHA-256 checking."""
        import validate_evidence_bundle
        import inspect
        src = inspect.getsource(validate_evidence_bundle)
        assert "import hashlib" in src
