"""
build_context_pack.py — Format Factory Context Pack Builder

Builds a machine-readable snapshot of the current project state,
consumed by every generated sprint to provide accurate context.

Writes:
  .supervisor/context-pack.yaml    — machine-readable state snapshot
  reports/supervisor/context-pack.md  — human-readable summary

Usage:
  python tools/supervisor/build_context_pack.py
  python tools/supervisor/build_context_pack.py --repo-root .
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def load_yaml(path: Path) -> dict:
    if path.exists():
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}
    return {}


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def read_current_mode(repo_root: Path) -> int:
    config_path = repo_root / ".supervisor" / "config.yaml"
    if not config_path.exists():
        return 0
    text = config_path.read_text(encoding="utf-8")
    m = re.search(r"Status:\s*MODE\s*(\d+)", text, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def read_git_head(repo_root: Path) -> str:
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def read_git_status(repo_root: Path) -> dict:
    try:
        import subprocess
        r = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5
        )
        lines = r.stdout.strip().splitlines() if r.returncode == 0 else []
        modified = [l for l in lines if l.startswith(" M")]
        untracked = [l for l in lines if l.startswith("??")]
        staged = [l for l in lines if l.startswith("M ")]
        return {
            "modified_count": len(modified),
            "untracked_count": len(untracked),
            "staged_count": len(staged),
            "total_changed": len(lines),
            "clean": len(lines) == 0,
        }
    except Exception:
        return {"clean": False, "total_changed": -1}


def read_latest_sprint(repo_root: Path) -> dict:
    """Read latest sprint info from continuation signal and project-memory."""
    signal_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    signal = load_json(signal_path)

    # Also try to read from project-memory.md
    memory_path = repo_root / ".supervisor" / "project-memory.md"
    latest_sprint_id = signal.get("source_sprint_id", "unknown")
    latest_sprint_run = "unknown"

    if latest_sprint_id and latest_sprint_id != "unknown":
        m = re.search(r"\br(\d+)\b", latest_sprint_id, re.IGNORECASE)
        if m:
            latest_sprint_run = m.group(0).upper()

    return {
        "sprint_id": latest_sprint_id,
        "run_id": latest_sprint_run,
        "autonomous_continue": signal.get("autonomous_continue", False),
        "iteration": signal.get("iteration", 0),
        "max_iterations": signal.get("max_iterations", 5),
        "hard_stops": signal.get("hard_stops_detected", []),
        "rework_items": signal.get("rework_items", []),
    }


def read_poc_matrix(repo_root: Path) -> dict:
    """Read POC target matrix for current test counts."""
    matrix_path = repo_root / "product-capability-matrix" / "poc-targets.yaml"
    matrix = load_yaml(matrix_path)

    result = {
        "sprint": matrix.get("sprint", "unknown"),
        "last_updated": matrix.get("last_updated", "unknown"),
        "commercial_net_products": {},
        "foss_python_products": {},
    }

    for product in matrix.get("commercial_net_products", []):
        fmt = product.get("format", "unknown")
        dotnet_status = product.get("dotnet_status", {})
        result["commercial_net_products"][fmt] = {
            "dotnet_tests": dotnet_status.get("dotnet_tests", 0),
            "gate_11_status": product.get("gate_11_g11g", "unknown"),
            "commercial_ready": product.get("commercial_product_ready", False),
        }

    for product in matrix.get("foss_python_products", []):
        fmt = product.get("format", "unknown")
        python_status = product.get("python_status", {})
        result["foss_python_products"][fmt] = {
            "gate_status": product.get("gate_status", "unknown"),
            "installed_workflow": python_status.get("installed_workflow", "unknown"),
        }

    return result


def read_skill_registry(repo_root: Path) -> dict:
    """Read governed skill registry."""
    registry_path = repo_root / ".supervisor" / "skill-registry.yaml"
    registry = load_yaml(registry_path)

    skills = registry.get("skills", [])
    active = [s for s in skills if s.get("status") == "active"]
    return {
        "total_skills": len(skills),
        "active_skills": len(active),
        "skill_ids": [s.get("skill_id", "?") for s in active],
        "source_edits_require_handoff": registry.get("global_controls", {}).get("source_edits_require_explicit_handoff", True),
        "ledger_required": registry.get("global_controls", {}).get("product_code_ledger_required_before_source_edit", True),
    }


def read_ledger(repo_root: Path) -> dict:
    """Read product-code change ledger summary."""
    ledger_path = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
    ledger = load_json(ledger_path)
    entries = ledger.get("entries", [])
    governed = [e for e in entries if e.get("classification") == "GOVERNED_PRODUCT_CHANGE"]
    backfilled = [e for e in entries if e.get("classification") == "BACKFILLED_PRE_GOVERNANCE"]
    return {
        "total_entries": len(entries),
        "governed_changes": len(governed),
        "backfilled": len(backfilled),
        "ledger_path": str(ledger_path.relative_to(repo_root)),
    }


def read_mcp_status(repo_root: Path) -> dict:
    """Classify MCP status based on physical file presence and mode."""
    mcp_path = repo_root / ".vscode" / "mcp.json"
    config_mode = read_current_mode(repo_root)

    if not mcp_path.exists():
        return {
            "classification": "MCP_CONFIG_MISSING",
            "file_present": False,
            "mode": config_mode,
            "description": ".vscode/mcp.json not found",
        }

    try:
        mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
        servers = mcp_data.get("servers", mcp_data.get("mcpServers", {}))
        server_count = len(servers) if isinstance(servers, dict) else 0
    except Exception:
        server_count = 0

    if config_mode >= 4:
        classification = "MCP_CONFIG_PRESENT_MODE4_ACTIVE"
    else:
        classification = "MCP_CONFIG_PRESENT_NOT_ACTIVE"

    return {
        "classification": classification,
        "file_present": True,
        "mode": config_mode,
        "server_count": server_count,
        "description": f".vscode/mcp.json present with {server_count} server(s); MODE {config_mode}",
    }


def build_context_pack(repo_root: Path) -> dict:
    """Build the full context pack."""
    timestamp = datetime.now().isoformat()

    return {
        "schema_version": "1.0",
        "generated_at": timestamp,
        "repo_root": str(repo_root),
        "git": {
            "head": read_git_head(repo_root),
            "status": read_git_status(repo_root),
        },
        "supervisor_mode": read_current_mode(repo_root),
        "latest_sprint": read_latest_sprint(repo_root),
        "poc_matrix": read_poc_matrix(repo_root),
        "skill_registry": read_skill_registry(repo_root),
        "product_code_ledger": read_ledger(repo_root),
        "mcp_status": read_mcp_status(repo_root),
        "authority": {
            "supervisor_is_advisory": True,
            "gate_approval_requires_babar_raza": True,
            "commit_requires_user_auth": True,
            "push_requires_user_auth": True,
            "publication_blocked": True,
        },
    }


def generate_md(pack: dict) -> str:
    sprint = pack["latest_sprint"]
    poc = pack["poc_matrix"]
    skills = pack["skill_registry"]
    ledger = pack["product_code_ledger"]
    mcp = pack["mcp_status"]
    git = pack["git"]

    fods_tests = poc["commercial_net_products"].get("FODS", {}).get("dotnet_tests", "?")
    fodt_tests = poc["commercial_net_products"].get("FODT", {}).get("dotnet_tests", "?")
    netpbm_tests = poc["commercial_net_products"].get("Netpbm", {}).get("dotnet_tests", "?")

    net_total = sum(
        v.get("dotnet_tests", 0)
        for v in poc["commercial_net_products"].values()
        if isinstance(v.get("dotnet_tests"), int)
    )

    return f"""# Supervisor Context Pack
