"""Coordinated I/O context manager for CLI tools.

CLI tools (write_plan_lock.py, autonomous_cycle.py, lifecycle_audit.py,
sprint_executor.py) write files via Bash, bypassing the PreToolUse hook
coordination plane.  Wrapping writes in ``coordinated_write()`` gives them
first-class coordination: preflight check before the write, journal entry
after -- without touching the hook layer.

Falls through as a no-op when no agent identity is available (``FF_AGENT_ID``
env var or explicit ``agent_id`` / ``session_id`` parameter), preserving
backward compatibility for manual and debug use.

See also: TC-SWB-004 (future task to wire CLI tools to this context manager).
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


@contextmanager
def coordinated_write(
    path: str | Path,
    *,
    agent_id: str | None = None,
    token: str | None = None,
    session_id: str | None = None,
    op: str = "edit",
    source: str = "cli",
) -> Generator[None, None, None]:
    """Acquire coordination before writing, journal after.

    Usage::

        from tools.supervisor.coordination.coordinated_io import coordinated_write

        with coordinated_write("path/to/file.json"):
            Path("path/to/file.json").write_text(data)

    Falls through (no-op yield) when no agent identity is available,
    so callers never need to guard on coordination state.

    Parameters
    ----------
    path : str or Path
        The file to be written, relative to the worktree root or absolute.
    agent_id : str, optional
        Explicit agent ID.  Falls back to ``FF_AGENT_ID`` env var.
    token : str, optional
        Explicit agent token.  Falls back to ``FF_AGENT_TOKEN`` env var.
    session_id : str, optional
        Session ID for identity resolution (alternative to agent_id+token).
    op : str
        Operation label for the coordination journal entry (default ``"edit"``).
    source : str
        Source label for the journal entry (default ``"cli"``).

    Raises
    ------
    CoordinationDenied
        When preflight refuses the write (conflict, baseline drift, etc.).
    """
    resource = str(path)

    # Resolve identity: explicit args > env vars.
    # No identity source at all -> fall through silently (backward compat).
    aid = agent_id or os.environ.get("FF_AGENT_ID")
    tok = token or os.environ.get("FF_AGENT_TOKEN")

    if not aid and not session_id:
        yield
        return

    # Lazy imports keep the module importable without the full coordination
    # stack (SQLite DB, worktree identity, etc.) when coordination is inactive.
    from .errors import CoordinationDenied
    from .preflight import preflight as _preflight
    from .preflight import record_write as _record_write

    result = _preflight(resource, op, agent_id=aid, token=tok,
                        session_id=session_id)
    if not result.allowed:
        raise CoordinationDenied(
            resource=resource,
            reason=result.reason,
            exit_code=result.exit_code,
            conflict_id=result.conflict_id,
        )

    try:
        yield
    finally:
        _record_write(resource, op, agent_id=aid, token=tok,
                      session_id=session_id, source=source)
