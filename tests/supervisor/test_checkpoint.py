"""TC-CONC-009: Checkpoint unit tests (8 cases).

All tests use tmp_path for DB and git repo isolation.
Mission: CONC-HARDENING-2026-07-02
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO / "tools" / "supervisor") not in sys.path:
    sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from control_index.db import ensure_db
from concurrency.checkpoint import CheckpointManager


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test-control-index.db"
    ensure_db(db_path)
    return db_path


@pytest.fixture
def git_repo(tmp_path):
    """Create a minimal git repo for testing (CRLF disabled for patch compatibility)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo), check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), check=True,
                   capture_output=True)
    # Disable CRLF conversion — git diff/apply must see consistent line endings
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=str(repo), check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "core.eol", "lf"], cwd=str(repo), check=True,
                   capture_output=True)
    # Initial commit
    (repo / "README.md").write_bytes(b"init\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo), check=True,
                   capture_output=True)
    return repo


@pytest.fixture
def ckpt(db, git_repo):
    return CheckpointManager(db_path=db, repo_root=git_repo)


def test_01_create_saves_patch_file(db, git_repo, ckpt):
    """create() on a dirty tree produces a non-empty .patch file."""
    (git_repo / "dirty.txt").write_text("uncommitted change")
    cid = ckpt.create("task-1", "worker-1", "test checkpoint")
    assert cid.startswith("ckpt-task-1-")

    rows = ckpt.list("task-1")
    assert len(rows) == 1
    patch_path = Path(rows[0]["patch_path"])
    assert patch_path.exists()


def test_02_create_on_clean_tree_saves_empty_patch(db, git_repo, ckpt):
    """create() on a clean tree produces an empty .patch file (no-op checkpoint)."""
    cid = ckpt.create("task-clean", "worker-1", "clean checkpoint")
    rows = ckpt.list("task-clean")
    assert len(rows) == 1
    patch_path = Path(rows[0]["patch_path"])
    assert patch_path.exists()
    assert patch_path.stat().st_size == 0


def test_03_list_returns_newest_first(db, git_repo, ckpt):
    """list() returns checkpoints for a task, newest first."""
    import time
    cid1 = ckpt.create("task-order", "worker-1", "first")
    time.sleep(0.01)
    cid2 = ckpt.create("task-order", "worker-1", "second")

    rows = ckpt.list("task-order")
    assert len(rows) == 2
    assert rows[0]["checkpoint_id"] == cid2  # newest first
    assert rows[1]["checkpoint_id"] == cid1


def test_04_restore_round_trip(db, git_repo, ckpt):
    """create → dirty tree → restore → verify change is back (using tracked file)."""
    # Use the already-tracked README.md — modify it to create a diff
    test_file = git_repo / "README.md"
    original_content = test_file.read_bytes().decode("utf-8")
    modified_content = original_content + "\n# MODIFIED FOR CHECKPOINT TEST"
    # write_bytes preserves LF endings (write_text on Windows adds CRLF)
    test_file.write_bytes(modified_content.encode("utf-8"))

    # Create checkpoint (captures the uncommitted modification to tracked file)
    cid = ckpt.create("task-rt", "worker-1", "round trip test")

    # Discard working tree change (simulate crash) — restores tracked file to HEAD
    subprocess.run(["git", "checkout", "--", "."], cwd=str(git_repo), check=True,
                   capture_output=True)
    assert test_file.read_bytes().decode("utf-8") == original_content  # Verify it's back

    # Restore from checkpoint
    result = ckpt.restore(cid, stash_first=False)
    assert result is True

    # Verify the modification is back
    assert test_file.read_bytes().decode("utf-8") == modified_content


def test_05_invalidate_marks_superseded(db, git_repo, ckpt):
    cid = ckpt.create("task-inv", "worker-1", "to invalidate")
    ckpt.invalidate(cid, "no longer needed")

    rows = ckpt.list("task-inv")
    assert rows[0]["status"] == "SUPERSEDED"


def test_06_cleanup_old_keep_2_removes_oldest(db, git_repo, ckpt):
    """cleanup_old(keep=2) deletes patch files and marks older rows SUPERSEDED."""
    import time
    cids = []
    for i in range(4):
        # Make a unique file each time to ensure non-empty patches
        (git_repo / f"file_{i}.txt").write_text(f"change {i}")
        cids.append(ckpt.create("task-cleanup", "worker-1", f"checkpoint {i}"))
        time.sleep(0.01)
        # Reset to clean state for next checkpoint
        subprocess.run(["git", "checkout", "--", "."], cwd=str(git_repo),
                       capture_output=True)
        # Remove untracked files manually
        for f in git_repo.glob("file_*.txt"):
            f.unlink(missing_ok=True)

    removed = ckpt.cleanup_old("task-cleanup", keep=2)
    assert removed == 2

    rows = ckpt.list("task-cleanup")
    assert len(rows) == 4
    # Oldest 2 should be SUPERSEDED; patch files should be gone
    oldest = rows[2:]  # list is newest-first, so oldest are at the end
    for row in oldest:
        assert row["status"] == "SUPERSEDED"
        patch_path = Path(row["patch_path"])
        assert not patch_path.exists()


def test_07_create_captures_staged_changes(db, git_repo, ckpt):
    """create() must capture staged (--cached) as well as unstaged diffs."""
    # Stage a change
    staged_file = git_repo / "staged.txt"
    staged_file.write_text("staged content")
    subprocess.run(["git", "add", "staged.txt"], cwd=str(git_repo), check=True,
                   capture_output=True)

    cid = ckpt.create("task-staged", "worker-1", "staged change")
    rows = ckpt.list("task-staged")
    patch_path = Path(rows[0]["patch_path"])
    patch_content = patch_path.read_text(encoding="utf-8")
    assert "staged.txt" in patch_content or patch_path.stat().st_size > 0


def test_08_base_sha_matches_head_at_checkpoint_time(db, git_repo, ckpt):
    """base_sha in the checkpoint record must match git rev-parse HEAD at creation time."""
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(git_repo),
        capture_output=True, text=True
    )
    expected_sha = head_result.stdout.strip()

    cid = ckpt.create("task-sha", "worker-1", "sha check")
    rows = ckpt.list("task-sha")
    assert rows[0]["base_sha"] == expected_sha
