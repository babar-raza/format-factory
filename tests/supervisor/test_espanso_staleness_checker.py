"""test_espanso_staleness_checker.py — Tests for espanso_staleness_checker.py

TC-P1-001-04 (FF-ESP-INT-001 / imperative-coalescing-bengio)

Tests:
  1. test_backfill_idempotent: Second --backfill-hashes run on unchanged source → 0 updates
  2. test_detect_unchanged: detect on source matching stored hashes → exit 0
  3. test_detect_modified: detect on source with modified block → exit 1
  4. test_update_map_appends: --update-map on source with new trigger → appends UNCLASSIFIED entry
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.supervisor.espanso_staleness_checker import (
    _compute_sha256,
    _extract_body_at_range,
    _find_blocks_in_source,
    cmd_backfill_hashes,
    cmd_detect,
    cmd_update_map,
)


def _make_source_lines(blocks: list[str]) -> list[str]:
    """Join block texts into source lines list."""
    return "\n".join(blocks).splitlines()


def _make_provenance_map(entries: list[dict], line_count: int) -> dict:
    return {
        "source_line_count": line_count,
        "block_count": len(entries),
        "provenance_entries": entries,
    }


def _make_args(map_path: Path, source_path: Path, backfill: bool = False, update: bool = False):
    ns = argparse.Namespace()
    ns.map = map_path
    ns.source = source_path
    ns.backfill_hashes = backfill
    ns.update_map = update
    return ns


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SOURCE = textwrap.dedent("""\
  - trigger: ":ff-trigger-a"
    replace: "value a line 1"
  - trigger: ":ff-trigger-b"
    replace: "value b line 1"
    extra: "extra b"
