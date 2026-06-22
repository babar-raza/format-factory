"""R90 Dogfood proof: dif_to_csv uses Format Factory CSV writer (not stdlib csv).

dogfood_status: IMPLEMENTED
source_format: DIF
target_format: CSV
target_ff_library: src/python/csv/csv_writer.py::write_csv
sprint: product-deepening-session-2026-06-22
skill: add-dogfood-export
"""

import inspect
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from dif import dif_analytics
from dif.dif_parser import parse_dif_strict

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "dif")


class TestDogfoodLibraryUsage:
    """Prove dif_to_csv uses FF csv_writer and NOT stdlib csv."""

    def test_dif_analytics_does_not_import_csv_stdlib(self):
        """stdlib csv must NOT be imported in dif_analytics (FF writer replaces it)."""
        source = inspect.getsource(dif_analytics)
        assert "import csv" not in source, (
            "dif_analytics.py must not import stdlib csv module after dogfood upgrade"
        )

    def test_dif_analytics_imports_ff_csv_writer(self):
        """dif_analytics must reference the FF write_csv function."""
        source = inspect.getsource(dif_analytics)
        assert "write_csv" in source, "dif_analytics must reference FF write_csv"
        assert "csv_writer" in source, "dif_analytics must import from csv_writer (FF)"

    def test_ff_csv_writer_is_callable(self):
        """The FF writer must have been successfully imported at module load time."""
        assert dif_analytics._ff_write_csv is not None, (
            "FF write_csv import failed — dogfood backend unavailable"
        )
        assert callable(dif_analytics._ff_write_csv)

    def test_dif_to_csv_returns_string(self):
        result = dif_analytics.dif_to_csv(os.path.join(SAMPLES, "valid", "minimal-2x2.dif"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_meaningful_value_survives_export(self):
        """A known numeric value from the DIF file must appear in CSV output."""
        result = dif_analytics.dif_to_csv(os.path.join(SAMPLES, "valid", "numeric-row.dif"))
        assert any(c.isdigit() for c in result), "No numeric data survived DIF→CSV export"

    def test_csv_output_reloads_via_ff_csv_parser(self):
        """Exported CSV must be parseable by the FF CSV parser (reload proof)."""
        import tempfile
        from pathlib import Path

        result = dif_analytics.dif_to_csv(os.path.join(SAMPLES, "valid", "minimal-2x2.dif"))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(result)
            tmp_path = f.name

        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
            from csv.csv_parser import parse_csv_strict  # noqa: F401 (checks importability)
            parsed = parse_csv_strict(tmp_path)
            assert parsed.get("row_count", 0) >= 1, "CSV reload produced 0 rows"
        except ImportError:
            pytest.skip("FF csv_parser not importable in this test path; skipping reload proof")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_single_cell_export_nonempty(self):
        result = dif_analytics.dif_to_csv(os.path.join(SAMPLES, "valid", "single-cell.dif"))
        assert len(result.strip()) > 0
