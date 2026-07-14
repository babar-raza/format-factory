"""
build_agent_bundle.py — Agent Bundle Generator (TC-ACP-005)

Reads .governance/capabilities/registry.yaml and generates a machine-readable
agent bundle YAML for a specified agent (codex or kilo).

The bundle contains:
- Paths to instruction/contract/pilot-spec files
- Capabilities accessible to the agent (filtered by agent_surfaces flag)
- Blocked capabilities with reasons
- Session state file paths
- Governance files to read at session start

Exit codes: 0 = success, 1 = error
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_REGISTRY = _REPO / ".governance" / "capabilities" / "registry.yaml"
_CONTRACT = _REPO / "docs" / "agents" / "canonical-agent-contract.yaml"
_PILOT_SPECS = _REPO / "docs" / "agents" / "pilots" / "pilot-specs.yaml"

_GOVERNANCE_FILES = [
    {"path": "CLAUDE.md", "role": "session-lifecycle", "required": True},
    {"path": "AGENTS.md", "role": "human-free-autonomy-doctrine", "required": True},
    {"path": "docs/governance/skill-only-policy.yaml", "role": "skill-execution-mechanics", "required": True},
    {"path": "docs/agents/canonical-agent-contract.yaml", "role": "rc-lifecycle-semantics", "required": True},
    {"path": "plans/master-plan.md", "role": "strategic-direction", "required": True},
]

_BLOCKED_BY_AGENT = {
    "codex": [
        {"capability_id": "RC-016/invoke_skills_by_name", "block_reason": "no skill dispatch mechanism", "rc_blocked": "RC-016"},
        {"capability_id": "RC-017/enforce_skill_first_policy", "block_reason": "no enforcement hook", "rc_blocked": "RC-017"},
        {"capability_id": "RC-004/load_instruction_files", "block_reason": "no native CLAUDE.md awareness; codex-adapter.md must exist", "rc_blocked": "RC-004"},
    ],
    "kilo": [
        {"capability_id": "RC-004/load_instruction_files", "block_reason": "KILO.md does not exist", "rc_blocked": "RC-004"},
        {"capability_id": "RC-016/invoke_skills_by_name", "block_reason": "no skill dispatch mechanism", "rc_blocked": "RC-016"},
        {"capability_id": "RC-017/enforce_skill_first_policy", "block_reason": "no enforcement hook", "rc_blocked": "RC-017"},
        {"capability_id": "RC-022/multi_sprint_autonomous_loop", "block_reason": "unknown if supported", "rc_blocked": "RC-022"},
    ],
}

_INSTRUCTION_FILES = {
    "codex": ".codex/codex.md",
    "kilo": "KILO.md",
}

_MODEL_REQUIREMENTS = {
    "codex": {
        "minimum_tier": "medium",
        "context_required": True,
        "reasoning_required": True,
        "notes": "Codex requires explicit file reads for governance; no native session state",
    },
    "kilo": {
        "minimum_tier": "high",
        "context_required": True,
        "reasoning_required": True,
        "notes": "Kilo platform capabilities unconfirmed; all surfaces UNVERIFIABLE_PLATFORM_UNKNOWN",
    },
}


def load_registry() -> list:
    if not _REGISTRY.exists():
        raise FileNotFoundError(f"Registry not found: {_REGISTRY}")
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8")) or {}
    return data.get("capabilities", [])


def filter_capabilities(caps: list, agent: str) -> tuple[list, list]:
    """Return (available, blocked) capability lists for the given agent."""
    available = []
    blocked = []
    for cap in caps:
        surfaces = cap.get("agent_surfaces", {})
        if surfaces.get(agent, False):
            available.append({
                "capability_id": cap["capability_id"],
                "status": cap.get("status", "active"),
                "parity_status": cap.get("parity_status", "UNKNOWN"),
                "command_file": cap.get("command_file", ""),
            })
        elif cap.get("status") == "active":
            blocked.append({
                "capability_id": cap["capability_id"],
                "block_reason": f"{agent}_supported not set to true in skill-registry.yaml (opt-in required, TC-ACP-002)",
                "rc_blocked": "RC-016",
            })
    return available, blocked


def build_bundle(agent: str) -> dict:
    caps = load_registry()
    available, surface_blocked = filter_capabilities(caps, agent)

    # Merge surface-blocked with known structural blocks
    all_blocked = _BLOCKED_BY_AGENT.get(agent, []) + surface_blocked

    instruction_file = _INSTRUCTION_FILES.get(agent, f"{agent.upper()}.md")
    instruction_exists = (_REPO / instruction_file).exists()

    return {
        "bundle": {
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agent": agent,
            "source": {
                "registry": str(_REGISTRY.relative_to(_REPO)),
                "contract": str(_CONTRACT.relative_to(_REPO)),
                "pilot_specs": str(_PILOT_SPECS.relative_to(_REPO)),
            },
            "instruction_file": instruction_file,
            "instruction_file_exists": instruction_exists,
            "contract_file": str(_CONTRACT.relative_to(_REPO)),
            "session_state": {
                "continuation_signal": ".local/supervisor/continuation-signal.json",
                "plan_lock": ".local/supervisor/active-plan-lock.json",
                "session_resume": "reports/supervisor/session-resume.md",
            },
            "capabilities": available,
            "governance": _GOVERNANCE_FILES,
            "blocked_capabilities": all_blocked,
            "model_requirements": _MODEL_REQUIREMENTS.get(agent, {}),
            "capability_counts": {
                "available": len(available),
                "blocked_surface": len(surface_blocked),
                "blocked_structural": len(_BLOCKED_BY_AGENT.get(agent, [])),
            },
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate agent bundle YAML")
    parser.add_argument("--agent", choices=["codex", "kilo"], required=True, help="Target agent platform")
    parser.add_argument("--output", default=None, help="Output path (default: docs/agents/bundles/<agent>-bundle.yaml)")
    args = parser.parse_args()

    out = Path(args.output) if args.output else _REPO / "docs" / "agents" / "bundles" / f"{args.agent}-bundle.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        bundle = build_bundle(args.agent)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    out.write_text(
        yaml.dump(bundle, default_flow_style=False, allow_unicode=True, sort_keys=True),
        encoding="utf-8",
    )
    counts = bundle["bundle"]["capability_counts"]
    print(
        f"Bundle: {args.agent} -> {out} "
        f"({counts['available']} available, {counts['blocked_surface']} surface-blocked, "
        f"{counts['blocked_structural']} structural-blocked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
