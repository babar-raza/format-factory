"""
R44 Lane 1B: Tests for replay_extracted_bundle.py pycache exclusion fix.

Verifies:
1. _should_exclude correctly identifies __pycache__ directories.
2. _should_exclude correctly identifies .pyc files.
3. _should_exclude correctly identifies .pytest_cache directories.
4. _should_exclude does NOT exclude regular .py source files.
5. extracted_dir_to_zip excludes __pycache__ files when repacking.
6. sys.dont_write_bytecode is set to True at module import time.
7. Repacked ZIP does not contain any __pycache__ entries.

Sprint: FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
"""

import pathlib
import sys
import zipfile


# Load module under test
_TOOLS_EVIDENCE = pathlib.Path(__file__).resolve().parents[2] / "tools" / "evidence"
sys.path.insert(0, str(_TOOLS_EVIDENCE))
from replay_extracted_bundle import _should_exclude, extracted_dir_to_zip  # noqa: E402


class TestShouldExclude:
    """Unit tests for _should_exclude()."""

    def test_pycache_directory_excluded(self, tmp_path):
        """Files inside __pycache__ must be excluded."""
        f = tmp_path / "__pycache__" / "foo.cpython-313.pyc"
        assert _should_exclude(f) is True

    def test_pyc_file_excluded(self, tmp_path):
        """Standalone .pyc files must be excluded."""
        f = tmp_path / "tools" / "foo.pyc"
        assert _should_exclude(f) is True

    def test_pytest_cache_excluded(self, tmp_path):
        """Files inside .pytest_cache must be excluded."""
        f = tmp_path / ".pytest_cache" / "v" / "cache" / "lastfailed"
        assert _should_exclude(f) is True

    def test_mypy_cache_excluded(self, tmp_path):
        """Files inside .mypy_cache must be excluded."""
        f = tmp_path / ".mypy_cache" / "3.13" / "foo.json"
        assert _should_exclude(f) is True

    def test_regular_py_file_not_excluded(self, tmp_path):
        """Regular .py source files must NOT be excluded."""
        f = tmp_path / "tools" / "evidence" / "validate_evidence_bundle.py"
        assert _should_exclude(f) is False

    def test_regular_md_file_not_excluded(self, tmp_path):
        """Regular .md files must NOT be excluded."""
        f = tmp_path / "reports" / "r44" / "final-verdict.md"
        assert _should_exclude(f) is False

    def test_yaml_file_not_excluded(self, tmp_path):
        """YAML files must NOT be excluded."""
        f = tmp_path / "tools" / "evidence" / "contracts" / "r44.yaml"
        assert _should_exclude(f) is False

    def test_pdb_file_excluded(self, tmp_path):
        """PDB debug files must be excluded."""
        f = tmp_path / "src" / "net" / "fods" / "FormatFactory.Fods.pdb"
        assert _should_exclude(f) is True


class TestExtractedDirToZip:
    """Integration tests for extracted_dir_to_zip()."""

    def test_pycache_not_in_repacked_zip(self, tmp_path):
        """__pycache__ files must not appear in the repacked ZIP."""
        # Set up a fake extracted bundle structure
        repo_dir = tmp_path / "repo"
        (repo_dir / "tools" / "evidence").mkdir(parents=True)
        (repo_dir / "tools" / "evidence" / "validate_evidence_bundle.py").write_text(
            "# validator", encoding="utf-8"
        )
        # Create pycache that would be created by Python imports
        pycache = repo_dir / "tools" / "evidence" / "__pycache__"
        pycache.mkdir(parents=True)
        (pycache / "validate_evidence_bundle.cpython-313.pyc").write_bytes(b"\x00\x01\x02")

        meta_dir = tmp_path / "bundle-metadata"
        meta_dir.mkdir()
        (meta_dir / "sprint-id.txt").write_text("sprint_id: test", encoding="utf-8")

        buf = extracted_dir_to_zip(tmp_path)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()

        pycache_entries = [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
        assert not pycache_entries, f"Repacked ZIP must not contain pycache: {pycache_entries}"

    def test_regular_files_included_in_repack(self, tmp_path):
        """Regular source files must appear in the repacked ZIP."""
        repo_dir = tmp_path / "repo"
        (repo_dir / "tools").mkdir(parents=True)
        (repo_dir / "tools" / "myfile.py").write_text("# source", encoding="utf-8")

        meta_dir = tmp_path / "bundle-metadata"
        meta_dir.mkdir()
        (meta_dir / "test.txt").write_text("test content", encoding="utf-8")

        buf = extracted_dir_to_zip(tmp_path)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()

        assert "repo/tools/myfile.py" in names, "Source .py files must be included"
        assert "bundle-metadata/test.txt" in names, "Metadata files must be included"

    def test_pytest_cache_not_in_repacked_zip(self, tmp_path):
        """.pytest_cache files must not appear in the repacked ZIP."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir(parents=True)
        (repo_dir / "normal.txt").write_text("ok", encoding="utf-8")
        pytest_cache = repo_dir / ".pytest_cache" / "v" / "cache"
        pytest_cache.mkdir(parents=True)
        (pytest_cache / "lastfailed").write_text("{}", encoding="utf-8")

        meta_dir = tmp_path / "bundle-metadata"
        meta_dir.mkdir()
        (meta_dir / "meta.txt").write_text("meta", encoding="utf-8")

        buf = extracted_dir_to_zip(tmp_path)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()

        cache_entries = [n for n in names if ".pytest_cache" in n]
        assert not cache_entries, f"Repacked ZIP must not contain .pytest_cache: {cache_entries}"


class TestDontWriteBytecode:
    """Verify sys.dont_write_bytecode is set by module import."""

    def test_dont_write_bytecode_is_set(self):
        """Importing replay_extracted_bundle must set sys.dont_write_bytecode = True."""
        assert sys.dont_write_bytecode is True, (
            "replay_extracted_bundle.py must set sys.dont_write_bytecode = True "
            "to prevent __pycache__ creation during replay"
        )
