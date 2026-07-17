"""test_scan_ungoverned_generators_proximity.py — TC-RG-002 (2026-07-17).

scan_ungoverned_generators() used to flag a file as an ungoverned-mutation
candidate if it had a write call ANYWHERE and a mutation-target string
(src/python/, registry/, .supervisor/, oracle/) ANYWHERE else in the same
file -- with no relation between the two. Manual triage of the 125 files this
produced against the real repo found the file-wide check conflated an
unrelated write (e.g. to reports/) with an unrelated mention of src/ etc.
elsewhere in the file (typically a module docstring describing what the tool
*reads*). The fix requires the mutation-target string to appear in a bounded
line window around the actual write call. Verified against the real repo:
125 -> 5 candidates (see plans/.claude/sfc-remaining-gaps-closure.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance.skills_first import audit  # noqa: E402


def test_write_call_matches_when_target_string_is_nearby():
    lines = [
        "def f():",
        '    local_path = root / "src" / "python" / mod  # comment mentions src/python/ nearby',
        "    abs_path.write_text(x)",
    ]
    assert audit._write_call_targets_mutation_path(lines, 2) is True


def test_write_call_does_not_match_when_target_string_is_far_away():
    # >8 lines between the docstring mention and the write call.
    lines = ["# scans src/python/{fmt}/ for all formats"] + ["pass"] * 15 + [
        "out.write_text(x)"]
    write_idx = len(lines) - 1
    assert audit._write_call_targets_mutation_path(lines, write_idx) is False


def test_write_call_does_not_match_with_no_target_string_in_file():
    lines = ["out_dir = REPO_ROOT / 'reports' / 'thing'", "out.write_text(x)"]
    assert audit._write_call_targets_mutation_path(lines, 1) is False


def test_scan_flags_file_with_write_call_near_registry_target(tmp_path, monkeypatch):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    (tools_dir / "real_gap.py").write_text(
        "def f():\n"
        "    # writes registry/thing.yaml directly\n"
        "    p.write_text('{}')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
    result = audit.scan_ungoverned_generators(limit=100)
    assert result["sample"] == ["tools/real_gap.py"]


def test_scan_does_not_flag_file_with_unrelated_docstring_mention(tmp_path, monkeypatch):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    filler = "\n".join(f"    step_{i} = {i}" for i in range(20))
    (tools_dir / "false_positive.py").write_text(
        '"""Reads src/python/{fmt}/ and writes a report."""\n'
        "def f():\n"
        f"{filler}\n"
        "    out.write_text('report')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
    result = audit.scan_ungoverned_generators(limit=100)
    assert result["sample"] == []


def test_real_repo_scan_reduced_to_small_triaged_set():
    """Regression pin against the actual repo: confirms the fix's real-world
    effect (125 -> a small set) without hardcoding the volatile file list."""
    result = audit.scan_ungoverned_generators(limit=1000)
    assert result["count"] <= 20, (
        f"expected the proximity fix to keep the real-repo signal small, got "
        f"{result['count']}: {result['sample']}")
