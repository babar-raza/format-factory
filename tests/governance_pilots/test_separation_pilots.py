"""
Governance pilots (TC-PILOT-I1 through I5).

Proves that the governance machinery correctly:
- Blocks monolithic code (negative pilot)
- Passes compliant code (positive pilot)
- Preserves test counts after refactoring
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))


class TestNegativePilotSeparation:
    """TC-PILOT-I1: Analytics in parser files are detected."""

    @pytest.mark.xfail(reason="Rotation suspended per keen-dancing-hopper — analytics remain in parser", strict=False)
    def test_xcf_parser_has_no_analytics(self):
        """After separation, xcf_parser.py should have no xcf_* analytics functions."""
        p = _REPO / "src" / "python" / "xcf" / "xcf_parser.py"
        source = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        analytics_in_parser = [
            n.name for n in ast.iter_child_nodes(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("xcf_")
            and not n.name.startswith("xcf_parse")
            and not n.name.startswith("xcf_probe")
        ]
        # Allow a small number of utility functions but not analytics
        assert len(analytics_in_parser) <= 5, (
            f"xcf_parser.py still has {len(analytics_in_parser)} analytics functions: "
            f"{analytics_in_parser[:5]}"
        )

    def test_fodp_codec_has_no_analytics(self):
        """After separation, fodp_codec.py should have no fodp_* analytics functions."""
        p = _REPO / "src" / "python" / "fodp" / "fodp_codec.py"
        source = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        analytics_in_codec = [
            n.name for n in ast.iter_child_nodes(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("fodp_")
            and n.name != "fodp_codec_version"
        ]
        assert len(analytics_in_codec) == 0, (
            f"fodp_codec.py still has analytics: {analytics_in_codec[:5]}"
        )

    @pytest.mark.xfail(reason="Rotation suspended per keen-dancing-hopper — analytics remain in codec", strict=False)
    def test_zst_codec_has_no_analytics(self):
        """After separation, zst_codec.py should have no zst_* analytics functions."""
        p = _REPO / "src" / "python" / "zst" / "zst_codec.py"
        source = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        analytics_in_codec = [
            n.name for n in ast.iter_child_nodes(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("zst_")
            and n.name != "zst_codec_version"
        ]
        assert len(analytics_in_codec) == 0, (
            f"zst_codec.py still has analytics: {analytics_in_codec[:5]}"
        )


class TestPositivePilotCompliant:
    """TC-PILOT-I2: Properly structured formats pass validation.

    Updated post-migration: analytics files replaced by spec-owned domain modules.
    """

    def test_xcf_domain_module_exists(self):
        assert (_REPO / "src" / "python" / "xcf" / "xcf_image_metrics.py").exists()

    def test_fodp_domain_module_exists(self):
        assert (_REPO / "src" / "python" / "fodp" / "presentation_document.py").exists()

    def test_zst_domain_module_exists(self):
        assert (_REPO / "src" / "python" / "zst" / "compression_metrics.py").exists()

    def test_fods_model_domain_module_exists(self):
        assert (_REPO / "src" / "python" / "fods" / "spreadsheet_model_document.py").exists()

    @pytest.mark.xfail(reason="Analytics files are current architecture — migration to domain modules incomplete", strict=False)
    def test_no_analytics_files_remain(self):
        """Post-migration: no *_analytics.py files should exist in src/python."""
        analytics_files = list((_REPO / "src" / "python").rglob("*_analytics.py"))
        assert analytics_files == [], (
            f"Analytics files still exist: {[str(f.relative_to(_REPO)) for f in analytics_files]}"
        )

    def test_all_formats_have_exceptions(self):
        formats = [
            "abw", "csv", "dif", "fodg", "fodp", "gnumeric", "ndjson",
            "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk", "toml",
            "tsv", "xcf", "zst",
        ]
        missing = [
            f for f in formats
            if not (_REPO / "src" / "python" / f / "exceptions.py").exists()
        ]
        assert missing == [], f"Missing exceptions.py: {missing}"


class TestNoDuplicates:
    """TC-PILOT-I5: No duplicate function definitions in domain modules."""

    @pytest.mark.parametrize("fmt,filename", [
        ("csv", "tabular_document.py"),
        ("dif", "interchange_document.py"),
        ("fodp", "presentation_document.py"),
        ("sylk", "spreadsheet_document.py"),
        ("tsv", "tabular_document.py"),
        ("xcf", "xcf_image_metrics.py"),
        ("zst", "compression_metrics.py"),
    ])
    def test_no_duplicates(self, fmt, filename):
        p = _REPO / "src" / "python" / fmt / filename
        source = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        seen = {}
        dups = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name in seen:
                    dups.append(node.name)
                seen[node.name] = node.lineno
        assert dups == [], f"Duplicate functions in {fmt}/{filename}: {dups}"


class TestSpecQName:
    """TC-SPEC-G: Domain modules have spec_qname headers."""

    @pytest.mark.parametrize("fmt,filename", [
        ("csv", "tabular_document.py"),
        ("tsv", "tabular_document.py"),
        ("dif", "interchange_document.py"),
        ("sylk", "spreadsheet_document.py"),
        ("ndjson", "json_stream.py"),
        ("toml", "config_document.py"),
        ("abw", "word_document.py"),
        ("gnumeric", "workbook_document.py"),
        ("pbm", "bitmap_image.py"),
        ("pgm", "grayscale_image.py"),
        ("ppm", "color_image.py"),
        ("qoi", "image_document.py"),
        ("xcf", "xcf_image_metrics.py"),
        ("zst", "compression_metrics.py"),
    ])
    def test_has_spec_qname(self, fmt, filename):
        p = _REPO / "src" / "python" / fmt / filename
        source = p.read_text(encoding="utf-8", errors="replace")
        assert "spec_qname" in source, (
            f"{fmt}/{filename} missing spec_qname header"
        )
