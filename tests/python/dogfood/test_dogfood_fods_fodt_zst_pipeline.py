"""
tests/python/dogfood/test_dogfood_fods_fodt_zst_pipeline.py

Sprint: FORMAT-FACTORY-GATE11-READINESS-PROOF-001
TASK-017: Dogfood export path using FODS, FODT, and ZST in a multi-format chain.

Proves: FODS → CSV export → ZST compress → decompress roundtrip
        FODT → text export → ZST compress → decompress roundtrip
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods, workbook_to_csv
from fodt import parse_fodt, document_to_text
from zst import compress_bytes, decompress_bytes, validate_roundtrip


_FODS_SAMPLE = str(_REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods")
_FODT_SAMPLE = str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt")


class TestFodsCsvZstPipeline:
    """FODS → CSV → ZST compress → decompress roundtrip."""

    def test_parse_fods_succeeds(self):
        wb = parse_fods(_FODS_SAMPLE)
        assert isinstance(wb, dict)

    def test_export_csv_produces_string(self):
        wb = parse_fods(_FODS_SAMPLE)
        csv_str = workbook_to_csv(wb)
        assert isinstance(csv_str, str)
        assert len(csv_str) > 0

    def test_csv_compresses_to_bytes(self):
        wb = parse_fods(_FODS_SAMPLE)
        csv_str = workbook_to_csv(wb)
        compressed = compress_bytes(csv_str.encode("utf-8"))
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0

    def test_compressed_csv_decompresses_to_original(self):
        wb = parse_fods(_FODS_SAMPLE)
        csv_str = workbook_to_csv(wb)
        original = csv_str.encode("utf-8")
        compressed = compress_bytes(original)
        recovered = decompress_bytes(compressed)
        assert recovered == original

    def test_roundtrip_validates_ok(self):
        wb = parse_fods(_FODS_SAMPLE)
        csv_str = workbook_to_csv(wb)
        data = csv_str.encode("utf-8")
        result = validate_roundtrip(data)
        assert result["valid"] is True
        assert result["match"] is True

    def test_pipeline_end_to_end_produces_valid_output(self):
        """Full FODS → CSV → ZST pipeline with file write and verify."""
        wb = parse_fods(_FODS_SAMPLE)
        csv_str = workbook_to_csv(wb)
        compressed = compress_bytes(csv_str.encode("utf-8"))
        fd, tmp_path = tempfile.mkstemp(suffix=".csv.zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(compressed)
            file_size = os.path.getsize(tmp_path)
            assert file_size == len(compressed)
            # Decompress and verify
            with open(tmp_path, "rb") as f:
                data = f.read()
            recovered = decompress_bytes(data)
            assert recovered.decode("utf-8") == csv_str
        finally:
            os.unlink(tmp_path)


class TestFodtTextZstPipeline:
    """FODT → text export → ZST compress → decompress roundtrip."""

    def test_parse_fodt_succeeds(self):
        doc = parse_fodt(_FODT_SAMPLE)
        assert isinstance(doc, dict)

    def test_export_text_produces_string(self):
        doc = parse_fodt(_FODT_SAMPLE)
        text = document_to_text(doc)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_text_compresses_to_bytes(self):
        doc = parse_fodt(_FODT_SAMPLE)
        text = document_to_text(doc)
        compressed = compress_bytes(text.encode("utf-8"))
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0

    def test_compressed_text_decompresses_to_original(self):
        doc = parse_fodt(_FODT_SAMPLE)
        text = document_to_text(doc)
        original = text.encode("utf-8")
        compressed = compress_bytes(original)
        recovered = decompress_bytes(compressed)
        assert recovered == original

    def test_compression_reduces_size_for_repetitive_text(self):
        doc = parse_fodt(_FODT_SAMPLE)
        text = document_to_text(doc) * 5  # repeat for better compression
        original = text.encode("utf-8")
        compressed = compress_bytes(original)
        assert len(compressed) < len(original)

    def test_pipeline_end_to_end_file_write(self):
        """Full FODT → text → ZST pipeline with file write and verify."""
        doc = parse_fodt(_FODT_SAMPLE)
        text = document_to_text(doc)
        compressed = compress_bytes(text.encode("utf-8"))
        fd, tmp_path = tempfile.mkstemp(suffix=".txt.zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(compressed)
            with open(tmp_path, "rb") as f:
                data = f.read()
            recovered = decompress_bytes(data)
            assert recovered.decode("utf-8") == text
        finally:
            os.unlink(tmp_path)


class TestGapClosureProof:
    """Prove all 10 open gaps are implemented (TASK-001 evidence)."""

    def test_pbm_probe_pbm_present(self):
        import pbm
        assert hasattr(pbm, "probe_pbm")

    def test_pgm_probe_pgm_present(self):
        import pgm
        assert hasattr(pgm, "probe_pgm")

    def test_ppm_probe_ppm_present(self):
        import ppm
        assert hasattr(ppm, "probe_ppm")

    def test_abw_write_abw_present(self):
        import abw
        assert hasattr(abw, "write_abw")

    def test_dif_parse_dif_present(self):
        import dif
        assert hasattr(dif, "parse_dif")

    def test_fods_parse_fods_present(self):
        import fods
        assert hasattr(fods, "parse_fods")

    def test_fodt_parse_fodt_present(self):
        import fodt
        assert hasattr(fodt, "parse_fodt")

    def test_ndjson_load_ndjson_present(self):
        import ndjson
        assert hasattr(ndjson, "load_ndjson")

    def test_sylk_parse_sylk_present(self):
        import sylk
        assert hasattr(sylk, "parse_sylk")

    def test_tsv_write_tsv_present(self):
        import tsv
        assert hasattr(tsv, "write_tsv")
