#!/usr/bin/env python3
"""
Computed state snapshot — produces state/current-state.json and state/current-state.md
from live repository evidence.

Usage:
    python tools/state/state_snapshot.py [--output-dir state/]
"""
import argparse
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Physical invariant layer — import from tools/evidence/
try:
    _EVIDENCE_DIR = str(pathlib.Path(__file__).resolve().parent.parent / "evidence")
    if _EVIDENCE_DIR not in sys.path:
        sys.path.insert(0, _EVIDENCE_DIR)
    from check_repo_invariants import check_all_invariants as _check_all_invariants
    _HAS_PHYSICAL_INVARIANTS = True
except ImportError:
    _HAS_PHYSICAL_INVARIANTS = False
    _check_all_invariants = None


def _load_yaml(path):
    if yaml:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    # minimal fallback
    return {}


def count_formats_in_registry():
    reg_path = ROOT / "registry" / "format-registry.yaml"
    if not reg_path.exists():
        return 0, []
    data = _load_yaml(reg_path)
    formats = data.get("formats", []) if isinstance(data, dict) else []
    return len(formats), [f.get("format_id", "?") for f in formats if isinstance(f, dict)]


def get_gate_summary():
    matrix_path = ROOT / "registry" / "format-completion-matrix.yaml"
    if not matrix_path.exists():
        return {}
    data = _load_yaml(matrix_path)
    return data.get("formats", {}) if isinstance(data, dict) else {}


def get_generated_requirements_status():
    gr_dir = ROOT / "generated-requirements"
    if not gr_dir.exists():
        return {}
    result = {}
    for fmt_dir in sorted(gr_dir.iterdir()):
        if fmt_dir.is_dir():
            files = list(fmt_dir.glob("*.yaml")) + list(fmt_dir.glob("*.yml"))
            result[fmt_dir.name] = {"file_count": len(files)}
    return result


def get_evidence_contract_status():
    contracts_dir = ROOT / "tools" / "evidence" / "contracts"
    if not contracts_dir.exists():
        return {"error": "contracts directory not found"}
    issues = []
    for c in sorted(contracts_dir.glob("*.yaml")):
        data = _load_yaml(c)
        if not data:
            continue
        if "required_artifacts" in data:
            issues.append(f"{c.name}: uses defunct required_artifacts key")
        meta = data.get("min_metadata_count", 0)
        if meta and meta < 30 and not data.get("emergency_blocker_bundle", False):
            if c.name.startswith(("r2", "r3")):
                issues.append(f"{c.name}: min_metadata_count={meta} < 30")
    return {"total_contracts": len(list(contracts_dir.glob("*.yaml"))), "issues": issues}


def get_latest_sprint():
    reports_dir = ROOT / "reports"
    latest_r = 0
    for d in reports_dir.iterdir():
        if d.is_dir() and d.name.startswith("r") and d.name[1:].isdigit():
            r_num = int(d.name[1:])
            if r_num > latest_r:
                latest_r = r_num
    if latest_r == 0:
        return {"latest": "unknown"}
    verdict_path = reports_dir / f"r{latest_r}" / "final-verdict.md"
    if verdict_path.exists():
        content = verdict_path.read_text(encoding="utf-8")
        # Try multiple verdict formats used across R25-R51+:
        # Format A: "## VERDICT: VALUE" or "**VERDICT: VALUE**" or "VERDICT: VALUE" inline
        # Format B: "**Verdict:** VALUE" or "**Verdict:** **VALUE**"
        # Format C: "## Verdict" heading followed by code-block "`VALUE`" on next line(s)
        verdict = None
        # Format A/B: VERDICT: or Verdict: followed by optional bold markers then value
        m = re.search(r"(?:^|\n)\s*\*{0,2}(?:VERDICT|Verdict):\*{0,2}\s*\*{0,2}([A-Z][A-Z0-9_]+)\*{0,2}", content)
        if m:
            verdict = m.group(1)
        # Format C: "## Verdict" heading + code-block value
        if not verdict:
            m = re.search(r"##\s+Verdict\s*\n+\s*`([A-Z][A-Z0-9_]+)`", content)
            if m:
                verdict = m.group(1)
        # Format D: "## Verdict" heading + plain-text value on next non-empty line
        if not verdict:
            m = re.search(r"##\s+Verdict\s*\n+\s*([A-Z][A-Z0-9_]{3,})\s*(?:\n|$)", content)
            if m:
                verdict = m.group(1)
        # Reject values that are just markdown noise (only underscores/digits — not a real id)
        if verdict and not re.match(r"[A-Z][A-Z0-9_]{3,}", verdict):
            verdict = None
        return {
            "latest_sprint_number": f"R{latest_r}",
            "verdict": verdict if verdict else "unknown",
        }
    return {"latest_sprint_number": f"R{latest_r}", "verdict": "no_final_verdict"}


