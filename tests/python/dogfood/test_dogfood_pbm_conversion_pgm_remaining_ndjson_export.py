"""
Dogfood pipeline: PBM conversion + remaining + PGM remaining → NDJSON export.
Covers PBM: crop, scale_nearest, pbm_min_row_black_count, convert_pbm_to_pgm, convert_pbm_to_ppm
Covers PGM: pgm_is_tall
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import crop as pbm_crop, scale_nearest, pbm_min_row_black_count
from pbm.pbm_to_pgm import convert_pbm_to_pgm
from pbm.pbm_to_ppm import convert_pbm_to_ppm
from pgm.pgm_parser import pgm_is_tall
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _checker_pbm():
    return str(next(f for f in sorted(_PBM_DIR.glob("*.pbm")) if "checker" in f.name or "2x2" in f.name))


def _gradient_pgm():
    return str(next(f for f in sorted(_PGM_DIR.glob("*.pgm")) if "gradient" in f.name or "2x2" in f.name))


def test_pbm_crop_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "cropped.pbm")
    result = pbm_crop(path, dest, 0, 0, 1, 1)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pbm", "function": "crop", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pbm_scale_nearest_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "scaled.pbm")
    result = scale_nearest(path, dest, 2)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pbm", "function": "scale_nearest", "ok": result.get("ok"), "width": result.get("width")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pbm_min_row_black_count_returns_int(tmp_path):
    path = _checker_pbm()
    result = pbm_min_row_black_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_min_row_black_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_convert_pbm_to_pgm_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "converted.pgm")
    result = convert_pbm_to_pgm(path, dest)
    assert isinstance(result, dict)
    assert result.get("width", 0) >= 1

    record = {"format": "pbm", "function": "convert_pbm_to_pgm", "width": result.get("width")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_convert_pbm_to_ppm_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "converted.ppm")
    result = convert_pbm_to_ppm(path, dest)
    assert isinstance(result, dict)

    record = {"format": "pbm", "function": "convert_pbm_to_ppm", "status": result.get("status", "done")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_pgm_is_tall_returns_bool(tmp_path):
    path = _gradient_pgm()
    result = pgm_is_tall(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_is_tall", "is_tall": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_tall"], bool)
    assert json.dumps(loaded[0]) is not None
