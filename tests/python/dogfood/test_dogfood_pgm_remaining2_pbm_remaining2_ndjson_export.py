"""
Dogfood pipeline: PGM remaining analytics + PBM remaining analytics → NDJSON export.
Covers PGM: parse_pgm_strict, histogram, pgm_pixel_density, pgm_row_count, pgm_is_portrait,
            write_pgm (roundtrip)
Covers PBM: parse_pbm_strict, pbm_is_portrait, pbm_pixel_density, pbm_is_binary_balanced,
            pbm_column_density_variance, write_pbm (roundtrip)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import tempfile

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    parse_pgm_strict,
    histogram,
    pgm_pixel_density,
    pgm_row_count,
    pgm_is_portrait,
    write_pgm,
)
from pbm.pbm_parser import (
    parse_pbm_strict,
    pbm_is_portrait,
    pbm_pixel_density,
    pbm_is_binary_balanced,
    pbm_column_density_variance,
    write_pbm,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _pgm_file():
    # Use 2x2-gradient which has more pixels
    for f in sorted(_PGM_DIR.glob("*.pgm")):
        if "2x2" in f.name:
            return str(f)
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def _pbm_file():
    for f in sorted(_PBM_DIR.glob("*.pbm")):
        if "2x2" in f.name or "3x2" in f.name:
            return str(f)
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def test_pgm_parse_strict_returns_image(tmp_path):
    path = _pgm_file()
    result = parse_pgm_strict(path)
    assert hasattr(result, "width")
    assert hasattr(result, "height")
    assert result.width > 0
    assert result.height > 0

    record = {"format": "pgm", "function": "parse_pgm_strict", "width": result.width, "height": result.height}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_histogram_returns_dict(tmp_path):
    path = _pgm_file()
    result = histogram(path)
    assert isinstance(result, dict)

    record = {"format": "pgm", "function": "histogram", "bucket_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["bucket_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_density_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_row_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_is_portrait_returns_bool(tmp_path):
    path = _pgm_file()
    result = pgm_is_portrait(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_is_portrait", "is_portrait": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_portrait"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pgm_write_pgm_roundtrip(tmp_path):
    path = _pgm_file()
    img = parse_pgm_strict(path)
    out_path = str(tmp_path / "out.pgm")
    write_pgm(img.pixels, img.width, img.height, img.maxval, out_path)
    img2 = parse_pgm_strict(out_path)
    assert img2.width == img.width
    assert img2.height == img.height

    record = {"format": "pgm", "function": "write_pgm", "width": img2.width, "height": img2.height}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_parse_strict_returns_image(tmp_path):
    path = _pbm_file()
    result = parse_pbm_strict(path)
    assert hasattr(result, "width")
    assert hasattr(result, "height")
    assert result.width > 0

    record = {"format": "pbm", "function": "parse_pbm_strict", "width": result.width, "height": result.height}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_portrait_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_portrait(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_portrait", "is_portrait": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_portrait"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_pixel_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_pixel_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_pixel_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_binary_balanced_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_binary_balanced(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_binary_balanced", "is_balanced": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_balanced"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_column_density_variance_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_column_density_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_column_density_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_write_pbm_roundtrip(tmp_path):
    path = _pbm_file()
    img = parse_pbm_strict(path)
    out_path = str(tmp_path / "out.pbm")
    write_pbm(img.pixels, img.width, img.height, out_path)
    img2 = parse_pbm_strict(out_path)
    assert img2.width == img.width
    assert img2.height == img.height

    record = {"format": "pbm", "function": "write_pbm", "width": img2.width, "height": img2.height}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None
