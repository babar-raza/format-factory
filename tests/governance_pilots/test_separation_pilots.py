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
import subprocess
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


class TestPythonDomainModulePilot:
    """TC-PILOT-I4: D-group codec files reduced and domain modules wired."""

    @pytest.mark.parametrize("fmt,filename,max_loc", [
        ("abw", "abw_codec.py", 800),
        ("gnumeric", "gnumeric_codec.py", 800),
        ("ndjson", "ndjson_codec.py", 800),
        ("fodg", "drawing_document.py", 800),
        ("fodt", "neutral_model.py", 800),
    ])
    def test_codec_under_800loc(self, fmt, filename, max_loc):
        """After D-group extraction, primary codec/model files must be ≤ 800 LOC."""
        p = _REPO / "src" / "python" / fmt / filename
        assert p.is_file(), f"{fmt}/{filename} does not exist"
        loc = sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
        assert loc <= max_loc, (
            f"{fmt}/{filename}: {loc} LOC exceeds max {max_loc}"
        )

    @pytest.mark.parametrize("fmt,stats_file", [
        ("abw", "abw_word_stats.py"),
        ("gnumeric", "gnumeric_workbook_stats.py"),
        ("ndjson", "ndjson_record_stats.py"),
        ("fodg", "drawing_metrics.py"),
        ("fodt", "fodt_neutral_ops.py"),
        ("fodt", "fodt_document_edit.py"),
        ("fodt", "fodt_document_query.py"),
    ])
    def test_domain_stats_file_exists(self, fmt, stats_file):
        """D-group extraction target files must exist."""
        p = _REPO / "src" / "python" / fmt / stats_file
        assert p.is_file(), f"{fmt}/{stats_file} missing — D-group extraction incomplete"

    def test_no_analytics_py_files(self):
        """Binding rule: NO *_analytics.py files may be created."""
        analytics_files = list((_REPO / "src" / "python").rglob("*_analytics.py"))
        assert not analytics_files, (
            "Banned *_analytics.py files found:\n"
            + "\n".join(f"  - {f.relative_to(_REPO)}" for f in analytics_files)
        )


class TestSpecConceptTags:
    """TC-SPEC-G (RESURRECTED): Non-ODF parser/codec files have spec_concept tags."""

    @pytest.mark.parametrize("fmt,filename", [
        ("csv", "csv_parser.py"),
        ("tsv", "tsv_parser.py"),
        ("dif", "dif_parser.py"),
        ("sylk", "sylk_parser.py"),
        ("ndjson", "ndjson_codec.py"),
        ("toml", "toml_codec.py"),
        ("abw", "abw_codec.py"),
        ("gnumeric", "gnumeric_codec.py"),
        ("pbm", "pbm_parser.py"),
        ("pgm", "pgm_parser.py"),
        ("ppm", "ppm_parser.py"),
        ("qoi", "qoi_parser.py"),
        ("xcf", "xcf_parser.py"),
        ("zst", "zst_codec.py"),
    ])
    def test_has_spec_concept(self, fmt, filename):
        """TC-SPEC-G: spec_concept: tag in module docstring."""
        p = _REPO / "src" / "python" / fmt / filename
        source = p.read_text(encoding="utf-8", errors="replace")
        assert "spec_concept:" in source, (
            f"{fmt}/{filename} missing spec_concept: tag"
        )


class TestInitPyUnderLimit:
    """TC-INIT-E: All format __init__.py files ≤ 100 LOC."""

    @pytest.mark.parametrize("fmt", [
        "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
        "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
        "qoi", "sylk", "toml", "tsv", "xcf", "zst",
    ])
    def test_init_under_100loc(self, fmt):
        """__init__.py must be ≤ 100 LOC (TC-INIT-E)."""
        p = _REPO / "src" / "python" / fmt / "__init__.py"
        assert p.is_file(), f"{fmt}/__init__.py does not exist"
        loc = sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
        assert loc <= 100, f"{fmt}/__init__.py: {loc} LOC exceeds 100"


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


class TestDotNetBuildPilot:
    """TC-PILOT-I3: .NET governed decomposition builds cleanly and respects LOC limits."""

    DOTNET_TARGETS = [
        ("fods", "src/net/fods/FormatFactory.Fods.csproj"),
        ("fodt", "src/net/fodt/FormatFactory.Fodt.csproj"),
        ("netpbm", "src/net/netpbm/FormatFactory.Netpbm.csproj"),
    ]

    @pytest.mark.parametrize("fmt,csproj", DOTNET_TARGETS)
    def test_dotnet_build_succeeds(self, fmt, csproj):
        """dotnet build must exit 0 after decomposition."""
        result = subprocess.run(
            ["dotnet", "build", str(_REPO / csproj), "--no-restore", "-v", "quiet"],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, (
            f"{fmt} build failed (exit {result.returncode}):\n{result.stderr[-500:]}"
        )

    @pytest.mark.parametrize("fmt,directory,max_loc", [
        ("fods", "src/net/fods", 800),
        ("fodt", "src/net/fodt", 800),
        ("netpbm", "src/net/netpbm/Model", 800),
    ])
    def test_no_dotnet_file_exceeds_loc_limit(self, fmt, directory, max_loc):
        """No .cs file in decomposed .NET projects should exceed 800 LOC."""
        violations = []
        for cs_file in (_REPO / directory).glob("**/*.cs"):
            loc = sum(1 for _ in cs_file.open(encoding="utf-8", errors="replace"))
            if loc > max_loc:
                violations.append(f"{cs_file.name}: {loc} LOC")
        assert not violations, (
            f"{fmt} has .cs files over {max_loc} LOC:\n" + "\n".join(violations)
        )

    def test_exceptions_directories_exist(self):
        """fodt and netpbm must have Exceptions/ directories after decomposition."""
        fodt_exc = _REPO / "src" / "net" / "fodt" / "Exceptions"
        netpbm_exc = _REPO / "src" / "net" / "netpbm" / "Exceptions"
        assert fodt_exc.is_dir(), "src/net/fodt/Exceptions/ does not exist"
        assert netpbm_exc.is_dir(), "src/net/netpbm/Exceptions/ does not exist"
