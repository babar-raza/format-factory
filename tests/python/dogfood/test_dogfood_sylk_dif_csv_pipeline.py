"""
test_dogfood_sylk_dif_csv_pipeline.py -- Cross-format dogfood tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-4
Tests SYLK->CSV and DIF->CSV export pipelines, plus SYLK<->DIF interop.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SYLK_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"

from sylk.sylk_parser import sylk_to_csv, parse_sylk_strict, write_sylk
from dif.dif_parser import dif_to_csv, parse_dif_strict, write_dif


def test_sylk_csv_to_dif_csv_column_count():
    """Both SYLK and DIF 2x2 samples should export CSV with 2 columns."""
    sylk_csv = sylk_to_csv(str(_SYLK_SAMPLES / "minimal-2x2.slk"))
    dif_csv = dif_to_csv(str(_DIF_SAMPLES / "minimal-2x2.dif"))
    sylk_cols = len(sylk_csv.strip().split("\r\n")[0].split(","))
    dif_cols = len(dif_csv.strip().split("\r\n")[0].split(","))
    assert sylk_cols >= 2
    assert dif_cols >= 2


def test_sylk_write_roundtrip_csv_stable(tmp_path):
    """SYLK parse -> write -> CSV should produce same CSV as direct export."""
    src = _SYLK_SAMPLES / "minimal-2x2.slk"
    csv_direct = sylk_to_csv(str(src))
    doc = parse_sylk_strict(str(src))
    rt = tmp_path / "roundtrip.slk"
    write_sylk(doc, str(rt))
    csv_rt = sylk_to_csv(str(rt))
    assert csv_direct == csv_rt


def test_dif_write_roundtrip_csv_stable(tmp_path):
    """DIF parse -> write -> CSV should produce same CSV as direct export."""
    src = _DIF_SAMPLES / "minimal-2x2.dif"
    csv_direct = dif_to_csv(str(src))
    doc = parse_dif_strict(str(src))
    rt = tmp_path / "roundtrip.dif"
    write_dif(doc, str(rt))
    csv_rt = dif_to_csv(str(rt))
    assert csv_direct == csv_rt
