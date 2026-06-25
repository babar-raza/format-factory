"""Tests for scan_residual_bypasses.py — Skill 12"""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from scan_residual_bypasses import get_src_mutations, load_governed_commits


def test_get_src_mutations_returns_dict():
    result = get_src_mutations(_REPO, n_commits=5)
    assert isinstance(result, dict)
    for sha, paths in result.items():
        assert len(sha) == 40
        assert all(p.startswith("src/") for p in paths)


def test_load_governed_commits_empty_dir_returns_empty_set(tmp_path):
    result = load_governed_commits(tmp_path)
    assert result == set()


def test_load_governed_commits_missing_dir_returns_empty_set(tmp_path):
    nonexistent = tmp_path / "transcripts_xyz"
    result = load_governed_commits(nonexistent)
    assert result == set()


def test_main_produces_output(tmp_path):
    import subprocess
    out = tmp_path / "bypass_report.yaml"
    result = subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "scan_residual_bypasses.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0
    assert out.exists()
    import yaml
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert "commits_scanned" in data
    assert "entries" in data
    assert "ungoverned_mutation_count" in data


def test_entries_have_required_fields(tmp_path):
    import subprocess
    import yaml
    out = tmp_path / "bypass_report.yaml"
    subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "scan_residual_bypasses.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    if not out.exists():
        pytest.skip("output not created")
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    for entry in data.get("entries", []):
        assert "commit_sha" in entry
        assert "verdict" in entry
        assert entry["verdict"] in ("GOVERNED", "UNGOVERNED_MUTATION")
