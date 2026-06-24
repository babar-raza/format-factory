"""
sync_skill_command_registry.py — Skill 13

Detect and repair discrepancies between skill-registry.yaml,
command-registry.yaml, and .claude/commands/*.md files.
Auto-repair: adds missing command-registry entries; syncs status fields.
Never deletes. Never modifies skill-registry.yaml.

Output: .supervisor/skill-command-registry-sync-report.yaml
LOC budget: <100 lines
"""
import argparse
from pathlib import Path
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_SKILL_REG = _REPO / ".supervisor" / "skill-registry.yaml"
_CMD_REG = _REPO / ".claude" / "commands" / "command-registry.yaml"
_CMD_DIR = _REPO / ".claude" / "commands"


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}


def _save(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")


def main(output_path: str | None = None) -> None:
    try:
        cmd_data = _load(_CMD_REG)
    except Exception as exc:
        _save(Path(output_path or str(_REPO / ".supervisor" / "skill-command-registry-sync-report.yaml")),
              {"status": "error", "error": str(exc), "auto_repaired": 0})
        return

    skills = {s["skill_id"]: s for s in _load(_SKILL_REG).get("skills", [])}
    cmd_entries = {e.get("command_id") or e.get("skill_id", ""): e
                   for e in cmd_data.get("commands", [])}
    md_files = {f.stem for f in _CMD_DIR.glob("*.md") if f.stem != "_readme"}

    flags, status_drift, new_entries = [], [], []
    repaired = 0

    for stem in sorted(md_files):
        if stem not in skills:
            flags.append({"check": "orphan_md", "item": stem, "result": "UNREGISTERED_COMMAND"})

    for sid, skill in skills.items():
        if sid not in cmd_entries:
            new_entries.append({"command_id": sid, "skill_id": sid,
                                 "status": skill.get("status", "active"),
                                 "command_file": skill.get("command_file", "")})
            repaired += 1
        elif skill.get("status") != cmd_entries[sid].get("status"):
            status_drift.append({"skill_id": sid, "from": cmd_entries[sid].get("status"),
                                  "to": skill.get("status")})
            cmd_entries[sid]["status"] = skill.get("status")
            repaired += 1
        cf = skill.get("command_file", "")
        if cf and not (_REPO / cf).exists():
            flags.append({"check": "broken_pointer", "item": sid, "result": "BROKEN_POINTER", "detail": cf})

    for cid in cmd_entries:
        if cid and cid not in skills:
            flags.append({"check": "orphan_entry", "item": cid, "result": "ORPHAN_COMMAND_ENTRY"})

    if new_entries or status_drift:
        bak = _REPO / ".local" / "archive" / "command-registry-pre-sync.yaml"
        bak.parent.mkdir(parents=True, exist_ok=True)
        _save(bak, cmd_data)
        cmd_data.setdefault("commands", []).extend(new_entries)
        _save(_CMD_REG, cmd_data)

    out = {"generated_by": "sync_skill_command_registry.py", "mission_id": "SKILL-FIRST-001",
           "auto_repaired": repaired, "status_drift": status_drift, "flags": flags,
           "new_entries_added": len(new_entries), "overall_verdict": "PASS" if not flags else "WARN"}
    dest = output_path or str(_REPO / ".supervisor" / "skill-command-registry-sync-report.yaml")
    _save(Path(dest), out)
    print(f"Sync: {repaired} repaired, {len(flags)} flags -> {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync skill and command registries")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    main(args.output)
