"""governance_validators_gate9_drift.py — V230 (TC-S6P4-SYS-005, select-6 Phase 4)

V230: validate_coverage_registry_drift
    Closes SF5: registry gate_9 block updates were fully decoupled from
    coverage-report generation -- nothing in the pipeline updated
    registry/format-registry.yaml when a coverage report was (re)generated,
    a purely manual step that was skipped for all 6 select-6 formats in a
    row. This is a drift *detector*, distinct from V227 (which enforces the
    implementation_authorized <-> gate_9_eligible linkage): V230 fires
    independently of implementation_authorized, for ANY format that has a
    coverage report at all, so drift is visible before a format is ever
    authorized, not just after.

    WARN  — a coverage report exists but the registry has no gate_9 block
            recording a coverage_source_digest at all (bookkeeping never
            done -- matches M2's finding). Non-blocking: this is the normal
            state for a format mid-Phase-4, not a regression.
    FAIL  — the registry DOES record a coverage_source_digest for this
            format's gate_9 block, but it no longer matches the report's
            current source_digest (src/python/<fmt>/ changed since the
            registry was last synced -- same severity class as V226's STALE
            check). Blocking: a stale digest is worse than no digest, since
            it actively asserts a now-false claim of currency.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from governance_validators_contract import validator

_NAME = "validate_coverage_registry_drift"
_COVERAGE_DIR_REL = "reports/spec-coverage"


def _result(result: str, summary: str, blocks: bool) -> dict:
    return {"validator": _NAME, "result": result, "summary": summary, "blocks_sprint": blocks}


def _load_registry(repo: Path) -> list[dict] | None:
    path = repo / "registry" / "format-registry.yaml"
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    formats = data.get("formats", data)
    if isinstance(formats, dict):
        return list(formats.values())
    if isinstance(formats, list):
        return formats
    return None


@validator(rule_id="V230", domain="governance")
def validate_coverage_registry_drift(declaration: dict, repo_root: "Path | None" = None) -> dict:
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    cov_dir = repo / _COVERAGE_DIR_REL
    if not cov_dir.is_dir():
        return _result("PASS", f"V230: {_COVERAGE_DIR_REL} does not exist; nothing to check", False)

    formats = _load_registry(repo)
    by_id = {f.get("format_id"): f for f in formats} if formats else {}

    no_bookkeeping: list[str] = []
    stale: list[str] = []
    for report_path in sorted(cov_dir.glob("*-coverage-report.json")):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        fmt = report.get("format_id")
        digest = report.get("source_digest")
        if not fmt or not digest:
            continue  # pre-hardening report without a digest; not this validator's concern
        entry = by_id.get(fmt, {})
        gate_9 = entry.get("gates", {}).get("gate_9", {}) if isinstance(entry, dict) else {}
        recorded_digest = gate_9.get("coverage_source_digest")
        if recorded_digest is None:
            no_bookkeeping.append(fmt)
        elif recorded_digest != digest:
            stale.append(fmt)

    if stale:
        return _result(
            "FAIL",
            f"V230 STALE: registry gate_9.coverage_source_digest no longer matches the "
            f"current coverage report for {stale} -- source changed since the registry "
            f"was last synced; re-run compute_feature_coverage.py and update the registry",
            True,
        )
    if no_bookkeeping:
        return _result(
            "WARN",
            f"V230: coverage report(s) exist with no registry gate_9.coverage_source_digest "
            f"recorded yet for {no_bookkeeping} -- normal mid-Phase-4, but must be closed "
            f"before implementation_authorized is set",
            False,
        )
    return _result("PASS", "V230: no coverage/registry drift detected", False)
