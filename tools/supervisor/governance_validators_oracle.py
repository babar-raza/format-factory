"""Oracle-depth governance validators (FF-XPLAN-001 W3-001).

Validates that oracle evidence meets minimum depth requirements.
"""
from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@validator(rule_id="V_VALIDATE_ORACLE_DEPTH_MINIMUM", domain="oracle")
def validate_oracle_depth_minimum(declaration: dict, repo_root: Path | None = None) -> dict:
    """V-ORACLE-DEPTH: WARN if any VERIFIED format has all-D0 oracle evidence.

    Checks oracle-run-summary.json for each format referenced in the declaration.
    Returns WARN (not FAIL) because D0 evidence is valid but insufficient for
    release gate G2 (which requires D1+).
    """
    if repo_root is None:
        repo_root = REPO_ROOT
    findings = []
    formats_checked = []

    # Check all formats that have oracle summaries
    oracle_dir = repo_root / "oracle" / "formats"
    if not oracle_dir.is_dir():
        return {
            "validator": "validate_oracle_depth_minimum",
            "result": "SKIP",
            "detail": "oracle/formats/ directory not found",
        }

    for fmt_dir in sorted(oracle_dir.iterdir()):
        if not fmt_dir.is_dir():
            continue
        summary_path = fmt_dir / "reports" / "oracle-run-summary.json"
        if not summary_path.exists():
            continue

        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        format_id = summary.get("format_id", fmt_dir.name)
        depth = summary.get("format_depth_score", "D0")
        pass_rate = summary.get("pass_rate", "0/0")
        formats_checked.append(format_id)

        if depth == "D0":
            findings.append({
                "format": format_id,
                "depth": depth,
                "pass_rate": pass_rate,
                "issue": "All oracle cases at D0 — no property comparison",
            })

    if findings:
        return {
            "validator": "validate_oracle_depth_minimum",
            "result": "WARN",
            "detail": f"{len(findings)}/{len(formats_checked)} formats at D0-only depth",
            "findings": findings,
        }

    return {
        "validator": "validate_oracle_depth_minimum",
        "result": "PASS",
        "detail": f"All {len(formats_checked)} formats at D1+ depth",
    }
