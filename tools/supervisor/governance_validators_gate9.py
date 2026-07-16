"""governance_validators_gate9.py — V227 (TC-S6P4-SYS-001, select-6 Phase 4)

V227: validate_gate9_implementation_authorization_linkage
    FAIL (blocks) when `implementation_authorized: true` in
    registry/format-registry.yaml is not backed by a real, eligible spec-
    coverage report. Mechanically enforces the rule `docs/gates.md` Gate 9
    criterion 7 has stated in prose since Phase 3 of the select-6 plan but
    that no validator ever checked (SF1, disclosed 2026-07-15): a coverage
    report at reports/spec-coverage/<fmt>-coverage-report.json must exist
    and show gate_9_eligible: true before implementation_authorized may be
    true. This is the SAME root-cause class already disclosed once before
    for the `gate-required` skill frontmatter (Phase 2's "pure documentation,
    zero runtime enforcement" finding) -- recurring in a different gate,
    now closed by an actual check instead of a second prose note.

    Deliberately blocks (not WARN): an unenforced Gate 9 rule is how six
    formats reached implementation_authorized-worthy claims with zero
    registry bookkeeping in the first place.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from governance_validators_contract import validator

_NAME = "validate_gate9_implementation_authorization_linkage"
_COVERAGE_DIR_REL = "reports/spec-coverage"
_BASELINE_REL = "registry/gate9-coverage-baseline.yaml"
_FIX_HINT = (
    "run: python tools/specification-authority-layer/compute_feature_coverage.py "
    "--format <fmt> --confirmed <fmt>-confirmed.json --deferred-reasons <fmt>-deferred.json"
)


def _load_grandfathered(repo: Path) -> set[str]:
    """Formats authorized before the coverage-gate machinery existed
    (2026-07-15, select-6 Phase 3). See registry/gate9-coverage-baseline.yaml
    docstring -- write-once, never grow this to dodge V227 for a new format."""
    path = repo / _BASELINE_REL
    if not path.exists():
        return set()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {e["format_id"] for e in data.get("grandfathered_pre_phase3", [])
            if e.get("format_id")}


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


@validator(rule_id="V227", domain="governance")
def validate_gate9_implementation_authorization_linkage(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    formats = _load_registry(repo)
    if formats is None:
        return _result("WARN", f"{_NAME}: registry/format-registry.yaml unreadable", False)

    grandfathered = _load_grandfathered(repo)
    authorized = [f for f in formats if f.get("implementation_authorized") is True
                 and f.get("format_id") not in grandfathered]
    if not authorized:
        return _result(
            "PASS",
            f"V227: no non-grandfathered formats currently authorized; nothing to check "
            f"({len(grandfathered)} pre-Phase-3 formats exempt per {_BASELINE_REL})",
            False,
        )

    problems: list[str] = []
    for entry in authorized:
        fmt = entry.get("format_id", "<unknown>")
        report_path = repo / _COVERAGE_DIR_REL / f"{fmt}-coverage-report.json"
        if not report_path.exists():
            problems.append(f"{fmt}: implementation_authorized=true but no coverage report "
                            f"at {_COVERAGE_DIR_REL}/{fmt}-coverage-report.json")
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{fmt}: coverage report unreadable ({exc})")
            continue
        if report.get("gate_9_eligible") is not True:
            problems.append(f"{fmt}: coverage report exists but gate_9_eligible is not true "
                            f"(got {report.get('gate_9_eligible')!r})")

    if problems:
        return _result(
            "FAIL",
            "V227: implementation_authorized set without an eligible coverage report for "
            + "; ".join(problems) + f" -- {_FIX_HINT}",
            True,
        )
    return _result(
        "PASS",
        f"V227: all {len(authorized)} implementation_authorized format(s) backed by an "
        f"eligible coverage report",
        False,
    )
