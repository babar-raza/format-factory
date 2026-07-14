"""
inventory_capabilities.py — Capability Sync Tool 1/7

Compile .supervisor/skill-registry.yaml + .claude/commands/command-registry.yaml
+ .supervisor/capability-routing-registry.yaml into a single canonical capability
registry at .governance/capabilities/registry.yaml.

Never modifies source registries. Read-only from all three sources.
Never deletes entries — deprecated capabilities are preserved with status=deprecated.

Exit codes: 0 = success, 1 = error
"""
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_SKILL_REG = _REPO / ".supervisor" / "skill-registry.yaml"
_CMD_REG = _REPO / ".claude" / "commands" / "command-registry.yaml"
_CMD_DIR = _REPO / ".claude" / "commands"
_ROUTING_REG = _REPO / ".supervisor" / "capability-routing-registry.yaml"
_GOVERNANCE_DIR = _REPO / ".governance" / "capabilities"
_REGISTRY_OUT = _GOVERNANCE_DIR / "registry.yaml"

# Stems to exclude from orphan detection (non-skill files in .claude/commands/)
_EXCLUDED_STEMS = {"_readme", "command-registry"}


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}


def _save(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=True),
                 encoding="utf-8")


def load_skills() -> dict:
    """Return {skill_id: skill_dict} from .supervisor/skill-registry.yaml."""
    data = _load(_SKILL_REG)
    return {s["skill_id"]: s for s in data.get("skills", []) if "skill_id" in s}


def load_commands() -> tuple[dict, set]:
    """Return ({command_id: entry}, set_of_md_stems)."""
    data = _load(_CMD_REG)
    cmd_dict = {}
    for e in data.get("commands", []):
        key = e.get("command_id") or e.get("skill_id", "")
        if key:
            cmd_dict[key] = e
    md_stems = {f.stem for f in _CMD_DIR.glob("*.md") if f.stem not in _EXCLUDED_STEMS}
    return cmd_dict, md_stems


def load_routing() -> dict:
    """Return {skill_id: [route_id, ...]} by inverting capability-routing-registry."""
    data = _load(_ROUTING_REG)
    inverted: dict[str, list] = {}
    for route in data.get("routes", []):
        route_id = route.get("route_id", "")
        for sid in route.get("preferred_skill_ids", []):
            inverted.setdefault(sid, []).append(route_id)
        for sid in route.get("fallback_skill_ids", []):
            inverted.setdefault(sid, [])  # ensure key exists even if fallback-only
    return inverted


def compute_parity_status(skill: dict, cmd_dict: dict, md_stems: set) -> dict:
    """Compute parity fields for a skill entry."""
    sid = skill["skill_id"]
    cf = skill.get("command_file", "")
    file_exists = bool(cf) and (_REPO / cf).exists()
    in_registry = sid in cmd_dict
    if file_exists and in_registry:
        parity = "FULL_PARITY"
    elif file_exists or in_registry:
        parity = "PARTIAL"
    else:
        parity = "MISSING_COMMAND"
    return {
        "command_file": cf,
        "command_file_exists": file_exists,
        "command_registry_entry": in_registry,
        "parity_status": parity,
    }


def compute_agent_surfaces(skill: dict, md_stems: set, routing: dict) -> dict:
    """Compute agent_surfaces for a skill entry.

    TC-ACP-002 (FF-AGENTS-PARITY-001, 2026-07-12): Changed codex surface from opt-out
    default (not codex_excluded) to explicit opt-in (codex_supported: true).
    Previously `codex: true` was the default for all 142 skills (false assurance).
    Now `codex: false` is the default unless `codex_supported: true` is explicit.
    """
    sid = skill["skill_id"]
    cf = skill.get("command_file", "")
    return {
        "claude_code": bool(cf) and (_REPO / cf).exists(),
        "codex": bool(skill.get("codex_supported", False)),  # TC-ACP-002: opt-in (was opt-out)
        "kilo": bool(skill.get("kilo_supported", False)),    # TC-ACP-002: new kilo surface field
        "ci": sid in routing and len(routing[sid]) > 0,
    }


