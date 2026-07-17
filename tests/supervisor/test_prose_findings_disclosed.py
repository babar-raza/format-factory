"""test_prose_findings_disclosed.py — TC-STRUCT-001 (2026-07-17).

Unit tests for write_plan_lock._parse_prose_findings_disclosed_from_plan:
the closure record's explicit, recorded self-disclosure field.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SUPERVISOR = Path(__file__).resolve().parents[2] / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from write_plan_lock import _parse_prose_findings_disclosed_from_plan  # noqa: E402


def test_none_when_section_absent(tmp_path):
    p = tmp_path / "plan.md"
    p.write_text("# Plan\n\n## Context\n\nNo disclosure section here.\n", encoding="utf-8")
    assert _parse_prose_findings_disclosed_from_plan(str(p)) is None


def test_empty_list_when_section_present_but_no_bullets(tmp_path):
    p = tmp_path / "plan.md"
    p.write_text(
        "# Plan\n\n## Prose Findings Disclosed\n\nNone.\n\n## Next Section\n",
        encoding="utf-8",
    )
    assert _parse_prose_findings_disclosed_from_plan(str(p)) == []


def test_extracts_bullet_items(tmp_path):
    p = tmp_path / "plan.md"
    p.write_text(
        "# Plan\n\n"
        "## Prose Findings Disclosed\n\n"
        "- Noted the coordination db has 53 registered agents, most stale.\n"
        "- Mentioned a possible perf concern in the audit scan, not investigated.\n\n"
        "## Next Section\n\nOther content.\n",
        encoding="utf-8",
    )
    items = _parse_prose_findings_disclosed_from_plan(str(p))
    assert len(items) == 2
    assert "coordination db" in items[0]
    assert "perf concern" in items[1]


def test_stops_at_next_heading(tmp_path):
    p = tmp_path / "plan.md"
    p.write_text(
        "## Prose Findings Disclosed\n\n"
        "- Item one.\n\n"
        "## Unrelated Section\n\n"
        "- Not a disclosure item.\n",
        encoding="utf-8",
    )
    items = _parse_prose_findings_disclosed_from_plan(str(p))
    assert items == ["Item one."]


def test_missing_file_returns_none():
    assert _parse_prose_findings_disclosed_from_plan("/nonexistent/path/plan.md") is None