def get_production_blockers():
    blockers = []
    if not (ROOT / "tools" / "state").exists():
        pass  # state manager is being created now
    if not (ROOT / "tools" / "package" / "build_review_package.py").exists():
        blockers.append("review_package_builder_missing")

    # Authority/governance blockers — these are real and persistent
    # G11-G requires Babar Raza written approval (not completed)
    package_manifest = ROOT / "reports" / "r42" / "package-artifact-manifest.yaml"
    if package_manifest.exists():
        text = package_manifest.read_text()
        if "gate_11: NOT_STARTED" in text or "G11-G" in text:
            blockers.append("G11-G_NOT_STARTED: Gate 11 commercial approval requires Babar Raza written approval")

    # Gate 8 security review packets awaiting human approval (ODS/ODT/QOI/XCF/DIF/PPM)
    gate8_formats_path = ROOT / "reports" / "r42" / "next-format-ranking.md"
    if gate8_formats_path.exists():
        text = gate8_formats_path.read_text()
        if "AWAITING_HUMAN_APPROVAL" in text:
            blockers.append("GATE8_AWAITING_HUMAN_APPROVAL: ODS/ODT/QOI/XCF/DIF/PPM Gate 8 security review pending")

    # Package proof gaps — check if package-artifact-manifest exists but artifacts are local-only
    if package_manifest.exists():
        text = package_manifest.read_text()
        if "push_status: NOT_PUSHED" in text or "LOCAL_POC_READY" in text:
            blockers.append("PACKAGE_NOT_PUSHED: All POC artifacts are local-only, not pushed to registry")

    # Check generated requirements input_source_hashes for prose
    gr_dir = ROOT / "generated-requirements"
    if gr_dir.exists():
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml:
            for fmt_dir in gr_dir.iterdir():
                if not fmt_dir.is_dir():
                    continue
                cr = fmt_dir / "commercial-requirements.yaml"
                if not cr.exists():
                    continue
                data = yaml.safe_load(cr.read_text()) or {}
                for val in (data.get("input_source_hashes") or {}).values():
                    if isinstance(val, str) and "(confirmed existing)" in val:
                        blockers.append(f"prose_provenance_in_{cr.name}")
                        break

    # Physical invariant layer — validates registry claims against filesystem reality
    if _HAS_PHYSICAL_INVARIANTS:
        try:
            inv_results = _check_all_invariants(ROOT)
            for inv in inv_results:
                if not inv["passed"]:
                    for detail in inv.get("details", [inv["name"]]):
                        blockers.append(f"{inv['id']}: {detail}")
        except Exception as exc:  # pragma: no cover
            blockers.append(f"physical_invariant_check_error: {exc}")
    else:
        blockers.append("check_repo_invariants_missing")

    return blockers


def build_snapshot():
    fmt_count, fmt_ids = count_formats_in_registry()
    return {
        "snapshot_version": "1.0.0",
        "format_count": fmt_count,
        "format_ids": fmt_ids,
        "gate_summary": get_gate_summary(),
        "generated_requirements": get_generated_requirements_status(),
        "evidence_contracts": get_evidence_contract_status(),
        "latest_sprint": get_latest_sprint(),
        "production_blockers": get_production_blockers(),
        "gate_11_approved": False,
        "commercial_product_ready": False,
    }


def snapshot_to_markdown(snapshot):
    lines = ["# Current State Snapshot", ""]
    lines.append(f"**Formats in registry:** {snapshot['format_count']}")
    lines.append(f"**Latest sprint:** {snapshot['latest_sprint'].get('latest_sprint_number', '?')} - {snapshot['latest_sprint'].get('verdict', '?')}")
    lines.append(f"**Gate 11 approved:** {snapshot['gate_11_approved']}")
    lines.append(f"**commercial_product_ready:** {snapshot['commercial_product_ready']}")
    lines.append("")
    lines.append("## Generated Requirements")
    for fmt, info in snapshot["generated_requirements"].items():
        lines.append(f"- {fmt}: {info['file_count']} files")
    lines.append("")
    lines.append("## Evidence Contracts")
    ec = snapshot["evidence_contracts"]
    lines.append(f"- Total: {ec.get('total_contracts', 0)}")
    for issue in ec.get("issues", []):
        lines.append(f"- ISSUE: {issue}")
    lines.append("")
    lines.append("## Production Blockers")
    for b in snapshot["production_blockers"]:
        lines.append(f"- {b}")
    if not snapshot["production_blockers"]:
        lines.append("- None detected")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Build computed state snapshot")
    parser.add_argument("--output-dir", default="state", help="Output directory")
    args = parser.parse_args()

    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshot = build_snapshot()

    json_path = out_dir / "current-state.json"
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Written: {json_path}")

    md_path = out_dir / "current-state.md"
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(snapshot_to_markdown(snapshot))
    print(f"Written: {md_path}")

    print(f"Formats: {snapshot['format_count']}")
    print(f"Latest sprint: {snapshot['latest_sprint']}")
    print(f"Production blockers: {len(snapshot['production_blockers'])}")
    print("STATE_SNAPSHOT: PASS")


if __name__ == "__main__":
    main()
