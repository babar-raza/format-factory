"""Dogfood: FODS(4)+PBM(1)+PGM(2) remaining gap-ledger gap functions -> NDJSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from fods import parse_fods
from fods.neutral_model import (
    fods_cell_entropy,
    fods_row_col_ratio,
    fods_row_fill_rate,
    fods_value_variance,
)
from pbm.pbm_parser import pbm_column_transition_count
from pgm.pgm_parser import pgm_edge_pixel_mean, pgm_pixel_median

_FODS = str(_REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods")
_PBM = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm")
_PGM = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm")


def _w(tmp_path, metric, val, suffix=""):
    out = tmp_path / f"{metric}{suffix}.ndjson"
    write_ndjson([{"metric": metric, "value": val}], str(out))
    return json.loads(out.read_text().strip())["value"]


# --- FODS (model-based API: parse_fods -> workbook dict -> analytics) ---

def test_fods_value_variance(tmp_path):
    doc = parse_fods(_FODS)
    val = fods_value_variance(doc)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "fods_value_variance", val) == 0.0


def test_fods_row_col_ratio(tmp_path):
    doc = parse_fods(_FODS)
    val = fods_row_col_ratio(doc)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "fods_row_col_ratio", val) == 1.0


def test_fods_row_fill_rate(tmp_path):
    doc = parse_fods(_FODS)
    val = fods_row_fill_rate(doc)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "fods_row_fill_rate", val) == 1.0


def test_fods_cell_entropy(tmp_path):
    doc = parse_fods(_FODS)
    val = fods_cell_entropy(doc)
    assert isinstance(val, float) and val == -0.0
    assert _w(tmp_path, "fods_cell_entropy", val) == 0.0


# --- PBM ---

def test_pbm_column_transition_count(tmp_path):
    val = pbm_column_transition_count(_PBM)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "pbm_column_transition_count", val) == 2


# --- PGM ---

def test_pgm_pixel_median(tmp_path):
    val = pgm_pixel_median(_PGM)
    assert isinstance(val, float) and val == 127.5
    assert _w(tmp_path, "pgm_pixel_median", val) == 127.5


def test_pgm_edge_pixel_mean(tmp_path):
    val = pgm_edge_pixel_mean(_PGM)
    assert isinstance(val, float) and val == 127.5
    assert _w(tmp_path, "pgm_edge_pixel_mean", val) == 127.5


def test_batch_ndjson_export(tmp_path):
    doc = parse_fods(_FODS)
    records = [
        {"fmt": "fods", "m": "fods_value_variance", "v": fods_value_variance(doc)},
        {"fmt": "fods", "m": "fods_row_col_ratio", "v": fods_row_col_ratio(doc)},
        {"fmt": "pbm", "m": "pbm_column_transition_count", "v": pbm_column_transition_count(_PBM)},
        {"fmt": "pgm", "m": "pgm_pixel_median", "v": pgm_pixel_median(_PGM)},
        {"fmt": "pgm", "m": "pgm_edge_pixel_mean", "v": pgm_edge_pixel_mean(_PGM)},
    ]
    out = tmp_path / "fods_pbm_pgm_gap_closure.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 5
    fmts = {json.loads(ln)["fmt"] for ln in lines}
    assert {"fods", "pbm", "pgm"} == fmts
