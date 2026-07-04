"""governance_validators_found_issue.py — V130-V133: Found-Issue lifecycle + proactive LOC scan.

Added 2026-07-04 as part of PQLM-GOV-001 governance healing plan.

V130 (PQLM-GOV-001, TC-VAL-002): validate_dotnet_loc_cap_static
    Proactive static scan of ALL .cs files in src/net/ regardless of changed_files.
    Closes GC-G (V78 reactive gap) and GC-C (cap creep accumulation).
    blocks_sprint: False (WARN — frozen known_violations are allowed; this is advisory).

V131 (PQLM-GOV-001, TC-VAL-002): validate_found_issue_disposition
    Each FI-XXX in declaration's found_issues must have a disposition from the 6-item list.
    blocks_sprint: False (WARN during GA period).

V132 (PQLM-GOV-001, TC-VAL-002): validate_found_issue_escalation
    FI items with risk_not_reduced disposition must have an escalation_plan field.
    blocks_sprint: False (WARN during GA period).

V133 (PQLM-GOV-001, TC-VAL-002): validate_found_issue_invalid_disposition
    FI disposition must be one of the 6 valid values. "pre-existing" alone is NOT valid.
    blocks_sprint: True (FAIL — invalid dispositions are never acceptable).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# 6-item valid disposition list
# ---------------------------------------------------------------------------
VALID_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "completed_verified",
        "completed_but_weakly_verified",
        "partially_done",
        "not_attempted",
        "claimed_unproven",
        "risk_not_reduced",
    }
)


def _result(vid: str, name: str, passed: bool, items: list, blocks: bool) -> dict:
    """Standard validator result shape."""
    result_label = "PASS" if passed else ("FAIL" if blocks else "WARN")
    return {
        "validator": name,
        "result": result_label,
        "blocks_sprint": (not passed) and blocks,
        "items": items,
        "summary": f"{vid}: {'OK' if passed else str(len(items)) + ' issue(s)'}",
    }


# ── V130 ──────────────────────────────────────────────────────────────────────


def validate_dotnet_loc_cap_static(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V130: Proactive static scan — ALL .cs files in src/net/ vs baseline_loc_cap.

    Unlike V78 (which only scans changed_files), this validator scans every .cs file
    in src/net/ on every run. Files exceeding their frozen baseline_loc_cap emit WARN.
    New files (not in known_violations) exceeding 800 LOC also emit WARN.

    blocks_sprint=False: these are informational — existing V78 already blocks regressions
    in sprint declarations. V130 surfaces silent drift between sprints.
    """
    _r = repo_root or Path(__file__).parent.parent.parent
    _baseline_path = _r / "registry" / "source-structure-baseline.json"
    try:
        import json

        _baseline = json.loads(_baseline_path.read_text(encoding="utf-8"))
        _known: dict = _baseline.get("known_violations", {})
    except Exception:
        _known = {}

    net_root = _r / "src" / "net"
    if not net_root.exists():
        return _result("V130", "dotnet_loc_cap_static", True, [], False)

    items: list[dict] = []
    for cs_path in sorted(net_root.rglob("*.cs")):
        try:
            actual_loc = sum(1 for _ in cs_path.open(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        rel_str = cs_path.relative_to(_r).as_posix()
        known_entry = _known.get(rel_str, {})
        cap = known_entry.get("baseline_loc_cap", 0) if known_entry else 0
        if known_entry and cap > 0:
            # Known violation: check against frozen cap (not 800)
            if actual_loc <= cap:
                continue  # Within frozen cap — no alert
            items.append(
                {
                    "file": rel_str,
                    "loc": actual_loc,
                    "cap": cap,
                    "reason": "exceeds_frozen_cap",
                }
            )
        elif actual_loc <= 800:
            continue  # New compliant file — always pass
        else:
            items.append(
                {
                    "file": rel_str,
                    "loc": actual_loc,
                    "cap": 800,
                    "reason": "new_file_exceeds_800_no_baseline",
                }
            )

    return _result("V130", "dotnet_loc_cap_static", not items, items, False)


# ── V131 ───────────���──────────────────────────────────────────────────────────


def validate_found_issue_disposition(declaration: dict) -> dict:
    """V131: Each found_issue entry must have a disposition field.

    When a sprint declares found_issues, each item must include a 'disposition' field.
    This ensures found issues are classified, not merely listed.
    blocks_sprint=False (WARN) during GA period.
    """
    found_issues: list[dict] = declaration.get("found_issues", [])
    if not found_issues:
        return _result("V131", "found_issue_disposition", True, [], False)

    missing: list[str] = []
    for item in found_issues:
        fi_id = item.get("id", "(no id)")
        if not item.get("disposition"):
            missing.append(f"[V131] {fi_id} missing 'disposition' field")

    return _result("V131", "found_issue_disposition", not missing, missing, False)


# ── V132 ──────────────────────────────────────────────────────────────────────


def validate_found_issue_escalation(declaration: dict) -> dict:
    """V132: FI items with risk_not_reduced disposition must include an escalation_plan.

    When a found issue is classified as 'risk_not_reduced', the sprint must provide an
    escalation_plan string explaining what will reduce the risk and by when.
    blocks_sprint=False (WARN) during GA period.
    """
    found_issues: list[dict] = declaration.get("found_issues", [])
    if not found_issues:
        return _result("V132", "found_issue_escalation", True, [], False)

    missing_plan: list[str] = []
    for item in found_issues:
        fi_id = item.get("id", "(no id)")
        if item.get("disposition") == "risk_not_reduced" and not item.get(
            "escalation_plan"
        ):
            missing_plan.append(
                f"[V132] {fi_id} has disposition=risk_not_reduced but no escalation_plan"
            )

    return _result("V132", "found_issue_escalation", not missing_plan, missing_plan, False)


# ─�� V133 ���─────────────────────────────────────────────────────────────────────


def validate_found_issue_invalid_disposition(declaration: dict) -> dict:
    """V133: FI disposition must be one of the 6 valid values.

    Invalid or absent dispositions (including 'pre-existing' used as the sole reason)
    are production defects — they indicate a found issue was not properly classified.
    blocks_sprint=True (FAIL) — invalid dispositions are never acceptable.

    Valid dispositions:
        completed_verified, completed_but_weakly_verified, partially_done,
        not_attempted, claimed_unproven, risk_not_reduced
    """
    found_issues: list[dict] = declaration.get("found_issues", [])
    if not found_issues:
        return _result("V133", "found_issue_invalid_disposition", True, [], True)

    invalid: list[str] = []
    for item in found_issues:
        fi_id = item.get("id", "(no id)")
        disp = item.get("disposition", "")
        if not disp:
            invalid.append(f"[V133] {fi_id} has no disposition — every FI must be classified")
        elif disp not in VALID_DISPOSITIONS:
            invalid.append(
                f"[V133] {fi_id} disposition='{disp}' is not in the 6-item valid list"
                f" (allowed: {', '.join(sorted(VALID_DISPOSITIONS))})"
            )

    return _result("V133", "found_issue_invalid_disposition", not invalid, invalid, True)
