"""Governed reclaim of STALE coordination leases (directive GAP-015/GAP-016).

Why
---
Commits are blocked by EXCLUSIVE_WRITE leases the coordination system itself
classifies as ``STALE``, owned by agents whose heartbeats are days old. Clearing
each one is a manual ``takeover`` + ``release`` cycle with a hand-written
reason, and the CLI has no bulk verb. In one session that manual cycle was
needed three separate times -- so every stale lease is a hard stop for an
unattended run.

This does not weaken the rule. ``STALE`` is already the reclaimable state and
takeover is already the sanctioned procedure; this removes the requirement that
a human perform it, and journals a reason per lease exactly as the manual path
does because it *calls* the same CLI rather than touching the database.

The GAP-016 safety interlock
----------------------------
An agent can be marked stale **while still working**: interactive heartbeat TTL
is 1800s and nothing heartbeats during a long turn. This session's own agent
went ``STALE_SUSPECT`` mid-work. Reclaiming purely on the recorded status would
therefore let automation seize a live agent's in-progress work -- strictly worse
than the stall it fixes.

So a lease is reclaimed only when its owner's process is confirmed **gone**. If
the owning pid is still running, or liveness cannot be determined, the lease is
skipped. Uncertainty always resolves to "leave it alone".

This is a preflight, not a gate: it always exits 0. A failure to reclaim must
never itself stop the run it exists to unblock.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
COORDINATION = [sys.executable, "-m", "tools.supervisor.coordination"]

STALE = "STALE"


def _run(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        [*COORDINATION, *args], cwd=REPO_ROOT, capture_output=True, text=True
    )
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def _snapshot() -> dict[str, Any]:
    """Current coordination state as the system itself reports it."""
    code, output = _run(["--json", "who", "--all"])
    start = output.find("{")
    if start < 0:
        raise RuntimeError(f"coordination returned no JSON (exit {code}): {output[:200]}")
    return json.loads(output[start:]).get("data", {})


def process_alive(pid: int | None) -> bool | None:
    """True if running, False if gone, None if undeterminable.

    None is deliberately distinct from False: an undeterminable process must be
    treated as possibly-alive, never reclaimed.
    """
    if not pid or pid <= 0:
        return None
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                timeout=20,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by another user
    except OSError:
        return None
    return True


def plan_reclaim(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Decide, per STALE lease, whether it is safe to reclaim. No side effects."""
    agents = {
        agent.get("agent_id"): agent for agent in snapshot.get("active_agents", [])
    }
    decisions: list[dict[str, Any]] = []
    liveness_cache: dict[int | None, bool | None] = {}

    for lease in snapshot.get("live_leases", []):
        if lease.get("status") != STALE:
            continue
        owner_id = lease.get("agent_id")
        owner = agents.get(owner_id, {})
        pid = owner.get("pid")
        if pid not in liveness_cache:
            liveness_cache[pid] = process_alive(pid)
        alive = liveness_cache[pid]

        decision: dict[str, Any] = {
            "lease_id": lease.get("lease_id"),
            "resource": lease.get("resource_display"),
            "owner": owner_id,
            "owner_pid": pid,
            "owner_task": lease.get("task_id"),
            "owner_alive": alive,
        }
        if alive is True:
            decision["action"] = "SKIP"
            decision["why"] = (
                f"owner process {pid} is still running; the lease is marked STALE "
                "only because nothing heartbeats during a long turn (GAP-016). "
                "Reclaiming it would seize live work."
            )
        elif alive is None:
            decision["action"] = "SKIP"
            decision["why"] = (
                "owner liveness could not be determined; uncertainty resolves to "
                "leaving the lease alone"
            )
        else:
            decision["action"] = "RECLAIM"
            decision["why"] = f"owner process {pid} is gone and the lease is STALE"
        decisions.append(decision)
    return decisions


def reclaim(decisions: list[dict[str, Any]], reason: str) -> list[dict[str, Any]]:
    """Take over then release each reclaimable lease through the governed CLI."""
    results: list[dict[str, Any]] = []
    for decision in decisions:
        if decision["action"] != "RECLAIM":
            results.append({**decision, "outcome": "skipped"})
            continue
        lease_id = decision["lease_id"]
        detail = (
            f"{reason} | resource={decision['resource']} "
            f"owner={decision['owner']} owner_pid={decision['owner_pid']} "
            f"(process confirmed gone) prior_task={decision['owner_task']}"
        )
        code, output = _run(["takeover", "--lease", lease_id, "--reason", detail])
        if code != 0:
            results.append(
                {**decision, "outcome": "takeover_failed", "detail": output[-300:]}
            )
            continue
        # The takeover mints a NEW lease id; find and release it so the resource
        # is left free rather than transferred to an agent that is not using it.
        new_id = None
        try:
            for lease in _snapshot().get("live_leases", []):
                if lease.get("resource_key") == decision["resource"] and lease.get(
                    "origin"
                ) == "takeover":
                    new_id = lease.get("lease_id")
                    break
        except (RuntimeError, json.JSONDecodeError):
            new_id = None
        if new_id:
            release_code, _ = _run(["release", "--lease", new_id])
            outcome = "reclaimed" if release_code == 0 else "taken_over_not_released"
        else:
            outcome = "taken_over_not_released"
        results.append({**decision, "outcome": outcome, "new_lease_id": new_id})
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.reclaim_stale_leases",
        description="Reclaim STALE coordination leases whose owner process is gone.",
    )
    parser.add_argument(
        "--reason",
        default="Automated preflight reclaim of a STALE lease whose owner process "
        "is confirmed gone (directive GAP-015).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report the decisions without taking over anything",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    try:
        decisions = plan_reclaim(_snapshot())
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        # A preflight must never stop the run it exists to unblock.
        print(f"[reclaim] could not read coordination state: {exc}", file=sys.stderr)
        return 0

    results = decisions if args.dry_run else reclaim(decisions, args.reason)

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
        return 0

    reclaimable = [d for d in decisions if d["action"] == "RECLAIM"]
    skipped = [d for d in decisions if d["action"] == "SKIP"]
    verb = "would reclaim" if args.dry_run else "reclaimed"
    print(f"[reclaim] {len(decisions)} STALE lease(s): {verb} {len(reclaimable)}, "
          f"skipped {len(skipped)}")
    for item in skipped:
        print(f"  SKIP    {item['resource']}  ({item['why']})")
    if not args.dry_run:
        for item in results:
            if item.get("outcome") not in (None, "skipped"):
                print(f"  {item['outcome'].upper():<24} {item['resource']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
