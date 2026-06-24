"""
skill_inventory.py — Pilot C / Skill 1 (inventory-skills)

Scan skill-registry.yaml and .claude/commands/ to produce mechanism inventory.
Supports partial-state resume: status: partial resumes from completed_skills count.

Output: .supervisor/skill-inventory.yaml
LOC budget: <90 lines
"""
import argparse
from pathlib import Path
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent


def _load_partial(dest: Path) -> tuple[list, set]:
    if not dest.exists():
        return [], set()
    try:
        data = yaml.safe_load(dest.read_text(encoding="utf-8", errors="replace")) or {}
        if data.get("status") == "partial":
            prior = data.get("skills", [])
            return prior, {s["skill_id"] for s in prior if "skill_id" in s}
    except Exception:
        pass
    return [], set()


def _scan(repo: Path, skip: set) -> list[dict]:
    reg = repo / ".supervisor" / "skill-registry.yaml"
    cmd_dir = repo / ".claude" / "commands"
    data = yaml.safe_load(reg.read_text(encoding="utf-8", errors="replace")) or {}
    md_stems = {f.stem for f in cmd_dir.glob("*.md") if f.stem != "_readme"}
    registered = {s.get("skill_id", "") for s in data.get("skills", [])}
    entries = []
    for s in data.get("skills", []):
        sid = s.get("skill_id", "")
        if not sid or sid in skip:
            continue
        cf = s.get("command_file", "")
        entries.append({"skill_id": sid, "status": s.get("status", "unknown"),
                        "mechanism_type": "ATOMIC_SKILL" if s.get("status") == "active" else s.get("status", "").upper(),
                        "command_file": cf,
                        "command_file_exists": bool(cf and (repo / cf).exists()),
                        "implementation_paths": s.get("implementation_paths", [])})
    for stem in sorted(md_stems - registered):
        if stem in skip:
            continue
        entries.append({"skill_id": stem, "status": "unregistered",
                        "mechanism_type": "UNREGISTERED_COMMAND",
                        "command_file": f".claude/commands/{stem}.md",
                        "command_file_exists": True})
    return entries


def main(output_path: str | None = None) -> None:
    dest = Path(output_path or str(_REPO / ".supervisor" / "skill-inventory.yaml"))
    prior, completed = _load_partial(dest)
    new_entries = _scan(_REPO, completed)
    all_entries = sorted(prior + new_entries, key=lambda x: x.get("skill_id", ""))
    out = {"generated_by": "skill_inventory.py", "mission_id": "SKILL-FIRST-001",
           "status": "complete", "total_skills": len(all_entries),
           "resumed_from_partial": len(completed) > 0, "skills": all_entries}
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(yaml.dump(out, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    print(f"Skill inventory: {len(all_entries)} entries -> {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inventory all registered skills")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    main(args.output)
