"""
Format Factory â€” Autonomous Host Daemon (Scaffold)
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Scaffold only. Loads and dispatches next-action files via next_action_runner.
CLAUDECODE=1 blocks nested Claude CLI invocation.
For H6 proof, must run OUTSIDE Claude Code session (CLAUDECODE=0).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root))


def _is_in_claudecode() -> bool:
    return os.environ.get("CLAUDECODE", "").strip() not in ("", "0")


def run_daemon(
    action_path: str,
    max_cycles: int = 1,
    dry_run: bool = False,
    backend: str = "auto",
) -> dict:
    """
    Run the daemon for up to max_cycles.
    Returns a daemon result dict.
    """
    in_session = _is_in_claudecode()

    if in_session and backend == "claude-cli":
        return {
            "status": "BLOCKED",
            "reason": "CLAUDE_CLI_FORBIDDEN_IN_CLAUDECODE_SESSION",
            "note": "Cannot invoke nested Claude CLI from inside Claude Code. Run from external host.",
        }

    results = []
    from tools.supervisor.next_action_runner import run_action

    for cycle in range(1, max_cycles + 1):
        action_result = run_action(action_path, dry_run=dry_run)
        results.append({"cycle": cycle, "result": action_result})
        if action_result.get("status") not in ("SUCCESS", "DRY_RUN"):
            break

    h_level = None
    success_count = sum(1 for r in results if r["result"].get("status") in ("SUCCESS",))
    if success_count >= 2:
        h_level = "H4"
    elif success_count == 1:
        h_level = "H3"

    return {
        "status": "COMPLETE" if success_count > 0 else "FAILED",
        "in_claudecode_session": in_session,
        "cycles_run": len(results),
        "proof_level": h_level,
        "results": results,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "HOST_INVOCATION_BLOCKED_BY_CLAUDECODE" if in_session
            else "Running in external host context"
        ),
    }


def get_external_host_command(action_path: str) -> str:
    """Return the PowerShell command to run this daemon from outside Claude Code."""
    daemon_path = Path(__file__).resolve()
    return (
        f"# Run from external PowerShell (NOT inside Claude Code):\n"
        f"$env:CLAUDECODE=''\n"
        f"python '{daemon_path}' --action '{action_path}' --max-cycles 2 --backend local\n"
        f"\n"
        f"# For H6 (external Claude CLI):\n"
        f"$env:CLAUDECODE=''\n"
        f"python '{daemon_path}' --action '{action_path}' --max-cycles 1 --backend claude-cli\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Format Factory Autonomous Host Daemon (scaffold)")
    parser.add_argument("--action", required=True, help="Path to next-action.json")
    parser.add_argument("--max-cycles", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backend", default="auto",
                        choices=["auto", "local", "llm-api", "mcp", "claude-cli"])
    parser.add_argument("--print-external-command", action="store_true",
                        help="Print PowerShell command for external host execution")
    args = parser.parse_args()

    if args.print_external_command:
        print(get_external_host_command(args.action))
        sys.exit(0)

    result = run_daemon(args.action, args.max_cycles, args.dry_run, args.backend)
    print(json.dumps(result, indent=2))

    status = result.get("status", "")
    sys.exit(0 if status in ("COMPLETE",) else 3)


if __name__ == "__main__":
    main()
