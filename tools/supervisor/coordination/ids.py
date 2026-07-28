"""Stable identifiers, secret tokens and best-effort process start times.

Identity model: (agent_id, secret token). The token hash is stored; the raw
token lives only in the runtime token file under <root>/runtime/. PID and
hostname are diagnostic corroboration, never authoritative (PID reuse).
"""
from __future__ import annotations

import hashlib
import secrets
import sys
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    return (dt or utcnow()).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")


def new_agent_id(provider: str, now: datetime | None = None) -> str:
    stamp = (now or utcnow()).strftime("%Y%m%dT%H%M%S")
    safe_provider = "".join(c for c in provider.lower() if c.isalnum() or c == "-") or "agent"
    return f"agent-{safe_provider}-{stamp}-{secrets.token_hex(3)}"


def new_lease_id() -> str:
    return f"lease-{secrets.token_hex(5)}"


def new_conflict_id() -> str:
    return f"conf-{secrets.token_hex(5)}"


def new_token() -> str:
    return secrets.token_hex(16)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def pid_start_time(pid: int, timeout: float = 3.0) -> str | None:
    """Best-effort process start time (PID-reuse corroboration).

    Only consulted during takeover verification -- never on the hot path.
    Returns an opaque string comparable for equality, or None.
    """
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            process = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
            if not process:
                return None
            created = wintypes.FILETIME()
            exited = wintypes.FILETIME()
            kernel = wintypes.FILETIME()
            user = wintypes.FILETIME()
            try:
                if not ctypes.windll.kernel32.GetProcessTimes(
                    process, ctypes.byref(created), ctypes.byref(exited),
                    ctypes.byref(kernel), ctypes.byref(user)
                ):
                    return None
                return str((created.dwHighDateTime << 32) | created.dwLowDateTime)
            finally:
                ctypes.windll.kernel32.CloseHandle(process)
        import subprocess
        out = subprocess.run(
            ["ps", "-p", str(int(pid)), "-o", "lstart="],
            capture_output=True, text=True, timeout=timeout,
        )
        value = out.stdout.strip()
        return value or None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def pid_alive(pid: int) -> bool:
    """PID liveness without psutil. On Windows os.kill(pid, 0) requires
    same-user ownership; PermissionError therefore means 'alive'."""
    import os

    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False
