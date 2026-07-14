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
from governance_validators_contract import validator  # noqa: F401

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


@validator(rule_id="V_VALIDATE_DOTNET_LOC_CAP_STATIC", domain="found_issue")
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


@validator(rule_id="V_VALIDATE_FOUND_ISSUE_DISPOSITION", domain="found_issue")
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


@validator(rule_id="V_VALIDATE_FOUND_ISSUE_ESCALATION", domain="found_issue")
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


@validator(rule_id="V_VALIDATE_FOUND_ISSUE_INVALID_DISPOSITION", domain="found_issue")
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


# ── V139-V142 ─────────────────────────────────────────────────────────────────
# Register-level found-issue ownership validators (FOUND-ISSUE-MVP-001, 2026-07-04)
#
# V139-V142 operate on the REGISTER (registry/found-issue-register.yaml).
# V130-V133 operate on the sprint DECLARATION (declaration['found_issues']).
# Both layers are needed — different scopes, complementary enforcement.
#
# OWNERSHIP_VALID_DISPOSITIONS (6 — from found-issue-ownership-policy.md §6):
#   HEALED_AND_VERIFIED, DUPLICATE_OF_ACTIVE_ISSUE, INVALID_FINDING_WITH_PROOF,
#   VALID_GOVERNED_EXCLUSION, BLOCKED_TRUE_EXTERNAL_DEPENDENCY,
#   WAITING_VALID_GATE_11_AUTHORIZATION
#
# These are DIFFERENT from VALID_DISPOSITIONS used by V133 (sprint-audit labels).
# ─────────────────────────────────────────────────────────────────────────────

import re  # noqa: E402

OWNERSHIP_VALID_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "HEALED_AND_VERIFIED",
        "DUPLICATE_OF_ACTIVE_ISSUE",
        "INVALID_FINDING_WITH_PROOF",
        "VALID_GOVERNED_EXCLUSION",
        "BLOCKED_TRUE_EXTERNAL_DEPENDENCY",
        "WAITING_VALID_GATE_11_AUTHORIZATION",
    }
)

_INVALID_DISMISSALS: frozenset[str] = frozenset(
    {
        "pre_existing", "pre-existing",
        "unrelated",
        "not_caused_by_me", "not caused by me",
        "ignored",
        "outside_current_task", "outside current task",
    }
)

_PROSE_DISMISSAL_PATTERNS: list[str] = [
    r"pre.?existing",
    r"not caused by",
    r"unrelated to",
    r"outside.*task",
    r"follow.?up recommended",
    r"probably harmless",
    r"somebody else",
    r"no time to",
    r"warning only",
    r"already failing",
]

_PROSE_RE = re.compile(
    "|".join(_PROSE_DISMISSAL_PATTERNS),
    re.IGNORECASE,
)


def _load_found_issue_register(repo_root: "Path | None") -> "list[dict] | None":
    """Load registry/found-issue-register.yaml issues list. Returns None if file missing."""
    try:
        import yaml as _yaml  # noqa: PLC0415
    except ImportError:
        return []

    _r = repo_root or Path(__file__).parent.parent.parent
    reg_path = _r / "registry" / "found-issue-register.yaml"
    if not reg_path.exists():
        return None
    try:
        data = _yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        return data.get("issues", []) if isinstance(data, dict) else []
    except Exception:
        return []


# ── V139 ──────────────────────────────────────────────────────────────────────


