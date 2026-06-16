"""
tests/python/dogfood/test_dogfood_qoi_zst_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-80
Dogfood export: QOI+ZST remaining analytics -> write as NDJSON -> verify.
QOI uses: qoi_is_landscape, qoi_is_portrait, qoi_max_dimension, qoi_dimension_ratio.
ZST uses: validate_file (path), probe_frame (bytes).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import qoi_is_landscape, qoi_is_portrait, qoi_max_dimension, qoi_dimension_ratio
from zst import validate_file, probe_frame
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


def _valid_qoi_files():
    return sorted(_QOI_DIR.glob("*.qoi"))


def _valid_zst_files():
    return sorted(_ZST_DIR.glob("*.zst"))


class TestQoiZstRemainingAnalyticsNdjsonExport:
    """QOI+ZST remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_qoi_remaining_basics(self):
        sample = str(next(_QOI_DIR.glob("*.qoi")))
        is_land = qoi_is_landscape(sample)
        is_port = qoi_is_portrait(sample)
        max_dim = qoi_max_dimension(sample)
        ratio = qoi_dimension_ratio(sample)
        assert isinstance(is_land, bool)
        assert isinstance(is_port, bool)
        assert max_dim >= 0
        assert isinstance(ratio, float)

    def test_zst_remaining_basics(self):
        sample = next(_ZST_DIR.glob("*.zst"))
        val = validate_file(sample)
        raw_bytes = sample.read_bytes()
        pf = probe_frame(raw_bytes)
        assert isinstance(val, dict)
        assert isinstance(pf, dict)

    def test_qoi_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            is_land = qoi_is_landscape(path)
            is_port = qoi_is_portrait(path)
            max_dim = qoi_max_dimension(path)
            ratio = qoi_dimension_ratio(path)
            assert isinstance(is_land, bool), f"qoi_is_landscape must be bool for {f.name}"
            assert isinstance(is_port, bool), f"qoi_is_portrait must be bool for {f.name}"
            assert max_dim >= 0, f"qoi_max_dimension must be >= 0 for {f.name}"
            assert isinstance(ratio, float), f"qoi_dimension_ratio must be float for {f.name}"
            records.append({
                "file": f.name,
                "is_landscape": is_land,
                "is_portrait": is_port,
                "max_dimension": max_dim,
                "dimension_ratio": ratio,
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_zst_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            val = validate_file(f)
            raw_bytes = f.read_bytes()
            pf = probe_frame(raw_bytes)
            assert isinstance(val, dict), f"validate_file must be dict for {f.name}"
            assert isinstance(pf, dict), f"probe_frame must be dict for {f.name}"
            records.append({
                "file": f.name,
                "validate_is_valid": val.get("valid", val.get("is_valid", False)),
                "probe_frame_type": str(pf.get("frame_type", pf.get("magic", "unknown"))),
                "source_format": "zst",
            })
        dest = tmp_path / "zst-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            is_land = qoi_is_landscape(path)
            max_dim = qoi_max_dimension(path)
            records.append({"file": f.name, "is_landscape": is_land, "max_dimension": max_dim})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["is_landscape"] == back["is_landscape"]
            assert orig["max_dimension"] == back["max_dimension"]

    def test_json_lines_valid(self, tmp_path):
        qoi_sample = str(next(_QOI_DIR.glob("*.qoi")))
        is_land = qoi_is_landscape(qoi_sample)
        ratio = qoi_dimension_ratio(qoi_sample)
        records = [{"file": "sample.qoi", "is_landscape": is_land, "dimension_ratio": ratio}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
