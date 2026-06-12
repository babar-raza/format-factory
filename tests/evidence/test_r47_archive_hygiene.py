"""
R47 Lane D: Source archive hygiene guard tests.

Two distinct test modes:
  Git mode (normal CI/dev): Uses git ls-files to verify no compiled artifacts are tracked.
  No-Git mode (extracted bundle replay): Reads .gitignore directly to verify compiled
  artifact patterns are excluded. Does NOT claim archive hygiene was proved via git.

Why separate modes: "no compiled artifacts in git" and "gitignore excludes compiled
patterns" are different invariants. The first requires a live git repo. The second
can be checked in any extracted source archive.
"""
import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

_COMPILED_ARTIFACT_PATTERNS = [
    r"\.pyc$",
    r"(^|/)__pycache__(/|$)",
    r"(^|/)bin/",
    r"(^|/)obj/",
    r"\.dll$",
    r"\.pdb$",
    r"\.pytest_cache",
]

_REQUIRED_GITIGNORE_ENTRIES = [
    "__pycache__/",
    "*.pyc",
    "bin/",
    "obj/",
    "*.dll",
    "*.pdb",
    ".pytest_cache/",
]


class TestGitTrackedArtifacts:
    """Guard: no compiled artifacts tracked in git (Git-mode only)."""

    def test_no_pyc_or_pycache_in_git_tracking(self):
        """*.pyc and __pycache__ must not appear in git-tracked files."""
        git_dir = REPO_ROOT / ".git"
        if not git_dir.exists():
            pytest.skip("No .git directory — Git-mode check not applicable")
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30,
        )
        tracked = result.stdout.splitlines()
        offenders = [f for f in tracked if f.endswith(".pyc") or "__pycache__" in f]
        assert not offenders, (
            f"Compiled Python artifacts are git-tracked: {offenders[:5]}. "
            "Remove them and update .gitignore."
        )

    def test_no_dotnet_build_artifacts_in_git_tracking(self):
        """.dll, .pdb, bin/, obj/ must not appear in git-tracked files."""
        git_dir = REPO_ROOT / ".git"
        if not git_dir.exists():
            pytest.skip("No .git directory — Git-mode check not applicable")
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30,
        )
        tracked = result.stdout.splitlines()
        offenders = [
            f for f in tracked
            if f.endswith((".dll", ".pdb")) or "/bin/" in f or "/obj/" in f
        ]
        assert not offenders, (
            f".NET build artifacts are git-tracked: {offenders[:5]}. "
            "Add bin/, obj/, *.dll, *.pdb to .gitignore and unstage these files."
        )


class TestGitignoreCoverage:
    """Guard: .gitignore must exclude known compiled artifact patterns.

    These tests run in both Git-mode AND no-Git extracted-bundle replay mode,
    because .gitignore is committed and therefore present in extracted archives.
    """

    def test_gitignore_exists(self):
        gitignore = REPO_ROOT / ".gitignore"
        assert gitignore.exists(), (
            ".gitignore not found. A .gitignore is required to prevent compiled "
            "artifacts from being accidentally committed or included in source archives."
        )

    def test_gitignore_excludes_python_compiled_artifacts(self):
        """__pycache__/ and *.pyc must be in .gitignore."""
        gitignore = REPO_ROOT / ".gitignore"
        content = gitignore.read_text(encoding="utf-8")
        required = ["__pycache__/", "*.pyc"]
        missing = [r for r in required if r not in content]
        assert not missing, (
            f".gitignore missing Python compiled artifact exclusions: {missing}. "
            "Add these entries to prevent source archive contamination."
        )

    def test_gitignore_excludes_dotnet_build_artifacts(self):
        """bin/, obj/, *.dll, *.pdb must be in .gitignore."""
        gitignore = REPO_ROOT / ".gitignore"
        content = gitignore.read_text(encoding="utf-8")
        required = ["bin/", "obj/", "*.dll", "*.pdb"]
        missing = [r for r in required if r not in content]
        assert not missing, (
            f".gitignore missing .NET build artifact exclusions: {missing}. "
            "Add these entries to prevent build output contamination."
        )

    def test_gitignore_excludes_local_build_outputs(self):
        """.local/ (local build outputs) must be in .gitignore."""
        gitignore = REPO_ROOT / ".gitignore"
        content = gitignore.read_text(encoding="utf-8")
        assert ".local/" in content or ".local/**" in content, (
            ".gitignore missing .local/ exclusion. "
            "Local build outputs must not be committed."
        )

    def test_gitignore_excludes_evidence_zips(self):
        """evidence-bundles/*.zip must be in .gitignore."""
        gitignore = REPO_ROOT / ".gitignore"
        content = gitignore.read_text(encoding="utf-8")
        assert "evidence-bundles/*.zip" in content, (
            ".gitignore missing evidence-bundles/*.zip. "
            "Evidence ZIPs must not be committed to prevent repo bloat."
        )

    def test_gitignore_no_git_replay_mode_documented(self):
        """In no-Git mode, this test confirms hygiene via .gitignore text (not git ls-files)."""
        git_dir = REPO_ROOT / ".git"
        gitignore = REPO_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore must be present even in no-Git extracted replay"
        content = gitignore.read_text(encoding="utf-8")
        # Verify the critical patterns are present for no-Git replay
        patterns_present = [r for r in _REQUIRED_GITIGNORE_ENTRIES if r in content]
        patterns_missing = [r for r in _REQUIRED_GITIGNORE_ENTRIES if r not in content]
        if not git_dir.exists():
            # No-Git mode: .gitignore text is our only hygiene proof
            assert not patterns_missing, (
                f"No-Git replay hygiene check FAIL — .gitignore missing: {patterns_missing}"
            )
        else:
            # Git mode: gitignore text check supplements git ls-files checks above
            assert not patterns_missing, (
                f".gitignore missing entries: {patterns_missing}"
            )
