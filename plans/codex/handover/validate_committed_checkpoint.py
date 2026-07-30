"""Validate the committed FF6 handover without touching the shared overlay.

generated_by: codex
visibility: internal

The normal handover validator intentionally observes its current worktree.
That is useful for detecting unexplained mutations, but a live, leased overlay
must not make the immutable GitLab checkpoint impossible to verify. This
wrapper creates a temporary detached worktree at the requested Git reference,
runs the fail-closed validator there, and removes only that temporary worktree.
It never changes a branch, stages files, or mutates the shared checkout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


HANDOVER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = HANDOVER_ROOT.parents[2]
VALIDATOR_RELATIVE = Path("plans/codex/handover/validate_handover.py")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _resolve_ref(ref: str) -> str:
    result = _git("rev-parse", "--verify", f"{ref}^{{commit}}")
    if result.returncode != 0:
        raise RuntimeError(
            f"cannot resolve {ref!r}: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def validate_committed_checkpoint(ref: str) -> dict[str, Any]:
    commit = _resolve_ref(ref)
    cleanup_error: str | None = None
    with tempfile.TemporaryDirectory(prefix="ff6-handover-") as parent:
        worktree = Path(parent) / "checkpoint"
        add = _git("worktree", "add", "--detach", str(worktree), commit)
        if add.returncode != 0:
            return {
                "result": "FAIL",
                "source_ref": ref,
                "resolved_commit": commit,
                "errors": [
                    "temporary detached worktree creation failed: "
                    + (add.stderr.strip() or add.stdout.strip())
                ],
            }
        try:
            validator = worktree / VALIDATOR_RELATIVE
            run = subprocess.run(
                [sys.executable, str(validator), "--require-clean"],
                cwd=worktree,
                check=False,
                capture_output=True,
                text=True,
            )
            try:
                nested: Any = json.loads(run.stdout)
            except json.JSONDecodeError:
                nested = {
                    "result": "FAIL",
                    "errors": ["validator did not emit JSON"],
                    "stdout": run.stdout,
                    "stderr": run.stderr,
                }
        finally:
            remove = _git("worktree", "remove", "--force", str(worktree))
            if remove.returncode != 0:
                cleanup_error = remove.stderr.strip() or remove.stdout.strip()

    nested_result = nested.get("result") if isinstance(nested, dict) else None
    errors: list[str] = []
    if nested_result != "PASS":
        errors.append("committed handover validator failed")
    if cleanup_error:
        errors.append(f"temporary worktree cleanup failed: {cleanup_error}")
    return {
        "result": "PASS" if not errors else "FAIL",
        "source_ref": ref,
        "resolved_commit": commit,
        "validation_mode": "TEMPORARY_DETACHED_WORKTREE",
        "shared_worktree_mutated": False,
        "validator": nested,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ref",
        default="origin/main",
        help="Commit-like reference to validate; defaults to GitLab origin/main.",
    )
    args = parser.parse_args(argv)
    try:
        result = validate_committed_checkpoint(args.ref)
    except (OSError, RuntimeError) as exc:
        result = {
            "result": "FAIL",
            "source_ref": args.ref,
            "errors": [str(exc)],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
