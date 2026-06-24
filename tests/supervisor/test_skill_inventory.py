"""Tests for skill_inventory.py — Pilot C / inventory-skills"""
import sys
from pathlib import Path
import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from skill_inventory import _scan, _load_partial


def test_scan_returns_entries():
    entries = _scan(_REPO, set())
    assert len(entries) > 0
    for e in entries:
        assert "skill_id" in e
        assert "status" in e
        assert "mechanism_type" in e


def test_scan_no_duplicates():
    entries = _scan(_REPO, set())
    ids = [e["skill_id"] for e in entries]
    assert len(ids) == len(set(ids)), "Duplicate skill_ids in scan output"


def test_scan_skips_completed(tmp_path):
    entries_all = _scan(_REPO, set())
    if not entries_all:
        pytest.skip("No entries found")
    first_id = entries_all[0]["skill_id"]
    entries_skipped = _scan(_REPO, {first_id})
    ids_skipped = {e["skill_id"] for e in entries_skipped}
    assert first_id not in ids_skipped


def test_load_partial_returns_empty_for_nonexistent(tmp_path):
    prior, completed = _load_partial(tmp_path / "nonexistent.yaml")
    assert prior == []
    assert completed == set()


def test_load_partial_detects_partial_status(tmp_path):
    partial_file = tmp_path / "partial.yaml"
    partial_data = {"status": "partial", "skills": [{"skill_id": "test-skill-a", "status": "active"}]}
    partial_file.write_text(yaml.dump(partial_data), encoding="utf-8")
    prior, completed = _load_partial(partial_file)
    assert len(prior) == 1
    assert "test-skill-a" in completed


def test_main_produces_complete_output(tmp_path):
    import subprocess
    out = tmp_path / "inventory.yaml"
    result = subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "skill_inventory.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0
    assert out.exists()
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["status"] == "complete"
    assert data["total_skills"] >= 62


def test_main_resumes_partial_state(tmp_path):
    import subprocess
    out = tmp_path / "inventory.yaml"
    partial_data = {"status": "partial", "skills": [
        {"skill_id": "add-python-api", "status": "active", "mechanism_type": "ATOMIC_SKILL",
         "command_file": ".claude/commands/add-python-api.md", "command_file_exists": True}
    ]}
    out.write_text(yaml.dump(partial_data), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "skill_inventory.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["status"] == "complete"
    assert data["resumed_from_partial"] is True
    ids = [s["skill_id"] for s in data["skills"]]
    assert ids.count("add-python-api") == 1
