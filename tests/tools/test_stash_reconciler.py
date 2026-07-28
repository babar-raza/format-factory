from __future__ import annotations

# generated_by: codex

import json
import subprocess
from pathlib import Path

import pytest

from tools.recovery import stash_reconciler


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repository(tmp_path: Path) -> dict[str, Path | str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    write(repo / "kept.txt", "base\n")
    write(repo / "deleted.txt", "delete me\n")
    git(repo, "add", "kept.txt", "deleted.txt")
    git(repo, "commit", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")

    write(repo / "kept.txt", "stash\n")
    write(repo / "added.txt", "added\n")
    (repo / "deleted.txt").unlink()
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "stash tree")
    stash_commit = git(repo, "rev-parse", "HEAD")

    git(repo, "checkout", "--detach", base)
    write(repo / "divergent.txt", "main\n")
    git(repo, "add", "divergent.txt")
    git(repo, "commit", "-m", "main")
    main = git(repo, "rev-parse", "HEAD")

    worktree = tmp_path / "worktree"
    git(repo, "worktree", "add", "--detach", str(worktree), main)
    archive = tmp_path / "archive"
    archive.mkdir()
    write(archive / "SHA256-MANIFEST.json", "{}\n")
    return {
        "archive": archive,
        "base": base,
        "main": main,
        "repo": repo,
        "stash": stash_commit,
        "worktree": worktree,
    }


def test_inventory_is_deterministic(repository: dict[str, Path | str], tmp_path: Path) -> None:
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    common = [
        "--main-commit",
        str(repository["main"]),
        "--stash",
        f"0:{repository['stash']}:{repository['base']}",
    ]
    assert stash_reconciler.main.__module__
    args = stash_reconciler.parser().parse_args(["--repo", str(repository["repo"]), "inventory", *common, "--output", str(first)])
    assert args.func(args) == 0
    args = stash_reconciler.parser().parse_args(["--repo", str(repository["repo"]), "inventory", *common, "--output", str(second)])
    assert args.func(args) == 0
    assert first.read_bytes() == second.read_bytes()


def test_materialize_unique_and_idempotent(
    repository: dict[str, Path | str], tmp_path: Path
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"mode": "unique", "paths": ["kept.txt", "added.txt", "deleted.txt"]}), encoding="utf-8")
    receipt = tmp_path / "receipt.json"
    argv = [
        "--repo", str(repository["repo"]), "materialize",
        "--worktree", str(repository["worktree"]),
        "--stash-commit", str(repository["stash"]),
        "--base-commit", str(repository["base"]),
        "--manifest", str(manifest),
        "--archive-dir", str(repository["archive"]),
        "--receipt", str(receipt),
    ]
    args = stash_reconciler.parser().parse_args(argv)
    assert args.func(args) == 0
    assert (Path(repository["worktree"]) / "kept.txt").read_text() == "stash\n"
    assert (Path(repository["worktree"]) / "added.txt").read_text() == "added\n"
    assert not (Path(repository["worktree"]) / "deleted.txt").exists()
    args = stash_reconciler.parser().parse_args(argv)
    assert args.func(args) == 0
    result = json.loads(receipt.read_text(encoding="utf-8"))
    assert sorted(result["no_op_paths"]) == ["added.txt", "deleted.txt", "kept.txt"]


def test_refuses_root_worktree(repository: dict[str, Path | str], tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"mode": "unique", "paths": ["kept.txt"]}), encoding="utf-8")
    args = stash_reconciler.parser().parse_args([
        "--repo", str(repository["repo"]), "materialize",
        "--worktree", str(repository["repo"]),
        "--stash-commit", str(repository["stash"]),
        "--base-commit", str(repository["base"]),
        "--manifest", str(manifest),
        "--archive-dir", str(repository["archive"]),
        "--receipt", str(tmp_path / "receipt.json"),
    ])
    with pytest.raises(ValueError, match="root worktree"):
        args.func(args)


@pytest.mark.parametrize("path", [".git/config", ".local/state.json", "../escape"])
def test_refuses_prohibited_paths(path: str) -> None:
    with pytest.raises(ValueError):
        stash_reconciler.safe_path(path)
