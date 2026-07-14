"""Oracle-depth governance validators (FF-XPLAN-001 W3-001, TC-W1A-003).

Validates that oracle evidence meets minimum depth requirements.
V143: validate_oracle_depth_minimum — WARN if D0-majority
V144: validate_stale_oracle_detection — WARN if stale-oracle-report.json absent or stale
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
            "blocks_sprint": False,
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
        depth_hist = summary.get("depth_histogram", {})
        formats_checked.append(format_id)

        # TC-OIS-007 / MCP-W5-001 Pillar 4: Distribution-aware depth check.
        # Fire if D0 is the majority case type, not only when ALL are D0.
        d0_count = depth_hist.get("D0", 0)
        d1_plus_count = sum(v for k, v in depth_hist.items() if k != "D0")
        total_cases = d0_count + d1_plus_count

        if depth == "D0":
            findings.append({
                "format": format_id,
                "depth": depth,
                "pass_rate": pass_rate,
                "issue": "All oracle cases at D0 — no property comparison",
            })
        elif total_cases > 0 and d0_count > d1_plus_count:
            findings.append({
                "format": format_id,
                "depth": depth,
                "pass_rate": pass_rate,
                "d0_count": d0_count,
                "d1_plus_count": d1_plus_count,
                "issue": f"D0-majority: {d0_count}/{total_cases} cases at D0 (format_depth_score={depth} from minority)",
            })

    if findings:
        return {
            "validator": "validate_oracle_depth_minimum",
            "result": "WARN",
            "detail": f"{len(findings)}/{len(formats_checked)} formats at D0-only depth",
            "findings": findings,
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_oracle_depth_minimum",
        "result": "PASS",
        "detail": f"All {len(formats_checked)} formats at D1+ depth",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_STALE_ORACLE_DETECTION", domain="oracle")
def validate_stale_oracle_detection(declaration: dict, repo_root: Path | None = None) -> dict:
    """V144: WARN if stale-oracle-report.json is absent or reports stale formats.

    TC-W1A-003: Stale oracle detection governance gate.
    Non-blocking WARN — instructs operators to re-run detect_stale_oracles.py.
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    report_path = repo_root / "oracle" / "reports" / "stale-oracle-report.json"
    if not report_path.exists():
        return {
            "validator": "validate_stale_oracle_detection",
            "result": "WARN",
            "detail": "oracle/reports/stale-oracle-report.json not found — run detect_stale_oracles.py",
            "blocks_sprint": False,
        }

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "validator": "validate_stale_oracle_detection",
            "result": "WARN",
            "detail": f"Could not parse stale-oracle-report.json: {e}",
            "blocks_sprint": False,
        }

    stale_formats = report.get("stale_formats", [])
    verdict = report.get("overall_verdict", "UNKNOWN")

    if stale_formats:
        return {
            "validator": "validate_stale_oracle_detection",
            "result": "WARN",
            "detail": f"{len(stale_formats)} stale oracle format(s): {stale_formats}",
            "stale_formats": stale_formats,
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_stale_oracle_detection",
        "result": "PASS",
        "detail": f"Stale oracle report present. Verdict: {verdict}",
        "blocks_sprint": False,
    }


# Formats that are structural/schema helpers, not product formats requiring oracle obligations.
_ORACLE_EXEMPT_FORMATS = frozenset({"odf-shared"})


@validator(rule_id="V_VALIDATE_FUTURE_FORMAT_ORACLE_ONBOARDING", domain="oracle")
def validate_future_format_oracle_onboarding(declaration: dict, repo_root: Path | None = None) -> dict:
    """V145: Every format in format-registry.yaml must have an oracle registry entry.

    TC-W2-001: Future-format auto-onboarding governance gate.
    FAIL (blocks_sprint=True) if any non-exempt format_id is missing from
    oracle/registry/format-oracle-registry.yaml.
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    import yaml  # noqa: PLC0415

    fmt_registry_path = repo_root / "registry" / "format-registry.yaml"
    oracle_registry_path = repo_root / "oracle" / "registry" / "format-oracle-registry.yaml"

    if not fmt_registry_path.exists():
        return {
            "validator": "validate_future_format_oracle_onboarding",
            "result": "SKIP",
            "detail": "registry/format-registry.yaml not found",
            "blocks_sprint": False,
        }
    if not oracle_registry_path.exists():
        return {
            "validator": "validate_future_format_oracle_onboarding",
            "result": "SKIP",
            "detail": "oracle/registry/format-oracle-registry.yaml not found",
            "blocks_sprint": False,
        }

    try:
        fmt_reg = yaml.safe_load(fmt_registry_path.read_text(encoding="utf-8"))
        oracle_reg = yaml.safe_load(oracle_registry_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "validator": "validate_future_format_oracle_onboarding",
            "result": "WARN",
            "detail": f"Could not parse registry files: {e}",
            "blocks_sprint": False,
        }

    formats_list = fmt_reg.get("formats", [])
    format_ids = {
        (f.get("format_id") if isinstance(f, dict) else f)
        for f in formats_list
        if not (isinstance(f, dict) and f.get("implementation_authorized") is False)
    } - _ORACLE_EXEMPT_FORMATS

    oracle_entries = oracle_reg.get("format_oracles", [])
    oracle_format_ids = {e.get("format_id") for e in oracle_entries if e.get("format_id")}

    missing = sorted(format_ids - oracle_format_ids)

    if missing:
        return {
            "validator": "validate_future_format_oracle_onboarding",
            "result": "FAIL",
            "detail": f"{len(missing)} format(s) missing oracle obligation: {missing}",
            "missing_formats": missing,
            "blocks_sprint": True,
        }

    return {
        "validator": "validate_future_format_oracle_onboarding",
        "result": "PASS",
        "detail": f"All {len(format_ids)} registered formats have oracle obligations",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_ORACLE_GATE_ADVANCEMENT", domain="oracle")
def validate_oracle_gate_advancement(declaration: dict, repo_root: Path | None = None) -> dict:
    """V146: WARN if any VERIFIED format lacks D1+ oracle depth evidence.

    TC-W2-002: Oracle gate-advancement governance gate.
    WARN (non-blocking) — formats at D0 block G2 gate but not sprints.
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    oracle_dir = repo_root / "oracle" / "formats"
    if not oracle_dir.is_dir():
        return {
            "validator": "validate_oracle_gate_advancement",
            "result": "SKIP",
            "detail": "oracle/formats/ directory not found",
            "blocks_sprint": False,
        }

    d0_formats = []
    verified_formats = []
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

        fmt_id = summary.get("format_id", fmt_dir.name)
        depth = summary.get("format_depth_score", "D0")
        verified_formats.append(fmt_id)
        if depth == "D0":
            d0_formats.append(fmt_id)

    if d0_formats:
        return {
            "validator": "validate_oracle_gate_advancement",
            "result": "WARN",
            "detail": f"{len(d0_formats)}/{len(verified_formats)} formats at D0 — G2 gate will block release",
            "d0_formats": d0_formats,
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_oracle_gate_advancement",
        "result": "PASS",
        "detail": f"All {len(verified_formats)} VERIFIED formats at D1+ — G2 gate clear",
        "blocks_sprint": False,
    }
