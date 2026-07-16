"""Skills-First Control — narrow, governed exception mechanism.

Implements the exception policy of docs/governance/skill-only-policy.yaml section 8
as executable, fail-closed logic. An exception temporarily accepts a specific
skills-first control finding (e.g., a deferred remediation) WITHOUT weakening the
gate silently. The gate treats a HIGH finding as blocking UNLESS a valid, non-
expired exception covers it.

An exception is VALID only if it has ALL required fields, a future expiry, a real
owner, a linked remediation task, and a reason that is not in the forbidden set.
Anything else (missing field, expired, ownerless, forbidden reason, broad scope)
is INVALID and does NOT downgrade the finding — fail-closed by construction.

Store: reports/skills-first-control/accepted-findings.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .registries import REPO_ROOT

STORE = REPO_ROOT / "reports" / "skills-first-control" / "accepted-findings.yaml"

_REQUIRED_FIELDS = (
    "exception_id", "finding_signature", "severity", "owner", "reason",
    "remediation_task", "created", "expires", "compensating_control",
)
# Convenience-driven reasons are never a valid basis for an exception.
FORBIDDEN_REASONS = {
    "no_skill_applicable", "small_change", "documentation_only", "urgent",
    "pre_existing", "one_time", "assistant_discretion", "convenience", "speed",
}


class ExceptionError(RuntimeError):
    pass


def _today() -> date:
    # date-only comparison; deterministic enough for expiry evaluation.
    return datetime.now(timezone.utc).date()


def _parse_date(s: Any) -> date | None:
    if isinstance(s, date):
        return s
    if not isinstance(s, str):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s[:len(fmt) + 6], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        return None


def load_exceptions() -> list[dict[str, Any]]:
    if not STORE.exists():
        return []
    try:
        data = yaml.safe_load(STORE.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ExceptionError(f"accepted-findings store not parseable: {exc}") from exc
    if data is None:
        return []
    if not isinstance(data, dict) or not isinstance(data.get("exceptions"), list):
        raise ExceptionError("accepted-findings store: expected {'exceptions': [...]}")
    return data["exceptions"]


def validate_exception(exc: dict[str, Any], today: date | None = None) -> list[str]:
    """Return list of reasons this exception is INVALID ([] == valid)."""
    today = today or _today()
    errs: list[str] = []
    if not isinstance(exc, dict):
        return ["exception is not a mapping"]
    for f in _REQUIRED_FIELDS:
        if not exc.get(f):
            errs.append(f"missing/empty required field: {f}")
    reason = str(exc.get("reason", "")).strip().lower().replace(" ", "_")
    if reason in FORBIDDEN_REASONS:
        errs.append(f"forbidden reason: {reason}")
    exp = _parse_date(exc.get("expires"))
    if exc.get("expires") and exp is None:
        errs.append("expires is not a parseable date")
    elif exp is not None and exp < today:
        errs.append(f"expired on {exp.isoformat()}")
    # Broad scope guard: a signature that is a bare wildcard is too broad.
    sig = str(exc.get("finding_signature", "")).strip()
    if sig in ("*", "**", "ALL", "all"):
        errs.append("finding_signature is too broad (wildcard not allowed)")
    return errs


def active_accepted_signatures(today: date | None = None) -> tuple[set[str], list[dict]]:
    """Return (set of covered finding signatures, list of invalid exceptions).

    Only VALID exceptions contribute to the covered set. Invalid ones are
    surfaced so the gate can FAIL on them (an invalid/expired/broad exception is
    itself a violation, never a silent pass)."""
    valid_sigs: set[str] = set()
    invalid: list[dict] = []
    for exc in load_exceptions():
        errs = validate_exception(exc, today)
        if errs:
            invalid.append({"exception_id": exc.get("exception_id", "<none>"),
                            "errors": errs})
        else:
            valid_sigs.add(str(exc["finding_signature"]))
    return valid_sigs, invalid


def finding_signature(finding: dict[str, Any]) -> str:
    """Stable signature for a finding: category + primary subject."""
    subject = (finding.get("skill_id") or finding.get("command_id")
               or finding.get("file") or finding.get("command_file")
               or finding.get("operation") or "")
    return f"{finding.get('category', '')}::{subject}"


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First exception governance")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    v = sub.add_parser("validate")
    v.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "list":
            print(json.dumps(load_exceptions(), indent=2, default=str))
            return 0
        if args.cmd == "validate":
            valid, invalid = active_accepted_signatures()
            out = {"valid_signatures": sorted(valid), "invalid_exceptions": invalid}
            print(json.dumps(out, indent=2))
            return 0 if not invalid else 1
    except ExceptionError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(_main())