# Format Factory — Machine-Readable State Snapshot
# Generated: {pack['generated_at']}
# ADVISORY ONLY — not a gate approval or authority document

## Current State

| Item | Value |
|------|-------|
| Git HEAD | {git['head']} |
| Working tree clean | {git['status'].get('clean', False)} |
| Supervisor mode | MODE {pack['supervisor_mode']} |
| Latest sprint | {sprint['run_id']} |
| Sprint ID | {sprint['sprint_id'][:60]}... |
| Autonomous continue | {sprint['autonomous_continue']} |
| Iteration | {sprint['iteration']}/{sprint['max_iterations']} |
| MCP status | {mcp['classification']} |
| Active skills | {skills['active_skills']} |
| Ledger entries | {ledger['total_entries']} total ({ledger['governed_changes']} governed) |

## .NET Test Counts (POC Matrix)

| Format | Tests | Gate 11 |
|--------|-------|---------|
| FODS | {fods_tests} | {poc['commercial_net_products'].get('FODS', {}).get('gate_11_status', '?')} |
| FODT | {fodt_tests} | {poc['commercial_net_products'].get('FODT', {}).get('gate_11_status', '?')} |
| Netpbm | {netpbm_tests} | {poc['commercial_net_products'].get('Netpbm', {}).get('gate_11_status', '?')} |
| **Total** | **{net_total}** | — |

## Skill Registry

Skills: {', '.join(skills['skill_ids'])}

## Governance

- Source edits require governed skill or handoff: {skills['source_edits_require_handoff']}
- Product-code ledger required: {skills['ledger_required']}
- Gate 11 approval: requires Babar Raza (NOT_STARTED)
- Publication: BLOCKED pending Gate 11 G11-G
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Format Factory supervisor context pack")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir or repo_root / "reports" / "supervisor"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=== BUILD CONTEXT PACK ===")
    pack = build_context_pack(repo_root)

    # Write .supervisor/context-pack.yaml
    context_yaml_path = repo_root / ".supervisor" / "context-pack.yaml"
    context_yaml_path.write_text(
        yaml.dump(pack, default_flow_style=False, sort_keys=False),
        encoding="utf-8"
    )
    print(f"  Written: {context_yaml_path}")

    # Write reports/supervisor/context-pack.md
    md_path = output_dir / "context-pack.md"
    md_path.write_text(generate_md(pack), encoding="utf-8")
    print(f"  Written: {md_path}")

    # Print summary
    sprint = pack["latest_sprint"]
    poc = pack["poc_matrix"]
    print(f"  Latest sprint: {sprint['run_id']} (iteration {sprint['iteration']}/{sprint['max_iterations']})")
    print(f"  Autonomous continue: {sprint['autonomous_continue']}")
    print(f"  MCP: {pack['mcp_status']['classification']}")
    net_total = sum(
        v.get("dotnet_tests", 0)
        for v in poc["commercial_net_products"].values()
        if isinstance(v.get("dotnet_tests"), int)
    )
    print(f"  .NET tests: {net_total} total")
    print("CONTEXT_PACK: BUILT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
