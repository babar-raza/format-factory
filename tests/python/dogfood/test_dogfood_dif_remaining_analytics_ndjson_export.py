"""
tests/python/dogfood/test_dogfood_dif_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-78
Dogfood export: DIF parse -> remaining analytics -> write as NDJSON -> verify.
Uses: probe_dif, get_header_info, dif_min_cell_length, dif_has_string_cells,
dif_max_numeric_value, dif_numeric_density.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    probe_dif,
    get_header_info,
    dif_min_cell_length,
    dif_has_string_cells,
    dif_max_numeric_value,
    dif_numeric_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifRemainingAnalyticsNdjsonExport:
    """DIF -> remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_probe_and_header_basics(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        probe = probe_dif(sample)
        header = get_header_info(sample)
        assert isinstance(probe, dict)
        assert isinstance(header, dict)

    def test_density_string_basics(self):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        min_len = dif_min_cell_length(sample)
        has_strings = dif_has_string_cells(sample)
        density = dif_numeric_density(sample)
        max_num = dif_max_numeric_value(sample)
        assert min_len >= 0
        assert isinstance(has_strings, bool)
        assert isinstance(density, float)
        assert max_num is None or isinstance(max_num, (int, float))

    def test_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            probe = probe_dif(path)
            header = get_header_info(path)
            min_len = dif_min_cell_length(path)
            has_strings = dif_has_string_cells(path)
            density = dif_numeric_density(path)
            max_num = dif_max_numeric_value(path)
            assert isinstance(probe, dict), f"probe_dif must be dict for {f.name}"
            assert isinstance(header, dict), f"get_header_info must be dict for {f.name}"
            assert min_len >= 0, f"dif_min_cell_length must be >= 0 for {f.name}"
            assert isinstance(has_strings, bool), f"dif_has_string_cells must be bool for {f.name}"
            assert isinstance(density, float), f"dif_numeric_density must be float for {f.name}"
            assert max_num is None or isinstance(max_num, (int, float)), f"dif_max_numeric_value must be numeric or None for {f.name}"
            records.append({
                "file": f.name,
                "probe_exists": probe.get("exists", False),
                "header_title": header.get("title", ""),
                "min_cell_length": min_len,
                "has_string_cells": has_strings,
                "numeric_density": density,
                "max_numeric_value": float(max_num) if max_num is not None else 0.0,
                "source_format": "dif",
            })
        dest = tmp_path / "dif-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            min_len = dif_min_cell_length(path)
            density = dif_numeric_density(path)
            records.append({
                "file": f.name,
                "min_cell_length": min_len,
                "numeric_density": density,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["min_cell_length"] == back["min_cell_length"]
            assert orig["numeric_density"] == back["numeric_density"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_DIF_DIR.glob("*.dif")))
        has_strings = dif_has_string_cells(sample)
        density = dif_numeric_density(sample)
        records = [{"file": "sample.dif", "has_string_cells": has_strings, "numeric_density": density}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_probe_header_export(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            probe = probe_dif(path)
            header = get_header_info(path)
            has_strings = dif_has_string_cells(path)
            density = dif_numeric_density(path)
            assert isinstance(probe, dict)
            assert isinstance(header, dict)
            records.append({
                "file": f.name,
                "probe_exists": probe.get("exists", False),
                "header_title": header.get("title", ""),
                "has_string_cells": has_strings,
                "numeric_density": density,
                "format": "dif",
            })
        dest = tmp_path / "probe-header.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(isinstance(r["has_string_cells"], bool) for r in loaded)
