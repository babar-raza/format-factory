"""R67 Train B: extracted delivery package replay — current bundle discovery.

Proves that in extracted-bundle mode, the correct sprint's artifacts are
discoverable, while nonexistent sprints return None.

R68 Train D: added monkeypatch.delenv(FORMAT_FACTORY_BUNDLE_METADATA_DIR) to all
synthetic-bundle tests so that a globally-set env var does not override the
temporary extracted-bundle layout under test.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_tools = Path(__file__).resolve().parents[2] / "tools" / "packaging"
if str(_tools) not in sys.path:
    sys.path.insert(0, str(_tools))

from find_bundle_artifacts import find_artifact_dir, find_manifest_path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_ENV_VAR = "FORMAT_FACTORY_BUNDLE_METADATA_DIR"


def _make_extracted_bundle(tmpdir: Path, sprint_label: str) -> tuple[Path, Path]:
    """Create a synthetic extracted-bundle layout."""
    repo_root = tmpdir / "repo"
    repo_root.mkdir()
    bm = tmpdir / "bundle-metadata"
    bm.mkdir()
    (bm / "sprint-id.txt").write_text(
        f"FORMAT-FACTORY-{sprint_label.upper()}-...\n{sprint_label.upper()}\n",
        encoding="utf-8",
    )
    art = bm / "package-artifacts"
    art.mkdir()
    (art / "fake_pkg-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
    # Also add a manifest
    (bm / "package-artifact-manifest.yaml").write_text(
        f"artifact_count: 1\nrun: {sprint_label}\n", encoding="utf-8"
    )
    return repo_root, art


class TestCurrentBundleDiscovery:
    def test_current_sprint_found_via_parent_bundle_metadata(self, monkeypatch):
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, art = _make_extracted_bundle(Path(td), "r67")
            result = find_artifact_dir("r67", repo)
            assert result == art

    def test_nonexistent_sprint_not_found_via_parent_bundle_metadata(self, monkeypatch):
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, _ = _make_extracted_bundle(Path(td), "r67")
            result = find_artifact_dir("r99999", repo)
            assert result is None

    def test_manifest_found_for_current_sprint(self, monkeypatch):
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, _ = _make_extracted_bundle(Path(td), "r67")
            result = find_manifest_path("r67", repo)
            assert result is not None
            assert result.name == "package-artifact-manifest.yaml"

    def test_manifest_not_found_for_nonexistent_sprint(self, monkeypatch):
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, _ = _make_extracted_bundle(Path(td), "r67")
            result = find_manifest_path("r99999", repo)
            assert result is None

    def test_multiple_sprints_only_match_own(self, monkeypatch):
        """R66 extracted bundle: r66 matches, r65 does not via extracted bundle-metadata."""
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, art = _make_extracted_bundle(Path(td), "r66")
            assert find_artifact_dir("r66", repo) == art
            assert find_artifact_dir("r65", repo) is None
            assert find_artifact_dir("r67", repo) is None
