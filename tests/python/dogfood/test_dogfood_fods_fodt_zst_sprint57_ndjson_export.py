"""Dogfood: FODS + FODT + ZST sprint57 analytics exported to NDJSON.

Exercises:
  - fods_row_to_sheet_ratio, fods_cell_type_variety, fods_file_size_bytes
  - fodt_word_per_heading, fodt_block_text_sum, fodt_digit_count, fodt_max_run_count
  - zst_size_exceeds_100k, zst_frame_count_ratio, zst_avg_compression_per_byte
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods_strict,
    fods_row_to_sheet_ratio,
    fods_cell_type_variety,
    fods_file_size_bytes,
)
from src.python.fodt import (
    fodt_word_per_heading,
    fodt_block_text_sum,
    fodt_digit_count,
    fodt_max_run_count,
)
from src.python.zst import (
    zst_size_exceeds_100k,
    zst_frame_count_ratio,
    zst_avg_compression_per_byte,
)

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


def _build_fods_record(path: str) -> dict:
    wb = parse_fods_strict(path)
    return {
        "format": "fods",
        "file": Path(path).name,
        "row_to_sheet_ratio": fods_row_to_sheet_ratio(wb),
        "cell_type_variety": fods_cell_type_variety(wb),
        "file_size_bytes": fods_file_size_bytes(path),
    }


def _build_fodt_record(path: str) -> dict:
    return {
        "format": "fodt",
        "file": Path(path).name,
        "word_per_heading": fodt_word_per_heading(path),
        "block_text_sum": fodt_block_text_sum(path),
        "digit_count": fodt_digit_count(path),
        "max_run_count": fodt_max_run_count(path),
    }


def _build_zst_record(path: str) -> dict:
    return {
        "format": "zst",
        "file": Path(path).name,
        "size_exceeds_100k": zst_size_exceeds_100k(path),
        "frame_count_ratio": zst_frame_count_ratio(path),
        "avg_compression_per_byte": zst_avg_compression_per_byte(path),
    }


class TestFodsSprint57NdjsonExport:
    def test_fods_records_exported(self, tmp_path):
        out = tmp_path / "fods_analytics.ndjson"
        records = []
        for f in sorted(_FODS_DIR.glob("*.fods")):
            records.append(_build_fods_record(str(f)))
        with open(out, "w") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")
        lines = [json.loads(l) for l in out.read_text().splitlines()]
        assert len(lines) == 4
        assert all(r["format"] == "fods" for r in lines)

    def test_fods_minimal_ratio(self, tmp_path):
        path = str(_FODS_DIR / "minimal-spreadsheet.fods")
        rec = _build_fods_record(path)
        assert rec["row_to_sheet_ratio"] == 1.0
        assert rec["cell_type_variety"] == 1
        assert rec["file_size_bytes"] == 1421

    def test_fods_typed_variety(self, tmp_path):
        path = str(_FODS_DIR / "typed-values-basic.fods")
        rec = _build_fods_record(path)
        assert rec["cell_type_variety"] == 3
        assert rec["row_to_sheet_ratio"] == 4.0


class TestFodtSprint57NdjsonExport:
    def test_fodt_records_exported(self, tmp_path):
        out = tmp_path / "fodt_analytics.ndjson"
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            records.append(_build_fodt_record(str(f)))
        with open(out, "w") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")
        lines = [json.loads(l) for l in out.read_text().splitlines()]
        assert len(lines) >= 3
        assert all(r["format"] == "fodt" for r in lines)

    def test_fodt_minimal_block_text_sum(self, tmp_path):
        path = str(_FODT_DIR / "minimal-document.fodt")
        rec = _build_fodt_record(path)
        assert rec["block_text_sum"] == 13
        assert rec["digit_count"] == 0
        assert rec["max_run_count"] == 1

    def test_fodt_headings_word_per_heading(self, tmp_path):
        path = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        rec = _build_fodt_record(path)
        assert rec["block_text_sum"] == 275
        assert rec["word_per_heading"] > 0


class TestZstSprint57NdjsonExport:
    def test_zst_records_exported(self, tmp_path):
        out = tmp_path / "zst_analytics.ndjson"
        records = []
        for f in sorted(_ZST_DIR.glob("*.zst")):
            records.append(_build_zst_record(str(f)))
        with open(out, "w") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")
        lines = [json.loads(l) for l in out.read_text().splitlines()]
        assert len(lines) >= 3
        assert all(r["format"] == "zst" for r in lines)

    def test_zst_minimal_compression(self, tmp_path):
        path = str(_ZST_DIR / "minimal-synthetic.zst")
        rec = _build_zst_record(path)
        assert rec["size_exceeds_100k"] is False
        assert rec["avg_compression_per_byte"] == 0.1
        assert rec["frame_count_ratio"] > 0

    def test_zst_block128k_exceeds(self, tmp_path):
        path = str(_ZST_DIR / "block-128k.zst")
        rec = _build_zst_record(path)
        assert rec["size_exceeds_100k"] is True

    def test_roundtrip_json_serializable(self, tmp_path):
        path = str(_ZST_DIR / "minimal-synthetic.zst")
        rec = _build_zst_record(path)
        serialized = json.dumps(rec)
        recovered = json.loads(serialized)
        assert recovered["size_exceeds_100k"] == rec["size_exceeds_100k"]
        assert recovered["avg_compression_per_byte"] == rec["avg_compression_per_byte"]
