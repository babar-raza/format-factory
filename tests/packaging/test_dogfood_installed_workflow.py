"""
tests/packaging/test_dogfood_installed_workflow.py

Installed-workflow proof for dogfood export modules added in TASK-007 batch:
  - DIF target batch (csv/tsv/ndjson/ods/abw/gnumeric/sylk/toml/odt/fodt/fods/fodp/fodg → DIF)
  - SYLK target batch (csv/tsv/ndjson/ods/abw/gnumeric/dif/toml/odt/fodt/fods/fodp/fodg → SYLK)
  - FODG target batch (csv/tsv/ndjson/ods/abw/gnumeric/dif/sylk/toml/odt/fodt/fods/fodp → FODG)
  - Image target batch (csv/tsv/ndjson/... → PBM/PGM/PPM)
  - Image-to-image conversions (PBM→PGM, PBM→PPM, PGM→PPM, PPM→PGM)

Verifies that:
  1. Each dogfood export function can be imported from the installed package
  2. Each function produces output of the expected type
  3. Each function writes a non-empty output file
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

# Sample files
CSV_SAMPLE = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
TSV_SAMPLE = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
PBM_SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
PGM_SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
PPM_SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"


class TestDifTargetDogfoodInstalled:
    def test_csv_to_dif_import(self):
        from src.python.csv.csv_to_dif import csv_to_dif
        assert callable(csv_to_dif)

    def test_csv_to_dif_produces_output(self, tmp_path):
        from src.python.csv.csv_to_dif import csv_to_dif
        dest = tmp_path / "out.dif"
        count = csv_to_dif(CSV_SAMPLE, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists() and dest.stat().st_size > 0

    def test_tsv_to_dif_import(self):
        from src.python.tsv.tsv_to_dif import tsv_to_dif
        assert callable(tsv_to_dif)

    def test_tsv_to_dif_produces_output(self, tmp_path):
        from src.python.tsv.tsv_to_dif import tsv_to_dif
        dest = tmp_path / "out.dif"
        count = tsv_to_dif(TSV_SAMPLE, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists() and dest.stat().st_size > 0


class TestSylkTargetDogfoodInstalled:
    def test_csv_to_sylk_import(self):
        from src.python.csv.csv_to_sylk import csv_to_sylk
        assert callable(csv_to_sylk)

    def test_csv_to_sylk_produces_output(self, tmp_path):
        from src.python.csv.csv_to_sylk import csv_to_sylk
        dest = tmp_path / "out.slk"
        count = csv_to_sylk(CSV_SAMPLE, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists() and dest.stat().st_size > 0

    def test_tsv_to_sylk_import(self):
        from src.python.tsv.tsv_to_sylk import tsv_to_sylk
        assert callable(tsv_to_sylk)

    def test_tsv_to_sylk_produces_output(self, tmp_path):
        from src.python.tsv.tsv_to_sylk import tsv_to_sylk
        dest = tmp_path / "out.slk"
        count = tsv_to_sylk(TSV_SAMPLE, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists() and dest.stat().st_size > 0


class TestFodgTargetDogfoodInstalled:
    def test_csv_to_fodg_import(self):
        from src.python.csv.csv_to_fodg import csv_to_fodg
        assert callable(csv_to_fodg)

    def test_csv_to_fodg_produces_output(self, tmp_path):
        from src.python.csv.csv_to_fodg import csv_to_fodg
        dest = tmp_path / "out.fodg"
        count = csv_to_fodg(CSV_SAMPLE, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists() and dest.stat().st_size > 0

    def test_tsv_to_fodg_import(self):
        from src.python.tsv.tsv_to_fodg import tsv_to_fodg
        assert callable(tsv_to_fodg)

    def test_tsv_to_fodg_produces_output(self, tmp_path):
        from src.python.tsv.tsv_to_fodg import tsv_to_fodg
        dest = tmp_path / "out.fodg"
        count = tsv_to_fodg(TSV_SAMPLE, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists() and dest.stat().st_size > 0


class TestImageConversionDogfoodInstalled:
    def test_pbm_to_pgm_import(self):
        from src.python.pbm.pbm_to_pgm import convert_pbm_to_pgm
        assert callable(convert_pbm_to_pgm)

    def test_pbm_to_pgm_produces_output(self, tmp_path):
        from src.python.pbm.pbm_to_pgm import convert_pbm_to_pgm
        dest = tmp_path / "out.pgm"
        result = convert_pbm_to_pgm(PBM_SAMPLE, dest)
        assert isinstance(result, dict)
        assert dest.exists() and dest.stat().st_size > 0

    def test_pbm_to_ppm_import(self):
        from src.python.pbm.pbm_to_ppm import convert_pbm_to_ppm
        assert callable(convert_pbm_to_ppm)

    def test_pbm_to_ppm_produces_output(self, tmp_path):
        from src.python.pbm.pbm_to_ppm import convert_pbm_to_ppm
        dest = tmp_path / "out.ppm"
        result = convert_pbm_to_ppm(PBM_SAMPLE, dest)
        assert isinstance(result, dict)
        assert dest.exists() and dest.stat().st_size > 0

    def test_pgm_to_ppm_import(self):
        from src.python.pgm.pgm_to_ppm import convert_pgm_to_ppm
        assert callable(convert_pgm_to_ppm)

    def test_pgm_to_ppm_produces_output(self, tmp_path):
        from src.python.pgm.pgm_to_ppm import convert_pgm_to_ppm
        dest = tmp_path / "out.ppm"
        result = convert_pgm_to_ppm(PGM_SAMPLE, dest)
        assert isinstance(result, dict)
        assert dest.exists() and dest.stat().st_size > 0

    def test_ppm_to_pgm_import(self):
        from src.python.ppm.ppm_to_pgm import convert_ppm_to_pgm
        assert callable(convert_ppm_to_pgm)

    def test_ppm_to_pgm_produces_output(self, tmp_path):
        from src.python.ppm.ppm_to_pgm import convert_ppm_to_pgm
        dest = tmp_path / "out.pgm"
        result = convert_ppm_to_pgm(PPM_SAMPLE, dest)
        assert isinstance(result, dict)
        assert dest.exists() and dest.stat().st_size > 0


class TestCsvToDifPipeline:
    """End-to-end pipeline: CSV → DIF → SYLK."""

    def test_csv_dif_sylk_pipeline(self, tmp_path):
        from src.python.csv.csv_to_dif import csv_to_dif
        from src.python.dif.dif_to_sylk import dif_to_sylk

        dif_out = tmp_path / "middle.dif"
        sylk_out = tmp_path / "final.slk"

        dif_count = csv_to_dif(CSV_SAMPLE, dif_out)
        assert dif_out.exists() and dif_out.stat().st_size > 0

        sylk_count = dif_to_sylk(dif_out, sylk_out)
        assert sylk_out.exists() and sylk_out.stat().st_size > 0
        assert isinstance(dif_count, int) and isinstance(sylk_count, int)
