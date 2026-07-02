"""Git-diff-based checkpoint manager for uncommitted working-tree state.

Creates recoverable patch files from `git diff HEAD` before risky operations,
preventing work loss when concurrent agents or restarts wipe the working tree.

Usage:
    from tools.supervisor.concurrency.checkpoint import CheckpointManager

    ckpt = CheckpointManager(db_path=db, repo_root=repo)
    checkpoint_id = ckpt.create("task-id", "worker-id", "pre-sprint snapshot")
    # ... work happens, something goes wrong ...
    ckpt.restore(checkpoint_id)  # patches applied back

Checkpoint files stored in .local/supervisor/checkpoints/ (gitignored via .local/).

Mission: CONC-HARDENING-2026-07-02
"""
from __future__ import annotations

import json
import secrets
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path

from .errors import CheckpointError, StaleBaseRevision

CHECKPOINT_SUBDIR = Path(".local") / "supervisor" / "checkpoints"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_git(args: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _import_db_funcs():
    """Import ensure_db, supporting both repo-root and tools/supervisor sys.path contexts."""
    try:
        from control_index.db import ensure_db  # supervisor/ on sys.path
        return ensure_db
    except ImportError:
        pass
    import sys
    _repo = Path(__file__).resolve().parents[3]
    if str(_repo) not in sys.path:
        sys.path.insert(0, str(_repo))
    from tools.supervisor.control_index.db import ensure_db  # repo root on sys.path
    return ensure_db


def _get_db_connection(db_path: Path):
    return _import_db_funcs()(db_path)


class CheckpointManager:
    """Git-diff-based checkpoint manager.

    Parameters
    ----------
    db_path:
        Path to control-index.db (for metadata storage)
    repo_root:
        Repository root; defaults to cwd
    """

    def __init__(self, db_path: Path, repo_root: Path | None = None) -> None:
        self.db_path = Path(db_path)
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._checkpoint_dir = self.repo_root / CHECKPOINT_SUBDIR
        _import_db_funcs()(self.db_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(
        self,
        task_id: str,
        worker_id: str,
        description: str = "",
    ) -> str:
        """Capture current uncommitted working-tree and staged diffs as a patch.

        Safe to call on a clean tree — writes an empty patch file.
        Returns the checkpoint_id.

        Captured state:
        - git diff --cached HEAD  (staged changes)
        - git diff HEAD           (unstaged changes relative to HEAD)
        """
        cid = (
            f"ckpt-{task_id[:32]}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-"
            f"{secrets.token_hex(4)}"
        )

        # Get HEAD SHA
        head_result = _run_git(["rev-parse", "HEAD"], self.repo_root, timeout=10)
        base_sha = head_result.stdout.strip() or "unknown"

        # Capture diffs
        staged_result = _run_git(["diff", "--cached", "HEAD"], self.repo_root)
        unstaged_result = _run_git(["diff", "HEAD"], self.repo_root)
        patch_content = staged_result.stdout + unstaged_result.stdout

        # Changed files
        status_result = _run_git(["status", "--porcelain"], self.repo_root, timeout=10)
        changed_files: list[str] = []
        for line in status_result.stdout.splitlines():
            line = line.strip()
            if line and len(line) > 2:
                changed_files.append(line[2:].strip())

        # Write patch file
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        patch_path = self._checkpoint_dir / f"{cid}.patch"
        # write_bytes preserves LF endings — write_text on Windows would add CRLF
        # which breaks git apply when context lines don't match the committed LF content
        patch_path.write_bytes(patch_content.encode("utf-8"))

        # Register in DB
        conn = _get_db_connection(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO concurrency_checkpoints
                (checkpoint_id, task_id, worker_id, description,
                 base_sha, patch_path, changed_files, created_at, status)
                VALUES (?,?,?,?,?,?,?,?,'VALID')
                """,
                (
                    cid, task_id, worker_id, description,
                    base_sha, str(patch_path.resolve()),
                    json.dumps(changed_files), _now_iso(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return cid

    def restore(self, checkpoint_id: str, *, stash_first: bool = True) -> bool:
        """Apply checkpoint patch back to the working tree.

        Parameters
        ----------
        checkpoint_id:
            ID returned by create()
        stash_first:
            If True and tree is dirty, git stash before applying.

        Returns True on success, False if git apply fails.
        Emits StaleBaseRevision warning if base_sha != current HEAD.
        Raises CheckpointError if checkpoint or patch file is missing.
        """
        conn = _get_db_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM concurrency_checkpoints WHERE checkpoint_id=?",
                (checkpoint_id,),
            ).fetchone()
        finally:
            conn.close()

        if not row:
            raise CheckpointError(f"Checkpoint not found: {checkpoint_id}")

        patch_path = Path(row["patch_path"])
        if not patch_path.exists():
            raise CheckpointError(f"Patch file missing: {patch_path}")

        # Check for stale base
        head_result = _run_git(["rev-parse", "HEAD"], self.repo_root, timeout=10)
        current_sha = head_result.stdout.strip()
        if current_sha and row["base_sha"] != "unknown" and row["base_sha"] != current_sha:
            warnings.warn(StaleBaseRevision(row["base_sha"], current_sha))

        # Stash dirty tree if requested
        if stash_first:
            status_result = _run_git(["status", "--porcelain"], self.repo_root, timeout=10)
            if status_result.stdout.strip():
                _run_git(
                    ["stash", "push", "--include-untracked", "-m",
                     f"pre-restore-{checkpoint_id}"],
                    self.repo_root,
                    timeout=30,
                )

        # Empty patch is a no-op (clean tree checkpoint)
        if not patch_path.stat().st_size:
            return True

        result = _run_git(["apply", str(patch_path)], self.repo_root, timeout=60)
        if result.returncode == 0:
            # Mark checkpoint as applied
            conn = _get_db_connection(self.db_path)
            try:
                conn.execute(
                    "UPDATE concurrency_checkpoints SET status='APPLIED' WHERE checkpoint_id=?",
                    (checkpoint_id,),
                )
                conn.commit()
            finally:
                conn.close()
            return True
        return False

    def list(self, task_id: str) -> list[dict]:
        """Return all checkpoints for a task, newest first."""
        conn = _get_db_connection(self.db_path)
        try:
            rows = conn.execute(
                """
                SELECT * FROM concurrency_checkpoints
                WHERE task_id=?
                ORDER BY created_at DESC
                """,
                (task_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def invalidate(self, checkpoint_id: str, reason: str = "") -> None:
        """Mark a checkpoint as SUPERSEDED. Does NOT delete the patch file."""
        conn = _get_db_connection(self.db_path)
        try:
            conn.execute(
                "UPDATE concurrency_checkpoints SET status='SUPERSEDED' "
                "WHERE checkpoint_id=?",
                (checkpoint_id,),
            )
            conn.commit()
        finally:
            conn.close()

    def cleanup_old(self, task_id: str, keep: int = 3) -> int:
        """Keep newest `keep` checkpoints; mark older ones SUPERSEDED + delete patch files.

        Returns count of checkpoints cleaned up.
        """
        all_checkpoints = self.list(task_id)
        to_remove = all_checkpoints[keep:]
        if not to_remove:
            return 0

        count = 0
        conn = _get_db_connection(self.db_path)
        try:
            for row in to_remove:
                pp = Path(row["patch_path"])
                if pp.exists():
                    pp.unlink(missing_ok=True)
                conn.execute(
                    "UPDATE concurrency_checkpoints SET status='SUPERSEDED' "
                    "WHERE checkpoint_id=?",
                    (row["checkpoint_id"],),
                )
                count += 1
            conn.commit()
        finally:
            conn.close()
        return count
