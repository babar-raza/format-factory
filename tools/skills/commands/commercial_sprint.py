"""
commercial_sprint.py -- Command: /commercial-sprint

Entry point for the /commercial-sprint skill command.

ALLOWED:
  - Argument parsing (format, sprint-id, dry-run mode)
  - Routing to format_context_resolver + lane_selector + commercial_sprint_dryrun
  - Validation of state before execution
  - Governance validation output

NOT ALLOWED:
  - Source mutation
  - Gate approval
  - Autonomous implementation
  - Publishing

Usage:
  python tools/skills/commands/commercial_sprint.py fods --dry-run
  python tools/skills/commands/commercial_sprint.py fodt --dry-run --report
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


def run(args=None):
    parser = argparse.ArgumentParser(
        prog="commercial-sprint",
        description="Commercial sprint skill command — dry-run orchestration",
    )
    parser.add_argument("format", help="Format ID (fods, fodt)")
    parser.add_argument("--sprint-id", default=None,
                        help="Sprint ID override (default: auto-generated)")
    parser.add_argument("--mission", default="Commercial sprint dry-run POC.",
                        help="Mission statement")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Dry-run mode (always true — implementation requires human auth)")
    parser.add_argument("--report", action="store_true",
                        help="Write report to reports/planning/")
    parser.add_argument("--json", action="store_true")
    parsed = parser.parse_args(args)

    fmt = parsed.format.lower()
    if fmt not in ("fods", "fodt"):
        print(f"ERROR: Unknown format {fmt!r}. Supported: fods, fodt")
        sys.exit(1)

    sprint_id = parsed.sprint_id or f"CONWAY-R7-{fmt.upper()}-SPRINT-001"

    # Governance pre-check: verify state before running
    from format_context_resolver import resolve_format_context
    ctx = resolve_format_context(fmt)
    req_state = ctx["requirements_state"]["status"]

    print(f"[commercial-sprint] Format: {fmt.upper()}")
    print(f"[commercial-sprint] Requirements state: {req_state}")

    if req_state != "REQUIREMENTS_AUTHORITATIVE":
        print(f"[commercial-sprint] BLOCKED: state is {req_state!r}")
        print("[commercial-sprint] REQUIREMENTS_AUTHORITATIVE required before sprint generation")
        print("[commercial-sprint] AUTONOMOUS_IMPLEMENTATION: NOT_AUTHORIZED")
        sys.exit(2)

    from commercial_sprint_dryrun import run_dryrun
    result = run_dryrun(
        fmt=fmt,
        sprint_id=sprint_id,
        sprint_mission=parsed.mission,
        output_report=parsed.report,
    )

    if parsed.json:
        print(json.dumps(result, indent=2))
        return

    print(f"[commercial-sprint] DRY_RUN_STATUS: {result['dryrun_status']}")
    print(f"[commercial-sprint] QUALITY_GATE: {result['prompt_quality_gate_status']}")
    print(f"[commercial-sprint] ACCEPTED_COUNT: {result['accepted_count']}")
    print(f"[commercial-sprint] COMMERCIAL_READY: {result['governance']['commercial_product_ready']}")
    print("[commercial-sprint] IMPLEMENTATION_REQUIRES_HUMAN_AUTHORIZATION: true")
    print("[commercial-sprint] DEC_034_IV_REQUIRED_BEFORE_PROMOTION: true")


if __name__ == "__main__":
    run()