def build_registry(skills: dict, cmd_dict: dict, md_stems: set, routing: dict,
                   timestamp: str, registry_id: str) -> dict:
    """Build the full capability registry dict."""
    capabilities = []

    for sid, skill in sorted(skills.items()):
        parity = compute_parity_status(skill, cmd_dict, md_stems)
        surfaces = compute_agent_surfaces(skill, md_stems, routing)
        entry = {
            "capability_id": sid,
            "status": skill.get("status", "active"),
            "agent_surfaces": surfaces,
            "parity_status": parity["parity_status"],
            "generated_at": timestamp,
            "command_file": parity["command_file"],
            "command_file_exists": parity["command_file_exists"],
            "command_registry_entry": parity["command_registry_entry"],
            "routing_routes": sorted(routing.get(sid, [])),
            "product_track": skill.get("product_track", ""),
            "purpose": (skill.get("purpose", "") or "")[:200],  # truncate long purposes
            "source_skill_registry_version": registry_id,
        }
        capabilities.append(entry)

    # Detect orphan commands: .md stems with no skill entry
    skill_ids = set(skills.keys())
    for stem in sorted(md_stems - skill_ids):
        capabilities.append({
            "capability_id": stem,
            "status": "active",
            "agent_surfaces": {"claude_code": True, "codex": False, "ci": False},
            "parity_status": "ORPHAN",
            "generated_at": timestamp,
            "command_file": f".claude/commands/{stem}.md",
            "command_file_exists": True,
            "command_registry_entry": stem in cmd_dict,
            "routing_routes": [],
            "product_track": "unknown",
            "purpose": "Orphan command — no corresponding skill-registry entry",
            "source_skill_registry_version": registry_id,
        })

    return capabilities


def merge_with_prior(new_caps: list, prior_path: Path) -> list:
    """Merge new capabilities with prior registry, preserving deprecated entries (never-delete)."""
    if not prior_path.exists():
        return new_caps
    prior = _load(prior_path)
    prior_caps = {c["capability_id"]: c for c in prior.get("capabilities", [])}
    new_ids = {c["capability_id"] for c in new_caps}
    # Add deprecated entries from prior that no longer appear in new inventory
    for cid, cap in prior_caps.items():
        if cid not in new_ids and cap.get("status") == "deprecated":
            new_caps.append(cap)
    return new_caps


def main(output_path: str | None = None) -> int:
    try:
        skills = load_skills()
        cmd_dict, md_stems = load_commands()
        routing = load_routing()
    except Exception as exc:
        print(f"ERROR loading source registries: {exc}")
        return 1

    # Load registry_id from skill-registry for provenance
    raw = _load(_SKILL_REG)
    registry_id = raw.get("registry_id", "unknown")

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    capabilities = build_registry(skills, cmd_dict, md_stems, routing, timestamp, registry_id)

    dest = Path(output_path) if output_path else _REGISTRY_OUT
    capabilities = merge_with_prior(capabilities, dest)

    # Sort by capability_id for stable output
    capabilities.sort(key=lambda c: c["capability_id"])

    output = {
        "generated_by": "inventory_capabilities.py",
        "generated_at": timestamp,
        "source_versions": {
            "skill_registry": registry_id,
            "command_registry": str(_CMD_REG.relative_to(_REPO)),
            "routing_registry": str(_ROUTING_REG.relative_to(_REPO)),
        },
        "capabilities": capabilities,
    }

    _save(dest, output)
    orphans = sum(1 for c in capabilities if c["parity_status"] == "ORPHAN")
    missing = sum(1 for c in capabilities if c["parity_status"] == "MISSING_COMMAND")
    full = sum(1 for c in capabilities if c["parity_status"] == "FULL_PARITY")
    print(f"Inventory: {len(capabilities)} capabilities "
          f"({full} FULL_PARITY, {missing} MISSING_COMMAND, {orphans} ORPHAN) -> {dest}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile capability registry from source registries")
    parser.add_argument("--output", default=None, help="Output path (default: .governance/capabilities/registry.yaml)")
    args = parser.parse_args()
    raise SystemExit(main(args.output))
