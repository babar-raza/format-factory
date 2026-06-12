"""
test_fodg_export_csv_pipeline.py -- FODG export_to_csv + roundtrip pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-40
Tests export_to_csv header present, roundtrip preserves page count,
export_to_csv with dest writes file, get_page_metadata returns list,
probe_fodg on roundtrip output.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    export_to_csv,
    roundtrip,
    get_page_metadata,
    probe_fodg,
    get_page_count,
    load,
)

_MODEL = create_fodg([{"name": "Slide1"}, {"name": "Slide2"}])


def _write_fodg(tmp_path):
    dest = tmp_path / "doc.fodg"
    write_fodg(_MODEL, str(dest))
    return dest


def test_export_to_csv_has_header(tmp_path):
    dest = _write_fodg(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "page_name,shape_index,text" in csv_str


def test_export_to_csv_with_dest(tmp_path):
    dest = _write_fodg(tmp_path)
    csv_dest = tmp_path / "out.csv"
    export_to_csv(str(dest), dest=str(csv_dest))
    assert csv_dest.exists()


def test_roundtrip_preserves_page_count(tmp_path):
    dest = _write_fodg(tmp_path)
    copy = tmp_path / "copy.fodg"
    result = roundtrip(str(dest), str(copy))
    assert get_page_count(result) == 2


def test_get_page_metadata_list(tmp_path):
    dest = _write_fodg(tmp_path)
    meta = get_page_metadata(str(dest))
    assert isinstance(meta, list)
    assert len(meta) == 2


def test_probe_fodg_roundtrip_output(tmp_path):
    dest = _write_fodg(tmp_path)
    copy = tmp_path / "probe_copy.fodg"
    roundtrip(str(dest), str(copy))
    assert probe_fodg(str(copy)) is True
