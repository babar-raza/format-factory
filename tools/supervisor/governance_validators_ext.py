"""governance_validators_ext.py — Extension validators for governance_validators.py

This file exists to keep governance_validators.py within its baseline_loc_cap.
New validators (V48+) are placed here and imported at the bottom of governance_validators.py.

Pattern mirrors analytics extraction pattern used for format codecs:
  governance_validators.py imports from governance_validators_ext at module bottom.
  governance_validator_runner.py registers both sets of validators in run_all_governance_validators().

TC-WHALE-GOVBLOCK-001 (2026-06-21): V48 extracted here per source baseline LOC cap policy.
TC-PG-006 (2026-06-23): V56 validate_hardening_target_identity — plan hardening must write to native plan.
TC-ANAL-SEG-HEAL-001 (2026-06-22): V50 added here — MODULE-NAME-001 forbidden module names.
zesty-conjuring-peacock (2026-06-23): V50 extended — *_analytics.py + bare analytics.py added to FORBIDDEN.
TC-QHARD-001 (2026-06-22): V51 validate_spec_qname_coverage — exported classes must have spec_qname.
TC-QHARD-002 (2026-06-22): V52 validate_compat_import_integrity — Compat/ facades import from real spec/ classes.
TC-QHARD-003 (2026-06-22): V53 validate_spec_authority_class_completeness — registry python_file entries exist.
TC-SGF-002 (2026-06-25): V-SGF-001 validate_skill_attribution_in_declaration — closes SKILL-GAP-012.
"""

from __future__ import annotations

