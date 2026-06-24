"""Tests for detect_ad_hoc_execution.py — Skill 3"""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from detect_ad_hoc_execution import load_registry, scan, _REPO as _TOOL_REPO


def test_load_registry_returns_sets():
    reg = _REPO / ".supervisor" / "skill-registry.yaml"
    if not reg.exists():
        pytest.skip("skill-registry.yaml not found")
    governed, commands = load_registry(reg)
    assert isinstance(governed, set)
    assert isinstance(commands, set)


def test_scan_classifies_all_py_files():
    tools_root = _REPO / "tools" / "supervisor"
    governed = {"detect_ad_hoc_execution.py", "validate_skill_contracts.py"}
    results = scan(tools_root, governed)
    assert len(results) > 0
    classifications = {r["classification"] for r in results}
    assert classifications <= {"GOVERNED", "AD_HOC"}


def test_scan_governed_file_classified_correctly():
    tools_root = _REPO / "tools" / "supervisor"
    governed = {"detect_ad_hoc_execution.py"}
    results = scan(tools_root, governed)
    entry = next((r for r in results if r["file"] == "detect_ad_hoc_execution.py"), None)
    assert entry is not None
    assert entry["classification"] == "GOVERNED"


def test_scan_unknown_file_is_ad_hoc():
    tools_root = _REPO / "tools" / "supervisor"
    governed: set = set()
    results = scan(tools_root, governed)
    for r in results:
        assert r["classification"] == "AD_HOC"


def test_main_produces_output(tmp_path):
    import subprocess
    out = tmp_path / "output.yaml"
    result = subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "detect_ad_hoc_execution.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0
    assert out.exists()
    import yaml
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["status"] == "complete"
    assert data["total_files"] > 0
