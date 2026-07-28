"""Regression tests for linked-worktree skill-guard root resolution."""

from __future__ import annotations

import runpy
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".hooks" / "pre-commit-skill-guard"


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def test_linked_hook_resolves_active_worktree(tmp_path: Path, monkeypatch) -> None:
    shared = tmp_path / "shared"
    linked = tmp_path / "linked"
    shared.mkdir()
    _git("init", cwd=shared)
    _git("config", "user.email", "test@example.invalid", cwd=shared)
    _git("config", "user.name", "Format Factory Test", cwd=shared)
    tracked = shared / "tracked.txt"
    tracked.write_text("baseline\n", encoding="utf-8")
    _git("add", "tracked.txt", cwd=shared)
    _git("commit", "-m", "baseline", cwd=shared)
    _git("worktree", "add", "-b", "linked-test", str(linked), cwd=shared)

    monkeypatch.chdir(linked)
    namespace = runpy.run_path(str(HOOK), run_name="worktree_skill_guard")

    assert namespace["REPO_ROOT"] == linked.resolve()
    assert namespace["TRANSCRIPT_DIRS"] == [
        linked.resolve() / ".local" / "transcripts",
        linked.resolve() / "reports",
    ]

    changed = linked / "src" / "python" / "example.py"
    changed.parent.mkdir(parents=True)
    changed.write_text("value = 1\n", encoding="utf-8")
    _git("add", "src/python/example.py", cwd=linked)
    assert namespace["get_staged_files"]() == ["src/python/example.py"]


def test_linked_hook_uses_git_environment_when_invoked_from_shared_root(
    tmp_path: Path, monkeypatch
) -> None:
    """Git may run a shared hook from the primary root with a linked index."""

    shared = tmp_path / "shared"
    linked = tmp_path / "linked"
    shared.mkdir()
    _git("init", cwd=shared)
    _git("config", "user.email", "test@example.invalid", cwd=shared)
    _git("config", "user.name", "Format Factory Test", cwd=shared)
    (shared / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    _git("add", "tracked.txt", cwd=shared)
    _git("commit", "-m", "baseline", cwd=shared)
    _git("worktree", "add", "-b", "environment-test", str(linked), cwd=shared)

    changed = linked / "src" / "python" / "example.py"
    changed.parent.mkdir(parents=True)
    changed.write_text("value = 1\n", encoding="utf-8")
    _git("add", "src/python/example.py", cwd=linked)
    linked_git_dir = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=linked,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    monkeypatch.chdir(shared)
    monkeypatch.setenv("GIT_DIR", linked_git_dir)
    monkeypatch.setenv("GIT_INDEX_FILE", str(Path(linked_git_dir) / "index"))
    namespace = runpy.run_path(str(HOOK), run_name="environment_worktree_guard")

    assert namespace["REPO_ROOT"] == linked.resolve()
    assert namespace["get_staged_files"]() == ["src/python/example.py"]


def test_non_git_execution_uses_physical_checkout(monkeypatch, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)

    namespace = runpy.run_path(str(HOOK), run_name="standalone_skill_guard")

    assert namespace["REPO_ROOT"] == HOOK.resolve().parent.parent
