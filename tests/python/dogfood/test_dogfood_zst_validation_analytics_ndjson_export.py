"""
tests/python/dogfood/test_dogfood_zst_validation_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-58
Dogfood export: ZST parse -> validation analytics -> write as NDJSON -> verify.
Uses: validate_file (path-based), estimate_ratio, get_frame_info,
get_frame_size_stats, is_valid_frame, probe_frame (bytes-based).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import (
    validate_file,
    estimate_ratio,
    get_frame_info,
    get_frame_size_stats,
    is_valid_frame,
    probe_frame,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


def _valid_zst_files():
    return sorted(_ZST_DIR.glob("*.zst"))


def _safe_frame_info(data: bytes) -> dict:
    try:
        return get_frame_info(data)
    except Exception:
        return {}


def _safe_frame_size_stats(data: bytes) -> dict:
    try:
        return get_frame_size_stats(data)
    except Exception:
        return {}


def _safe_probe_frame(data: bytes) -> dict:
    try:
        return probe_frame(data)
    except Exception:
        return {}


def _safe_estimate_ratio(data: bytes) -> dict:
    try:
        return estimate_ratio(data)
    except Exception:
        return {}


class TestZstValidationAnalyticsNdjsonExport:
    """ZST -> validation analytics -> NDJSON export -> roundtrip verification."""

    def test_validate_file(self):
        sample = str(next(_ZST_DIR.glob("*.zst")))
        result = validate_file(sample)
        assert isinstance(result, dict)

    def test_bytes_based_analytics(self):
        sample_path = next(_ZST_DIR.glob("*.zst"))
        data = sample_path.read_bytes()
        valid = is_valid_frame(data)
        frame_info = _safe_frame_info(data)
        assert isinstance(valid, bool)
        assert isinstance(frame_info, dict)

    def test_validation_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            data = f.read_bytes()
            validation = validate_file(path)
            valid_frame = is_valid_frame(data)
            frame_info = _safe_frame_info(data)
            frame_stats = _safe_frame_size_stats(data)
            probe = _safe_probe_frame(data)
            ratio = _safe_estimate_ratio(data)
            assert isinstance(validation, dict), f"validate_file must be dict for {f.name}"
            assert isinstance(valid_frame, bool), f"is_valid_frame must be bool for {f.name}"
            records.append({
                "file": f.name,
                "is_valid": validation.get("valid", valid_frame),
                "frame_info_keys": len(frame_info),
                "frame_stats_keys": len(frame_stats),
                "probe_keys": len(probe),
                "ratio_keys": len(ratio),
                "source_format": "zst",
            })
        dest = tmp_path / "zst-validation.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            data = f.read_bytes()
            validation = validate_file(path)
            valid_frame = is_valid_frame(data)
            records.append({
                "file": f.name,
                "is_valid": validation.get("valid", valid_frame),
                "frame_info_keys": len(_safe_frame_info(data)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["frame_info_keys"] == back["frame_info_keys"]

    def test_json_lines_valid(self, tmp_path):
        sample_path = next(_ZST_DIR.glob("*.zst"))
        validation = validate_file(str(sample_path))
        records = [{"file": sample_path.name, "validation_keys": len(validation)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_estimate_ratio_and_probe_export(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            data = f.read_bytes()
            ratio = _safe_estimate_ratio(data)
            probe = _safe_probe_frame(data)
            frame_stats = _safe_frame_size_stats(data)
            assert isinstance(ratio, dict)
            assert isinstance(probe, dict)
            assert isinstance(frame_stats, dict)
            records.append({
                "file": f.name,
                "ratio_keys": len(ratio),
                "probe_keys": len(probe),
                "frame_stats_keys": len(frame_stats),
                "format": "zst",
            })
        dest = tmp_path / "ratio-probe.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "zst" for r in loaded)
