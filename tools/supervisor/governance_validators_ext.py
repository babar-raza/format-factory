"""governance_validators_ext.py — Extension validators for governance_validators.py

This file exists to keep governance_validators.py within its baseline_loc_cap.
New validators (V48+) are placed here and imported at the bottom of governance_validators.py.

Pattern mirrors analytics extraction pattern used for format codecs:
  governance_validators.py imports from governance_validators_ext at module bottom.
  governance_validator_runner.py registers both sets of validators in run_all_governance_validators().

TC-WHALE-GOVBLOCK-001 (2026-06-21): V48 extracted here per source baseline LOC cap policy.
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
