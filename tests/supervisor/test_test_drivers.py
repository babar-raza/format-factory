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
    _validate_language,
    _SUPPORTED_LANGUAGE,
    validate_template_renderer_compatibility,
    ContractViolationError,
    scan_for_forbidden_placeholders,
    is_maintained_test,
    validate_fixture_contract,
    FORBIDDEN_PLACEHOLDER_PATTERNS,
    VALID_FIXTURE_SOURCES,
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


# ---------------------------------------------------------------------------
# TC-DRV-004: Language policy (PYTHON_ONLY_BY_DESIGN)
# ---------------------------------------------------------------------------

class TestLanguagePolicy:
    def test_unsupported_language_raises(self):
        with pytest.raises(ValueError, match="PYTHON_ONLY_BY_DESIGN"):
            _validate_language("csharp")

    def test_dotnet_raises(self):
        with pytest.raises(ValueError):
            _validate_language("dotnet")

    def test_java_raises(self):
        with pytest.raises(ValueError):
            _validate_language("java")

    def test_python_accepted(self):
        _validate_language("python")  # must not raise

    def test_python_uppercase_accepted(self):
        _validate_language("Python")  # case-insensitive

    def test_python_allcaps_accepted(self):
        _validate_language("PYTHON")

    def test_supported_language_constant(self):
        assert _SUPPORTED_LANGUAGE == "python"


# ---------------------------------------------------------------------------
# TC-DRV-005: Contract validation + drift detection
# ---------------------------------------------------------------------------

class TestContractValidation:
    def test_compatibility_passes(self):
        validate_template_renderer_compatibility()  # must not raise

    def test_compatibility_raises_on_drift(self, tmp_path, monkeypatch):
        import tools.supervisor.test_drivers as td
        import yaml

        contracts_path = tmp_path / "driver-contracts.yaml"
        bad_contracts = {
            "driver_templates": [
                {
                    "template_id": "getter_test",
                    "renderer_id": "render_getter_test",
                    "required_arguments": ["function_name", "module", "class_name", "return_type_safe", "extra_arg"],
                }
            ],
            "driver_renderers": [
                {
                    "renderer_id": "render_getter_test",
                    "provided_arguments": ["function_name", "module", "class_name", "return_type_safe"],
                }
            ],
        }
        contracts_path.write_text(yaml.dump(bad_contracts), encoding="utf-8")
        monkeypatch.setattr(td, "_DRIVERS_DIR", tmp_path)
        with pytest.raises(ContractViolationError):
            td.validate_template_renderer_compatibility()

    def test_contract_violation_error_is_exception(self):
        err = ContractViolationError("test msg")
        assert isinstance(err, Exception)
        assert "test msg" in str(err)


# ---------------------------------------------------------------------------
# TC-DRV-006: Placeholder scanning
# ---------------------------------------------------------------------------

class TestPlaceholderScanner:
    def test_detects_assert_is_not_none(self):
        code = "assert result is not None"
        found = scan_for_forbidden_placeholders(code)
        assert len(found) > 0

    def test_detects_isinstance_object(self):
        code = "assert isinstance(result, object)"
        found = scan_for_forbidden_placeholders(code)
        assert len(found) > 0

    def test_detects_fixture_required(self):
        code = "# FIXTURE_REQUIRED: replace with real bytes"
        found = scan_for_forbidden_placeholders(code)
        assert len(found) > 0

    def test_detects_expected_value_required(self):
        code = "# EXPECTED_VALUE_REQUIRED: assert something"
        found = scan_for_forbidden_placeholders(code)
        assert len(found) > 0

    def test_detects_oracle_required(self):
        code = "# ORACLE_REQUIRED: verify spec"
        found = scan_for_forbidden_placeholders(code)
        assert len(found) > 0

    def test_detects_scaffold_status_header(self):
        code = "# SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED"
        found = scan_for_forbidden_placeholders(code)
        assert len(found) > 0

    def test_clean_code_returns_empty(self):
        code = "def test_it():\n    assert result == expected\n"
        found = scan_for_forbidden_placeholders(code)
        assert found == []

    def test_forbidden_patterns_list_nonempty(self):
        assert len(FORBIDDEN_PLACEHOLDER_PATTERNS) > 0


# ---------------------------------------------------------------------------
# TC-DRV-006: is_maintained_test gate
# ---------------------------------------------------------------------------

class TestMaintainedGate:
    def test_scaffold_is_not_maintained(self):
        scaffold = render_getter_test(_SOURCE_PATH, "get_cell", "row: int", "str")
        assert is_maintained_test(scaffold) is False

    def test_clean_code_is_maintained(self):
        clean = "def test_it():\n    assert result == 'value'\n"
        assert is_maintained_test(clean) is True

    def test_code_with_fixture_required_not_maintained(self):
        code = "# FIXTURE_REQUIRED: provide bytes\ndef test_it():\n    pass\n"
        assert is_maintained_test(code) is False


# ---------------------------------------------------------------------------
# TC-DRV-009: Fixture contract
# ---------------------------------------------------------------------------

class TestFixtureContract:
    def test_empty_bytes_with_empty_contract_passes(self):
        validate_fixture_contract(b"", "empty_input_contract")  # must not raise

    def test_empty_bytes_with_real_source_raises(self):
        with pytest.raises(ValueError):
            validate_fixture_contract(b"", "repository_golden_sample")

    def test_real_bytes_accepted(self):
        validate_fixture_contract(b"real content bytes", "minimal_valid_bytes")  # must not raise


# ---------------------------------------------------------------------------
# TC-DRV-009: Documentation drift detection
# ---------------------------------------------------------------------------

class TestDocumentationDrift:
    _README = Path(__file__).resolve().parents[2] / "drivers" / "_readme.md"

    def _read_readme(self) -> str:
        return self._README.read_text(encoding="utf-8")

    def test_readme_exists(self):
        assert self._README.is_file(), "drivers/_readme.md missing"

    def test_readme_has_language_policy(self):
        content = self._read_readme()
        assert "PYTHON_ONLY_BY_DESIGN" in content

    def test_readme_has_consumer_list(self):
        content = self._read_readme()
        assert "test_drivers" in content

    def test_readme_has_promotion_lifecycle(self):
        content = self._read_readme()
        assert "SCAFFOLD" in content or "MAINTAINED" in content

    def test_readme_has_placeholder_policy(self):
        content = self._read_readme()
        assert "FIXTURE_REQUIRED" in content or "EXPECTED_VALUE_REQUIRED" in content

    def test_readme_has_validation_command(self):
        content = self._read_readme()
        assert "pytest" in content
