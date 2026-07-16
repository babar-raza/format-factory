"""governance_validators_gate9_baseline_integrity.py — V231
(TC-S6P4-FINAL-001b, select-6 Phase 4 final re-audit, 2026-07-16)

Closes the residual half of SF1: registry/gate9-coverage-baseline.yaml's own
docstring says it is "WRITE-ONCE for existing entries: do not add a NEW
format here to dodge V227" -- but that was a comment, not a check. Nothing
stopped a future edit from silently appending a format_id to
`grandfathered_pre_phase3` to bypass V227/V228/V229 for a format that never
actually produced a coverage report. This mirrors the exact class of gap the
final independent re-audit was designed to catch: a prose rule with no
mechanical enforcement (the same pattern already disclosed for the
`gate-required` skill frontmatter and for Gate 9 criterion 7 itself, SF1).

V231: validate_gate9_baseline_integrity
    FAIL (blocks) when the set of `format_id`s in
    registry/gate9-coverage-baseline.yaml's `grandfathered_pre_phase3` list
    does not match a pinned sha256 digest of the 7 formats frozen at
    2026-07-15 (zst, fodp, fodg, gnumeric, abw, ndjson, toml). A legitimate,
    reviewed one-time correction to the frozen set must update
    `_EXPECTED_BASELINE_SHA256` in this file in the SAME commit -- a source
    change that is visible to code review and git history, unlike a bare
    YAML data edit. Silent growth (adding a format to dodge V227 without
    touching this file) now fails loudly instead of being invisible.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from governance_validators_contract import validator

_NAME = "validate_gate9_baseline_integrity"
_BASELINE_REL = "registry/gate9-coverage-baseline.yaml"

# Pinned at TC-S6P4-SYS-001 (2026-07-15): sha256 of the "|"-joined, sorted
# format_ids frozen in registry/gate9-coverage-baseline.yaml at that time.
# sorted(["zst","fodp","fodg","gnumeric","abw","ndjson","toml"]) joined by "|"
# == "abw|fodg|fodp|gnumeric|ndjson|toml|zst"
_EXPECTED_BASELINE_SHA256 = (
    "cb5108d0dce4064e7ff496e7bba766422bdded4486b4ea4e29b3c4c0a0ec8dc6"
)
_FIX_HINT = (
    "if this is a reviewed, legitimate one-time correction to the frozen "
    "set, update _EXPECTED_BASELINE_SHA256 in "
    "tools/supervisor/governance_validators_gate9_baseline_integrity.py in "
    "the SAME commit as the YAML change; if not, revert "
    "registry/gate9-coverage-baseline.yaml -- adding a format here to skip "
    "V227/V228/V229 without a real coverage report is exactly what this "
    "validator exists to catch"
)


def _result(result: str, summary: str, blocks: bool) -> dict:
    return {"validator": _NAME, "result": result, "summary": summary, "blocks_sprint": blocks}


def _canonical_digest(format_ids: list[str]) -> str:
    canon = "|".join(sorted(format_ids))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


@validator(rule_id="V231", domain="governance")
def validate_gate9_baseline_integrity(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    path = repo / _BASELINE_REL
    if not path.exists():
        return _result(
            "WARN", f"{_NAME}: {_BASELINE_REL} not found (nothing to verify)", False
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _result("WARN", f"{_NAME}: {_BASELINE_REL} unreadable ({exc})", False)

    entries = data.get("grandfathered_pre_phase3", []) if isinstance(data, dict) else []
    format_ids = [e.get("format_id") for e in entries if isinstance(e, dict) and e.get("format_id")]
    actual_digest = _canonical_digest(format_ids)

    if actual_digest != _EXPECTED_BASELINE_SHA256:
        return _result(
            "FAIL",
            f"V231: {_BASELINE_REL} grandfathered_pre_phase3 set has drifted from the pinned "
            f"baseline (expected sha256 {_EXPECTED_BASELINE_SHA256}, got {actual_digest} for "
            f"format_ids {sorted(format_ids)}) -- {_FIX_HINT}",
            True,
        )
    return _result(
        "PASS",
        f"V231: {_BASELINE_REL} grandfathered_pre_phase3 set ({len(format_ids)} formats) "
        f"matches the pinned baseline digest",
        False,
    )
