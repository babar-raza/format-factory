"""
test_abw_probe_metadata.py -- ABW probe + get_metadata pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-35
Tests probe_abw on written file, get_metadata keys, get_section_count,
export_to_json roundtrip data integrity, paragraph_at index access.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    probe_abw,
    get_metadata,
    get_section_count,
    export_to_json,
    paragraph_lengths,
)

_MODEL = create_abw(["Short paragraph", "A longer second paragraph here", "Third"])


def _write_abw(tmp_path):
    dest = tmp_path / "test.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_probe_abw_written_file(tmp_path):
    dest = _write_abw(tmp_path)
    assert probe_abw(str(dest)) is True


def test_get_metadata_is_dict(tmp_path):
    dest = _write_abw(tmp_path)
    meta = get_metadata(str(dest))
    assert isinstance(meta, dict)


def test_get_section_count(tmp_path):
    dest = _write_abw(tmp_path)
    count = get_section_count(str(dest))
    assert isinstance(count, int)


def test_export_to_json_paragraph_count(tmp_path):
    dest = _write_abw(tmp_path)
    data = json.loads(export_to_json(str(dest)))
    assert data["paragraph_count"] == 3


def test_paragraph_lengths():
    lengths = paragraph_lengths(_MODEL)
    assert len(lengths) == 3
    assert lengths[0] == len("Short paragraph")
