"""test_advisory_analyzer.py — SFC-GAP-C (2026-07-17).

Correctness tests for the observe-only would-block analyzer against a seeded
synthetic advisory-log.jsonl. The analyzer must never recommend a promotion
threshold (there is no real traffic baseline yet) and must gracefully report
zero events for a check with no log entries at all (not an error).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"))

from coordination.advisory_analyzer import analyze  # noqa: E402


def _seed_log(root: Path, records: list[dict]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with (root / "advisory-log.jsonl").open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def test_no_log_file_returns_well_formed_empty_report(tmp_path):
    report = analyze(tmp_path, "skill_resolution")
    assert report["total_events"] == 0
    assert report["would_block_rate"] is None
    assert report["sample_would_block_events"] == []


def test_filters_by_check_id(tmp_path):
    _seed_log(tmp_path, [
        {"ts": "2026-07-17T00:00:00+00:00", "check": "skill_resolution",
         "would_block": True, "tier": "SKILL_EXISTS_BUT_NO_MANIFEST",
         "agent": "a1", "file": "x.py"},
        {"ts": "2026-07-17T00:00:01+00:00", "check": "some_other_check",
         "would_block": True, "agent": "a2", "file": "y.py"},
    ])
    report = analyze(tmp_path, "skill_resolution")
    assert report["total_events"] == 1
    assert report["would_block_count"] == 1


def test_would_block_rate_computed_correctly(tmp_path):
    records = [
        {"ts": f"2026-07-17T00:00:0{i}+00:00", "check": "skill_resolution",
         "would_block": (i < 3), "tier": "SKILL_EXISTS_BUT_NO_MANIFEST",
         "agent": f"a{i}", "file": f"f{i}.py"}
        for i in range(10)
    ]
    _seed_log(tmp_path, records)
    report = analyze(tmp_path, "skill_resolution")
    assert report["total_events"] == 10
    assert report["would_block_count"] == 3
    assert report["would_block_rate"] == 0.3


def test_tier_breakdown_and_distinct_counts(tmp_path):
    _seed_log(tmp_path, [
        {"ts": "t1", "check": "skill_resolution", "would_block": True,
         "tier": "SKILL_EXISTS_BUT_NO_MANIFEST", "agent": "a1", "file": "f1.py"},
        {"ts": "t2", "check": "skill_resolution", "would_block": True,
         "tier": "SKILL_EXISTS_BUT_NO_MANIFEST", "agent": "a1", "file": "f2.py"},
        {"ts": "t3", "check": "skill_resolution", "would_block": False,
         "tier": "NO_SKILL_RESOLVED_FOR_PATH", "agent": "a2", "file": "f3.py"},
    ])
    report = analyze(tmp_path, "skill_resolution")
    assert report["tier_breakdown"] == {"SKILL_EXISTS_BUT_NO_MANIFEST": 2}
    assert report["distinct_agents"] == 2
    assert report["distinct_paths"] == 3


def test_never_recommends_a_promotion_threshold(tmp_path):
    _seed_log(tmp_path, [
        {"ts": "t1", "check": "skill_resolution", "would_block": True,
         "tier": "SKILL_EXISTS_BUT_NO_MANIFEST", "agent": "a1", "file": "f1.py"},
    ])
    report = analyze(tmp_path, "skill_resolution")
    assert "recommend" not in json.dumps(report).lower().replace(
        "no promotion/rollback recommendation is computed here", "")
    for forbidden in ("threshold", "auto_promote", "should_enforce"):
        assert forbidden not in report


def test_malformed_log_lines_are_skipped_not_fatal(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "advisory-log.jsonl").write_text(
        "not json at all\n"
        '{"ts": "t1", "check": "skill_resolution", "would_block": true,'
        ' "tier": "SKILL_EXISTS_BUT_NO_MANIFEST"}\n'
        "\n",
        encoding="utf-8")
    report = analyze(tmp_path, "skill_resolution")
    assert report["total_events"] == 1
