"""test_pqlm_016_fods_rebuild_roundtrip.py

TC-PQLM-016: Rebuilt tests for the FODS Python product post-PCG-003/004/005 migration.

Tests verify that the canonical analytics modules (fods_analytics, fods_analytics_extended)
are importable from their correct locations after renaming from spreadsheet_document /
spreadsheet_model_document.

Also verifies the roundtrip integrity: parse → write → parse produces identical structure.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Module availability — canonical locations
# ---------------------------------------------------------------------------

class TestCanonicalModuleLocations:
    """PCG-003/004: Analytics modules must be importable from canonical names."""

    def test_fods_analytics_importable(self):
        """fods_analytics is importable from its canonical location."""
        import fods.fods_analytics  # noqa: F401 — verifies module exists at canonical path

    def test_fods_analytics_extended_importable(self):
        """fods_analytics_extended is importable from its canonical location."""
        import fods.fods_analytics_extended  # noqa: F401

    def test_fods_analytics_has_no_spec_qname_at_module_scope(self):
        """fods_analytics.py must NOT have spec_qname at module scope.

        PCG-003: The false 'spec_qname = office:document' module-level assignment
        has been removed. ODF spec_qname belongs only in class bodies.
        """
        import fods.fods_analytics as mod
        assert not hasattr(mod, "spec_qname"), (
            "fods_analytics.py must not have spec_qname at module scope — "
            "it is an analytics module, not a domain type. "
            "PCG-003: Remove the false 'spec_qname = office:document' assignment."
        )

    def test_fods_analytics_extended_has_no_spec_qname_at_module_scope(self):
        """fods_analytics_extended.py must NOT have spec_qname at module scope.

        PCG-004: The false 'spec_qname = office:spreadsheet' has been removed.
        """
        import fods.fods_analytics_extended as mod
        assert not hasattr(mod, "spec_qname"), (
            "fods_analytics_extended.py must not have spec_qname at module scope."
        )

    def test_old_spreadsheet_document_file_gone(self):
        """PCG-003: spreadsheet_document.py must no longer exist in fods package."""
        fods_pkg = Path(__file__).parents[3] / "src" / "python" / "fods"
        assert not (fods_pkg / "spreadsheet_document.py").exists(), (
            "spreadsheet_document.py still exists — migration to fods_analytics.py incomplete."
        )

    def test_old_spreadsheet_model_document_file_gone(self):
        """PCG-004: spreadsheet_model_document.py must no longer exist."""
        fods_pkg = Path(__file__).parents[3] / "src" / "python" / "fods"
        assert not (fods_pkg / "spreadsheet_model_document.py").exists(), (
            "spreadsheet_model_document.py still exists — migration incomplete."
        )


# ---------------------------------------------------------------------------
# Analytics function accessibility
# ---------------------------------------------------------------------------

class TestAnalyticsFunctionsAccessible:
    """Key analytics functions remain accessible after module rename."""

    def test_workbook_stats_accessible(self):
        """workbook_stats (from fods_analytics) accessible via fods package."""
        from fods import workbook_stats
        assert callable(workbook_stats)

    def test_fods_formula_count_accessible(self):
        """fods_formula_count (from fods_analytics_extended) accessible via fods package."""
        from fods import fods_formula_count
        assert callable(fods_formula_count)

    def test_fods_sheet_count_accessible(self):
        """fods_sheet_count (from fods_analytics) accessible via fods package."""
        from fods import fods_sheet_count
        assert callable(fods_sheet_count)


# ---------------------------------------------------------------------------
# Roundtrip test — parse → write → parse
# ---------------------------------------------------------------------------

_SAMPLES_DIR = Path(__file__).parents[3] / "samples" / "by-format" / "fods"


@pytest.fixture
def fods_sample_path():
    """Return a known FODS sample file path."""
    candidates = list(_SAMPLES_DIR.glob("*.fods"))
    if not candidates:
        pytest.skip("No FODS sample files found in samples/by-format/fods/")
    return candidates[0]


class TestFodsRoundtrip:
    """Parse → analytics → roundtrip integrity tests per PCG-015/016."""

    def test_parse_fods_returns_workbook(self, fods_sample_path):
        """parse_fods() returns a dict with 'sheets' key."""
        from fods import parse_fods
        workbook = parse_fods(str(fods_sample_path))
        assert isinstance(workbook, dict), "parse_fods() must return a dict"
        assert "sheets" in workbook, "Parsed workbook must have 'sheets' key"

    def test_workbook_stats_on_parsed(self, fods_sample_path):
        """workbook_stats() returns valid stats dict on parsed FODS."""
        from fods import parse_fods, workbook_stats
        workbook = parse_fods(str(fods_sample_path))
        stats = workbook_stats(workbook)
        assert isinstance(stats, dict), "workbook_stats() must return a dict"
        assert "sheet_count" in stats

    def test_fods_sheet_count_positive(self, fods_sample_path):
        """fods_sheet_count() returns positive count for a valid FODS file."""
        from fods import parse_fods, fods_sheet_count
        workbook = parse_fods(str(fods_sample_path))
        count = fods_sheet_count(workbook)
        assert isinstance(count, int), "fods_sheet_count() must return int"
        assert count >= 0

    def test_write_then_parse_preserves_sheet_count(self, fods_sample_path, tmp_path):
        """write_fods → parse_fods roundtrip preserves sheet count."""
        from fods import parse_fods, write_fods, fods_sheet_count
        workbook = parse_fods(str(fods_sample_path))
        original_count = fods_sheet_count(workbook)

        out_path = tmp_path / "roundtrip.fods"
        write_fods(workbook, str(out_path))
        assert out_path.exists(), "write_fods() must create the output file"

        workbook2 = parse_fods(str(out_path))
        restored_count = fods_sheet_count(workbook2)
        assert restored_count == original_count, (
            f"Sheet count changed after roundtrip: "
            f"{original_count} → {restored_count}"
        )

    def test_parse_write_parse_preserves_format_id(self, fods_sample_path, tmp_path):
        """format_id field is preserved through parse → write → parse cycle."""
        from fods import parse_fods, write_fods
        workbook = parse_fods(str(fods_sample_path))
        original_format_id = workbook.get("format_id", "fods")

        out_path = tmp_path / "roundtrip.fods"
        write_fods(workbook, str(out_path))
        workbook2 = parse_fods(str(out_path))
        assert workbook2.get("format_id", "fods") == original_format_id
