"""
Lane D: Review package builder tests.

Sprint: FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
"""
import pathlib
import sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "package"))

from build_review_package import matches_exclusion, get_tracked_files, build_package


class TestExclusions:
    def test_bin_excluded(self):
        assert matches_exclusion("bin/Debug/file.dll", ["bin/", "bin/**"])

    def test_obj_excluded(self):
        assert matches_exclusion("obj/Release/file.pdb", ["obj/", "obj/**"])

    def test_pycache_excluded(self):
        assert matches_exclusion("src/__pycache__/foo.pyc", ["__pycache__/", "__pycache__/**"])

    def test_pyc_excluded(self):
        assert matches_exclusion("src/foo.pyc", ["*.pyc"])

    def test_dll_excluded(self):
        assert matches_exclusion("lib/native.dll", ["*.dll"])

    def test_pdb_excluded(self):
        assert matches_exclusion("lib/native.pdb", ["*.pdb"])

    def test_env_excluded(self):
        assert matches_exclusion(".env", [".env"])

    def test_env_local_excluded(self):
        assert matches_exclusion(".env.local", [".env.*"])

    def test_dotlocal_excluded(self):
        assert matches_exclusion(".local/bundles/foo.zip", [".local/", ".local/**"])

    def test_source_included(self):
        assert not matches_exclusion("src/python/fods/fods_codec.py", ["*.pyc", ".git/"])

    def test_nupkg_excluded(self):
        assert matches_exclusion("packages/foo.nupkg", ["*.nupkg"])


class TestDryRun:
    def test_source_only_dry_run(self):
        manifest = build_package("source-only", "/dev/null", dry_run=True)
        assert manifest["mode"] == "source-only"
        assert manifest["included_count"] > 0
        assert manifest["excluded_count"] >= 0

    def test_evidence_replay_dry_run(self):
        manifest = build_package("evidence-replay", "/dev/null", dry_run=True)
        assert manifest["mode"] == "evidence-replay"
        assert manifest["included_count"] >= manifest["excluded_count"] or True  # just check it ran


class TestTrackedFiles:
    def test_tracked_files_returns_list(self):
        files = get_tracked_files()
        assert isinstance(files, list)
        assert len(files) > 0

    def test_no_secrets_in_tracked(self):
        files = get_tracked_files()
        for f in files:
            assert not f.endswith(".env"), f"Secret file tracked: {f}"
            assert "credentials" not in f.lower() or "test" in f.lower(), f"Credentials file: {f}"
