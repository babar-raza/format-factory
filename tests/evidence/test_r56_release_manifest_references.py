"""
test_r56_release_manifest_references.py — R56 Train B: Release manifest reference integrity tests.

Validates the R56 rule: release manifest entries that reference individual manifest files
must point to files that actually exist in the repo (i.e., are included in the bundle).

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R55-006
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def check_release_manifest_references(zf) -> "list[str]":
    """Check that release manifest format entries reference files that exist in the bundle repo.

    Reads release-manifests/python-foss/_matrix.yaml from the bundle and checks that each
    format's `manifest:` field points to a file that is present under repo/.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []
    matrix_entry = None
    for entry in zf.namelist():
        if entry.endswith("release-manifests/python-foss/_matrix.yaml"):
            matrix_entry = entry
            break

    if not matrix_entry:
        return errors  # no matrix, no check

    try:
        matrix_content = zf.read(matrix_entry).decode("utf-8", errors="replace")
    except Exception as exc:
        errors.append(f"RELEASE_MANIFEST_UNREADABLE: {exc}")
        return errors

    # Find all manifest: references in the YAML
    import re
    manifest_refs = re.findall(r"^\s+manifest:\s+(.+)$", matrix_content, re.MULTILINE)
    all_entries = set(zf.namelist())

    for ref in manifest_refs:
        ref = ref.strip()
        # Manifest refs look like "release-manifests/python-foss/fods.yaml"
        # In the bundle they appear under repo/
        repo_path = f"repo/{ref}"
        if repo_path not in all_entries:
            errors.append(
                f"RELEASE_MANIFEST_MISSING_REFERENCE: _matrix.yaml references manifest={ref!r} "
                f"but {repo_path!r} is not in the bundle. "
                f"Create the manifest file or remove the reference. (R56-IV-R55-006)"
            )
    return errors


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _make_bundle_with_matrix(matrix_content: str, extra_files: dict = None) -> "zipfile.ZipFile":
    """Create in-memory bundle with the given _matrix.yaml and optional extra files."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo/release-manifests/python-foss/_matrix.yaml", matrix_content)
        if extra_files:
            for path, content in extra_files.items():
                zf.writestr(path, content)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


MATRIX_WITH_EXISTING_REFS = """\
formats:
  - format_id: zst
    manifest: release-manifests/python-foss/zst.yaml
  - format_id: fodp
    manifest: release-manifests/python-foss/fodp.yaml
"""

MATRIX_WITH_MISSING_FODS_FODT = """\
formats:
  - format_id: zst
    manifest: release-manifests/python-foss/zst.yaml
  - format_id: fods
    manifest: release-manifests/python-foss/fods.yaml
  - format_id: fodt
    manifest: release-manifests/python-foss/fodt.yaml
"""


class TestReleaseManifestReferences:

    def test_all_references_present_passes(self):
        """All manifest references pointing to existing bundle files pass."""
        extra = {
            "repo/release-manifests/python-foss/zst.yaml": "format_id: zst\n",
            "repo/release-manifests/python-foss/fodp.yaml": "format_id: fodp\n",
        }
        with _make_bundle_with_matrix(MATRIX_WITH_EXISTING_REFS, extra) as zf:
            errors = check_release_manifest_references(zf)
        assert errors == [], f"All present refs must pass: {errors}"

    def test_missing_fods_manifest_fails(self):
        """_matrix.yaml references fods.yaml that doesn't exist — fails (IV-R55-006)."""
        # Only include zst.yaml; fods.yaml and fodt.yaml are absent
        extra = {
            "repo/release-manifests/python-foss/zst.yaml": "format_id: zst\n",
        }
        with _make_bundle_with_matrix(MATRIX_WITH_MISSING_FODS_FODT, extra) as zf:
            errors = check_release_manifest_references(zf)
        assert errors, "Missing fods.yaml reference must fail"
        assert any("fods.yaml" in e for e in errors), f"fods.yaml must be in error: {errors}"

    def test_missing_fodt_manifest_fails(self):
        """_matrix.yaml references fodt.yaml that doesn't exist — fails."""
        extra = {
            "repo/release-manifests/python-foss/zst.yaml": "format_id: zst\n",
            "repo/release-manifests/python-foss/fods.yaml": "format_id: fods\n",
            # fodt.yaml intentionally absent
        }
        with _make_bundle_with_matrix(MATRIX_WITH_MISSING_FODS_FODT, extra) as zf:
            errors = check_release_manifest_references(zf)
        assert errors, "Missing fodt.yaml reference must fail"
        assert any("fodt.yaml" in e for e in errors), f"fodt.yaml must be in error: {errors}"

    def test_no_matrix_file_passes(self):
        """Bundle without _matrix.yaml is not penalized (not all sprints have release manifests)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "test")
        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            errors = check_release_manifest_references(zf)
        assert errors == [], f"No matrix should not fail: {errors}"

    def test_r55_defect_scenario_reproduced(self):
        """Reproduce R55 IV-R55-006: _matrix.yaml references fods.yaml and fodt.yaml but neither exists."""
        r55_matrix = """\
formats:
  - format_id: zst
    manifest: release-manifests/python-foss/zst.yaml
  - format_id: fods
    manifest: release-manifests/python-foss/fods.yaml
  - format_id: fodt
    manifest: release-manifests/python-foss/fodt.yaml
"""
        # Provide zst.yaml but not fods.yaml or fodt.yaml
        extra = {
            "repo/release-manifests/python-foss/zst.yaml": "format_id: zst\n",
        }
        with _make_bundle_with_matrix(r55_matrix, extra) as zf:
            errors = check_release_manifest_references(zf)
        assert len(errors) >= 2, f"Must catch both missing fods.yaml and fodt.yaml: {errors}"
        missing = [e for e in errors if "fods.yaml" in e or "fodt.yaml" in e]
        assert len(missing) == 2, f"Both fods.yaml and fodt.yaml must be reported: {errors}"
        assert any("RELEASE_MANIFEST_MISSING_REFERENCE" in e for e in errors)

    def test_all_refs_present_with_fods_fodt_passes(self):
        """If fods.yaml and fodt.yaml are both present, passes."""
        extra = {
            "repo/release-manifests/python-foss/zst.yaml": "format_id: zst\n",
            "repo/release-manifests/python-foss/fods.yaml": "format_id: fods\n",
            "repo/release-manifests/python-foss/fodt.yaml": "format_id: fodt\n",
        }
        with _make_bundle_with_matrix(MATRIX_WITH_MISSING_FODS_FODT, extra) as zf:
            errors = check_release_manifest_references(zf)
        assert errors == [], f"All present refs must pass: {errors}"
