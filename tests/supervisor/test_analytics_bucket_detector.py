"""
tests/supervisor/test_analytics_bucket_detector.py

Tests for tools/validators/analytics_bucket_detector.py.
TC-ANAL-SEG-HEAL-001 (2026-06-22).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "tools" / "validators"))
from analytics_bucket_detector import scan, _REPO


class TestForbiddenNameDetection:

    def test_analytics_extra_file_pattern_matches(self):
        """*_analytics_extra.py pattern should be flagged as forbidden name."""
        import re
        FORBIDDEN = re.compile(r"[^/\\]+_(analytics_extra|extra|misc)\.py$")
        assert FORBIDDEN.search("src/python/fodg/fodg_analytics_extra.py")
        assert FORBIDDEN.search("src/python/csv/csv_extra.py")
        assert FORBIDDEN.search("src/python/ods/ods_misc.py")
        assert not FORBIDDEN.search("src/python/fodg/fodg_analytics.py")
        assert not FORBIDDEN.search("src/python/fodg/drawing_document.py")

    def test_scan_returns_required_keys(self):
        """scan() result must have all required keys."""
        result = scan()
        assert "verdict" in result
        assert "forbidden_name_violations" in result
        assert "arithmetic_function_violations" in result
        assert "clean_files" in result
        assert "summary" in result

    def test_verdict_is_string(self):
        """verdict is CLEAN or VIOLATIONS_FOUND."""
        result = scan()
        assert result["verdict"] in ("CLEAN", "VIOLATIONS_FOUND")

    def test_summary_has_counts(self):
        """summary dict has required count fields."""
        result = scan()
        s = result["summary"]
        assert "total_violations" in s
        assert "forbidden_name_count" in s
        assert "arithmetic_function_files" in s
        assert "clean_count" in s

    def test_forbidden_name_count_is_zero(self):
        """After FODG healing, no forbidden-name files should exist."""
        result = scan()
        assert result["summary"]["forbidden_name_count"] == 0, (
            f"Forbidden name violations found: {result['forbidden_name_violations']}"
        )

    def test_fodg_analytics_files_deleted(self):
        """fodg_analytics.py and fodg_analytics_extra.py must not exist."""
        src = _REPO / "src" / "python"
        assert not (src / "fodg" / "fodg_analytics.py").exists()
        assert not (src / "fodg" / "fodg_analytics_extra.py").exists()

    def test_drawing_document_exists(self):
        """drawing_document.py must exist after healing."""
        src = _REPO / "src" / "python"
        assert (src / "fodg" / "drawing_document.py").exists()


class TestArithmeticFunctionDetection:

    def test_detector_finds_arithmetic_functions(self, tmp_path):
        """Detector classifies arithmetic-named functions as violations."""
        analytics = tmp_path / "test_analytics.py"
        analytics.write_text(
            "def csv_row_count_mod_7_times_3(): return 42\n"
            "def csv_page_count(): return 1\n"
        )
        # Scan the tmp directory directly (custom scan)
        from analytics_bucket_detector import _ARITH_FN, _get_functions
        fns = _get_functions(analytics)
        arith = [f for f in fns if _ARITH_FN.match(f)]
        assert "csv_row_count_mod_7_times_3" in arith

    def test_domain_function_not_flagged(self, tmp_path):
        """Legitimate domain functions are NOT flagged as arithmetic."""
        from analytics_bucket_detector import _ARITH_FN
        assert not _ARITH_FN.match("fodg_total_shape_count")
        assert not _ARITH_FN.match("fodg_page_count")
        assert not _ARITH_FN.match("fodg_is_empty_document")
        assert not _ARITH_FN.match("xcf_is_landscape")

    def test_drawing_document_is_clean(self):
        """drawing_document.py has no arithmetic functions."""
        from analytics_bucket_detector import _ARITH_FN, _get_functions
        src = _REPO / "src" / "python" / "fodg" / "drawing_document.py"
        if src.exists():
            fns = _get_functions(src)
            arith = [f for f in fns if _ARITH_FN.match(f)]
            assert arith == [], f"Unexpected arithmetic functions in drawing_document.py: {arith}"
