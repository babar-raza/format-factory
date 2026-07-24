"""Pre-execution gate for /new-format-kickstart (TC-PA-010).

Blocks a new format package whose name collides with a Python stdlib module.
`src/python/csv/` is the defect this exists to prevent -- see
namespace_collision.py for the measured, two-mode failure analysis.

A name colliding with a widely-installed PyPI import name (not stdlib) does
NOT block -- it ALLOWs with a WARN detail. That collision is contingent on the
competing distribution actually being installed alongside ours, which is not
true today for any format package in this repo (see TC-PA-039 disposition,
revised 2026-07-20: `toml` stays `toml`, rename is not required). Blocking
package creation over a hypothetical future PyPI name clash is disproportionate;
the WARN keeps it visible without forcing a rename.

USAGE (from the skill, BEFORE creating src/python/<format_name>/; repo root)

    python -m tools.governance.skill_gates.format_name_gate --format-name csv

Exit codes:
  0 = ALLOW   -- name is free, or WARN (popular-PyPI collision, non-blocking)
  1 = BLOCKED -- stdlib collision, or invalid identifier

Invoked with `-m` (not as a path) so the gate needs no sys.path bootstrap of its
own -- consistent with the hygiene rule its sibling gate enforces.

ENFORCEMENT HONESTY: deterministic verdict when run; nothing forces the agent to
run it. V250 (sprint pipeline, parallel agent) is the blocking counterpart and
should import namespace_collision.check_name rather than restate the name lists.
"""
from __future__ import annotations

import argparse
import json

from tools.governance.skill_gates import namespace_collision


def run(format_name: str) -> dict:
    res = namespace_collision.check_name(format_name)
    suggestion = None
    if res.blocked and res.verdict != namespace_collision.VERDICT_INVALID:
        suggestion = f"ff_{format_name.strip().lower()}"
    warn = res.verdict == namespace_collision.VERDICT_POPULAR
    return {
        "gate": "new-format-kickstart",
        "format_name": res.name,
        "verdict": "BLOCKED" if res.blocked else ("WARN" if warn else "ALLOW"),
        "collision_verdict": res.verdict,
        "detail": res.detail,
        "suggested_name": suggestion,
        "stop_condition": ("BLOCKED: stdlib_collision" if res.blocked else None),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Pre-execution gate for /new-format-kickstart (TC-PA-010)")
    ap.add_argument("--format-name", required=True,
                    help="candidate package name, e.g. 'sylk'")
    args = ap.parse_args(argv)

    result = run(args.format_name)
    print(json.dumps(result, indent=2))
    return 1 if result["verdict"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
