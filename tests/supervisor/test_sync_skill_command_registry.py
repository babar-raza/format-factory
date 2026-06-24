"""Tests for sync_skill_command_registry.py — Skill 13"""
import sys
from pathlib import Path
import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")


def test_sync_adds_missing_command_entry(tmp_path, monkeypatch):
    skill_reg = tmp_path / "skill-registry.yaml"
    cmd_reg = tmp_path / "command-registry.yaml"
    (tmp_path / "commands").mkdir()
    skill_data = {"skills": [
        {"skill_id": "new-skill", "purpose": "Test", "command": "/new-skill",
         "status": "active", "command_file": "commands/new-skill.md"}
    ]}
    cmd_data = {"commands": []}
    _write_yaml(skill_reg, skill_data)
    _write_yaml(cmd_reg, cmd_data)

    import sync_skill_command_registry as mod
    orig_repo = mod._REPO
    orig_skill = mod._SKILL_REG
    orig_cmd = mod._CMD_REG
    orig_dir = mod._CMD_DIR
    monkeypatch.setattr(mod, "_REPO", tmp_path)
    monkeypatch.setattr(mod, "_SKILL_REG", skill_reg)
    monkeypatch.setattr(mod, "_CMD_REG", cmd_reg)
    monkeypatch.setattr(mod, "_CMD_DIR", tmp_path / "commands")

    out = tmp_path / "report.yaml"
    mod.main(str(out))

    report = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert report["new_entries_added"] == 1
    assert report["auto_repaired"] == 1

    updated = yaml.safe_load(cmd_reg.read_text(encoding="utf-8"))
    assert any(e.get("command_id") == "new-skill" for e in updated.get("commands", []))


def test_sync_detects_orphan_md_file(tmp_path, monkeypatch):
    skill_reg = tmp_path / "skill-registry.yaml"
    cmd_reg = tmp_path / "command-registry.yaml"
    cmd_dir = tmp_path / "commands"
    cmd_dir.mkdir()
    (cmd_dir / "orphan-command.md").write_text("# orphan", encoding="utf-8")

    _write_yaml(skill_reg, {"skills": []})
    _write_yaml(cmd_reg, {"commands": []})

    import sync_skill_command_registry as mod
    monkeypatch.setattr(mod, "_REPO", tmp_path)
    monkeypatch.setattr(mod, "_SKILL_REG", skill_reg)
    monkeypatch.setattr(mod, "_CMD_REG", cmd_reg)
    monkeypatch.setattr(mod, "_CMD_DIR", cmd_dir)

    out = tmp_path / "report.yaml"
    mod.main(str(out))

    report = yaml.safe_load(out.read_text(encoding="utf-8"))
    orphan_flags = [f for f in report["flags"] if f["result"] == "UNREGISTERED_COMMAND"]
    assert len(orphan_flags) == 1
    assert orphan_flags[0]["item"] == "orphan-command"


def test_sync_idempotent(tmp_path, monkeypatch):
    skill_reg = tmp_path / "skill-registry.yaml"
    cmd_reg = tmp_path / "command-registry.yaml"
    cmd_dir = tmp_path / "commands"
    cmd_dir.mkdir()

    _write_yaml(skill_reg, {"skills": [
        {"skill_id": "a-skill", "purpose": "A", "command": "/a", "status": "active",
         "command_file": "commands/a-skill.md"}
    ]})
    _write_yaml(cmd_reg, {"commands": []})

    import sync_skill_command_registry as mod
    monkeypatch.setattr(mod, "_REPO", tmp_path)
    monkeypatch.setattr(mod, "_SKILL_REG", skill_reg)
    monkeypatch.setattr(mod, "_CMD_REG", cmd_reg)
    monkeypatch.setattr(mod, "_CMD_DIR", cmd_dir)

    out1 = tmp_path / "report1.yaml"
    mod.main(str(out1))
    out2 = tmp_path / "report2.yaml"
    mod.main(str(out2))

    r2 = yaml.safe_load(out2.read_text(encoding="utf-8"))
    assert r2["auto_repaired"] == 0