""")


@pytest.fixture()
def tmp_source(tmp_path: Path) -> Path:
    src = tmp_path / "format-factory.yml"
    src.write_text(SAMPLE_SOURCE, encoding="utf-8")
    return src


@pytest.fixture()
def tmp_map(tmp_path: Path) -> Path:
    return tmp_path / "espanso-provenance-map.yaml"


# ---------------------------------------------------------------------------
# Test 1: Backfill is idempotent
# ---------------------------------------------------------------------------

def test_backfill_idempotent(tmp_source: Path, tmp_map: Path) -> None:
    """Second --backfill-hashes run on unchanged source updates 0 entries."""
    lines = tmp_source.read_text(encoding="utf-8").splitlines()
    block1_body = "\n".join(lines[0:2])
    block2_body = "\n".join(lines[2:5])

    initial_map = _make_provenance_map(
        entries=[
            {
                "block_id": 1,
                "primary_trigger": ":ff-trigger-a",
                "line_range": [1, 2],
                "body_sha256": None,
            },
            {
                "block_id": 2,
                "primary_trigger": ":ff-trigger-b",
                "line_range": [3, 5],
                "body_sha256": None,
            },
        ],
        line_count=len(lines),
    )
    tmp_map.write_text(yaml.dump(initial_map, allow_unicode=True), encoding="utf-8")

    args = _make_args(tmp_map, tmp_source, backfill=True)

    # First run: populates body_sha256 for 2 entries
    rc1 = cmd_backfill_hashes(args)
    assert rc1 == 0

    data_after_first = yaml.safe_load(tmp_map.read_text(encoding="utf-8"))
    for entry in data_after_first["provenance_entries"]:
        assert entry.get("body_sha256") is not None

    # Second run: nothing changes → 0 updates
    rc2 = cmd_backfill_hashes(args)
    assert rc2 == 0

    data_after_second = yaml.safe_load(tmp_map.read_text(encoding="utf-8"))
    # Hashes must match across runs
    hashes_1 = [e["body_sha256"] for e in data_after_first["provenance_entries"]]
    hashes_2 = [e["body_sha256"] for e in data_after_second["provenance_entries"]]
    assert hashes_1 == hashes_2


# ---------------------------------------------------------------------------
# Test 2: Detect mode exits 0 when source matches stored hashes
# ---------------------------------------------------------------------------

def test_detect_unchanged(tmp_source: Path, tmp_map: Path, capsys) -> None:
    """--detect exits 0 when all stored body_sha256 match current source."""
    lines = tmp_source.read_text(encoding="utf-8").splitlines()
    block1_body = _extract_body_at_range(lines, [1, 2])
    block2_body = _extract_body_at_range(lines, [3, 5])

    provenance = _make_provenance_map(
        entries=[
            {
                "block_id": 1,
                "primary_trigger": ":ff-trigger-a",
                "line_range": [1, 2],
                "body_sha256": _compute_sha256(block1_body),
            },
            {
                "block_id": 2,
                "primary_trigger": ":ff-trigger-b",
                "line_range": [3, 5],
                "body_sha256": _compute_sha256(block2_body),
            },
        ],
        line_count=len(lines),
    )
    tmp_map.write_text(yaml.dump(provenance, allow_unicode=True), encoding="utf-8")

    args = _make_args(tmp_map, tmp_source)
    rc = cmd_detect(args)
    assert rc == 0


# ---------------------------------------------------------------------------
# Test 3: Detect mode exits 1 when a block is modified
# ---------------------------------------------------------------------------

def test_detect_modified(tmp_source: Path, tmp_map: Path, capsys) -> None:
    """--detect exits 1 when a stored body_sha256 differs from current source."""
    lines = tmp_source.read_text(encoding="utf-8").splitlines()
    block1_body = _extract_body_at_range(lines, [1, 2])
    block2_body = _extract_body_at_range(lines, [3, 5])

    # Store a deliberately wrong hash for block 1
    provenance = _make_provenance_map(
        entries=[
            {
                "block_id": 1,
                "primary_trigger": ":ff-trigger-a",
                "line_range": [1, 2],
                "body_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
            },
            {
                "block_id": 2,
                "primary_trigger": ":ff-trigger-b",
                "line_range": [3, 5],
                "body_sha256": _compute_sha256(block2_body),
            },
        ],
        line_count=len(lines),
    )
    tmp_map.write_text(yaml.dump(provenance, allow_unicode=True), encoding="utf-8")

    args = _make_args(tmp_map, tmp_source)
    rc = cmd_detect(args)
    assert rc == 1

    out, _ = capsys.readouterr()
    assert "MODIFIED" in out


# ---------------------------------------------------------------------------
# Test 4: --update-map appends new UNCLASSIFIED entries
# ---------------------------------------------------------------------------

def test_update_map_appends(tmp_source: Path, tmp_map: Path, capsys) -> None:
    """--update-map appends new triggers not in the map as UNCLASSIFIED entries."""
    lines = tmp_source.read_text(encoding="utf-8").splitlines()

    # Only register the first trigger; the second is "new"
    provenance = _make_provenance_map(
        entries=[
            {
                "block_id": 1,
                "primary_trigger": ":ff-trigger-a",
                "all_triggers": [":ff-trigger-a"],
                "line_range": [1, 2],
                "body_sha256": _compute_sha256(_extract_body_at_range(lines, [1, 2])),
                "disposition": "PRODUCT_CAPABILITY",
            },
        ],
        line_count=len(lines),
    )
    tmp_map.write_text(yaml.dump(provenance, allow_unicode=True), encoding="utf-8")

    args = _make_args(tmp_map, tmp_source, update=True)
    rc = cmd_update_map(args)
    assert rc == 0

    data = yaml.safe_load(tmp_map.read_text(encoding="utf-8"))
    entries = data["provenance_entries"]
    # Should now have 2 entries
    assert len(entries) == 2

    # The new entry must be UNCLASSIFIED
    new_entry = next(e for e in entries if e["primary_trigger"] == ":ff-trigger-b")
    assert new_entry["disposition"] == "UNCLASSIFIED"
    assert new_entry.get("body_sha256") is not None

    out, _ = capsys.readouterr()
    assert "Appended 1 new" in out
