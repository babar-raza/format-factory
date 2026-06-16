"""
Dogfood pipeline: PBM mutation + PGM mutation → NDJSON export.
Covers PBM: flip_horizontal, invert, rotate_90
Covers PGM: flip_horizontal, normalize, threshold
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import flip_horizontal as pbm_flip, invert as pbm_invert, rotate_90 as pbm_rotate
from pgm.pgm_parser import flip_horizontal as pgm_flip, normalize as pgm_normalize, threshold as pgm_threshold
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _checker_pbm():
    return str(next(f for f in sorted(_PBM_DIR.glob("*.pbm")) if "checker" in f.name or "2x2" in f.name))


def _gradient_pgm():
    return str(next(f for f in sorted(_PGM_DIR.glob("*.pgm")) if "gradient" in f.name or "2x2" in f.name))


def test_pbm_flip_horizontal_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "flipped.pbm")
    result = pbm_flip(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pbm", "function": "flip_horizontal", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pbm_invert_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "inverted.pbm")
    result = pbm_invert(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pbm", "function": "invert", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pbm_rotate_90_returns_dict(tmp_path):
    path = _checker_pbm()
    dest = str(tmp_path / "rotated.pbm")
    result = pbm_rotate(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pbm", "function": "rotate_90", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pgm_flip_horizontal_returns_dict(tmp_path):
    path = _gradient_pgm()
    dest = str(tmp_path / "pgm_flipped.pgm")
    result = pgm_flip(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pgm", "function": "flip_horizontal", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pgm_normalize_returns_dict(tmp_path):
    path = _gradient_pgm()
    dest = str(tmp_path / "normalized.pgm")
    result = pgm_normalize(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pgm", "function": "normalize", "ok": result.get("ok"), "new_maxval": result.get("new_maxval")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_pgm_threshold_returns_dict(tmp_path):
    path = _gradient_pgm()
    dest = str(tmp_path / "thresholded.pgm")
    result = pgm_threshold(path, dest, 128)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "pgm", "function": "threshold", "threshold": 128, "above_count": result.get("above_count", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["threshold"] == 128
    assert json.dumps(loaded[0]) is not None
