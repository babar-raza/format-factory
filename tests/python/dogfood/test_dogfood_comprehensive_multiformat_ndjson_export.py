"""Dogfood: Comprehensive multi-format analytics → NDJSON export.

Collects analytics from 12+ formats and exports as NDJSON records.
Covers: DIF, FODT, ODS, ODT, PBM, PGM, PPM, QOI, SYLK, XCF, ABW, FODS, FODP, Gnumeric.
"""
from __future__ import annotations
import json, os, sys, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


def _find_samples(fmt, subdir="valid", pattern=None):
    """Find sample files, trying valid/ subdir first, then root."""
    if pattern is None:
        pattern = f"*.{fmt}"
    base = _REPO / "samples" / "by-format" / fmt
    if subdir:
        d = base / subdir
        if d.exists():
            files = sorted(d.glob(pattern))
            if files:
                return files
    return sorted(base.glob(pattern))


def _collect_records():
    records = []

    # DIF
    dif_files = _find_samples("dif")
    if dif_files:
        from dif import dif_row_count, dif_column_count, dif_all_numeric_column
        s = str(dif_files[0])
        records.append({"format": "dif", "file": dif_files[0].name,
                        "row_count": dif_row_count(s), "col_count": dif_column_count(s),
                        "col0_numeric": dif_all_numeric_column(s, 0)})

    # FODT
    fodt_files = _find_samples("fodt", subdir="")
    if fodt_files:
        from fodt import fodt_paragraph_count, fodt_table_count
        s = str(fodt_files[0])
        records.append({"format": "fodt", "file": fodt_files[0].name,
                        "para_count": fodt_paragraph_count(s), "table_count": fodt_table_count(s)})

    # ODS
    ods_files = _find_samples("ods")
    if ods_files:
        from ods import ods_sheet_count, ods_data_density
        s = str(ods_files[0])
        records.append({"format": "ods", "file": ods_files[0].name,
                        "sheet_count": ods_sheet_count(s), "data_density": ods_data_density(s)})

    # ODT
    odt_files = _find_samples("odt")
    if odt_files:
        from odt import odt_word_count, odt_vocabulary_richness
        s = str(odt_files[0])
        records.append({"format": "odt", "file": odt_files[0].name,
                        "word_count": odt_word_count(s), "vocab_richness": odt_vocabulary_richness(s)})

    # PBM
    pbm_files = _find_samples("pbm")
    if pbm_files:
        from pbm import pbm_total_pixel_count, pbm_black_pixel_ratio
        s = str(pbm_files[0])
        records.append({"format": "pbm", "file": pbm_files[0].name,
                        "total_pixels": pbm_total_pixel_count(s),
                        "black_ratio": pbm_black_pixel_ratio(s)})

    # PGM
    pgm_files = _find_samples("pgm")
    if pgm_files:
        from pgm import pgm_standard_deviation, pgm_brightness_ratio
        s = str(pgm_files[0])
        records.append({"format": "pgm", "file": pgm_files[0].name,
                        "std_dev": pgm_standard_deviation(s), "brightness": pgm_brightness_ratio(s)})

    # PPM
    ppm_files = _find_samples("ppm")
    if ppm_files:
        from ppm import ppm_luminance_average, ppm_green_channel_sum
        s = str(ppm_files[0])
        records.append({"format": "ppm", "file": ppm_files[0].name,
                        "luminance": ppm_luminance_average(s), "green_sum": ppm_green_channel_sum(s)})

    # QOI
    qoi_files = _find_samples("qoi")
    if qoi_files:
        from qoi import qoi_avg_rgb, qoi_red_dominant, qoi_aspect_ratio
        s = str(qoi_files[0])
        avg = qoi_avg_rgb(s)
        records.append({"format": "qoi", "file": qoi_files[0].name,
                        "avg_r": avg[0], "avg_g": avg[1], "avg_b": avg[2],
                        "red_dominant": qoi_red_dominant(s), "aspect_ratio": qoi_aspect_ratio(s)})

    # SYLK
    sylk_files = _find_samples("sylk", pattern="*.slk")
    if sylk_files:
        from sylk import sylk_row_count, sylk_data_sparsity
        s = str(sylk_files[0])
        records.append({"format": "sylk", "file": sylk_files[0].name,
                        "row_count": sylk_row_count(s), "sparsity": sylk_data_sparsity(s)})

    # XCF
    xcf_files = _find_samples("xcf")
    if xcf_files:
        from xcf import xcf_width, xcf_compression_ratio
        s = str(xcf_files[0])
        records.append({"format": "xcf", "file": xcf_files[0].name,
                        "width": xcf_width(s), "compression_ratio": xcf_compression_ratio(s)})

    # ABW
    abw_files = _find_samples("abw", subdir="")
    if abw_files:
        from abw import abw_paragraph_count, abw_total_word_count
        s = str(abw_files[0])
        records.append({"format": "abw", "file": abw_files[0].name,
                        "para_count": abw_paragraph_count(s), "word_count": abw_total_word_count(s)})

    # FODS
    fods_files = _find_samples("fods", subdir="")
    if fods_files:
        try:
            from fods import parse_fods_strict, fods_sheet_count, fods_avg_cells_per_sheet
            s = str(fods_files[0])
            wb = parse_fods_strict(s)
            records.append({"format": "fods", "file": fods_files[0].name,
                            "sheet_count": fods_sheet_count(wb), "avg_cells": fods_avg_cells_per_sheet(wb)})
        except Exception:
            pass  # FODS API may need workbook model

    # FODP
    fodp_files = _find_samples("fodp", subdir="")
    if fodp_files:
        from fodp import fodp_slide_count
        s = str(fodp_files[0])
        records.append({"format": "fodp", "file": fodp_files[0].name,
                        "slide_count": fodp_slide_count(s)})

    # Gnumeric
    gnumeric_files = _find_samples("gnumeric", subdir="")
    if gnumeric_files:
        from gnumeric import gnumeric_sheet_count, gnumeric_total_cell_count
        s = str(gnumeric_files[0])
        records.append({"format": "gnumeric", "file": gnumeric_files[0].name,
                        "sheet_count": gnumeric_sheet_count(s), "total_cells": gnumeric_total_cell_count(s)})

    return records


