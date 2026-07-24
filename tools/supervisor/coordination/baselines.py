"""Baseline fingerprints, write journal and change attribution (TC-COORD-004).

Attribution never trusts git status (git records THAT a file changed, not
WHICH process changed it). It compares the current content hash against:
the lease baseline, this agent's journaled writes, other agents' journaled
writes, and the committed HEAD blob. Anything unattributable is UNKNOWN and
the write is refused -- preservation is the failure mode, never overwrite.
"""
from __future__ import annotations

import hashlib
import sqlite3
import subprocess
from pathlib import Path

from .db import NowFn, default_now

# Classifications
UNCHANGED = "UNCHANGED"
OWN_CHANGE = "OWN_CHANGE"
OTHER_AGENT_CHANGE = "OTHER_AGENT_CHANGE"
PRE_EXISTING_USER_CHANGE = "PRE_EXISTING_USER_CHANGE"
GENERATED = "GENERATED"
DELETED_EXTERNALLY = "DELETED_EXTERNALLY"
UNKNOWN = "UNKNOWN"
NO_BASELINE = "NO_BASELINE"

# Writes may proceed for these. NO_BASELINE = first touch under a dir lease
# (or a takeover lease's mandatory recapture): the preflight captures the
# current content as baseline+pre-hash BEFORE the write, so nothing is lost.
WRITE_OK = frozenset({UNCHANGED, OWN_CHANGE, NO_BASELINE})


def sha256_file(path: str | Path) -> str | None:
    p = Path(path)
    try:
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        return None


def _normalized_sha256(data: bytes) -> str:
    """Line-ending-insensitive content hash. Needed for HEAD comparison on
    Windows: `git show HEAD:path` emits the LF blob while the checked-out
    file may carry CRLF (core.autocrlf), so raw hashes never match."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def head_blob_sha256(worktree_path: str | Path, display_rel: str) -> str | None:
    """Normalized sha256 of the committed HEAD content for a repo path."""
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{display_rel}"],
            cwd=str(worktree_path), capture_output=True, timeout=15)
        if out.returncode != 0:
            return None
        return _normalized_sha256(out.stdout)
    except (OSError, subprocess.SubprocessError):
        return None


def normalized_sha256_file(path: str | Path) -> str | None:
    try:
        return _normalized_sha256(Path(path).read_bytes())
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        return None


class BaselineTracker:
    def __init__(self, now_fn: NowFn = default_now):
        self.now_fn = now_fn

    def capture(self, conn: sqlite3.Connection, lease_id: str,
                entries: list[tuple[str, str]], worktree_path: str | Path) -> int:
        """Capture (file_key, display) baselines for a lease. Overwrites any
        prior baseline for the same (lease, file) -- used at claim time and
        at takeover recapture. Returns count captured."""
        n = 0
        for file_key, display in entries:
            path = Path(worktree_path) / display
            sha = sha256_file(path)
            size = path.stat().st_size if sha is not None else None
            conn.execute(
                "INSERT INTO lease_baselines(lease_id, file_key, file_display,"
                " baseline_sha256, baseline_size, captured_at)"
                " VALUES(?,?,?,?,?,?)"
                " ON CONFLICT(lease_id, file_key) DO UPDATE SET"
                " baseline_sha256=excluded.baseline_sha256,"
                " baseline_size=excluded.baseline_size,"
                " captured_at=excluded.captured_at, head_sha256=NULL",
                (lease_id, file_key, display, sha, size, self.now_fn()))
            n += 1
        return n

    def get_baseline(self, conn: sqlite3.Connection, lease_id: str,
                     file_key: str) -> sqlite3.Row | None:
        return conn.execute(
            "SELECT * FROM lease_baselines WHERE lease_id=? AND file_key=?",
            (lease_id, file_key)).fetchone()

    def journal(self, conn: sqlite3.Connection, agent_id: str,
                lease_id: str | None, file_key: str, op: str,
                pre_sha256: str | None, post_sha256: str | None,
                source: str = "cli") -> None:
        conn.execute(
            "INSERT INTO write_journal(agent_id, lease_id, file_key, op,"
            " pre_sha256, post_sha256, source, recorded_at)"
            " VALUES(?,?,?,?,?,?,?,?)",
            (agent_id, lease_id, file_key, op, pre_sha256, post_sha256,
             source, self.now_fn()))

    def classify_change(self, conn: sqlite3.Connection, agent_id: str,
                        lease_id: str, file_key: str,
                        worktree_path: str | Path) -> tuple[str, dict]:
        """(classification, detail). See module docstring for semantics."""
        base = self.get_baseline(conn, lease_id, file_key)
        display = base["file_display"] if base is not None else file_key
        current = sha256_file(Path(worktree_path) / display)
        detail: dict = {"current_sha256": current}

        if base is None:
            return NO_BASELINE, detail
        baseline = base["baseline_sha256"]
        detail["baseline_sha256"] = baseline

        if current == baseline:
            return UNCHANGED, detail
        if current is None and baseline is not None:
            return DELETED_EXTERNALLY, detail

        # Attribution via the write journal (newest matching post-hash wins).
        match = conn.execute(
            "SELECT agent_id, source, entry_id FROM write_journal"
            " WHERE file_key=? AND post_sha256=?"
            " ORDER BY entry_id DESC LIMIT 1", (file_key, current)).fetchone()
        if match is not None:
            detail["journal_entry_id"] = match["entry_id"]
            if match["agent_id"] == agent_id:
                return OWN_CHANGE, detail
            detail["apparent_owner"] = match["agent_id"]
            if match["source"] == "guard":
                return GENERATED, detail
            return OTHER_AGENT_CHANGE, detail

        # Lazy HEAD comparison (newline-normalized): content equal to the
        # committed state means an external revert-to-HEAD happened after our
        # claim. Refused: that is exactly the "cleanup over concurrent work"
        # hazard.
        head = base["head_sha256"]
        if head is None:
            head = head_blob_sha256(worktree_path, display)
            if head is not None:
                conn.execute(
                    "UPDATE lease_baselines SET head_sha256=? WHERE"
                    " lease_id=? AND file_key=?", (head, lease_id, file_key))
        detail["head_sha256"] = head
        current_norm = normalized_sha256_file(Path(worktree_path) / display)
        detail["head_match"] = (head is not None and current_norm == head)
        if detail["head_match"]:
            return PRE_EXISTING_USER_CHANGE, detail

        return UNKNOWN, detail
