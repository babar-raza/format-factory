from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .worktrees import canonical_shared_root


class CoordinationError(RuntimeError):
    def __init__(self, message: str, exit_code: int = 5):
        super().__init__(message)
        self.exit_code = exit_code


class CoordinationAdapter:
    """Invoke the shared coordination CLI; never access its SQLite store."""

    def __init__(self, repo: Path):
        self.repo = repo
        self.command_root = canonical_shared_root(repo)

    def invoke(self, *args: str, allow_status_nonzero: bool = False) -> str:
        command = ["python", "-m", "tools.supervisor.coordination", *args]
        result = subprocess.run(
            command,
            cwd=self.command_root,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode and not allow_status_nonzero:
            code = 6 if result.returncode in {2, 5, 6} else 5
            raise CoordinationError(result.stderr.strip() or result.stdout.strip(), code)
        return result.stdout

    def status(self) -> str:
        return self.invoke("status", allow_status_nonzero=True)

    def claim(self, resource: str, task: str) -> str:
        return self.invoke(
            "claim",
            "--resource",
            resource,
            "--mode",
            "EXCLUSIVE_WRITE",
            "--task",
            task,
        )

    def takeover(self, lease_id: str, reason: str) -> str:
        if not reason.strip():
            raise CoordinationError("takeover requires an audited reason", 2)
        return self.invoke(
            "takeover",
            "--lease",
            lease_id,
            "--reason",
            reason,
        )

    def heartbeat(self) -> str:
        return self.invoke("heartbeat")

    def release(self, resource: str | None = None) -> str:
        args = ["release", "--resource", resource] if resource else ["release", "--all"]
        return self.invoke(*args)
