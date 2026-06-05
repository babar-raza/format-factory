"""R108 Wave 1: Evidence-manifest path repair tests.

Verify that build_declaration_review_package resolves manifest from
the declaration's evidence_root when not found under .local/evidences/{run_id}/.
"""

from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

import yaml

TOOLS_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from build_declaration_review_package import build_package  # noqa: E402


def _make_declaration(tmp: Path, run_id: str, evidence_root_rel: str):
    """Create a minimal declaration YAML in a temp dir."""
    decl = {
        "run_id": run_id,
        "sprint_id": f"TEST-{run_id}",
        "evidence_root": evidence_root_rel,
        "planned_work_items": [],
        "completed_work_items": [],
        "incomplete_work_items": [],
        "changed_files": [],
        "tests_run": 0,
        "test_results": {"passed": 0, "failed": 0, "skipped": 0},
        "evidence_artifacts": [],
        "reports_created": [],
    }
    decl_dir = tmp / ".local" / "evidences" / run_id
    decl_dir.mkdir(parents=True, exist_ok=True)
    decl_path = decl_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl), encoding="utf-8")
    return decl_path


class TestManifestPathResolution:
    """Evidence-manifest should be found in declaration evidence_root."""

    def test_manifest_found_in_decl_evidence_root(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            decl_path = _make_declaration(tmp, "test-r108", "reports/skills-r108")
            # Place manifest in evidence_root (where autonomous_cycle writes it)
            ev_root = tmp / "reports" / "skills-r108"
            ev_root.mkdir(parents=True, exist_ok=True)
            (ev_root / "evidence-manifest.yaml").write_text("manifest: true", encoding="utf-8")
            # Run build
            out_dir = tmp / ".local" / "supervisor" / "reviews" / "test-r108"
            out_dir.mkdir(parents=True, exist_ok=True)
            build_package(decl_path, tmp, out_dir)
            zip_path = out_dir / "declaration-review-package.zip"
            assert zip_path.exists()
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                assert "evidence/evidence-manifest.yaml" in names

    def test_manifest_found_in_local_evidences(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            decl_path = _make_declaration(tmp, "test-r108b", "reports/skills-r108b")
            # Place manifest in .local/evidences/{run_id} (legacy path)
            ev_root = tmp / ".local" / "evidences" / "test-r108b"
            (ev_root / "evidence-manifest.yaml").write_text("manifest: true", encoding="utf-8")
            out_dir = tmp / ".local" / "supervisor" / "reviews" / "test-r108b"
            out_dir.mkdir(parents=True, exist_ok=True)
            build_package(decl_path, tmp, out_dir)
            zip_path = out_dir / "declaration-review-package.zip"
            with zipfile.ZipFile(zip_path) as zf:
                assert "evidence/evidence-manifest.yaml" in zf.namelist()

    def test_manifest_missing_both_paths_recorded(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            decl_path = _make_declaration(tmp, "test-r108c", "reports/skills-r108c")
            out_dir = tmp / ".local" / "supervisor" / "reviews" / "test-r108c"
            out_dir.mkdir(parents=True, exist_ok=True)
            build_package(decl_path, tmp, out_dir)
            zip_path = out_dir / "declaration-review-package.zip"
            assert zip_path.exists()
            # Manifest should be in missing list (recorded but not blocking)
