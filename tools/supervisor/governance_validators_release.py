"""governance_validators_release.py — V144: Python release gate consistency validators.

Added 2026-07-06 as part of PYREL-001 Python product release system.

V144: validate_gate10_status_consistency
    Gate 10 status values in format-registry.yaml must be passed|failed|not_started.
    Non-standard strings (e.g. 'local_release_candidate_ready_verified') are rejected.
    blocks_sprint: True — non-standard values block release gate evaluation.
"""

from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

from pathlib import Path


# ---------------------------------------------------------------------------
# Result helper — matches standard runner schema
# ---------------------------------------------------------------------------

def _result(vid: str, name: str, passed: bool, items: list, blocks: bool = False) -> dict:
    """Standard validator result shape compatible with governance_validator_runner.py."""
    result_label = "PASS" if passed else ("FAIL" if blocks else "WARN")
    return {
        "validator": name,
        "result": result_label,
        "blocks_sprint": (not passed) and blocks,
        "items": items,
        "summary": f"{vid}: {'OK' if passed else str(len(items)) + ' issue(s)'}",
    }


# ---------------------------------------------------------------------------
# V144: Gate 10 status consistency
# ---------------------------------------------------------------------------

VALID_GATE10_STATUSES = frozenset({"passed", "failed", "not_started"})


@validator(rule_id="V_VALIDATE_GATE10_STATUS_CONSISTENCY", domain="governance",
           description="V144: Gate 10 status values must be passed|failed|not_started")
def validate_gate10_status_consistency(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V144: All gate_10.status values in format-registry.yaml must be standard values.

    Non-standard strings like 'local_release_candidate_ready_verified' indicate
    informally-managed gate state and block release gate evaluation (PYREL-001).
    blocks_sprint: True.
    """
    violations: list[str] = []

    root = Path(repo_root) if repo_root else Path(".")
    reg_path = root / "registry" / "format-registry.yaml"

    if not reg_path.exists():
        return _result("V144", "validate_gate10_status_consistency", True, [])

    try:
        import yaml
        reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    except Exception as e:
        violations.append(f"[V144] Failed to parse format-registry.yaml: {e}")
        return _result("V144", "validate_gate10_status_consistency", False, violations, True)

    for entry in reg.get("formats", []):
        fid = entry.get("id") or entry.get("format_id", "unknown")
        if fid == "odf-shared":
            continue
        gate_10 = entry.get("gates", {}).get("gate_10", None)
        if gate_10 is None:
            # Missing gate_10 key is a warning, not a hard block
            violations.append(
                f"[V144] {fid}: gates.gate_10 key is missing — add gate_10.status: not_started"
            )
            continue
        status = gate_10.get("status", None)
        if status is None:
            violations.append(f"[V144] {fid}: gates.gate_10.status is missing")
        elif status not in VALID_GATE10_STATUSES:
            violations.append(
                f"[V144] {fid}: gates.gate_10.status='{status}' is not a valid value. "
                f"Must be one of: {sorted(VALID_GATE10_STATUSES)}"
            )

    # blocks_sprint=True only if there are non-standard (not just missing) violations
    has_nonstandard = any("[V144]" in v and "not a valid value" in v for v in violations)
    return _result("V144", "validate_gate10_status_consistency", not violations, violations,
                   has_nonstandard)