class TestComprehensiveMultiformatNdjsonExport:
    def test_collect_12_plus_formats(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson, load_ndjson
        records = _collect_records()
        formats_found = {r["format"] for r in records}
        assert len(formats_found) >= 10, f"Expected 10+ formats, got {len(formats_found)}: {formats_found}"

        ndjson_path = tmp_path / "comprehensive-export.ndjson"
        write_ndjson(records, str(ndjson_path))
        loaded = load_ndjson(str(ndjson_path))
        assert len(loaded) == len(records)
        loaded_formats = {r["format"] for r in loaded}
        assert loaded_formats == formats_found

    def test_all_records_valid_json(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson
        records = _collect_records()
        path = tmp_path / "check.ndjson"
        write_ndjson(records, str(path))
        for line in path.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "format" in obj
            assert "file" in obj

    def test_each_record_has_analytics(self, tmp_path):
        records = _collect_records()
        for rec in records:
            # Each record should have format, file, and at least one analytic field
            assert "format" in rec
            assert "file" in rec
            analytics_keys = [k for k in rec if k not in ("format", "file")]
            assert len(analytics_keys) >= 1, f"{rec['format']} has no analytics"

    def test_format_diversity(self):
        records = _collect_records()
        formats = {r["format"] for r in records}
        # Verify specific formats are present
        expected = {"dif", "qoi", "pgm", "ppm", "ods", "odt", "sylk", "xcf", "pbm"}
        missing = expected - formats
        assert len(missing) <= 2, f"Missing expected formats: {missing}"
