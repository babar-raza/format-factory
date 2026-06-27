"""
validate_parity.py — Capability Sync Tool 2/7

Validates the compiled capability registry (.governance/capabilities/registry.yaml)
against the capability schema and runs four priority parity checks.

Priority levels:
  P1 (fatal): skill_has_command_file, command_has_skill
  P2 (warn):  command_in_registry, routing_coverage

Exit codes: 0 = PASS or WARN, 1 = FAIL (P1 failures exist)

Output: .governance/capabilities/parity-report.yaml
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_REGISTRY = _REPO / ".governance" / "capabilities" / "registry.yaml"
_REPORT = _REPO / ".governance" / "capabilities" / "parity-report.yaml"
_ROUTING_REG = _REPO / ".supervisor" / "capability-routing-registry.yaml"
_SKILL_REG = _REPO / ".supervisor" / "skill-registry.yaml"


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}


def _save(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=True),
                 encoding="utf-8")


def check_skill_has_command_file(capabilities: list) -> dict:
    """P1: Every active skill must have command_file_exists=True."""
    failures = []
    for cap in capabilities:
        if cap.get("status") == "deprecated":
            continue
        if cap.get("parity_status") == "ORPHAN":
            continue
        if not cap.get("command_file_exists", False):
            failures.append(f"{cap['capability_id']}: command_file_exists=False (file: {cap.get('command_file', 'missing')})")
    return {
        "check_id": "skill_has_command_file",
        "priority": "P1",
        "verdict": "FAIL" if failures else "PASS",
        "failures": failures,
        "failure_count": len(failures),
    }


def check_command_has_skill(capabilities: list) -> dict:
    """P1: No orphan command files (ORPHAN parity_status = command with no skill entry)."""
    failures = [cap["capability_id"] for cap in capabilities if cap.get("parity_status") == "ORPHAN"]
    return {
        "check_id": "command_has_skill",
        "priority": "P1",
        "verdict": "FAIL" if failures else "PASS",
        "failures": failures,
        "failure_count": len(failures),
    }


def check_command_in_registry(capabilities: list) -> dict:
    """P2: Active skills with command_file should also appear in command-registry.yaml."""
    failures = []
    for cap in capabilities:
        if cap.get("status") == "deprecated":
            continue
        if cap.get("parity_status") == "ORPHAN":
            continue
        if cap.get("command_file_exists") and not cap.get("command_registry_entry"):
            failures.append(f"{cap['capability_id']}: has command_file but missing from command-registry.yaml")
    return {
        "check_id": "command_in_registry",
        "priority": "P2",
        "verdict": "WARN" if failures else "PASS",
        "failures": failures,
        "failure_count": len(failures),
    }


def check_routing_coverage(capabilities: list) -> dict:
    """P2: All preferred_skill_ids in routing-registry must exist in skill-registry."""
    routing_data = _load(_ROUTING_REG)
    skill_data = _load(_SKILL_REG)
    known_skills = {s["skill_id"] for s in skill_data.get("skills", []) if "skill_id" in s}
    failures = []
    for route in routing_data.get("routes", []):
        route_id = route.get("route_id", "unknown")
        for sid in route.get("preferred_skill_ids", []):
            if sid not in known_skills:
                failures.append(f"route '{route_id}': preferred_skill_id '{sid}' not in skill-registry")
    return {
        "check_id": "routing_coverage",
        "priority": "P2",
        "verdict": "WARN" if failures else "PASS",
        "failures": failures,
        "failure_count": len(failures),
    }


def main(registry_path: str | None = None, output_path: str | None = None) -> int:
    reg_path = Path(registry_path) if registry_path else _REGISTRY
    if not reg_path.exists():
        print(f"ERROR: Registry not found at {reg_path}. Run inventory_capabilities.py first.")
        return 1

    registry = _load(reg_path)
    capabilities = registry.get("capabilities", [])
    source_versions = registry.get("source_versions", {})

    checks = [
        check_skill_has_command_file(capabilities),
        check_command_has_skill(capabilities),
        check_command_in_registry(capabilities),
        check_routing_coverage(capabilities),
    ]

    # Count by parity_status
    parity_counts: dict[str, int] = {}
    for cap in capabilities:
        ps = cap.get("parity_status", "UNKNOWN")
        parity_counts[ps] = parity_counts.get(ps, 0) + 1

    # Determine overall verdict
    p1_failures = any(c["priority"] == "P1" and c["verdict"] == "FAIL" for c in checks)
    p2_warnings = any(c["priority"] == "P2" and c["verdict"] == "WARN" for c in checks)
    if p1_failures:
        overall = "FAIL"
    elif p2_warnings:
        overall = "WARN"
    else:
        overall = "PASS"

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report = {
        "generated_by": "validate_parity.py",
        "generated_at": timestamp,
        "source_versions": source_versions,
        "total_capabilities": len(capabilities),
        "parity_counts": parity_counts,
        "checks": checks,
        "overall_verdict": overall,
    }

    dest = Path(output_path) if output_path else _REPORT
    _save(dest, report)

    # Print summary
    for c in checks:
        status_label = "FAIL" if c["verdict"] in ("FAIL",) else ("WARN" if c["verdict"] == "WARN" else "PASS")
        msg = f"  [{c['priority']}] {c['check_id']}: {status_label}"
        if c["failure_count"]:
            msg += f" ({c['failure_count']} issues)"
        print(msg)

    print(f"\nParity report: {overall} ({len(capabilities)} capabilities) -> {dest}")

    return 1 if p1_failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate capability registry parity")
    parser.add_argument("--registry", default=None, help="Registry path (default: .governance/capabilities/registry.yaml)")
    parser.add_argument("--output", default=None, help="Report output path")
    args = parser.parse_args()
    raise SystemExit(main(args.registry, args.output))
