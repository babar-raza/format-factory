"""committed_fs.py — Read files from git HEAD instead of the working tree.

Eliminates governance-validator flapping caused by concurrent agents writing
to the working tree while validators read it. All reads come from the last
committed state, which is immutable (commits are serialized by git's own
locking).

Usage in governance_validator_runner.py:
    from committed_fs import committed_repo_root

    root = committed_repo_root(repo_root)  # returns tmpdir Path
    # pass `root` to validators instead of `repo_root`

Usage in source_digest():
    from committed_fs import committed_read_bytes, committed_list_files

    for relpath in committed_list_files(repo_root, f"src/python/{fmt}"):
        content = committed_read_bytes(repo_root, relpath)
        ...
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def committed_read_text(repo_root: Path, relpath: str, encoding: str = "utf-8") -> str:
    """Read a file from HEAD. Raises FileNotFoundError if the path doesn't exist at HEAD."""
    fwd = relpath.replace("\\", "/")
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{fwd}"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise OSError(f"git show timed out for {fwd}") from exc

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        if "does not exist" in stderr or "not exist in" in stderr or "fatal:" in stderr:
            raise FileNotFoundError(f"{fwd} does not exist at HEAD")
        raise OSError(f"git show failed for {fwd}: {stderr}")

    return result.stdout.decode(encoding, errors="replace")


def committed_read_bytes(repo_root: Path, relpath: str) -> bytes:
    """Read a file's raw bytes from HEAD."""
    fwd = relpath.replace("\\", "/")
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{fwd}"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise OSError(f"git show timed out for {fwd}") from exc

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        if "does not exist" in stderr or "not exist in" in stderr or "fatal:" in stderr:
            raise FileNotFoundError(f"{fwd} does not exist at HEAD")
        raise OSError(f"git show failed for {fwd}: {stderr}")

    return result.stdout


def committed_list_files(repo_root: Path, tree_prefix: str) -> list[str]:
    """List all files under a directory at HEAD. Returns repo-relative paths (forward-slash)."""
    fwd = tree_prefix.replace("\\", "/").rstrip("/")
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD", f"{fwd}/"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired as exc:
        raise OSError(f"git ls-tree timed out for {fwd}") from exc

    if result.returncode != 0:
        return []

    lines = result.stdout.decode("utf-8", errors="replace").strip()
    if not lines:
        return []
    return sorted(lines.splitlines())


def committed_file_exists(repo_root: Path, relpath: str) -> bool:
    """Check if a file exists at HEAD."""
    fwd = relpath.replace("\\", "/")
    result = subprocess.run(
        ["git", "cat-file", "-t", f"HEAD:{fwd}"],
        cwd=str(repo_root),
        capture_output=True,
        timeout=5,
    )
    return result.returncode == 0


def committed_repo_root(repo_root: Path) -> Path:
    """Export HEAD into a temp directory and return the path.

    The caller is responsible for cleanup (use as a context manager with
    tempfile.TemporaryDirectory, or let the OS reclaim on process exit).

    This is the heavy-weight approach — for targeted use (source_digest,
    specific validators), prefer committed_read_bytes / committed_list_files.
    """
    tmpdir = tempfile.mkdtemp(prefix="ff-committed-")
    subprocess.run(
        ["git", "archive", "HEAD"],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        timeout=60,
    )
    return Path(tmpdir)
