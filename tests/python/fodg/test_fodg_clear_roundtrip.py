"""
test_fodg_clear_roundtrip.py -- FODG clear_page + write+reload roundtrip tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-35
Tests clear_page (page count unchanged), write+reload after clear,
create_fodg names, probe_fodg on written file, export_to_txt.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    clear_page,
    write_fodg,
    load,
    page_names,
    get_page_count,
    probe_fodg,
    export_to_txt,
)

_MODEL = create_fodg([{"name": "Main"}, {"name": "Appendix"}])


def test_clear_page_count_unchanged():
    m2 = clear_page(_MODEL, 0)
    assert get_page_count(m2) == 2


def test_clear_page_write_reload(tmp_path):
    m2 = clear_page(_MODEL, 0)
    dest = tmp_path / "cleared.fodg"
    write_fodg(m2, str(dest))
    m3 = load(str(dest))
    assert get_page_count(m3) == 2
    assert "Main" in page_names(m3)


def test_create_fodg_page_names():
    names = page_names(_MODEL)
    assert "Main" in names
    assert "Appendix" in names


def test_probe_fodg_written_file(tmp_path):
    dest = tmp_path / "probe.fodg"
    write_fodg(_MODEL, str(dest))
    assert probe_fodg(str(dest)) is True


def test_export_to_txt_is_string(tmp_path):
    dest = tmp_path / "out.fodg"
    write_fodg(_MODEL, str(dest))
    txt = export_to_txt(str(dest))
    assert isinstance(txt, str)
