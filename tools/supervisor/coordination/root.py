"""Coordination root resolution and the single path canonicalizer.

Design rules (plan lazy-hugging-lovelace, section 5.1):
- The coordination root lives OUTSIDE the repository by default because this
  repo (including .git and .local) is OneDrive-synced and SQLite WAL sidecars
  under sync interference are a corruption risk on a per-edit hot path.
  Default: %LOCALAPPDATA%/ff-coordination/<repo_key>/ where repo_key is
  derived from the git COMMON dir, so every process and every linked worktree
  of the same repository on this machine shares one root.
- FF_AGENT_COORDINATION_ROOT overrides everything (separately launched agents
  can be pointed at an explicit shared path).
- Git discovery is pure-filesystem (no subprocess) so preflight stays fast:
  walk up for a `.git` entry; a `.git` FILE (linked worktree) is parsed for
  `gitdir:` and the worktree's `commondir` file.
- canonical_resource() is the ONLY path canonicalizer in the system. Hook,
  CLI, generator guard and pre-commit all call it. Keys are repo-relative,
  forward-slash, casefolded (Windows case-insensitivity), realpath-resolved
  (symlink bypass resistance), and rejected if they escape the worktree.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

ENV_ROOT = "FF_AGENT_COORDINATION_ROOT"
DB_FILENAME = "coordination.db"

# Resources that are namespaces, not paths.
LOGICAL_PREFIXES = ("logical:", "cmd:")


def _norm(p: str | Path) -> str:
    """Machine-comparable absolute form: realpath + normcase, forward slashes."""
    return os.path.normcase(os.path.realpath(str(p))).replace("\\", "/")


def find_git_entry(start: str | Path | None = None) -> Path | None:
    """Walk up from start (default cwd) to the first dir containing `.git`."""
    cur = Path(os.path.realpath(str(start or os.getcwd())))
    for candidate in (cur, *cur.parents):
        if (candidate / ".git").exists():
            return candidate / ".git"
    return None


def git_common_dir(start: str | Path | None = None) -> Path | None:
    """Resolve the git common dir without subprocess.

    Main checkout: `.git` is a directory -> that directory.
    Linked worktree: `.git` is a file `gitdir: <path>`; that path contains a
    `commondir` file pointing (possibly relatively) at the shared .git dir.
    """
    entry = find_git_entry(start)
    if entry is None:
        return None
    if entry.is_dir():
        return entry
    try:
        text = entry.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None
    if not text.startswith("gitdir:"):
        return None
    gitdir = Path(text[len("gitdir:"):].strip())
    if not gitdir.is_absolute():
        gitdir = (entry.parent / gitdir).resolve()
    commondir_file = gitdir / "commondir"
    if commondir_file.exists():
        try:
            rel = commondir_file.read_text(encoding="utf-8").strip()
        except OSError:
            return gitdir
        common = Path(rel)
        if not common.is_absolute():
            common = (gitdir / common).resolve()
        return common
    return gitdir


def worktree_top(start: str | Path | None = None) -> Path | None:
    """Top-level directory of the current worktree (parent of the .git entry)."""
    entry = find_git_entry(start)
    if entry is None:
        return None
    return entry.parent


def repo_key(start: str | Path | None = None) -> tuple[str, bool]:
    """(stable machine-local key for this repository, anchored?).

    Keyed on the git common dir so all worktrees share it. When git discovery
    fails we key on the cwd and flag the root as unanchored (doctor warns).
    """
    common = git_common_dir(start)
    if common is not None:
        return hashlib.sha256(_norm(common).encode("utf-8")).hexdigest()[:16], True
    anchor = _norm(start or os.getcwd())
    return hashlib.sha256(anchor.encode("utf-8")).hexdigest()[:16], False


def _state_base() -> Path:
    """Per-user local (non-roaming, non-synced) state directory."""
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local)
    xdg = os.environ.get("XDG_STATE_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".local" / "state"


def resolve_coordination_root(start: str | Path | None = None) -> Path:
    override = os.environ.get(ENV_ROOT)
    if override:
        return Path(os.path.abspath(os.path.expanduser(override)))
    key, _anchored = repo_key(start)
    return _state_base() / "ff-coordination" / key


def is_anchored(start: str | Path | None = None) -> bool:
    return repo_key(start)[1]


def db_path(root: Path | None = None, start: str | Path | None = None) -> Path:
    return (root or resolve_coordination_root(start)) / DB_FILENAME


def worktree_identity(start: str | Path | None = None) -> tuple[str, str]:
    """(worktree_id, worktree_path). worktree_id is stable per worktree top."""
    top = worktree_top(start)
    if top is None:
        anchor = os.path.realpath(str(start or os.getcwd()))
        return hashlib.sha256(_norm(anchor).encode("utf-8")).hexdigest()[:12], anchor
    return hashlib.sha256(_norm(top).encode("utf-8")).hexdigest()[:12], str(top)


def repo_identity(start: str | Path | None = None) -> str:
    """Root-commit sha (stable repo identity). Subprocess; NOT on the hot path
    (used only at registration). Falls back to 'unknown'."""
    top = worktree_top(start)
    if top is None:
        return "unknown"
    try:
        out = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            cwd=str(top), capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip().splitlines()[-1][:40]
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def is_logical(resource: str) -> bool:
    return resource.startswith(LOGICAL_PREFIXES)


def canonical_resource(resource: str, top: str | Path | None = None) -> tuple[str, str]:
    """Return (key, display) for a resource.

    Logical/command resources pass through casefolded. Filesystem resources
    become repo-relative forward-slash casefolded keys; realpath resolution
    defeats symlink and `..` tricks; anything resolving outside the worktree
    raises ResourceEscape.
    """
    from .errors import ResourceEscape

    resource = resource.strip()
    if is_logical(resource):
        return resource.casefold(), resource

    top = Path(top) if top is not None else worktree_top()
    if top is None:
        raise ResourceEscape(resource, "no worktree found")

    raw = Path(resource)
    absolute = raw if raw.is_absolute() else Path(top) / raw
    resolved = _norm(absolute)
    top_norm = _norm(top)
    if resolved == top_norm:
        rel = "."
    elif resolved.startswith(top_norm + "/"):
        rel = resolved[len(top_norm) + 1:]
    else:
        raise ResourceEscape(resource, resolved)

    key = rel.casefold()
    # Human display keeps the caller's spelling, repo-relative when possible.
    display = str(raw).replace("\\", "/")
    return key, display


def ancestor_keys(key: str) -> list[str]:
    """All directory ancestor keys of a file/dir key, nearest first."""
    parts = key.split("/")
    return ["/".join(parts[:i]) for i in range(len(parts) - 1, 0, -1)]
