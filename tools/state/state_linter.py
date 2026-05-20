#!/usr/bin/env python3
"""
State linter — flags common project hygiene issues from live repo evidence.

Usage:
    python tools/state/state_linter.py
"""
import pathlib
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_yaml(path):
    if yaml:
        with open(path) as f:
            return yaml.safe_load(f)
    return {}


def lint_contracts():
    """Check evidence contracts for schema issues."""
    findings = []
    contracts_dir = ROOT / "tools" / "evidence" / "contracts"
    if not contracts_dir.exists():
        return [{"severity": "error", "check": "contracts_dir", "message": "contracts directory not found"}]
    for c in sorted(contracts_dir.glob("*.yaml")):
        data = _load_yaml(c)
        if not data:
            continue
        if "required_artifacts" in data:
            findings.append({
                "severity": "error",
                "check": "required_artifacts",
                "file": c.name,
                "message": f"{c.name} uses defunct required_artifacts key",
            })
        meta = data.get("min_metadata_count", 0)
        if meta and meta < 30 and not data.get("emergency_blocker_bundle", False):
            if c.name.startswith(("r2", "r3")):
                findings.append({
                    "severity": "warning",
                    "check": "below_floor_metadata",
                    "file": c.name,
                    "message": f"{c.name}: min_metadata_count={meta} < 30",
                })
    return findings


def lint_gate_overclaim():
    """Check for Gate 11 overclaim in registry."""
    findings = []
    reg_path = ROOT / "registry" / "format-registry.yaml"
    if not reg_path.exists():
        return []
    data = _load_yaml(reg_path)
    formats = data.get("formats", []) if isinstance(data, dict) else []
    for fmt in formats:
        if not isinstance(fmt, dict):
            continue
        fid = fmt.get("format_id", "?")
        gates = fmt.get("gates", {})
        if isinstance(gates, dict):
            g11 = gates.get("gate_11", {})
            if isinstance(g11, dict) and g11.get("status") == "approved":
                findings.append({
                    "severity": "error",
                    "check": "gate11_overclaim",
                    "file": "format-registry.yaml",
                    "message": f"{fid}: Gate 11 claims approved status",
                })
    return findings


def lint_commercial_ready():
    """Check for commercial_product_ready: true without evidence."""
    findings = []
    reg_path = ROOT / "registry" / "format-registry.yaml"
    if not reg_path.exists():
        return []
    content = reg_path.read_text()
    if "commercial_product_ready: true" in content:
        findings.append({
            "severity": "error",
            "check": "commercial_ready_overclaim",
            "file": "format-registry.yaml",
            "message": "commercial_product_ready: true found without Gate 11 approval",
        })
    return findings


def lint_stale_requirements():
    """Check for prose-style provenance in generated requirements input_source_hashes."""
    findings = []
    gr_dir = ROOT / "generated-requirements"
    if not gr_dir.exists():
        return []
    try:
        import yaml
    except ImportError:
        return findings
    for fmt_dir in gr_dir.iterdir():
        if not fmt_dir.is_dir():
            continue
        cr_file = fmt_dir / "commercial-requirements.yaml"
        if not cr_file.exists():
            continue
        data = yaml.safe_load(cr_file.read_text()) or {}
        input_hashes = data.get("input_source_hashes", {})
        for key, val in input_hashes.items():
            if isinstance(val, str) and "(confirmed existing)" in val:
                findings.append({
                    "severity": "warning",
                    "check": "prose_provenance",
                    "file": str(cr_file.relative_to(ROOT)),
                    "message": f"Prose in input_source_hashes[{key}]: {val}",
                })
    return findings


def lint_skill_hardcoding():
    """Check for FODS/FODT-only skill hardcoding."""
    findings = []
    skills_dir = ROOT / "tools" / "skills" / "commands"
    if not skills_dir.exists():
        return []
    for f in skills_dir.glob("*.py"):
        content = f.read_text()
        if "fods" in content.lower() or "fodt" in content.lower():
            # Check if it's just a default or hardcoded
            if "format_id" not in content.lower() and "registry" not in content.lower():
                findings.append({
                    "severity": "info",
                    "check": "skill_hardcoding",
                    "file": f.name,
                    "message": f"{f.name} references FODS/FODT (may need registry-driven support)",
                })
    return findings


def run_all_lints():
    all_findings = []
    all_findings.extend(lint_contracts())
    all_findings.extend(lint_gate_overclaim())
    all_findings.extend(lint_commercial_ready())
    all_findings.extend(lint_stale_requirements())
    all_findings.extend(lint_skill_hardcoding())
    return all_findings


def main():
    findings = run_all_lints()
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    infos = [f for f in findings if f["severity"] == "info"]

    for f in findings:
        print(f"[{f['severity'].upper()}] {f['check']}: {f['message']}")

    print(f"\nTotal: {len(findings)} findings ({len(errors)} errors, {len(warnings)} warnings, {len(infos)} info)")
    if errors:
        print("STATE_LINT: FAIL")
        sys.exit(1)
    else:
        print("STATE_LINT: PASS")


if __name__ == "__main__":
    main()
