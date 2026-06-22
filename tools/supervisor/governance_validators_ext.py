"""governance_validators_ext.py — Extension validators for governance_validators.py

This file exists to keep governance_validators.py within its baseline_loc_cap.
New validators (V48+) are placed here and imported at the bottom of governance_validators.py.

Pattern mirrors analytics extraction pattern used for format codecs:
  governance_validators.py imports from governance_validators_ext at module bottom.
  governance_validator_runner.py registers both sets of validators in run_all_governance_validators().

TC-WHALE-GOVBLOCK-001 (2026-06-21): V48 extracted here per source baseline LOC cap policy.
TC-ANAL-SEG-HEAL-001 (2026-06-22): V50 added here — MODULE-NAME-001 forbidden module names.
"""

from __future__ import annotations

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


def validate_forbidden_module_names(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V50 — MODULE-NAME-001: Forbid generic analytics-bucket module names.

    Blocks creation of NEW files matching:
      *_analytics_extra.py, *_extra.py, *_misc.py
      *_helpers.py / *_utils.py containing format-prefixed spec behavior

    Deletion of these files (where file does NOT exist on disk) is ALWAYS allowed.
    The validator checks Path(repo / path).exists() before flagging — so deleting
    a forbidden-named file in a sprint does NOT cause this validator to self-block.

    These names indicate code grouped by convenience, not spec hierarchy.
    Every product module must map to a spec section, element, or domain concept.

    Added 2026-06-22 (TC-ANAL-SEG-HEAL-001) as part of spec-level segregation healing.
    """
    import re

    repo = repo_root or _REPO_ROOT
    FORBIDDEN = re.compile(
        r"src/python/[^/]+/[^/]+_(analytics_extra|extra|misc)\.py$"
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
