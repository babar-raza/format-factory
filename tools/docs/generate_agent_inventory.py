"""Generate agent ecosystem inventory from repository evidence.

Documents how AI agents participate in development: Claude Code, Codex,
Kilo, supervisor orchestration, skills, and decision boundaries.

Usage:
    python tools/docs/generate_agent_inventory.py
    python tools/docs/generate_agent_inventory.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


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


def _extract_agents_md_sections(repo_root: Path) -> list[dict]:
    """Extract top-level section headings from AGENTS.md."""
    path = repo_root / "AGENTS.md"
    if not path.exists():
        return []
    sections = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^## ([A-Z][\w]*)\. (.+)", line)
            if m:
                sections.append({"code": m.group(1), "title": m.group(2)})
    except Exception:
        pass
    return sections


def _collect_agent_config(repo_root: Path) -> dict:
    """Read agent configuration files."""
    # Claude settings
    claude = _read_json(repo_root / ".claude" / "settings.json")

    # Kilo
    kilo_path = repo_root / ".kilo" / "kilo.jsonc"
    kilo_exists = kilo_path.exists()

    # Codex adapter
    codex_adapter = (repo_root / "docs" / "governance" / "codex-adapter.md").exists()

    return {
        "claude_configured": claude is not None,
        "kilo_configured": kilo_exists,
        "codex_adapter_exists": codex_adapter,
    }


def _collect_policies(repo_root: Path) -> dict:
    """Read autonomous execution policies."""
    data = _read_yaml(repo_root / ".supervisor" / "policies.yaml")
    if not data or not isinstance(data, dict):
        return {}

    auto = data.get("autonomous_continuation", {})
    hard = auto.get("hard_prohibitions", data.get("hard_prohibitions", []))
    if isinstance(hard, dict):
        hard = list(hard.keys())

    checkpoint = data.get("checkpoint", {})

    return {
        "max_iterations": auto.get("max_iterations"),
        "checkpoint_interval": checkpoint.get("every_n_sprints",
                                              auto.get("checkpoint_every_n_sprints")),
        "hard_prohibitions": hard if isinstance(hard, list) else [],
        "supervisor_advisory_only": data.get("authority", {}).get(
            "supervisor_overrides_registry", True) is False,
    }


def _collect_commands(repo_root: Path) -> dict:
    """Count and categorize commands."""
    cmd_dir = repo_root / ".claude" / "commands"
    if not cmd_dir.is_dir():
        return {"total": 0}
    files = [f.stem for f in cmd_dir.glob("*.md") if f.name != "_readme.md"]
    return {"total": len(files)}


def _collect_supervisor_tools(repo_root: Path) -> dict:
    """Count supervisor tool files."""
    sup_dir = repo_root / "tools" / "supervisor"
    if not sup_dir.is_dir():
        return {"total": 0}
    py_files = list(sup_dir.glob("*.py"))
    return {"total": len(py_files)}


def collect_agent_inventory(repo_root: Path = REPO_ROOT) -> dict:
    """Collect complete agent ecosystem inventory."""
    skills = _read_yaml(repo_root / ".supervisor" / "skill-registry.yaml")
    skill_count = len(skills.get("skills", [])) if skills and isinstance(skills, dict) else 0

    return {
        "agents_md_sections": _extract_agents_md_sections(repo_root),
        "config": _collect_agent_config(repo_root),
        "policies": _collect_policies(repo_root),
        "commands": _collect_commands(repo_root),
        "supervisor_tools": _collect_supervisor_tools(repo_root),
        "skill_count": skill_count,
    }


def render_agent_inventory_markdown(agents: dict) -> str:
    """Render agent ecosystem as markdown."""
    config = agents.get("config", {})
    policies = agents.get("policies", {})
    sections = agents.get("agents_md_sections", [])

    lines = [
        "## Agent Ecosystem",
        "",
        "Format Factory development is orchestrated by AI agents operating under "
        "a governed contract. All shipped library code is pure, deterministic, "
        "and contains no LLM calls at runtime.",
        "",
        "### Agent Roles",
        "",
        "| Agent | Role | Status |",
        "|---|---|---|",
        f"| Claude Code | Primary development executor | {'Configured' if config.get('claude_configured') else 'Not configured'} |",
        f"| Codex | Secondary executor with governance adapter | {'Adapter present' if config.get('codex_adapter_exists') else 'Not configured'} |",
        f"| Kilo | Specialized orchestration | {'Configured' if config.get('kilo_configured') else 'Not configured'} |",
        f"| Supervisor | Autonomous sprint orchestration and grading | Active |",
        "",
        "### Orchestration Model",
        "",
        "- **Skill-first execution**: All product work routes through registered skills "
        f"({agents.get('skill_count', 0)} registered)",
        f"- **Commands**: {agents.get('commands', {}).get('total', 0)} command files in `.claude/commands/`",
        f"- **Supervisor tools**: {agents.get('supervisor_tools', {}).get('total', 0)} Python modules in `tools/supervisor/`",
        f"- **Max iterations per loop**: {policies.get('max_iterations', 'N/A')}",
        f"- **Checkpoint interval**: Every {policies.get('checkpoint_interval') or 'N/A'} sprints",
        f"- **Supervisor authority**: {'Advisory only (repo is final authority)' if policies.get('supervisor_advisory_only') else 'Override capable'}",
        "",
        "### Decision Boundaries",
        "",
        "| Decision | Authority |",
        "|---|---|",
        "| Product implementation | Agent-owned (via registered skills) |",
        "| Test execution | Agent-owned |",
        "| Evidence declaration | Agent-owned |",
        "| Sprint grading | Supervisor (automated) |",
        "| Git commit | SCM Agent (sprint policy must authorize) |",
        "| Git push | Requires credentials + explicit policy |",
        "| Gate 1-10 approval | Agent-owned (evidence-based) |",
        "| Gate 11 execution | Human required (Babar Raza) |",
        "| Package publication | Requires credentials |",
        "",
        "### Hard Prohibitions (autonomous agents cannot perform)",
        "",
    ]
    for h in policies.get("hard_prohibitions", []):
        lines.append(f"- {h}")

    # AGENTS.md governance sections
    if sections:
        lines.extend([
            "",
            "### Governance Contract (AGENTS.md Sections)",
            "",
            "| Section | Title |",
            "|---|---|",
        ])
        for s in sections:
            lines.append(f"| {s['code']} | {s['title']} |")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate agent inventory")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    agents = collect_agent_inventory(args.repo_root)
    if args.json:
        print(json.dumps(agents, indent=2))
    else:
        print(render_agent_inventory_markdown(agents))
    return 0


if __name__ == "__main__":
    sys.exit(main())
