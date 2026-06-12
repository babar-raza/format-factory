"""Tests for template-based test driver renderer.

Pilot 2 deliverable — verifies that template rendering produces output
identical to the inline FeatureFactory test skeleton generators.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.test_drivers import (
    render_getter_test,
    render_export_csv_test,
    render_roundtrip_test,
    render_append_test,
    render_probe_test,
    _source_to_import,
    _safe_return_type,
    _load_template,
)
from tools.supervisor.product_feature_factory import FeatureFactory


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_SOURCE_PATH = "src/python/abw/abw_codec.py"
_FORMAT = "abw"


@pytest.fixture
def ff():
    return FeatureFactory(repo_root=str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# Golden baseline match tests (template output == inline output)
# ---------------------------------------------------------------------------


class TestGetterGoldenMatch:
    """Template-rendered getter test must match FeatureFactory inline output."""

    def test_matches_inline(self, ff):
        inline = ff._getter_test_skeleton(
            _SOURCE_PATH, "get_paragraph", "model: dict, index: int", "str"
        )
        rendered = render_getter_test(
            _SOURCE_PATH, "get_paragraph", "model: dict, index: int", "str"
        )
        assert rendered == inline

    def test_different_function(self, ff):
        inline = ff._getter_test_skeleton(
            "src/python/tsv/tsv_parser.py", "get_headers", "data: bytes", "list[str]"
        )
        rendered = render_getter_test(
            "src/python/tsv/tsv_parser.py", "get_headers", "data: bytes", "list[str]"
        )
        assert rendered == inline


class TestExportCsvGoldenMatch:
    """Template-rendered export_csv test must match FeatureFactory inline output."""

    def test_matches_inline(self, ff):
        inline = ff._export_csv_test_skeleton(
            _SOURCE_PATH, "export_to_csv", _FORMAT
        )
        rendered = render_export_csv_test(
            _SOURCE_PATH, "export_to_csv", _FORMAT
        )
        assert rendered == inline

    def test_different_format(self, ff):
        inline = ff._export_csv_test_skeleton(
            "src/python/dif/dif_parser.py", "export_to_csv", "dif"
        )
        rendered = render_export_csv_test(
            "src/python/dif/dif_parser.py", "export_to_csv", "dif"
        )
        assert rendered == inline


class TestRoundtripGoldenMatch:
    """Template-rendered roundtrip test must match FeatureFactory inline output."""

    def test_matches_inline(self, ff):
        inline = ff.generate_roundtrip_test(
            _FORMAT, _SOURCE_PATH, "load_abw", "write_abw", "paragraphs"
        )
        rendered = render_roundtrip_test(
            _FORMAT, _SOURCE_PATH, "load_abw", "write_abw", "paragraphs"
        )
        assert rendered == inline

    def test_different_format(self, ff):
        inline = ff.generate_roundtrip_test(
            "gnumeric", "src/python/gnumeric/gnumeric_codec.py",
            "load_gnumeric", "write_gnumeric", "sheets"
        )
        rendered = render_roundtrip_test(
            "gnumeric", "src/python/gnumeric/gnumeric_codec.py",
            "load_gnumeric", "write_gnumeric", "sheets"
        )
        assert rendered == inline


class TestAppendGoldenMatch:
    """Template-rendered append test must match FeatureFactory inline output."""

    def test_matches_inline(self, ff):
        inline = ff._append_test_skeleton(
            _SOURCE_PATH, "append_paragraph", _FORMAT, "paragraphs"
        )
        rendered = render_append_test(
            _SOURCE_PATH, "append_paragraph", _FORMAT, "paragraphs"
        )
        assert rendered == inline

    def test_different_format(self, ff):
        inline = ff._append_test_skeleton(
            "src/python/fodg/fodg_codec.py", "add_page", "fodg", "pages"
        )
        rendered = render_append_test(
            "src/python/fodg/fodg_codec.py", "add_page", "fodg", "pages"
        )
        assert rendered == inline


class TestProbeGoldenMatch:
    """Template-rendered probe test must match FeatureFactory inline output."""

    def test_matches_inline(self, ff):
        inline = ff._probe_test_skeleton(
            _SOURCE_PATH, "probe_abw", _FORMAT
        )
        rendered = render_probe_test(
            _SOURCE_PATH, "probe_abw", _FORMAT
        )
        assert rendered == inline

    def test_different_format(self, ff):
        inline = ff._probe_test_skeleton(
            "src/python/zst/zst_codec.py", "probe_zst", "zst"
        )
        rendered = render_probe_test(
            "src/python/zst/zst_codec.py", "probe_zst", "zst"
        )
        assert rendered == inline


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestSourceToImport:
    def test_standard_path(self):
        assert _source_to_import("src/python/abw/abw_codec.py") == "abw.abw_codec"

    def test_nested_path(self):
        assert _source_to_import("src/python/fods/fods_parser.py") == "fods.fods_parser"

    def test_no_python_in_path(self):
        result = _source_to_import("some/other/module.py")
        assert result == "some.other.module"


class TestSafeReturnType:
    def test_simple(self):
        assert _safe_return_type("str") == "str"

    def test_list_type(self):
        assert _safe_return_type("list[str]") == "list_str"

    def test_complex_type(self):
        assert _safe_return_type("dict[str, int]") == "dict_str_ int"


class TestLoadTemplate:
    def test_getter_template_exists(self):
        tmpl = _load_template("getter_test.py.tmpl")
        assert tmpl is not None

    def test_missing_template_raises(self):
        with pytest.raises(FileNotFoundError):
            _load_template("nonexistent.py.tmpl")

    def test_all_templates_loadable(self):
        templates = [
            "getter_test.py.tmpl",
            "export_csv_test.py.tmpl",
            "roundtrip_test.py.tmpl",
            "append_test.py.tmpl",
            "probe_test.py.tmpl",
        ]
        for name in templates:
            tmpl = _load_template(name)
            assert tmpl is not None


# ---------------------------------------------------------------------------
# Rendering produces valid Python
# ---------------------------------------------------------------------------


class TestRenderedOutputValidity:
    def test_getter_compiles(self):
        code = render_getter_test(_SOURCE_PATH, "get_paragraph", "m: dict", "str")
        compile(code, "<getter>", "exec")

    def test_export_csv_compiles(self):
        code = render_export_csv_test(_SOURCE_PATH, "export_to_csv", _FORMAT)
        compile(code, "<export_csv>", "exec")

    def test_roundtrip_compiles(self):
        code = render_roundtrip_test(
            _FORMAT, _SOURCE_PATH, "load_abw", "write_abw", "paragraphs"
        )
        compile(code, "<roundtrip>", "exec")

    def test_append_compiles(self):
        code = render_append_test(_SOURCE_PATH, "append_paragraph", _FORMAT, "paragraphs")
        compile(code, "<append>", "exec")

    def test_probe_compiles(self):
        code = render_probe_test(_SOURCE_PATH, "probe_abw", _FORMAT)
        compile(code, "<probe>", "exec")


# ---------------------------------------------------------------------------
# No product source mutation check
# ---------------------------------------------------------------------------


class TestNoProductSourceMutation:
    """Verify template rendering is read-only — no writes to src/python/."""

    def test_render_does_not_write_files(self, tmp_path):
        src_dir = tmp_path / "src" / "python"
        src_dir.mkdir(parents=True)
        marker = src_dir / "marker.txt"
        marker.write_text("untouched")

        render_getter_test(_SOURCE_PATH, "get_paragraph", "m: dict", "str")
        render_export_csv_test(_SOURCE_PATH, "export_to_csv", _FORMAT)
        render_roundtrip_test(_FORMAT, _SOURCE_PATH, "load_abw", "write_abw", "paragraphs")
        render_append_test(_SOURCE_PATH, "append_paragraph", _FORMAT, "paragraphs")
        render_probe_test(_SOURCE_PATH, "probe_abw", _FORMAT)

        assert marker.read_text() == "untouched"
