from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class WorktreeObservation:
    path: str
    branch: str | None
    commit: str
    dirty: bool
    canonical: bool
    branch_exists: bool | None = None
    abandoned: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def observe_worktrees(repo: Path) -> list[WorktreeObservation]:
    result = _run(repo, "worktree", "list", "--porcelain")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git worktree list failed")
    blocks = [block for block in result.stdout.split("\n\n") if block.strip()]
    canonical = repo.resolve()
    observations: list[WorktreeObservation] = []
    for block in blocks:
        values: dict[str, str] = {}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            values[key] = value
        path = Path(values["worktree"]).resolve()
        status = _run(path, "status", "--porcelain")
        branch = values.get("branch", "").removeprefix("refs/heads/") or None
        branch_exists = None
        if branch:
            branch_exists = (
                _run(
                    repo,
                    "show-ref",
                    "--verify",
                    "--quiet",
                    f"refs/heads/{branch}",
                ).returncode
                == 0
            )
        observations.append(
            WorktreeObservation(
                path=str(path),
                branch=branch,
                commit=values.get("HEAD", ""),
                dirty=bool(status.stdout.strip()),
                canonical=path == canonical,
                branch_exists=branch_exists,
                abandoned=branch_exists is False,
            )
        )
    return observations


def parse_active_tasks(status_text: str) -> dict[str, str]:
    active: dict[str, str] = {}
    pattern = re.compile(r"^\s*(\S+)\s+\[ACTIVE\].*?\btask=([^\s]+)", re.MULTILINE)
    for match in pattern.finditer(status_text):
        task = match.group(2)
        if task != "-":
            active[task.lower()] = match.group(1)
    return active


def canonical_shared_root(repo: Path) -> Path:
    result = _run(repo, "rev-parse", "--git-common-dir")
    if result.returncode:
        return repo
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = (repo / common).resolve()
    return common.parent if common.name == ".git" else repo


def verify_commit_occurrence(repo: Path, ref: str, branch: str | None) -> dict[str, str]:
    resolved = _run(repo, "rev-parse", f"{ref}^{{commit}}")
    if resolved.returncode:
        raise RuntimeError(f"checkpoint commit does not exist: {ref}")
    commit = resolved.stdout.strip()
    if branch:
        branch_check = _run(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
        if branch_check.returncode:
            raise RuntimeError(f"checkpoint branch does not exist: {branch}")
        ancestor = _run(repo, "merge-base", "--is-ancestor", commit, branch)
        if ancestor.returncode:
            raise RuntimeError(f"checkpoint {commit} is not an ancestor of {branch}")
    body = _run(repo, "cat-file", "-p", commit)
    if body.returncode:
        raise RuntimeError(f"cannot read checkpoint commit object: {commit}")
    return {
        "source_commit": commit,
        "commit_object_digest": hashlib.sha256(
            body.stdout.encode("utf-8")
        ).hexdigest(),
    }
