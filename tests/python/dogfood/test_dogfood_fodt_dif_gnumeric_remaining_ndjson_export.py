"""
tests/python/dogfood/test_dogfood_fodt_dif_gnumeric_remaining_ndjson_export.py

Dogfood export: FODT/DIF/Gnumeric remaining analytics -> NDJSON export -> verify.
Addresses rework item: REWORK-DOGFOOD-FODT-DIF-GNUMERIC-REMAINING-NDJSON
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import fodt_char_per_word, fodt_avg_block_length, fodt_max_block_text_length
from dif import dif_value_sum, dif_avg_string_length
from gnumeric import gnumeric_formula_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


class TestFodtRemainingAnalyticsNdjsonExport:
    def test_fodt_char_per_word_export(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            val = fodt_char_per_word(str(f))
            records.append({"file": f.name, "char_per_word": val})
        out = tmp_path / "fodt_char_per_word.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        assert all("char_per_word" in r for r in loaded)

    def test_fodt_avg_block_length_export(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            val = fodt_avg_block_length(str(f))
            records.append({"file": f.name, "avg_block_length": val})
        out = tmp_path / "fodt_avg_block.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        assert all(r["avg_block_length"] >= 0 for r in loaded)

    def test_fodt_max_block_text_length_export(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            val = fodt_max_block_text_length(str(f))
            records.append({"file": f.name, "max_block_length": val})
        out = tmp_path / "fodt_max_block.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) >= 1
        assert all(r["max_block_length"] > 0 for r in loaded)

    def test_fodt_minimal_exact_values(self, tmp_path):
        minimal = str(_FODT_DIR / "minimal-document.fodt")
        records = [{"char_per_word": fodt_char_per_word(minimal),
                    "avg_block": fodt_avg_block_length(minimal),
                    "max_block": fodt_max_block_text_length(minimal)}]
        out = tmp_path / "fodt_minimal.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert loaded[0]["char_per_word"] == 6.0
        assert loaded[0]["avg_block"] == 13.0
        assert loaded[0]["max_block"] == 13


class TestDifRemainingAnalyticsNdjsonExport:
    def test_dif_value_sum_export(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            val = dif_value_sum(str(f))
            records.append({"file": f.name, "value_sum": val})
        out = tmp_path / "dif_value_sum.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        assert all("value_sum" in r for r in loaded)

    def test_dif_avg_string_length_export(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            val = dif_avg_string_length(str(f))
            records.append({"file": f.name, "avg_str_len": val})
        out = tmp_path / "dif_avg_str.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) >= 2
        assert all(r["avg_str_len"] >= 0 for r in loaded)

    def test_dif_minimal_exact_values(self, tmp_path):
        minimal = str(_DIF_DIR / "minimal-2x2.dif")
        records = [{"value_sum": dif_value_sum(minimal),
                    "avg_str_len": dif_avg_string_length(minimal)}]
        out = tmp_path / "dif_minimal.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert loaded[0]["value_sum"] == 141.0
        assert loaded[0]["avg_str_len"] > 0

    def test_dif_pipeline_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            records.append({
                "file": f.name,
                "value_sum": dif_value_sum(str(f)),
                "avg_str_len": dif_avg_string_length(str(f)),
            })
        out = tmp_path / "dif_combined.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        assert all(r["value_sum"] >= 0 for r in loaded)


class TestGnumericRemainingAnalyticsNdjsonExport:
    def test_gnumeric_formula_count_export(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            val = gnumeric_formula_count(str(f))
            records.append({"file": f.name, "formula_count": val})
        out = tmp_path / "gnumeric_formula.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) >= 1
        assert all(r["formula_count"] >= 0 for r in loaded)

    def test_gnumeric_formula_zero_for_samples(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            val = gnumeric_formula_count(str(f))
            records.append({"file": f.name, "formula_count": val})
        out = tmp_path / "gnumeric_formula2.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert all(r["formula_count"] == 0 for r in loaded)

    def test_gnumeric_pipeline_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            records.append({
                "file": f.name,
                "formula_count": gnumeric_formula_count(str(f)),
            })
        out = tmp_path / "gnumeric_combined.jsonl"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_gnumeric_ndjson_is_valid_json_lines(self, tmp_path):
        records = [{"file": "minimal-spreadsheet.gnumeric",
                    "formula_count": gnumeric_formula_count(
                        str(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric"))}]
        out = tmp_path / "gnumeric_valid.jsonl"
        write_ndjson(records, str(out))
        lines = out.read_text().strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["formula_count"] == 0
