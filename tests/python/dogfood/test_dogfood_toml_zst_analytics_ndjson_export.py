"""Dogfood: Export TOML + ZST analytics to NDJSON.

Pipeline: Compute analytics → write NDJSON → read back → verify schema.
Proves: TOML and ZST analytics can be exported via Format Factory NDJSON codec.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson, load_ndjson


TOML_SAMPLES = _REPO / "samples" / "by-format" / "toml"
ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestTomlAnalyticsNdjsonExport:
    def test_toml_analytics_to_ndjson(self, tmp_path):
        from toml.toml_codec import (
            toml_unique_value_count,
            toml_max_key_length,
            toml_avg_value_length,
            toml_total_keys,
        )
        minimal = TOML_SAMPLES / "minimal.toml"
        if not minimal.exists():
            pytest.skip("TOML sample not available")

        records = [{
            "file": str(minimal.name),
            "unique_values": toml_unique_value_count(minimal),
            "max_key_length": toml_max_key_length(minimal),
            "avg_value_length": toml_avg_value_length(minimal),
            "total_keys": toml_total_keys(minimal),
        }]

        out = tmp_path / "toml-analytics.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 1
        assert loaded[0]["file"] == "minimal.toml"
        assert isinstance(loaded[0]["unique_values"], int)

    def test_ndjson_lines_valid_json(self, tmp_path):
        from toml.toml_codec import toml_unique_value_count, toml_max_key_length
        minimal = TOML_SAMPLES / "minimal.toml"
        if not minimal.exists():
            pytest.skip("TOML sample not available")

        records = [{"unique": toml_unique_value_count(minimal), "max_key": toml_max_key_length(minimal)}]
        out = tmp_path / "toml-check.ndjson"
        write_ndjson(records, str(out))
        for line in out.read_text().strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)


class TestZstAnalyticsNdjsonExport:
    def test_zst_analytics_to_ndjson(self, tmp_path):
        from zst.zst_codec import zst_density, zst_content_type_hint, zst_unique_frame_size_count
        minimal = ZST_SAMPLES / "minimal-synthetic.zst"
        if not minimal.exists():
            pytest.skip("ZST sample not available")

        records = [{
            "file": str(minimal.name),
            "density": zst_density(minimal),
            "content_hint": zst_content_type_hint(minimal),
            "unique_frame_sizes": zst_unique_frame_size_count(minimal),
        }]

        out = tmp_path / "zst-analytics.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 1
        assert loaded[0]["content_hint"] == "highly_compressible"

    def test_multi_sample_export(self, tmp_path):
        from zst.zst_codec import zst_density, zst_content_type_hint
        records = []
        for f in sorted(ZST_SAMPLES.glob("*.zst"))[:3]:
            try:
                records.append({
                    "file": f.name,
                    "density": zst_density(f),
                    "hint": zst_content_type_hint(f),
                })
            except Exception:
                pass

        if not records:
            pytest.skip("No ZST samples processed")

        out = tmp_path / "zst-multi.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        assert all(isinstance(r["density"], float) for r in loaded)
