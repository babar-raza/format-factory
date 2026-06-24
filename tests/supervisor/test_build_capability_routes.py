"""Tests for build_capability_routes.py — Skill 6"""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from build_capability_routes import load_registered_skills, check_routes


def test_load_registered_skills_returns_set():
    reg = _REPO / ".supervisor" / "skill-registry.yaml"
    if not reg.exists():
        pytest.skip("skill-registry.yaml not found")
    skills = load_registered_skills(reg)
    assert isinstance(skills, set)
    assert len(skills) > 0


def test_check_routes_with_real_registry():
    reg = _REPO / ".supervisor" / "skill-registry.yaml"
    routing = _REPO / ".supervisor" / "capability-routing-registry.yaml"
    if not reg.exists() or not routing.exists():
        pytest.skip("registry files not found")
    registered = load_registered_skills(reg)
    results = check_routes(routing, registered)
    assert len(results) == 30
    verdicts = {r["verdict"] for r in results}
    assert verdicts <= {"ROUTE_ACTIVE", "MISSING_SKILL_CAPABILITY", "BROKEN_REFERENCE"}


def test_missing_skill_flagged(tmp_path):
    import yaml
    routing_content = {"routes": [
        {"route_id": "test_route", "current_status": "ROUTE_ACTIVE",
         "preferred_skill_ids": ["nonexistent-skill-xyz"], "gap_id": None}
    ]}
    routing_file = tmp_path / "routing.yaml"
    routing_file.write_text(yaml.dump(routing_content), encoding="utf-8")
    results = check_routes(routing_file, {"real-skill"})
    assert results[0]["verdict"] == "BROKEN_REFERENCE"
    assert "nonexistent-skill-xyz" in results[0]["unresolved_skill_ids"]


def test_missing_capability_route_preserved(tmp_path):
    import yaml
    routing_content = {"routes": [
        {"route_id": "rollback", "current_status": "MISSING_SKILL_CAPABILITY",
         "preferred_skill_ids": [], "gap_id": "SKILL-GAP-011"}
    ]}
    routing_file = tmp_path / "routing.yaml"
    routing_file.write_text(yaml.dump(routing_content), encoding="utf-8")
    results = check_routes(routing_file, set())
    assert results[0]["verdict"] == "MISSING_SKILL_CAPABILITY"


def test_main_produces_output(tmp_path):
    import subprocess
    out = tmp_path / "routes.yaml"
    result = subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "build_capability_routes.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0
    assert out.exists()
    import yaml
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["total_routes"] == 30
