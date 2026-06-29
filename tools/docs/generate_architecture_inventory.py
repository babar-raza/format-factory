"""Generate architecture inventory from repository evidence.

Documents the 11-layer architecture, governance validators, capabilities,
skills, and gate pipeline.

Usage:
    python tools/docs/generate_architecture_inventory.py
    python tools/docs/generate_architecture_inventory.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

LAYER_DEFINITIONS = [
    {"id": "L01", "name": "Specification Authority Layer (SAL)",
     "paths": ["tools/spec/", "shared/qname-registry/"],
     "purpose": "Extracts machine-readable facts from format specifications"},
    {"id": "L02", "name": "QName Registry",
     "paths": ["shared/qname-registry/"],
     "purpose": "Maps spec element names to canonical class names"},
    {"id": "L03", "name": "Capability Layer",
     "paths": ["reports/capability-layer/", ".governance/capabilities/"],
     "purpose": "Tracks per-format capability status and gap ledger"},
    {"id": "L05", "name": "Oracle Layer",
     "paths": ["oracle/"],
     "purpose": "Deterministic verification against spec-derived test cases"},
    {"id": "L06", "name": "Product Source",
     "paths": ["src/python/", "src/net/"],
     "purpose": "Parser, writer, and model implementations per format"},
    {"id": "L07", "name": "Test Layer",
     "paths": ["tests/"],
     "purpose": "Unit, integration, roundtrip, and security tests"},
    {"id": "L08", "name": "Evidence Layer",
     "paths": [".local/evidences/"],
     "purpose": "Sprint evidence declarations and review packages"},
    {"id": "L09", "name": "State Layer",
     "paths": [".local/supervisor/"],
     "purpose": "Continuation signals, plan locks, action queues"},
    {"id": "L11", "name": "Supervisor Layer",
     "paths": ["tools/supervisor/", "reports/supervisor/"],
     "purpose": "Autonomous sprint orchestration and grading"},
    {"id": "L12", "name": "Governance Layer",
     "paths": ["tools/supervisor/governance_validators*.py", ".governance/"],
     "purpose": "Programmatic governance enforcement (validators)"},
    {"id": "L13", "name": "Skills Layer",
     "paths": [".supervisor/skill-registry.yaml", ".claude/commands/"],
     "purpose": "Registered skill catalog and command routing"},
]


def _read_yaml(path: Path):
    if not path.exists():
        return None
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _collect_layers(repo_root: Path) -> list[dict]:
    """Check layer paths and count files."""
    layers = []
    for layer in LAYER_DEFINITIONS:
        info = {**layer, "exists": False, "file_count": 0}
        for p in layer["paths"]:
            if "*" in p:
                matches = list(repo_root.glob(p))
                if matches:
                    info["exists"] = True
                    info["file_count"] += len(matches)
            else:
                full = repo_root / p
                if full.exists():
                    info["exists"] = True
                    if full.is_dir():
                        info["file_count"] += sum(1 for _ in full.rglob("*") if _.is_file())
                    elif full.is_file():
                        info["file_count"] += 1
        layers.append(info)
    return layers


def _collect_validators(repo_root: Path) -> dict:
    """Scan governance validator files and extract validator names."""
    modules: dict[str, list[str]] = {}
    total = 0
    for f in sorted(repo_root.glob("tools/supervisor/governance_validators*.py")):
        names = []
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"^def (validate_\w+)", line)
                if m:
                    names.append(m.group(1))
        except Exception:
            pass
        if names:
            modules[f.name] = names
            total += len(names)
    return {"modules": modules, "total": total, "module_count": len(modules)}


def _collect_capabilities(repo_root: Path) -> dict:
    """Read capability registry and group by track."""
    data = _read_yaml(repo_root / ".governance" / "capabilities" / "registry.yaml")
    if not data or not isinstance(data, dict):
        return {"total": 0, "active": 0, "tracks": {}}
    caps = data.get("capabilities", [])
    tracks: dict[str, int] = {}
    active = 0
    for c in caps:
        status = c.get("status", "unknown")
        track = c.get("product_track") or "unclassified"
        if status == "active":
            active += 1
        tracks[track] = tracks.get(track, 0) + 1
    return {"total": len(caps), "active": active, "tracks": tracks}


def _collect_skills(repo_root: Path) -> dict:
    """Read skill registry summary."""
    data = _read_yaml(repo_root / ".supervisor" / "skill-registry.yaml")
    if not data or not isinstance(data, dict):
        return {"total": 0}
    skills = data.get("skills", [])
    statuses: dict[str, int] = {}
    for s in skills:
        st = s.get("status", "unknown")
        statuses[st] = statuses.get(st, 0) + 1
    return {"total": len(skills), "statuses": statuses}


def _collect_gates(repo_root: Path) -> list[dict]:
    """Read gate contract registry."""
    data = _read_yaml(repo_root / "registry" / "gate-contract-registry.yaml")
    if not data:
        return []
    gates_list = data.get("gates", []) if isinstance(data, dict) else data
    if not isinstance(gates_list, list):
        return []
    result = []
    for g in gates_list:
        result.append({
            "gate_id": g.get("gate_id", g.get("id", "?")),
            "title": g.get("title", g.get("name", "?")),
            "autonomous": g.get("autonomous", g.get("agent_executable", True)),
        })
    return result


def collect_architecture_inventory(repo_root: Path = REPO_ROOT) -> dict:
    """Collect complete architecture inventory."""
    return {
        "layers": _collect_layers(repo_root),
        "validators": _collect_validators(repo_root),
        "capabilities": _collect_capabilities(repo_root),
        "skills": _collect_skills(repo_root),
        "gates": _collect_gates(repo_root),
    }


def render_architecture_markdown(arch: dict) -> str:
    """Render architecture inventory as markdown."""
    lines = []

    # Layers
    lines.extend([
        "## Architecture — Layer Inventory",
        "",
        "Format Factory is organized into 11 independent layers, each with defined "
        "responsibilities and contracts.",
        "",
        "| Layer | Name | Purpose | Files |",
        "|---|---|---|---|",
    ])
    for layer in arch.get("layers", []):
        status = "Active" if layer["exists"] else "Missing"
        lines.append(
            f"| {layer['id']} | {layer['name']} | {layer['purpose']} "
            f"| {layer['file_count']} |"
        )

    # Validators
    val = arch.get("validators", {})
    lines.extend([
        "",
        "## Governance Validators",
        "",
        f"**{val.get('total', 0)} validators** across "
        f"**{val.get('module_count', 0)} modules**",
        "",
        "| Module | Validators |",
        "|---|---|",
    ])
    for mod_name, names in val.get("modules", {}).items():
        lines.append(f"| `{mod_name}` | {len(names)} |")

    # Capabilities
    caps = arch.get("capabilities", {})
    lines.extend([
        "",
        "## Capabilities",
        "",
        f"**{caps.get('active', 0)} active** of {caps.get('total', 0)} total capabilities",
        "",
        "| Product Track | Count |",
        "|---|---|",
    ])
    for track, count in sorted(caps.get("tracks", {}).items()):
        lines.append(f"| {track} | {count} |")

    # Skills
    skills = arch.get("skills", {})
    lines.extend([
        "",
        "## Registered Skills",
        "",
        f"**{skills.get('total', 0)} skills** registered in the skill registry",
        "",
    ])
    statuses = skills.get("statuses", {})
    if statuses:
        lines.append("| Status | Count |")
        lines.append("|---|---|")
        for st, count in sorted(statuses.items()):
            lines.append(f"| {st} | {count} |")
        lines.append("")

    # Gates
    gates = arch.get("gates", [])
    if gates:
        lines.extend([
            "## Gate Pipeline",
            "",
            f"**{len(gates)} gates** in the acquisition pipeline",
            "",
            "| Gate | Title | Agent-Executable |",
            "|---|---|---|",
        ])
        for g in gates:
            auto = "Yes" if g.get("autonomous", True) else "No (human required)"
            lines.append(f"| {g['gate_id']} | {g['title']} | {auto} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate architecture inventory")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    arch = collect_architecture_inventory(args.repo_root)
    if args.json:
        print(json.dumps(arch, indent=2, default=str))
    else:
        print(render_architecture_markdown(arch))
    return 0


if __name__ == "__main__":
    sys.exit(main())