@validator(rule_id="V_VALIDATE_FOUND_ISSUE_REGISTER_PRESENT", domain="found_issue")
def validate_found_issue_register_present(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V139: When tests fail, found-issue-register.yaml should have entries.

    WARN (not FAIL) during GA period — blocks_sprint=False.
    Skips check if no sprint_id / run_id in declaration (can't correlate issues).
    """
    # tests_run may be int (total count) or dict — use test_results for pass/fail breakdown
    test_results = declaration.get("test_results", {}) or {}
    if not isinstance(test_results, dict):
        test_results = {}
    failing_tests = declaration.get("failing_tests", []) or []
    failed_count = test_results.get("failed", 0) or 0

    has_failures = failed_count > 0 or bool(failing_tests)
    if not has_failures:
        return _result("V139", "found_issue_register_present", True, [], False)

    sprint_id = declaration.get("sprint_id") or declaration.get("run_id")
    if not sprint_id:
        return _result("V139", "found_issue_register_present", True, [], False)

    issues = _load_found_issue_register(repo_root)
    if issues is None:
        return _result(
            "V139",
            "found_issue_register_present",
            False,
            ["[V139] registry/found-issue-register.yaml missing; tests failed but no issues registered"],
            False,
        )

    if not issues:
        return _result(
            "V139",
            "found_issue_register_present",
            False,
            [f"[V139] {failed_count or len(failing_tests)} test failure(s) detected but found-issue-register has no entries"],
            False,
        )

    return _result("V139", "found_issue_register_present", True, [], False)


# ── V140 ──────────────────────────────────────────────────────────────────────

_STATUS_TO_BUCKET: dict[str, str] = {
    "discovered": "active",
    "classified": "active",
    "taskcarded": "active",
    "in_repair": "active",
    "verified": "healed_and_verified",
    "closed": "healed_and_verified",
    "duplicate": "duplicate",
    "invalid": "invalid_with_proof",
    "governed_exclusion": "governed_exclusion",
    "blocked_external": "blocked_true_external",
    "waiting_gate_11": "waiting_gate_11",
}


@validator(rule_id="V_VALIDATE_ISSUE_ACCOUNTING_RECONCILES", domain="found_issue")
def validate_issue_accounting_reconciles(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V140: All register statuses must map to accounting buckets without remainder.

    blocks_sprint=True — unaccounted issues are never acceptable.
    Missing register file = PASS (no issues to reconcile).
    """
    issues = _load_found_issue_register(repo_root)
    if issues is None or not issues:
        return _result("V140", "issue_accounting_reconciles", True, [], True)

    unknown: list[str] = []
    for issue in issues:
        issue_id = issue.get("issue_id", "(no id)")
        status = issue.get("status", "")
        if status not in _STATUS_TO_BUCKET:
            unknown.append(
                f"[V140] {issue_id} has unknown status='{status}' "
                f"(valid: {', '.join(sorted(_STATUS_TO_BUCKET))})"
            )

    return _result("V140", "issue_accounting_reconciles", not unknown, unknown, True)


# ── V141 ──────────────────────────────────────────────────────────────────────


@validator(rule_id="V_VALIDATE_NO_PROSE_ONLY_FINDINGS", domain="found_issue")
def validate_no_prose_only_findings(declaration: dict) -> dict:
    """V141: Detect dismissal language in worker_self_verdict or work item notes.

    WARN (blocks_sprint=False) — advisory during GA period.
    """
    hits: list[str] = []

    verdict = declaration.get("worker_self_verdict", "") or ""
    if _PROSE_RE.search(verdict):
        m = _PROSE_RE.search(verdict)
        hits.append(f"[V141] worker_self_verdict contains dismissal language: '{m.group()}'")

    for item in declaration.get("planned_work_items", []) or []:
        notes = item.get("notes", "") or ""
        if _PROSE_RE.search(notes):
            m = _PROSE_RE.search(notes)
            item_id = item.get("id", "(no id)")
            hits.append(
                f"[V141] work item {item_id} notes contain dismissal language: '{m.group()}'"
            )

    return _result("V141", "no_prose_only_findings", not hits, hits, False)


# ── V142 ──────────────────────────────────────────────────────────────────────


@validator(rule_id="V_VALIDATE_INVALID_OWNERSHIP_DISPOSITION", domain="found_issue")
def validate_invalid_ownership_disposition(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V142: No issue in found-issue-register.yaml may use an invalid ownership disposition.

    OWNERSHIP dispositions are the 6 from found-issue-ownership-policy.md §6.
    These differ from V133 sprint-audit dispositions — different scopes.
    blocks_sprint=True — invalid dispositions are never acceptable.
    Missing register file = PASS.
    """
    issues = _load_found_issue_register(repo_root)
    if issues is None or not issues:
        return _result("V142", "invalid_ownership_disposition", True, [], True)

    invalid: list[str] = []
    for issue in issues:
        issue_id = issue.get("issue_id", "(no id)")
        disp = issue.get("disposition", "")
        if not disp:
            continue  # In-flight issue with no disposition yet — not a violation

        disp_norm = disp.lower().replace("-", "_").replace(" ", "_")
        invalid_norm = {d.lower().replace("-", "_").replace(" ", "_") for d in _INVALID_DISMISSALS}
        if disp_norm in invalid_norm:
            invalid.append(
                f"[V142] {issue_id} disposition='{disp}' is an invalid dismissal "
                f"(not one of the 6 valid ownership dispositions; see found-issue-ownership-policy.md §6)"
            )

    return _result("V142", "invalid_ownership_disposition", not invalid, invalid, True)


# ---------------------------------------------------------------------------
# TC-FIOP-005: Section-21 Validators (V_VALIDATE_FI_*)
# ---------------------------------------------------------------------------


@validator(rule_id="V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED", domain="found_issue")
def validate_found_issue_task_closure_unaccounted(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED: Block sprint if undisposed issues exist at closure.

    FAIL+blocks_sprint if declaration has any found_issues entry without disposition
    AND the worker_self_grade is PASS or PARTIAL (indicating a closure attempt).
    """
    grade = declaration.get("worker_self_grade", "")
    if grade not in ("PASS", "PARTIAL"):
        return _result("V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED",
                       "found_issue_task_closure_unaccounted", True, [], True)
    found_issues = declaration.get("found_issues") or []
    undisposed = [
        fi.get("issue_id", "(no id)")
        for fi in found_issues
        if isinstance(fi, dict) and not fi.get("disposition")
    ]
    return _result("V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED",
                   "found_issue_task_closure_unaccounted", not undisposed,
                   [f"{iid}: no disposition set" for iid in undisposed], True)


@validator(rule_id="V_VALIDATE_FI_NO_DELETED_TEST", domain="found_issue")
def validate_found_issue_no_deleted_test_without_analysis(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V_VALIDATE_FI_NO_DELETED_TEST: WARN if tests removed without analysis.

    WARN-only (blocks_sprint=False) — test_removal_analysis is a new optional field.
    """
    import re
    changed = declaration.get("changed_files") or []
    removed_tests = [
        f for f in changed
        if isinstance(f, str) and re.search(r"tests[/\\].*test_.*\.py$", f)
        and declaration.get("removed_files") and f in declaration.get("removed_files", [])
    ]
    if not removed_tests or declaration.get("test_removal_analysis"):
        return _result("V_VALIDATE_FI_NO_DELETED_TEST",
                       "found_issue_no_deleted_test_without_analysis", True, [], False)
    return _result("V_VALIDATE_FI_NO_DELETED_TEST",
                   "found_issue_no_deleted_test_without_analysis", False,
                   [f"Removed test file without analysis: {f}" for f in removed_tests], False)


@validator(rule_id="V_VALIDATE_FI_DOWNSTREAM_PATCH", domain="found_issue")
def validate_found_issue_downstream_patch_while_upstream_defective(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V_VALIDATE_FI_DOWNSTREAM_PATCH: WARN if only downstream changes with active GOV_BLOCK.

    Advisory — warns when rework_items contains GOV_BLOCK but all changed files are reports/registry.
    """
    rework = declaration.get("rework_items") or []
    has_govblock = any(
        "GOV_BLOCK" in str(item) for item in rework
        if isinstance(item, (str, dict))
    )
    if not has_govblock:
        return _result("V_VALIDATE_FI_DOWNSTREAM_PATCH",
                       "found_issue_downstream_patch_while_upstream_defective", True, [], False)
    changed = declaration.get("changed_files") or []
    has_upstream = any(
        isinstance(f, str) and (f.startswith("src/") or f.startswith("tools/"))
        for f in changed
    )
    if has_upstream:
        return _result("V_VALIDATE_FI_DOWNSTREAM_PATCH",
                       "found_issue_downstream_patch_while_upstream_defective", True, [], False)
    return _result("V_VALIDATE_FI_DOWNSTREAM_PATCH",
                   "found_issue_downstream_patch_while_upstream_defective", False,
                   ["Evidence suggests downstream-only changes while upstream GOV_BLOCK remains unresolved"],
                   False)


@validator(rule_id="V_VALIDATE_FI_CLOSURE_NO_VERIFY", domain="found_issue")
def validate_found_issue_closure_without_verification(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V_VALIDATE_FI_CLOSURE_NO_VERIFY: FAIL if any closed issue lacks verification_verdict.

    FAIL+blocks_sprint if a HEALED_AND_VERIFIED or closed issue has null/empty verification_verdict.
    """
    repo = repo_root or Path(__file__).parent.parent.parent
    register_path = repo / "registry" / "found-issue-register.yaml"
    if not register_path.exists():
        return _result("V_VALIDATE_FI_CLOSURE_NO_VERIFY",
                       "found_issue_closure_without_verification", True, [], True)
    try:
        import yaml as _yaml
        data = _yaml.safe_load(register_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return _result("V_VALIDATE_FI_CLOSURE_NO_VERIFY",
                       "found_issue_closure_without_verification", True, [], True)
    issues = data.get("issues") or []
    unverified = [
        issue.get("issue_id", "(no id)")
        for issue in issues
        if isinstance(issue, dict)
        and issue.get("disposition") in ("HEALED_AND_VERIFIED",)
        and not issue.get("verification_verdict")
    ]
    return _result("V_VALIDATE_FI_CLOSURE_NO_VERIFY",
                   "found_issue_closure_without_verification", not unverified,
                   [f"{iid}: closed as HEALED_AND_VERIFIED but no verification_verdict" for iid in unverified],
                   True)


@validator(rule_id="V_VALIDATE_FI_UNTASKCARDED_REPORT", domain="found_issue")
def validate_found_issue_untaskcarded_in_final_report(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V_VALIDATE_FI_UNTASKCARDED_REPORT: WARN if issue-language in verdict without found_issues.

    Advisory — WARN if worker_self_verdict contains issue keywords but found_issues is empty.
    """
    import re
    verdict = declaration.get("worker_self_verdict", "") or ""
    issue_pattern = re.compile(
        r"\b(failed|broken|error in|cannot|exception|invalid)\b", re.IGNORECASE
    )
    ok_pattern = re.compile(r"\b(no |all |0 |zero )\w*\s*(failed|broken|error|invalid)\b", re.IGNORECASE)
    has_issue_lang = bool(issue_pattern.search(verdict)) and not bool(ok_pattern.search(verdict))
    found_issues = declaration.get("found_issues") or []
    if not has_issue_lang or found_issues:
        return _result("V_VALIDATE_FI_UNTASKCARDED_REPORT",
                       "found_issue_untaskcarded_in_final_report", True, [], False)
    return _result("V_VALIDATE_FI_UNTASKCARDED_REPORT",
                   "found_issue_untaskcarded_in_final_report", False,
                   ["Issue-language detected in worker_self_verdict but found_issues is empty — consider registering"],
                   False)


@validator(rule_id="V_VALIDATE_FI_FIXTURE_EDIT", domain="found_issue")
def validate_found_issue_no_fixture_edit_without_authority(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V_VALIDATE_FI_FIXTURE_EDIT: WARN if fixture files changed without authority reference.

    Advisory — WARN if test fixture files are changed without found_issues entries or fixture_authority_ref.
    """
    import re
    changed = declaration.get("changed_files") or []
    fixture_pattern = re.compile(r"tests[/\\].*\.(yaml|json|txt|csv|ods|fods|tsv)$")
    fixture_changes = [f for f in changed if isinstance(f, str) and fixture_pattern.search(f)]
    found_issues = declaration.get("found_issues") or []
    has_authority = bool(declaration.get("fixture_authority_ref")) or bool(found_issues)
    if not fixture_changes or has_authority:
        return _result("V_VALIDATE_FI_FIXTURE_EDIT",
                       "found_issue_no_fixture_edit_without_authority", True, [], False)
    return _result("V_VALIDATE_FI_FIXTURE_EDIT",
                   "found_issue_no_fixture_edit_without_authority", False,
                   [f"Fixture file changed without authority: {f}" for f in fixture_changes[:5]],
                   False)
