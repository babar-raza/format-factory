"""grader_promotion.py — Grader shadow observation summary and promotion CLI.

Sub-commands:
  summary    -- Print agreement rate between stable and shadow graders
  recommend  -- Print promotion/demotion recommendation based on agreement rate

Usage:
  python tools/canary/grader_promotion.py summary [--shadow-provider <id>]
  python tools/canary/grader_promotion.py recommend [--shadow-provider <id>] [--threshold 0.95]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SHADOW_LOG_PATH = _REPO_ROOT / ".local" / "supervisor" / "grader-shadow-log.jsonl"


def load_observations(shadow_provider: str = "") -> list[dict]:
    """Load grader shadow observations, optionally filtered by shadow_provider."""
    if not SHADOW_LOG_PATH.exists():
        return []
    observations = []
    for line in SHADOW_LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
            if shadow_provider and rec.get("shadow_provider") != shadow_provider:
                continue
            observations.append(rec)
        except Exception:
            pass
    return observations


def cmd_summary(args: argparse.Namespace) -> int:
    """Print agreement rate between stable and shadow graders."""
    obs = load_observations(getattr(args, "shadow_provider", ""))
    if not obs:
        print("No shadow grading observations found.")
        return 0

    total = len(obs)
    with_shadow = [o for o in obs if o.get("shadow_grade") is not None]
    agreed = [o for o in with_shadow if o.get("agreement") is True]
    disagreed = [o for o in with_shadow if o.get("agreement") is False]
    errors = [o for o in obs if o.get("error")]

    print(f"Grader Shadow Observations: {total} total")
    print(f"  With shadow grade: {len(with_shadow)}")
    print(f"  Agreed:           {len(agreed)}")
    print(f"  Disagreed:        {len(disagreed)}")
    print(f"  Errors:           {len(errors)}")
    if with_shadow:
        rate = len(agreed) / len(with_shadow)
        print(f"  Agreement rate:   {rate:.1%}")

    # Print disagreement details
    if disagreed:
        print("\nDisagreements:")
        for o in disagreed[:5]:
            print(f"  item={o.get('item_id')} stable={o.get('stable_grade')} shadow={o.get('shadow_grade')}")
    return 0


def cmd_recommend(args: argparse.Namespace) -> int:
    """Print promotion/demotion recommendation based on agreement rate."""
    obs = load_observations(getattr(args, "shadow_provider", ""))
    threshold = getattr(args, "threshold", 0.95)
    if not obs:
        print("INSUFFICIENT_DATA: No shadow grading observations found.")
        return 0

    with_shadow = [o for o in obs if o.get("shadow_grade") is not None]
    if not with_shadow:
        print("INSUFFICIENT_DATA: No observations with shadow grades yet.")
        return 0

    agreed = [o for o in with_shadow if o.get("agreement") is True]
    rate = len(agreed) / len(with_shadow)

    if rate >= threshold:
        print(f"RECOMMENDATION: PROMOTE_TO_PRIMARY — agreement rate {rate:.1%} >= threshold {threshold:.1%}")
        print("  Shadow grader produces equivalent results. Consider switching primary.")
    elif rate < 0.5:
        print(f"RECOMMENDATION: KEEP_IN_SHADOW — agreement rate {rate:.1%} < 50%")
        print("  Shadow grader disagrees too often. Do not promote.")
    else:
        print(f"RECOMMENDATION: CONTINUE_OBSERVATION — agreement rate {rate:.1%} between 50%-{threshold:.1%}")
        print("  Collect more observations before making a promotion decision.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Grader shadow observation summary and promotion CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_summary = sub.add_parser("summary", help="Print agreement rate summary")
    p_summary.add_argument("--shadow-provider", default="", help="Filter by shadow provider ID")

    p_recommend = sub.add_parser("recommend", help="Print promotion recommendation")
    p_recommend.add_argument("--shadow-provider", default="", help="Filter by shadow provider ID")
    p_recommend.add_argument("--threshold", type=float, default=0.95, help="Agreement rate threshold for promotion (default: 0.95)")

    args = parser.parse_args()
    dispatch = {"summary": cmd_summary, "recommend": cmd_recommend}
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