import ast
import re as _re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def validate_architecture_only_stub_gate(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V48 (TC-ZS-001): RELEASE_GATE and Gate 11 items must not cite architecture_only stubs.

    Scans evidence_paths for all RELEASE_GATE items. If any cited file contains the
    'GENERATED — architecture_only' marker, the sprint is blocked.
    For PRODUCT_SOURCE items: WARN only (blocks_sprint=False).

    Prevents architectural skeleton stubs from being accepted as behavioral proof
    at commercial gate checkpoints (Gate 11, RELEASE_GATE).
    Implemented 2026-06-21 (ZERO-STUB-AUDIT-20260621, TC-ZS-001).
    Extracted to governance_validators_ext.py (TC-WHALE-GOVBLOCK-001, 2026-06-21).
    """
    repo = repo_root or _REPO_ROOT
    _ARCH_MARKER = "GENERATED \u2014 architecture_only"
    _ARCH_MARKER2 = "architecture_only"
    gate_violations = []
    product_warnings = []

    for item in declaration.get("planned_work_items", []):
        itype = item.get("item_type", "")
        is_gate = itype in ("RELEASE_GATE", "READINESS")
        is_product = itype in ("PRODUCT_SOURCE", "PRODUCT_TEST")
        if not (is_gate or is_product):
            continue
        item_id = item.get("item_id", "UNKNOWN")
        for path_str in item.get("evidence_paths", []):
            if not (path_str.endswith(".py") or path_str.endswith(".cs")):
                continue
            p = (repo / path_str) if not Path(path_str).is_absolute() else Path(path_str)
            if not p.exists():
                continue
            try:
                first_lines = p.read_text(encoding="utf-8", errors="replace")[:500]
            except OSError:
                continue
            if _ARCH_MARKER in first_lines or (
                _ARCH_MARKER2 in first_lines and "TODO" in first_lines
            ):
                entry = {
                    "item_id": item_id,
                    "evidence_path": path_str,
                    "issue": "Evidence file is an architecture_only stub \u2014 not behavioral proof",
                }
                if is_gate:
                    gate_violations.append(entry)
                else:
                    product_warnings.append(entry)

    all_issues = gate_violations + product_warnings
    result = "FAIL" if gate_violations else ("WARN" if product_warnings else "PASS")
    return {
        "validator": "validate_architecture_only_stub_gate",
        "result": result,
        "items": all_issues,
        "summary": (
            f"V48: {len(gate_violations)} RELEASE_GATE item(s) cite architecture_only stubs (blocked); "
            f"{len(product_warnings)} PRODUCT item(s) cite stubs (warned)"
            if all_issues else "V48: No architecture_only stubs cited as evidence"
        ),
        "blocks_sprint": bool(gate_violations),
    }


def validate_hardening_target_identity(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V56 (TC-PG-006): Verify plan hardening writes to the native plan, not a fallback.

    Scans evidence_paths in all work items for .md files under plans/ or .claude/plans/.
    If any cited plan file is:
      - plans/snoopy-juggling-seal.md AND snoopy is NOT the active plan → FAIL
      - any plan file other than the active plan → WARN

    Active plan is resolved from .local/supervisor/plan-locks/ (IN_PROGRESS locks).
    Falls back to no-op PASS if no plan lock exists (no per-chat plan active).

    Severity: FAIL for snoopy as wrong-target; WARN for other wrong-target plans.
    blocks_sprint: True only on FAIL.

    Added 2026-06-23 (TC-PG-006, keen-snacking-quiche plan governance healing).
    """
    import json

    repo = repo_root or _REPO_ROOT

    # Resolve active plan path from IN_PROGRESS lock files
    active_plan_path: str | None = None
    locks_dir = repo / ".local" / "supervisor" / "plan-locks"
    if locks_dir.is_dir():
        for lf in sorted(locks_dir.glob("*.json")):
            try:
                lock = json.loads(lf.read_text(encoding="utf-8"))
                if lock.get("status") == "IN_PROGRESS":
                    active_plan_path = str(lock.get("plan_path", "")).replace("\\", "/")
                    break
            except Exception:
                continue

    # Also try shared lock
    if not active_plan_path:
        shared = repo / ".local" / "supervisor" / "active-plan-lock.json"
        if shared.exists():
            try:
                lock = json.loads(shared.read_text(encoding="utf-8"))
                if lock.get("status") == "IN_PROGRESS":
                    active_plan_path = str(lock.get("plan_path", "")).replace("\\", "/")
            except Exception:
                pass

    if not active_plan_path:
        # No active plan — nothing to enforce
        return {
            "validator": "validate_hardening_target_identity",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V49: No active per-chat plan lock — hardening target check skipped",
        }

    # Normalise the active plan path for comparison
    active_norm = active_plan_path.rstrip("/")

    # Scan all work item evidence_paths for .md files in plans/ or .claude/plans/
    _PLAN_PATTERNS = _re.compile(
        r"((?:plans/|\.claude/plans/|C:[/\\]Users[/\\][^/\\]+[/\\]\.claude[/\\]plans[/\\])[^/\s]+\.md)"
    )
    fail_items = []
    warn_items = []

    all_items = []
    if declaration:
        all_items = (
            declaration.get("completed_work_items", [])
            + declaration.get("planned_work_items", [])
        )
        # Scan global evidence_paths (hardening sprint evidence)
        for ep in declaration.get("evidence_paths", []):
            all_items.append({"item_id": "DECLARATION_LEVEL", "evidence_paths": [ep]})
        # evidence_artifacts are modified-file records, not hardening targets.
        # Skip plan_file type entries — those are governance corrections (e.g. adding
        # plan_identity front-matter to a plan, which is not a hardening-target mismatch).
        for ea in declaration.get("evidence_artifacts", []):
            if isinstance(ea, dict) and ea.get("type") not in ("plan_file", "governance_ledger"):
                all_items.append({
                    "item_id": "DECLARATION_LEVEL",
                    "evidence_paths": [ea.get("path", "")],
                })

    for item in all_items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("item_id", "<unknown>")
        for path_str in item.get("evidence_paths", []):
            path_norm = str(path_str).replace("\\", "/")
            # Only check plan-like paths
            if not _PLAN_PATTERNS.search(path_norm):
                continue
            # Normalise
            if path_norm == active_norm or path_norm.endswith("/" + active_norm.split("/")[-1]):
                continue  # This IS the active plan — correct
            if "master-plan-memory.md" in path_norm:
                continue  # Ledger — not a hardening target mismatch
            # snoopy specifically cited while NOT being the active plan → FAIL
            if "snoopy-juggling-seal.md" in path_norm:
                fail_items.append({
                    "item_id": item_id,
                    "evidence_path": path_str,
                    "active_plan": active_plan_path,
                    "issue": (
                        "snoopy-juggling-seal.md cited as hardening target "
                        "but it is NOT the active per-chat plan"
                    ),
                    "severity": "FAIL",
                })
            else:
                warn_items.append({
                    "item_id": item_id,
                    "evidence_path": path_str,
                    "active_plan": active_plan_path,
                    "issue": (
                        f"Plan file {path_str!r} cited as hardening evidence "
                        f"but active plan is {active_plan_path!r}"
                    ),
                    "severity": "WARN",
                })

    all_issues = fail_items + warn_items
    result = "FAIL" if fail_items else ("WARN" if warn_items else "PASS")
    return {
        "validator": "validate_hardening_target_identity",
        "result": result,
        "blocks_sprint": bool(fail_items),
        "items": all_issues,
        "summary": (
            f"V56: {len(fail_items)} FAIL item(s) (wrong plan cited as hardening target); "
            f"{len(warn_items)} WARN item(s)"
            if all_issues
            else f"V56: Hardening evidence targets active plan ({active_plan_path})"
        ),
    }


def validate_forbidden_module_names(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V50 — MODULE-NAME-001: Forbid generic analytics-bucket module names.

    Blocks creation of or modification of files matching:
      *_analytics.py, *_analytics_extra.py, *_extra.py, *_misc.py, bare analytics.py
      *_helpers.py / *_utils.py containing format-prefixed spec behavior

    Deletion of these files (where file does NOT exist on disk) is ALWAYS allowed.
    The validator checks Path(repo / path).exists() before flagging — so deleting
    a forbidden-named file in a sprint does NOT cause this validator to self-block.

    These names indicate code grouped by convenience, not spec hierarchy.
    Every product module must map to a spec section, element, or domain concept.

    Added 2026-06-22 (TC-ANAL-SEG-HEAL-001) as part of spec-level segregation healing.
    Extended 2026-06-23 (zesty-conjuring-peacock): *_analytics.py and bare analytics.py
    added to FORBIDDEN — all analytics-bucket patterns now blocked, not just overflow files.
    """
    import re

    repo = repo_root or _REPO_ROOT
    FORBIDDEN = re.compile(
        r"src/python/[^/]+/"
        r"(?:[^/]+_(?:analytics_extra|analytics|extra|misc)|analytics)\.py$"
    )
    CONDITIONAL = re.compile(
        r"src/python/[^/]+/[^/]+_(helpers|utils)\.py$"
    )
    FORMAT_FN = re.compile(
        r"def (?:abw|csv|dif|fodg|fods|fodt|fodp|gnumeric|ndjson|"
        r"ods|odt|pbm|pgm|ppm|qoi|sylk|toml|tsv|xcf|zst)_"
    )

    violations = []
    changed = declaration.get("changed_files", [])
    for path in changed:
        # CRITICAL: skip files being DELETED (they don't exist on disk).
        # Allows deletion sprints to remove forbidden-named files without self-blocking.
        full_path = repo / path
        if not full_path.exists():
            continue
        if FORBIDDEN.search(path):
            violations.append({
                "path": path,
                "rule": "MODULE-NAME-001",
                "type": "forbidden_suffix",
                "message": f"Forbidden analytics-bucket module suffix in {path!r}",
            })
        elif CONDITIONAL.search(path):
            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
                if FORMAT_FN.search(content):
                    violations.append({
                        "path": path,
                        "rule": "MODULE-NAME-001",
                        "type": "conditional_forbidden",
                        "message": (
                            f"Format-prefixed spec behavior found in conditionally-forbidden "
                            f"module {path!r}"
                        ),
                    })
            except OSError:
                pass

    blocks = len(violations) > 0
    return {
        "validator": "validate_forbidden_module_names",
        "rule_id": "MODULE-NAME-001",
        "result": "FAIL" if blocks else "PASS",
        "blocks_sprint": blocks,
        "items": violations,
        "summary": (
            f"V50: {len(violations)} forbidden module name(s) found"
            if blocks else "V50: No forbidden module names"
        ),
    }


# ---------------------------------------------------------------------------
# V51-V53, V59, V62 — extracted to governance_validators_spec.py (TC-GOVBLOCK-SPEC-001)
# Re-exported here for backward compatibility with any direct callers.
# ---------------------------------------------------------------------------

from governance_validators_spec import (  # noqa: E402
    validate_spec_qname_coverage,
    validate_compat_import_integrity,
    validate_spec_authority_class_completeness,
    validate_cross_language_parity,
    validate_spec_fact_refs_density,
    _FORMATS,
    _FACADE_ONLY_FORMATS,
    _ERROR_SUFFIXES,
    _CONSTANTS,
    _has_spec_qname,
    _all_symbols_for_format,
)



# ---------------------------------------------------------------------------
# V54 — Cross-lane: product item mutating supervisor machinery files
# ---------------------------------------------------------------------------

_PRODUCT_SOURCE_ITEM_TYPES = frozenset({
    "PRODUCT_SOURCE", "TEST", "REQUIREMENT", "READINESS", "RELEASE_GATE",
    "PRODUCT_IMPLEMENTATION", "PRODUCT_TESTING",
    "PRODUCT_CAPABILITY_EXPANSION", "PRODUCT_EXPORT_OR_DOGFOOD",
})

_MACHINERY_SUPERVISOR_PREFIXES = (
    "tools/supervisor/",
    "tools/validators/",
    "tools/requirements_authority/",
)


def validate_cross_lane_product_touching_machinery(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V54: WARN if a product-track item declares changed_files under tools/supervisor/.

    Product sprints should not mutate supervisor machinery files. Cross-lane mutations
    indicate architectural drift — work that belongs to the MACHINERY track is being
    bundled with PRODUCT_SOURCE items.

    Severity: Conditional-blocking (blocks_sprint=True when violations found).
    Promoted 2026-06-24 after 3 clean sprints (FF-V54V55-PROMOTE-20260624).
    Exception: items with lane_exception='MACHINERY_HEALING' bypass.

    Added 2026-06-23 (FF-FORENSIC-AUDIT-20260623 / A4) as part of lane boundary hardening.
    """
    if declaration is None:
        return {
            "validator": "validate_cross_lane_product_touching_machinery",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V54: No declaration provided — skipped",
        }

    warnings = []
    all_items = (
        declaration.get("completed_work_items", [])
        + declaration.get("planned_work_items", [])
    )

    # Also check at declaration level (some declarations list changed_files globally)
    global_changed = declaration.get("changed_files", [])

    for item in all_items:
        if not isinstance(item, dict):
            continue
        itype = item.get("item_type", "")
        if itype not in _PRODUCT_SOURCE_ITEM_TYPES:
            continue
        # Exception: MACHINERY_HEALING hybrid items are legitimately cross-lane
        if item.get("lane_exception") == "MACHINERY_HEALING":
            continue

        changed = item.get("changed_files", []) or global_changed
        for path in changed:
            path_str = str(path).replace("\\", "/")
            if any(path_str.startswith(pfx) for pfx in _MACHINERY_SUPERVISOR_PREFIXES):
                warnings.append({
                    "item_id": item.get("item_id", "<unknown>"),
                    "item_type": itype,
                    "changed_file": path_str,
                    "issue": (
                        f"Product-track item ({itype}) declares change to machinery file "
                        f"{path_str!r} — potential cross-lane contamination"
                    ),
                    "severity": "WARN",
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_cross_lane_product_touching_machinery",
        "result": result,
        "blocks_sprint": bool(warnings),
        "items": warnings,
        "summary": (
            f"V54: {len(warnings)} product item(s) mutating machinery files"
            if warnings else "V54: No cross-lane product→machinery contamination detected"
        ),
    }


# ---------------------------------------------------------------------------
# V55 — Cross-lane: machinery item mutating product src/ files
# ---------------------------------------------------------------------------

_MACHINERY_ITEM_TYPES = frozenset({
    "GOVERNANCE_TASKCARD", "GOVERNANCE_DOC", "GOVERNANCE_REVIEW",
    "SPEC_AUTHORITY_MACHINERY", "REQUIREMENT_CAPABILITY_MACHINERY",
    "ACTION_QUEUE_MACHINERY", "AUTONOMY_ORCHESTRATOR_MACHINERY",
    "SUPERVISOR_VERDICT_MACHINERY", "VALIDATOR_OR_EVIDENCE_MACHINERY",
    "PROMPT_GENERATION_MACHINERY", "GOVERNED_SKILL_OR_GENERATOR_MACHINERY",
})

_PRODUCT_SRC_PREFIXES = (
    "src/python/",
    "src/net/",
)


def validate_cross_lane_machinery_touching_product(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V55: WARN if a machinery-track item declares changed_files under src/.

    Machinery sprints should not mutate product source files. Cross-lane mutations
    risk destabilizing product behavior during infrastructure work.

    Severity: Conditional-blocking (blocks_sprint=True when violations found).
    Promoted 2026-06-24 after 3 clean sprints (FF-V54V55-PROMOTE-20260624).
    Exception: items with lane_exception='MACHINERY_HEALING' bypass (analytics
    separation sprints that extract src/ code to analytics files are cross-lane).

    Added 2026-06-23 (FF-FORENSIC-AUDIT-20260623 / A4) as part of lane boundary hardening.
    """
    if declaration is None:
        return {
            "validator": "validate_cross_lane_machinery_touching_product",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V55: No declaration provided — skipped",
        }

    warnings = []
    all_items = (
        declaration.get("completed_work_items", [])
        + declaration.get("planned_work_items", [])
    )
    global_changed = declaration.get("changed_files", [])

    for item in all_items:
        if not isinstance(item, dict):
            continue
        itype = item.get("item_type", "")
        if itype not in _MACHINERY_ITEM_TYPES:
            continue
        # Exception: MACHINERY_HEALING items are legitimately cross-lane
        if item.get("lane_exception") == "MACHINERY_HEALING":
            continue

        changed = item.get("changed_files", []) or global_changed
        for path in changed:
            path_str = str(path).replace("\\", "/")
            if any(path_str.startswith(pfx) for pfx in _PRODUCT_SRC_PREFIXES):
                warnings.append({
                    "item_id": item.get("item_id", "<unknown>"),
                    "item_type": itype,
                    "changed_file": path_str,
                    "issue": (
                        f"Machinery-track item ({itype}) declares change to product source "
                        f"{path_str!r} — potential cross-lane contamination"
                    ),
                    "severity": "WARN",
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_cross_lane_machinery_touching_product",
        "result": result,
        "blocks_sprint": bool(warnings),
        "items": warnings,
        "summary": (
            f"V55: {len(warnings)} machinery item(s) mutating product src/ files"
            if warnings else "V55: No cross-lane machinery→product contamination detected"
        ),
    }


_LEDGER_SRC_PREFIXES = ("src/python/", "src/net/")


def validate_changed_files_in_ledger(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V57: WARN if src/python/ or src/net/ changed files have no product-code-change-ledger entry.

    Cross-validates declaration changed_files against reports/r90/product-code-change-ledger.json.
    Every src/ file modified after governance tracking began should have a ledger entry.

    Severity: WARN-only (blocks_sprint=False) until ledger is fully backfilled.
    Activation cutoff: sprint where 90% of src/ entries have ledger coverage.

    Added 2026-06-23 (TC-VNK-003) as V57.
    """
    import json as _json

    if declaration is None:
        return {
            "validator": "validate_changed_files_in_ledger",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V57: No declaration provided — skipped",
        }

    _root = repo_root or Path(__file__).resolve().parents[2]
    ledger_path = _root / "reports" / "r90" / "product-code-change-ledger.json"

    # Build set of ledger-tracked paths
    ledger_paths: set[str] = set()
    if ledger_path.exists():
        try:
            ledger_data = _json.loads(ledger_path.read_text(encoding="utf-8"))
            entries = ledger_data if isinstance(ledger_data, list) else ledger_data.get("entries", [])
            for entry in entries:
                for sf in entry.get("source_files", []):
                    raw = str(sf.get("path", "")).replace("\\", "/")
                    if raw:
                        ledger_paths.add(raw)
        except Exception:
            pass  # If ledger is unreadable, skip — WARN-only validator

    # Collect declaration changed_files
    changed_files = declaration.get("changed_files", [])
    warnings = []
    for path in changed_files:
        path_str = str(path).replace("\\", "/")
        if not any(path_str.startswith(pfx) for pfx in _LEDGER_SRC_PREFIXES):
            continue
        if path_str not in ledger_paths:
            warnings.append({
                "path": path_str,
                "issue": f"src/ file {path_str!r} has no product-code-change-ledger entry",
                "severity": "WARN",
            })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_changed_files_in_ledger",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V57: {len(warnings)} src/ file(s) missing ledger entry"
            if warnings else "V57: All src/ changed files have ledger entries (or no src/ files changed)"
        ),
    }


def validate_expansion_fallback_refs(declaration: dict) -> dict:
    """V58 (FALLBACK-REF-001): Detect EXPANSION-FALLBACK-* synthetic gap references.

    autonomous_task_generator.py injects gap_ledger_ref="EXPANSION-FALLBACK-{FORMAT}-{fn}"
    for functions not in the real gap-ledger. These pass TC-GUARD-001's non-empty check but
    are NOT real GAP-* entries. This validator surfaces them for review.

    WARN-only (blocks_sprint=False) to allow transitional use without hard-blocking existing
    deepening work. Classifies as LEDGER_ENTRY_CLAIMED_UNPROVEN.
    """
    _FALLBACK_PREFIX = "EXPANSION-FALLBACK-"
    _CHECKED = {"PRODUCT_SOURCE", "PRODUCT_TEST"}
    violations = []
    total_checked = 0
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in _CHECKED:
            continue
        total_checked += 1
        ref = item.get("gap_ledger_ref", "")
        if isinstance(ref, str) and ref.startswith(_FALLBACK_PREFIX):
            violations.append({
                "item_id": item.get("item_id", "UNKNOWN"),
                "gap_ledger_ref": ref,
                "classification": "LEDGER_ENTRY_CLAIMED_UNPROVEN",
            })
    pct = (len(violations) / total_checked * 100) if total_checked > 0 else 0.0
    result = "WARN" if violations else "PASS"
    return {
        "validator": "validate_expansion_fallback_refs",
        "result": result,
        "blocks_sprint": False,
        "violations": violations,
        "total_checked": total_checked,
        "fallback_count": len(violations),
        "fallback_pct": round(pct, 1),
        "detail": (
            f"{len(violations)}/{total_checked} PRODUCT_SOURCE/TEST items use "
            f"EXPANSION-FALLBACK synthetic gap refs ({pct:.0f}%). "
            "These are not real gap-ledger entries. "
            "Replace with real GAP-{FORMAT}-* IDs from gap-ledger.json when available."
        ) if violations else "No EXPANSION-FALLBACK refs detected.",
    }


# V59 validate_cross_language_parity: extracted to governance_validators_spec.py


# ---------------------------------------------------------------------------
# V60 — TC-TCF-010: validate_terminal_closure_completeness
# ---------------------------------------------------------------------------


def validate_terminal_closure_completeness(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V60 (TC-TCF-010): WARN if RELEASE_GATE/READINESS items cite a plan with open taskcards.

    Scans evidence_paths for plan files (.md in plans/ or .claude/plans/). If any
    cited plan has open taskcards (not CLOSED/SUPERSEDED/EXCLUDED), produces WARN.

    This prevents declaring release readiness when underlying plans still have
    incomplete work.

    Severity: WARN-only (blocks_sprint=False). Advisory at gate level.
    Added 2026-06-23 (TC-FORENSICS-TERMINAL-20260623, TC-TCF-010).
    """
    if declaration is None:
        return {
            "validator": "validate_terminal_closure_completeness",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V60: No declaration provided -- skipped",
        }

    repo = repo_root or _REPO_ROOT
    _GATE_TYPES = {"RELEASE_GATE", "READINESS"}
    _PLAN_RE = _re.compile(
        r"((?:plans/|\.claude/plans/)[^\s]+\.md)"
    )
    warnings = []

    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in _GATE_TYPES:
            continue
        item_id = item.get("item_id", "UNKNOWN")
        for path_str in item.get("evidence_paths", []):
            if not _PLAN_RE.search(str(path_str)):
                continue
            p = (repo / path_str) if not Path(path_str).is_absolute() else Path(path_str)
            if not p.exists():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Use the same taskcard regex patterns as lifecycle_audit.py
            tc_table = _re.findall(
                r"\|\s*(TC-[A-Z0-9]+-[A-Z0-9-]+)\s*\|\s*"
                r"(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)\s*\|",
                text, _re.IGNORECASE,
            )
            tc_block = _re.findall(
                r"^#{1,4}\s+(TC-[A-Z0-9]+-[A-Z0-9-]+)\b[^\n]*\n"
                r"(?:[^\n]*\n){0,4}?"
                r"[^\n]*\*{0,2}Status:?\*{0,2}\s*(CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED)",
                text, _re.IGNORECASE | _re.MULTILINE,
            )
            all_tcs = {}
            for tc_id, status in tc_table + tc_block:
                all_tcs.setdefault(tc_id.upper(), status.upper())
            open_tcs = [
                tc for tc, st in all_tcs.items()
                if st not in ("CLOSED", "SUPERSEDED", "EXCLUDED")
            ]
            if open_tcs:
                warnings.append({
                    "item_id": item_id,
                    "plan_path": str(path_str),
                    "open_taskcards": open_tcs,
                    "issue": (
                        f"RELEASE_GATE/READINESS item cites plan with "
                        f"{len(open_tcs)} open taskcard(s): {', '.join(open_tcs[:5])}"
                    ),
                })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_terminal_closure_completeness",
        "result": result,
        "blocks_sprint": False,
        "items": warnings,
        "summary": (
            f"V60: {len(warnings)} gate item(s) cite plans with open taskcards"
            if warnings else "V60: No gate items cite plans with open taskcards"
        ),
    }


# ---------------------------------------------------------------------------
# V61 — TC-TCF-010: validate_error_fallback_safety
# ---------------------------------------------------------------------------


def validate_error_fallback_safety(
    declaration: dict | None = None,
    repo_root: Path | None = None,
) -> dict:
    """V61 (TC-TCF-010): Verify write_plan_lock.py error fallback writes ITERATION_REQUIRED.

    Structural smoke test: reads write_plan_lock.py and verifies that error fallback
    paths (except ImportError / except Exception blocks) write ITERATION_REQUIRED,
    not TERMINAL_CLOSED. This prevents regression of defect D6.

    Severity: FAIL if TERMINAL_CLOSED found in error fallback. blocks_sprint=True.
    Added 2026-06-23 (TC-FORENSICS-TERMINAL-20260623, TC-TCF-010).
    """
    repo = repo_root or _REPO_ROOT
    target = repo / "tools" / "supervisor" / "write_plan_lock.py"

    if not target.exists():
        return {
            "validator": "validate_error_fallback_safety",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V61: write_plan_lock.py not found -- skipped",
        }

    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {
            "validator": "validate_error_fallback_safety",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V61: Could not read write_plan_lock.py -- skipped",
        }

    # Look for except blocks that ASSIGN status = "TERMINAL_CLOSED"
    # Only flag direct assignments like: status = "TERMINAL_CLOSED"
    # Do NOT flag comparisons, conditionals, or string mentions
    _ASSIGN_RE = _re.compile(r'^\s*status\s*=\s*["\']TERMINAL_CLOSED["\']')
    violations = []
    lines = text.splitlines()
    in_except = False
    except_line = 0
    except_indent = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("except ") or stripped.startswith("except:"):
            in_except = True
            except_line = i
            except_indent = indent
        elif in_except and indent <= except_indent and stripped and not stripped.startswith("#"):
            # Dedented past except block
            if not stripped.startswith("except"):
                in_except = False
        if in_except and _ASSIGN_RE.match(line):
            violations.append({
                "line": i,
                "except_start": except_line,
                "content": stripped,
                "issue": (
                    f"Error fallback at line {i} assigns status='TERMINAL_CLOSED' "
                    f"(D6 regression) -- should be ITERATION_REQUIRED"
                ),
            })

    result = "FAIL" if violations else "PASS"
    return {
        "validator": "validate_error_fallback_safety",
        "result": result,
        "blocks_sprint": bool(violations),
        "items": violations,
        "summary": (
            f"V61: {len(violations)} error fallback path(s) still write TERMINAL_CLOSED (D6 regression!)"
            if violations else "V61: Error fallback paths correctly write ITERATION_REQUIRED"
        ),
    }


# V62 validate_spec_fact_refs_density: extracted to governance_validators_spec.py


# ---------------------------------------------------------------------------
# V63 — TC-MACH-SRC-001: public API surface ratio validator
# ---------------------------------------------------------------------------


def validate_public_api_surface_ratio(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V63 (TC-MACH-SRC-001): WARN when __init__.py has >50 exports with <20% tested.

    Forward governance only — does not retroactively clean up existing exports.
    WARN-only mode (not BLOCK).
    """
    root = repo_root or _REPO_ROOT
    items = declaration.get("completed_work_items", [])
    if isinstance(items, list) and items and isinstance(items[0], str):
        items = declaration.get("planned_work_items", [])
    if not items:
        return {
            "validator": "validate_public_api_surface_ratio",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V63: No work items to check",
        }

    warnings = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("item_type", "")
        if item_type != "PRODUCT_SOURCE":
            continue

        changed = item.get("changed_files", [])
        for f in changed:
            if not isinstance(f, str):
                continue
            if not f.endswith("__init__.py"):
                continue
            if not (f.startswith("src/python/") or f.startswith("src/net/")):
                continue

            init_path = root / f.replace("/", "\\") if "\\" in str(root) else root / f
            if not init_path.exists():
                continue

            try:
                content = init_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
            except Exception:
                continue

            # Count exports: look for __all__ or top-level names
            export_count = 0
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                export_count = len(node.value.elts)
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith("_"):
                        export_count += 1

            if export_count > 50:
                # Check test coverage ratio (best-effort)
                fmt_parts = f.replace("\\", "/").split("/")
                if len(fmt_parts) >= 3:
                    fmt_name = fmt_parts[2]  # e.g., "ndjson" from "src/python/ndjson/__init__.py"
                    test_dir = root / "tests" / "python" / fmt_name
                    test_count = 0
                    if test_dir.exists():
                        test_count = sum(1 for p in test_dir.rglob("test_*.py") if "analytics" not in p.name)
                    coverage_ratio = test_count / export_count if export_count else 1.0
                    if coverage_ratio < 0.2:
                        item_id = item.get("item_id", item.get("id", "unknown"))
                        warnings.append({
                            "item_id": item_id,
                            "file": f,
                            "export_count": export_count,
                            "test_count": test_count,
                            "coverage_ratio": round(coverage_ratio, 2),
                            "issue": f"__init__.py has {export_count} exports but only {test_count} non-analytics test files ({coverage_ratio:.0%})",
                            "severity": "WARN",
                        })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_public_api_surface_ratio",
        "result": result,
        "blocks_sprint": False,  # WARN-only mode
        "items": warnings,
        "summary": (
            f"V63: {len(warnings)} __init__.py file(s) have low test coverage ratio"
            if warnings else "V63: All modified __init__.py files have acceptable test coverage"
        ),
    }


# V69 — TC-FL-005: skill_idempotency_declared_validator
# WARN-only: fires when a PRODUCT_SOURCE work item claims a skill_id for a skill
# that still has idempotency: not_specified in the skill registry.
def validate_skill_idempotency_declared(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V69 (TC-FL-005): WARN if a PRODUCT_SOURCE item invokes a skill with idempotency: not_specified.

    Guards against regressions where newly-added skills omit an idempotency declaration.
    WARN-only (never blocks_sprint=True) — purpose is regression detection.
    """
    from pathlib import Path as _Path
    import yaml as _yaml

    _r = repo_root or Path(__file__).parent.parent.parent
    _registry_path = _r / ".supervisor" / "skill-registry.yaml"

    # Build skill_id → idempotency lookup
    _skill_idempotency: dict = {}
    try:
        _reg = _yaml.safe_load(_registry_path.read_text(encoding="utf-8"))
        for _skill in _reg.get("skills", []):
            _sid = _skill.get("skill_id")
            if _sid:
                _skill_idempotency[_sid] = _skill.get("idempotency", "not_specified")
    except Exception:
        return {
            "validator": "validate_skill_idempotency_declared",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V67: Skill registry unavailable — skipped",
        }

    warnings = []
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in ("PRODUCT_SOURCE", "PRODUCT_TEST", "GOVERNANCE_TASKCARD"):
            continue
        skill_id = item.get("skill_id") or item.get("skill_used")
        if not skill_id:
            continue
        idempotency = _skill_idempotency.get(skill_id, "unknown")
        if idempotency in ("not_specified", "unknown"):
            warnings.append({
                "item_id": item.get("item_id", "unknown"),
                "skill_id": skill_id,
                "idempotency": idempotency,
                "issue": f"Skill '{skill_id}' has idempotency: {idempotency} — declare idempotency in skill registry",
            })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_skill_idempotency_declared",
        "result": result,
        "blocks_sprint": False,  # WARN-only
        "items": warnings,
        "summary": (
            f"V69: {len(warnings)} work item(s) use skill(s) without idempotency declaration"
            if warnings else "V69: All work items use skills with declared idempotency"
        ),
    }


# V70 — TC-FL-006: sal_authority_chain_validator
# WARN-only: fires when a PRODUCT_SOURCE work item cites spec_fact_refs for a format
# whose qname registry has authority_source: code_introspection (circular authority).
# Guides agent to use empirical_refs instead.
def validate_sal_authority_chain(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V70 (TC-FL-006): WARN when spec_fact_refs cited for code_introspection formats.

    For formats where authority_source is code_introspection/community_informal_spec/
    informational_rfc, spec_fact_refs IDs are not truly SAL-extracted facts.
    The agent should use empirical_refs instead to avoid false authority claims.
    WARN-only — never blocks sprint.
    """
    from pathlib import Path as _Path
    import yaml as _yaml

    _r = repo_root or _Path(__file__).parent.parent.parent
    _qname_dir = _r / "shared" / "qname-registry"
    _NON_AUTHORITATIVE = {"code_introspection", "community_informal_spec", "informational_rfc"}

    # Build format → authority_source map from qname registries
    _fmt_authority: dict = {}
    try:
        for _yf in _qname_dir.glob("*.yaml"):
            if _yf.name == "schema.yaml":
                continue
            fmt = _yf.stem
            try:
                entries = _yaml.safe_load(_yf.read_text(encoding="utf-8"))
                if isinstance(entries, list) and entries:
                    for e in entries:
                        if isinstance(e, dict) and "authority_source" in e:
                            _fmt_authority[fmt] = e["authority_source"]
                            break
            except Exception:
                pass
    except Exception:
        pass

    warnings = []
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in ("PRODUCT_SOURCE", "PRODUCT_TEST"):
            continue
        # Get format_id from item
        fmt_id = item.get("format_id") or ""
        if not fmt_id:
            continue
        authority = _fmt_authority.get(fmt_id.lower(), "unknown")
        if authority not in _NON_AUTHORITATIVE:
            continue  # authoritative or unknown — skip
        spec_refs = item.get("spec_fact_refs", [])
        if not spec_refs:
            continue  # no spec_fact_refs — no issue
        warnings.append({
            "item_id": item.get("item_id", "unknown"),
            "format_id": fmt_id,
            "authority_source": authority,
            "spec_fact_refs": spec_refs,
            "issue": (
                f"Format '{fmt_id}' has authority_source: {authority} but item cites "
                f"spec_fact_refs {spec_refs}. Use empirical_refs for non-authoritative formats."
            ),
        })

    result = "WARN" if warnings else "PASS"
    return {
        "validator": "validate_sal_authority_chain",
        "result": result,
        "blocks_sprint": False,  # WARN-only
        "items": warnings,
        "summary": (
            f"V70: {len(warnings)} item(s) cite spec_fact_refs for non-authoritative format(s)"
            if warnings else "V70: SAL authority chain clean — no circular refs detected"
        ),
    }


# V71 — TC-FL-007: lane_dag_ordering_validator
# Enforces: system-healing (Lane 1-6) gaps must be resolved before product deepening (Lane 7-13).
# WARN for P4+ open system-healing gaps; FAIL for P2+ open system-healing gaps.
# System-healing gaps are identified by gap_id prefix patterns.
_SYSTEM_HEALING_GAP_PREFIXES = (
    "GAP-CHAIN-",       # SAL chain broken
    "GAP-FORENSICS-",   # forensic investigation findings
    "GAP-SAL-",         # SAL authority
    "GAP-PROD-INV-QNAME-",  # QName compliance
    "GAP-PROD-INV-MASQ-",   # analytics masquerade (architecture debt)
    "GAP-PROD-INV-MODEL-",  # domain model missing
)
_SYSTEM_HEALING_GAP_CLOSED_STATUSES = {"closed", "DEFERRED_BY_DESIGN", "WONT_FIX", "deferred"}
_SYSTEM_HEALING_HIGH_PRIORITY = {"P0", "P1", "P2"}  # blocks sprint (FAIL)
_SYSTEM_HEALING_WARN_PRIORITY = {"P3", "P4"}         # WARN only


def validate_lane_dag_ordering(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V71 (TC-FL-007): Enforce Lane DAG — system healing before product deepening.

    For any PRODUCT_SOURCE item targeting a format:
    - Check if any open system-healing (Lane 1-6 proxy) gaps exist for that format
    - P2+ open gaps: FAIL (blocks_sprint=True)
    - P4+ open gaps: WARN (blocks_sprint=False)
    - Closed or DEFERRED_BY_DESIGN gaps do not trigger

    Gap ID prefixes that represent system healing:
      GAP-CHAIN-*, GAP-FORENSICS-*, GAP-SAL-*, GAP-PROD-INV-QNAME-*,
      GAP-PROD-INV-MASQ-*, GAP-PROD-INV-MODEL-*
    """
    import json as _json
    from pathlib import Path as _Path

    _r = repo_root or _Path(__file__).parent.parent.parent
    _gl_path = _r / "reports" / "capability-layer" / "gap-ledger.json"

    # Load gap-ledger; skip if unavailable
    try:
        _gl_data = _json.loads(_gl_path.read_text(encoding="utf-8"))
        _gl_entries = _gl_data if isinstance(_gl_data, list) else _gl_data.get("gaps", [])
    except Exception:
        return {
            "validator": "validate_lane_dag_ordering",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V71: Gap ledger unavailable — lane DAG check skipped",
        }

    # Build format → open system-healing gaps
    _open_healing_by_format: dict = {}
    for gap in _gl_entries:
        gid = gap.get("gap_id", "")
        status = gap.get("status", "open")
        if status in _SYSTEM_HEALING_GAP_CLOSED_STATUSES:
            continue
        if not any(gid.startswith(p) for p in _SYSTEM_HEALING_GAP_PREFIXES):
            continue
        # Extract format from gap_id (e.g., GAP-CHAIN-CSV-SAL-MRH-001 → csv)
        fmt = gap.get("format") or ""
        if not fmt:
            # Try to extract from gap_id second segment
            parts = gid.split("-")
            if len(parts) >= 3:
                fmt = parts[2].lower()
        if fmt:
            _open_healing_by_format.setdefault(fmt, []).append({
                "gap_id": gid, "priority": gap.get("priority", "P4"), "status": status,
            })

    fail_items = []
    warn_items = []
    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") not in ("PRODUCT_SOURCE", "PRODUCT_TEST"):
            continue
        fmt_id = (item.get("format_id") or "").lower()
        if not fmt_id:
            continue
        open_gaps = _open_healing_by_format.get(fmt_id, [])
        for gap in open_gaps:
            entry = {
                "item_id": item.get("item_id", "unknown"),
                "format_id": fmt_id,
                "gap_id": gap["gap_id"],
                "gap_priority": gap["priority"],
                "gap_status": gap["status"],
                "issue": (
                    f"Open system-healing gap {gap['gap_id']} (priority={gap['priority']}) "
                    f"must be resolved before PRODUCT_SOURCE work on '{fmt_id}'."
                ),
            }
            if gap["priority"] in _SYSTEM_HEALING_HIGH_PRIORITY:
                fail_items.append(entry)
            else:
                warn_items.append(entry)

    if fail_items:
        return {
            "validator": "validate_lane_dag_ordering",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": fail_items + warn_items,
            "summary": (
                f"V71: {len(fail_items)} P2+ system-healing gap(s) block product work "
                f"(Lane 1-6 must complete before Lane 7-13)"
            ),
        }
    if warn_items:
        return {
            "validator": "validate_lane_dag_ordering",
            "result": "WARN",
            "blocks_sprint": False,
            "items": warn_items,
            "summary": f"V71: {len(warn_items)} P3-P4 system-healing gap(s) pending (WARN-only)",
        }
    return {
        "validator": "validate_lane_dag_ordering",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V71: Lane DAG ordering satisfied — no open system-healing gaps block product work",
    }


# V72 — TC-FL-010: artifact_identity_validator
# WARN for PRODUCT_SOURCE items; FAIL for RELEASE_GATE items missing artifact_id/authority.
_VALID_AUTHORITY_VALUES = {"AUTHORITATIVE", "VERIFIED_DERIVATION", "AI_DRAFT", "UNVERIFIED"}


def validate_artifact_identity(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V72 (TC-FL-010): Check evidence_artifacts have artifact_id and authority fields.

    RELEASE_GATE items: FAIL (blocks_sprint=True) when evidence artifacts lack artifact_id
      and authority fields.
    PRODUCT_SOURCE/GOVERNANCE_TASKCARD items: WARN only (blocks_sprint=False).
    """
    _RELEASE_GATE_TYPES = {"RELEASE_GATE", "READINESS"}
    _WARN_TYPES = {"PRODUCT_SOURCE", "PRODUCT_TEST", "GOVERNANCE_TASKCARD"}

    fail_items = []
    warn_items = []

    for item in declaration.get("planned_work_items", []):
        item_type = item.get("item_type", "")
        if item_type not in _RELEASE_GATE_TYPES and item_type not in _WARN_TYPES:
            continue

        for artifact in item.get("evidence_artifacts", []):
            issues = []
            if not artifact.get("artifact_id"):
                issues.append("missing artifact_id")
            authority = artifact.get("authority")
            if not authority:
                issues.append("missing authority")
            elif authority not in _VALID_AUTHORITY_VALUES:
                issues.append(f"invalid authority '{authority}' (must be one of {sorted(_VALID_AUTHORITY_VALUES)})")

            if issues:
                entry = {
                    "item_id": item.get("item_id", "unknown"),
                    "item_type": item_type,
                    "artifact_path": artifact.get("path", "unknown"),
                    "issues": issues,
                    "issue": f"Artifact '{artifact.get('path', '?')}': {'; '.join(issues)}",
                }
                if item_type in _RELEASE_GATE_TYPES:
                    fail_items.append(entry)
                else:
                    warn_items.append(entry)

    if fail_items:
        return {
            "validator": "validate_artifact_identity",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": fail_items + warn_items,
            "summary": (
                f"V72: {len(fail_items)} RELEASE_GATE artifact(s) missing artifact_id/authority"
            ),
        }
    if warn_items:
        return {
            "validator": "validate_artifact_identity",
            "result": "WARN",
            "blocks_sprint": False,
            "items": warn_items,
            "summary": f"V72: {len(warn_items)} artifact(s) missing identity fields (WARN-only)",
        }
    return {
        "validator": "validate_artifact_identity",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V72: All evidence artifacts have required identity fields",
    }


# ---------------------------------------------------------------------------
# V-SGF-001: validate_skill_attribution_in_declaration (TC-SGF-002)
# Closes SKILL-GAP-012: declaration bypass — agents that skip declarations
# bypass all governance validators.
#
# Enforcement levels (per TC-SGF-002 spec):
#   - Missing declared_skill_ids → WARN only until 2026-09-01, then BLOCK
#   - declared_skill_ids present but contains unregistered IDs → BLOCK immediately
#   - declared_skill_ids with all valid active IDs → PASS
#   - Non-PRODUCT_SOURCE items → skip
# ---------------------------------------------------------------------------

_SKILL_REGISTRY_CACHE: dict | None = None
_SKILL_ATTRIBUTION_WARN_CUTOFF = "2026-09-01"  # date after which WARN becomes BLOCK


def _load_skill_registry(repo_root: Path | None) -> set[str]:
    """Return the set of active skill_ids from skill-registry.yaml."""
    import yaml as _yaml

    if repo_root is None:
        return set()
    registry_path = repo_root / ".supervisor" / "skill-registry.yaml"
    if not registry_path.exists():
        return set()
    try:
        data = _yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        skills = data.get("skills", [])
        return {
            s["skill_id"]
            for s in skills
            if isinstance(s, dict)
            and s.get("status") in ("active",)
            and not s.get("deprecated", False)
            and "skill_id" in s
        }
    except Exception:
        return set()


def validate_skill_attribution_in_declaration(
    declaration: dict, repo_root: Path
) -> dict:
    """
    V-SGF-001: Check that PRODUCT_SOURCE work items in the declaration have
    a `declared_skill_ids` field populated with registered active skill IDs.

    WARN-only for missing field (until 2026-09-01), BLOCK for unregistered IDs.
    """
    from datetime import date

    items = declaration.get("completed_work_items", []) + declaration.get("planned_work_items", [])
    product_source_items = [
        item for item in items
        if isinstance(item, dict) and item.get("item_type") in ("PRODUCT_SOURCE", "PRODUCT_TEST")
    ]

    if not product_source_items:
        return {
            "validator": "validate_skill_attribution_in_declaration",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V-SGF-001: No PRODUCT_SOURCE/PRODUCT_TEST items — skill attribution check skipped",
        }

    active_skill_ids = _load_skill_registry(repo_root)

    missing_attribution: list[dict] = []
    unregistered_skill_ids: list[dict] = []

    for item in product_source_items:
        item_id = item.get("item_id", item.get("id", "UNKNOWN"))
        declared = item.get("declared_skill_ids")

        if declared is None or (isinstance(declared, list) and len(declared) == 0):
            missing_attribution.append({
                "item_id": item_id,
                "reason": "missing_skill_attribution",
                "declared_skill_ids": declared,
            })
            continue

        if not isinstance(declared, list):
            missing_attribution.append({
                "item_id": item_id,
                "reason": "declared_skill_ids_not_a_list",
                "declared_skill_ids": declared,
            })
            continue

        # Check each declared skill_id against registry
        if active_skill_ids:  # only block if registry loaded successfully
            for sid in declared:
                if sid not in active_skill_ids:
                    unregistered_skill_ids.append({
                        "item_id": item_id,
                        "reason": "unregistered_skill_id",
                        "skill_id": sid,
                        "registered_example": sorted(active_skill_ids)[:3] if active_skill_ids else [],
                    })

    # Unregistered skill IDs → BLOCK immediately (TC-SGF-002 spec)
    if unregistered_skill_ids:
        return {
            "validator": "validate_skill_attribution_in_declaration",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": unregistered_skill_ids + missing_attribution,
            "summary": (
                f"V-SGF-001: {len(unregistered_skill_ids)} item(s) declare unregistered skill IDs — BLOCKED"
            ),
        }

    # Missing declared_skill_ids → WARN until 2026-09-01, then BLOCK
    if missing_attribution:
        today = date.today()
        cutoff = date(2026, 9, 1)
        blocks = today >= cutoff

        return {
            "validator": "validate_skill_attribution_in_declaration",
            "result": "FAIL" if blocks else "WARN",
            "blocks_sprint": blocks,
            "items": missing_attribution,
            "summary": (
                f"V-SGF-001: {len(missing_attribution)} PRODUCT_SOURCE item(s) missing declared_skill_ids "
                f"({'BLOCKED' if blocks else 'WARN-only until 2026-09-01'})"
            ),
        }

    return {
        "validator": "validate_skill_attribution_in_declaration",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": (
            f"V-SGF-001: All {len(product_source_items)} PRODUCT_SOURCE item(s) have valid skill attribution"
        ),
    }


# V74 (TC-PDL-005): validate_ledger_continuation_gate extracted to governance_validators_ledger.py
# to keep this file within its baseline_loc_cap. Imported here for backward compatibility.
from governance_validators_ledger import validate_ledger_continuation_gate  # noqa: F401, E402
