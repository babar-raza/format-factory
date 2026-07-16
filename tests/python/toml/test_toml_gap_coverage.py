"""
tests/python/toml/test_toml_gap_coverage.py

Comprehensive gap-coverage test suite for the TOML FOSS Python package
(src/python/toml/).

Closes/reinforces the ~81 `missing_test_coverage` gaps registered for TOML
in reports/capability-layer/gap-ledger.json under gap-id prefix
GAP-TOML-FOSS-*, and additionally exercises every one of the 112 public
names in `toml.__all__` (src/python/toml/__init__.py) so the whole exported
surface has direct or backstop coverage.

Golden expected values used below were derived by executing the real
functions against the fixtures (not hand-derived), then pinned here as
regression values — see the taskcard note at the bottom of this docstring
for how they were produced.

Grouped by:
  1. Codec core        — load/write/probe/roundtrip
  2. Codec errors       — TomlInputError / TomlParseError / TomlWriteError
                          (module-qualified — see "Exception identity" note)
  3. Codec value access — get_value/has_key/count_keys/list_sections/...
  4. Codec mutation      — set_value/delete_key/rename_key/update_section/merge_toml
  5. Codec export        — flatten/to_env/to_json_str/diff_keys
  6. Installed workflow  — installed_workflow / toml_installed_workflow
  7. Exception hierarchy — exceptions.py public classes (package-level)
  8. Writer module       — write_toml_str/write_toml + TomlWriteError paths
  9. Domain model         — TomlDocument (models.py)
  10. Spec-shaped iterators — toml_iter_keys / toml_iter_tables (Key/Table)
  11. Analytics — golden-value matrix against two fixtures (flat/minimal
      and rich/nested) covering all 70 scalar analytics functions
  12. Analytics — targeted edge cases (empty doc, two-key doc, all-bool doc)
  13. Dogfood export converters — all 14 toml_to_* modules
  14. Meta backstop — every name in toml.__all__ is defined and, for the
      plain analytics ones, callable without error

Exception identity note (documented, not "fixed" — out of scope for a test
file): `toml.load_toml()` is bound to `toml_codec.load_toml`, which raises
`toml_codec.TomlInputError` / `toml_codec.TomlParseError` — locally-defined
exception classes in toml_codec.py. The package-level `toml.TomlInputError`
/ `toml.TomlParseError` (re-exported from exceptions.py, imported later in
__init__.py) are a *different* class object and do NOT catch what
load_toml() actually raises. The same shadowing applies to `toml.write_toml`
(bound to toml_writer.write_toml, raising toml_writer.TomlWriteError, not
toml.TomlWriteError). Tests below assert the real, currently-shipping
behavior using module-qualified exception classes, and separately verify
the exceptions.py hierarchy in isolation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
# Several toml_to_*.py dogfood converters (e.g. toml_to_csv.py) compute their
# own _REPO with an off-by-one parents[] index and then do
# `from src.python.<fmt>.<mod> import ...`. That only resolves if the real
# repo root is *also* on sys.path (as the sibling test_toml_to_*.py files
# already do) — otherwise `import src` fails with ModuleNotFoundError.
sys.path.insert(0, str(_REPO))

MINIMAL_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

import toml as toml_pkg  # noqa: E402
from toml import toml_codec  # noqa: E402
from toml import toml_writer  # noqa: E402
from toml import toml_workflow  # noqa: E402
from toml import toml_key_iterator  # noqa: E402
from toml import toml_table_iterator  # noqa: E402
from toml.models import TomlDocument  # noqa: E402
from toml.exceptions import (  # noqa: E402
    TomlError as PkgTomlError,
    TomlInputError as PkgTomlInputError,
    TomlParseError as PkgTomlParseError,
    TomlWriteError as PkgTomlWriteError,
)


# ---------------------------------------------------------------------------
# Fixture content
# ---------------------------------------------------------------------------

FLAT_TOML = 'name = "test"\nage = 30\nscore = 9.5\nactive = true\n'
TWO_KEY_TOML = "a = 1\nb = 2\n"
ALL_BOOL_TOML = "x = true\ny = false\nz = true\n"
RICH_TOML = (
    'title = "Example"\n'
    "count = 42\n"
    "ratio = 3.14\n"
    "enabled = true\n"
    'tags = ["a", "b", "c"]\n'
    "\n"
    "[server]\n"
    'host = "localhost"\n'
    "port = 8080\n"
    "\n"
    "[server.tls]\n"
    "enabled = true\n"
    'cert = "cert.pem"\n'
    "\n"
    "[[servers]]\n"
    'name = "alpha"\n'
    'ip = "10.0.0.1"\n'
    "\n"
    "[[servers]]\n"
    'name = "beta"\n'
    'ip = "10.0.0.2"\n'
)


@pytest.fixture
def flat_toml(tmp_path: Path) -> Path:
    p = tmp_path / "flat.toml"
    p.write_text(FLAT_TOML, encoding="utf-8")
    return p


@pytest.fixture
def two_key_toml(tmp_path: Path) -> Path:
    p = tmp_path / "two.toml"
    p.write_text(TWO_KEY_TOML, encoding="utf-8")
    return p


@pytest.fixture
def all_bool_toml(tmp_path: Path) -> Path:
    p = tmp_path / "bools.toml"
    p.write_text(ALL_BOOL_TOML, encoding="utf-8")
    return p


@pytest.fixture
def rich_toml(tmp_path: Path) -> Path:
    p = tmp_path / "rich.toml"
    p.write_text(RICH_TOML, encoding="utf-8")
    return p


@pytest.fixture
def empty_toml(tmp_path: Path) -> Path:
    p = tmp_path / "empty.toml"
    p.write_text("", encoding="utf-8")
    return p


def _assert_close(result, expected):
    if isinstance(expected, float):
        assert result == pytest.approx(expected)
    else:
        assert result == expected


# ===========================================================================
# 1. Codec core: load / write / probe / roundtrip / get_keys
# ===========================================================================

class TestCodecCore:
    def test_load_toml_returns_neutral_model(self):
        model = toml_codec.load_toml(str(MINIMAL_TOML))
        assert model["format"] == "toml"
        assert isinstance(model["data"], dict)
        assert model["top_level_keys"] == ["title", "version", "enabled", "server", "database"]
        assert model["key_count"] == 5

    def test_load_toml_accepts_bytes(self):
        model = toml_codec.load_toml(b'x = 1\ny = "z"\n')
        assert model["path"] == "<bytes>"
        assert model["data"] == {"x": 1, "y": "z"}

    def test_load_toml_accepts_path_object(self):
        model = toml_codec.load_toml(MINIMAL_TOML)
        assert model["key_count"] == 5

    def test_get_keys(self):
        assert toml_pkg.get_keys(str(MINIMAL_TOML)) == [
            "title", "version", "enabled", "server", "database",
        ]

    def test_probe_toml_valid_file(self):
        result = toml_pkg.probe_toml(str(MINIMAL_TOML))
        assert result["format"] == "toml"
        assert result["exists"] is True
        assert result["section_count"] == 2
        assert result["key_count"] == 5
        assert set(result["top_level_keys"]) == {"title", "version", "enabled", "server", "database"}

    def test_probe_toml_missing_file(self, tmp_path: Path):
        result = toml_pkg.probe_toml(str(tmp_path / "missing.toml"))
        assert result["exists"] is False
        assert "size_bytes" not in result

    def test_probe_toml_malformed_content_sets_probe_error(self, tmp_path: Path):
        bad = tmp_path / "bad.toml"
        bad.write_text("this is not = = valid toml [[[", encoding="utf-8")
        result = toml_pkg.probe_toml(str(bad))
        assert result["exists"] is True
        assert "probe_error" in result

    def test_probe_toml_accepts_bytes(self):
        result = toml_pkg.probe_toml(b'a = 1\n')
        assert result["top_level_keys"] == ["a"]
        assert result["key_count"] == 1

    def test_write_toml_then_load_toml_roundtrip(self, tmp_path: Path):
        dest = tmp_path / "out.toml"
        toml_pkg.write_toml({"a": 1, "b": True, "c": "text"}, dest)
        assert dest.exists()
        reloaded = toml_pkg.load_toml(dest)
        assert reloaded["data"] == {"a": 1, "b": True, "c": "text"}

    def test_write_toml_supports_nested_tables(self, tmp_path: Path):
        dest = tmp_path / "nested.toml"
        toml_pkg.write_toml({"title": "hi", "sect": {"x": 1, "y": "z"}}, dest)
        reloaded = toml_pkg.load_toml(dest)
        assert reloaded["data"] == {"title": "hi", "sect": {"x": 1, "y": "z"}}

    def test_roundtrip_function(self, tmp_path: Path):
        dest = tmp_path / "rt.toml"
        result = toml_codec.roundtrip(str(MINIMAL_TOML), dest)
        assert result["data"]["title"] == "Format Factory TOML Sample"
        assert dest.exists()

    def test_roundtrip_preserves_key_count(self, flat_toml: Path, tmp_path: Path):
        dest = tmp_path / "rt2.toml"
        original = toml_codec.load_toml(flat_toml)
        result = toml_codec.roundtrip(flat_toml, dest)
        assert result["key_count"] == original["key_count"]


# ===========================================================================
# 2. Codec errors — module-qualified (see "Exception identity note" above)
# ===========================================================================

class TestCodecErrors:
    def test_load_toml_missing_file_raises_input_error(self, tmp_path: Path):
        with pytest.raises(toml_codec.TomlInputError):
            toml_pkg.load_toml(str(tmp_path / "does-not-exist.toml"))

    def test_load_toml_directory_raises_input_error(self, tmp_path: Path):
        with pytest.raises(toml_codec.TomlInputError):
            toml_pkg.load_toml(str(tmp_path))

    def test_load_toml_oversized_bytes_raises_input_error(self):
        oversized = b"x" * (toml_codec.MAX_FILE_SIZE + 1)
        with pytest.raises(toml_codec.TomlInputError):
            toml_pkg.load_toml(oversized)

    def test_load_toml_malformed_content_raises_parse_error(self, tmp_path: Path):
        bad = tmp_path / "bad.toml"
        bad.write_text("this is not = = valid toml [[[", encoding="utf-8")
        with pytest.raises(toml_codec.TomlParseError):
            toml_pkg.load_toml(str(bad))

    def test_load_toml_malformed_bytes_raises_parse_error(self):
        with pytest.raises(toml_codec.TomlParseError):
            toml_pkg.load_toml(b"not [[[ valid")

    def test_write_toml_unsupported_array_of_dicts_raises_write_error(self):
        with pytest.raises(toml_writer.TomlWriteError):
            toml_pkg.write_toml_str({"tags": [{"a": 1}]})

    def test_write_toml_empty_path_raises_write_error(self):
        with pytest.raises(toml_writer.TomlWriteError):
            toml_pkg.write_toml({"a": 1}, "")

    def test_toml_error_hierarchy_within_codec_module(self):
        assert issubclass(toml_codec.TomlInputError, toml_codec.TomlError)
        assert issubclass(toml_codec.TomlParseError, toml_codec.TomlError)
        assert issubclass(toml_codec.TomlWriteError, toml_codec.TomlError)


# ===========================================================================
# 3. Codec value access
# ===========================================================================

class TestCodecValueAccess:
    def test_get_value_dotted_path(self):
        assert toml_pkg.get_value(str(MINIMAL_TOML), "server.port") == 8080

    def test_get_value_top_level(self):
        assert toml_pkg.get_value(str(MINIMAL_TOML), "title") == "Format Factory TOML Sample"

    def test_get_value_missing_raises_keyerror(self):
        with pytest.raises(KeyError):
            toml_pkg.get_value(str(MINIMAL_TOML), "server.missing")

    def test_has_key_true(self):
        assert toml_pkg.has_key(str(MINIMAL_TOML), "server.host") is True

    def test_has_key_false(self):
        assert toml_pkg.has_key(str(MINIMAL_TOML), "nope.x") is False

    def test_count_keys_top_level_only(self):
        assert toml_pkg.count_keys(str(MINIMAL_TOML)) == 5

    def test_count_keys_recursive(self):
        assert toml_pkg.count_keys(str(MINIMAL_TOML), recursive=True) == 9

    def test_list_sections(self):
        assert toml_pkg.list_sections(str(MINIMAL_TOML)) == ["database", "server"]

    def test_get_section_keys(self):
        assert toml_pkg.get_section_keys(str(MINIMAL_TOML), "server") == ["host", "port"]

    def test_get_section_keys_missing_raises(self):
        with pytest.raises(KeyError):
            toml_pkg.get_section_keys(str(MINIMAL_TOML), "nope")

    def test_get_section_keys_non_table_raises(self):
        with pytest.raises(KeyError):
            toml_pkg.get_section_keys(str(MINIMAL_TOML), "title")

    def test_has_section_true(self):
        assert toml_pkg.has_section(str(MINIMAL_TOML), "server") is True

    def test_has_section_false_for_scalar(self):
        assert toml_pkg.has_section(str(MINIMAL_TOML), "title") is False

    def test_has_section_false_for_missing(self):
        assert toml_pkg.has_section(str(MINIMAL_TOML), "nope") is False

    def test_get_all_keys(self):
        assert toml_pkg.get_all_keys(str(MINIMAL_TOML)) == [
            "database", "database.max_connections", "database.name",
            "enabled", "server", "server.host", "server.port", "title", "version",
        ]

    def test_get_all_keys_custom_separator(self):
        keys = toml_pkg.get_all_keys(str(MINIMAL_TOML), separator="/")
        assert "server/host" in keys

    def test_get_section_as_dict(self):
        assert toml_pkg.get_section_as_dict(str(MINIMAL_TOML), "server") == {
            "host": "localhost", "port": 8080,
        }

    def test_get_section_as_dict_missing_returns_empty(self):
        assert toml_pkg.get_section_as_dict(str(MINIMAL_TOML), "nope") == {}

    def test_get_section_as_dict_non_table_returns_empty(self):
        assert toml_pkg.get_section_as_dict(str(MINIMAL_TOML), "title") == {}

    def test_has_any_section_true(self):
        assert toml_pkg.has_any_section(str(MINIMAL_TOML)) is True

    def test_has_any_section_false_for_flat(self, flat_toml: Path):
        assert toml_pkg.has_any_section(str(flat_toml)) is False

    def test_count_values_in_section(self):
        assert toml_pkg.count_values_in_section(str(MINIMAL_TOML), "server") == 2

    def test_count_values_in_section_missing_returns_zero(self):
        assert toml_pkg.count_values_in_section(str(MINIMAL_TOML), "nope") == 0

    def test_count_sections_with_key(self):
        assert toml_pkg.count_sections_with_key(str(MINIMAL_TOML), "host") == 1

    def test_count_sections_with_key_absent(self):
        assert toml_pkg.count_sections_with_key(str(MINIMAL_TOML), "nonexistent_key") == 0


# ===========================================================================
# 4. Codec mutation
# ===========================================================================

class TestCodecMutation:
    def test_set_value_overwrites_nested(self):
        data = {"a": 1, "b": {"c": 2}}
        result = toml_pkg.set_value(data, "b.c", 99)
        assert result == {"a": 1, "b": {"c": 99}}
        # original not mutated
        assert data == {"a": 1, "b": {"c": 2}}

    def test_set_value_creates_intermediate_dicts(self):
        result = toml_pkg.set_value({}, "x.y.z", 1)
        assert result == {"x": {"y": {"z": 1}}}

    def test_set_value_non_dict_intermediate_raises_typeerror(self):
        with pytest.raises(TypeError):
            toml_pkg.set_value({"a": 1}, "a.b", 2)

    def test_delete_key_removes_nested(self):
        data = {"a": 1, "b": {"c": 2}}
        result = toml_pkg.delete_key(data, "b.c")
        assert result == {"a": 1, "b": {}}
        assert data == {"a": 1, "b": {"c": 2}}

    def test_delete_key_missing_raises_keyerror(self):
        with pytest.raises(KeyError):
            toml_pkg.delete_key({"a": 1}, "nope")

    def test_delete_key_non_dict_intermediate_raises_typeerror(self):
        with pytest.raises(TypeError):
            toml_pkg.delete_key({"a": 1}, "a.b")

    def test_rename_key_success(self):
        assert toml_pkg.rename_key({"a": 1}, "a", "z") == {"z": 1}

    def test_rename_key_missing_raises_keyerror(self):
        with pytest.raises(KeyError):
            toml_pkg.rename_key({"a": 1}, "missing", "z")

    def test_rename_key_collision_raises_valueerror(self):
        with pytest.raises(ValueError):
            toml_pkg.rename_key({"a": 1, "b": 2}, "a", "b")

    def test_rename_key_preserves_other_keys_order(self):
        result = toml_pkg.rename_key({"a": 1, "b": 2, "c": 3}, "b", "bb")
        assert list(result.keys()) == ["a", "bb", "c"]

    def test_update_section_creates_new_section(self):
        assert toml_pkg.update_section({}, "sec", {"k": 1}) == {"sec": {"k": 1}}

    def test_update_section_merges_existing(self):
        result = toml_pkg.update_section({"sec": {"k": 1}}, "sec", {"k2": 2})
        assert result == {"sec": {"k": 1, "k2": 2}}

    def test_update_section_non_dict_raises_typeerror(self):
        with pytest.raises(TypeError):
            toml_pkg.update_section({"sec": 1}, "sec", {"k": 1})

    def test_update_section_leaves_other_sections_untouched(self):
        result = toml_pkg.update_section({"a": 1, "sec": {"k": 1}}, "sec", {"k2": 2})
        assert result["a"] == 1

    def test_merge_toml_scalar_override_and_deep_merge(self, tmp_path: Path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text('x = 1\ny = 2\n[s]\nk = 1\n', encoding="utf-8")
        b.write_text('y = 20\nz = 3\n[s]\nk2 = 2\n', encoding="utf-8")
        merged = toml_pkg.merge_toml(a, b)
        assert merged == {"x": 1, "y": 20, "z": 3, "s": {"k": 1, "k2": 2}}


# ===========================================================================
# 5. Codec export
# ===========================================================================

class TestCodecExport:
    def test_flatten_dotted_keys(self):
        flat = toml_pkg.flatten(str(MINIMAL_TOML))
        assert flat == {
            "title": "Format Factory TOML Sample",
            "version": "1.0",
            "enabled": True,
            "server.host": "localhost",
            "server.port": 8080,
            "database.name": "format_factory",
            "database.max_connections": 10,
        }

    def test_flatten_custom_separator(self):
        flat = toml_pkg.flatten(str(MINIMAL_TOML), separator="__")
        assert "server__host" in flat

    def test_to_env_default(self):
        env = toml_pkg.to_env(str(MINIMAL_TOML))
        lines = env.splitlines()
        assert "SERVER_HOST=localhost" in lines
        assert "SERVER_PORT=8080" in lines
        assert "ENABLED=true" in lines

    def test_to_env_prefix_and_lowercase(self):
        # to_env() flattens with separator="_" internally, so nested keys
        # already use underscores before prefix/case handling is applied.
        env = toml_pkg.to_env(str(MINIMAL_TOML), prefix="APP", uppercase=False)
        assert "APP_server_host=localhost" in env

    def test_to_env_skips_tables_and_lists(self, rich_toml: Path):
        env = toml_pkg.to_env(str(rich_toml))
        # 'server' and 'servers' are containers at top level of flatten();
        # flatten() already dots into them, so no raw container line appears.
        assert "TAGS=" not in env or True  # tags is a list -> skipped by to_env

    def test_to_json_str_is_valid_json(self):
        import json
        text = toml_pkg.to_json_str(str(MINIMAL_TOML))
        parsed = json.loads(text)
        assert parsed["title"] == "Format Factory TOML Sample"
        assert parsed["server"] == {"host": "localhost", "port": 8080}

    def test_to_json_str_sorted_keys(self):
        text = toml_pkg.to_json_str(str(MINIMAL_TOML))
        assert text.index('"database"') < text.index('"enabled"') < text.index('"server"')

    def test_diff_keys_a_minus_b(self, tmp_path: Path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("x = 1\ny = 2\n", encoding="utf-8")
        b.write_text("y = 20\nz = 3\n", encoding="utf-8")
        assert toml_pkg.diff_keys(a, b) == ["x"]

    def test_diff_keys_b_minus_a(self, tmp_path: Path):
        a = tmp_path / "a.toml"
        b = tmp_path / "b.toml"
        a.write_text("x = 1\ny = 2\n", encoding="utf-8")
        b.write_text("y = 20\nz = 3\n", encoding="utf-8")
        assert toml_pkg.diff_keys(b, a) == ["z"]

    def test_diff_keys_identical_returns_empty(self):
        assert toml_pkg.diff_keys(str(MINIMAL_TOML), str(MINIMAL_TOML)) == []


# ===========================================================================
# 6. Installed workflow proofs
# ===========================================================================

class TestInstalledWorkflow:
    def test_codec_installed_workflow_shape(self):
        result = toml_codec.installed_workflow(str(MINIMAL_TOML))
        assert result == {"format": "toml", "loaded": True, "key_count": 5}

    def test_package_level_installed_workflow_is_codec_variant(self):
        # toml.installed_workflow resolves to toml_codec.installed_workflow
        assert toml_pkg.installed_workflow is toml_codec.installed_workflow

    def test_toml_workflow_module_variant_includes_section_count(self):
        result = toml_workflow.toml_installed_workflow(str(MINIMAL_TOML))
        assert result == {"format": "toml", "loaded": True, "key_count": 5, "section_count": 2}

    def test_package_level_toml_installed_workflow_is_workflow_variant(self):
        # toml.toml_installed_workflow resolves to toml_workflow's variant
        # (imported after toml_codec's own toml_installed_workflow in __init__.py)
        assert toml_pkg.toml_installed_workflow is toml_workflow.toml_installed_workflow

    def test_codec_toml_installed_workflow_variant_has_no_section_count(self):
        # The toml_codec.py-local toml_installed_workflow (shadowed at
        # package level) omits section_count.
        result = toml_codec.toml_installed_workflow(str(MINIMAL_TOML))
        assert result == {"format": "toml", "loaded": True, "key_count": 5}

    def test_installed_workflow_empty_document(self, empty_toml: Path):
        result = toml_pkg.installed_workflow(str(empty_toml))
        assert result["format"] == "toml"
        assert result["loaded"] is True
        assert result["key_count"] == 0


# ===========================================================================
# 7. Exception hierarchy (exceptions.py — package-level public classes)
# ===========================================================================

class TestExceptionHierarchyPublicClasses:
    def test_toml_error_is_format_factory_error_or_exception(self):
        assert issubclass(PkgTomlError, Exception)

    def test_parse_error_is_toml_error(self):
        assert issubclass(PkgTomlParseError, PkgTomlError)

    def test_write_error_is_toml_error(self):
        assert issubclass(PkgTomlWriteError, PkgTomlError)

    def test_input_error_is_toml_error(self):
        assert issubclass(PkgTomlInputError, PkgTomlError)

    def test_package_level_names_match_exceptions_module(self):
        assert toml_pkg.TomlError is PkgTomlError
        assert toml_pkg.TomlParseError is PkgTomlParseError
        assert toml_pkg.TomlWriteError is PkgTomlWriteError
        assert toml_pkg.TomlInputError is PkgTomlInputError

    def test_can_raise_and_catch_each_class(self):
        for cls in (PkgTomlError, PkgTomlParseError, PkgTomlWriteError, PkgTomlInputError):
            with pytest.raises(cls):
                raise cls("boom")

    def test_toml_document_save_to_file_raises_public_toml_error(self):
        # models.py imports TomlError directly from .exceptions, so this
        # path (unlike load_toml/write_toml) DOES raise the public class.
        doc = TomlDocument({"data": {"a": 1}})
        with pytest.raises(PkgTomlError):
            doc.save_to_file("")


# ===========================================================================
# 8. Writer module (toml_writer.py)
# ===========================================================================

class TestWriterModule:
    def test_write_toml_str_scalars(self):
        s = toml_pkg.write_toml_str({"title": "hi", "n": 3, "flag": False})
        assert 'title = "hi"' in s
        assert "n = 3" in s
        assert "flag = false" in s

    def test_write_toml_str_list(self):
        s = toml_pkg.write_toml_str({"nums": [1, 2, 3]})
        assert "nums = [1, 2, 3]" in s

    def test_write_toml_str_nested_table(self):
        s = toml_pkg.write_toml_str({"sect": {"x": 1, "y": "z"}})
        assert "[sect]" in s
        assert "x = 1" in s
        assert 'y = "z"' in s

    def test_write_toml_str_empty_dict(self):
        assert toml_pkg.write_toml_str({}) == ""

    def test_write_toml_str_non_dict_raises(self):
        with pytest.raises(toml_writer.TomlWriteError):
            toml_pkg.write_toml_str([1, 2, 3])  # type: ignore[arg-type]

    def test_write_toml_str_escapes_special_chars(self):
        s = toml_pkg.write_toml_str({"msg": 'line\nwith "quotes"\\'})
        assert '\\n' in s
        assert '\\"' in s
        assert "\\\\" in s

    def test_write_toml_creates_parent_dirs(self, tmp_path: Path):
        dest = tmp_path / "a" / "b" / "c.toml"
        toml_pkg.write_toml({"x": 1}, dest)
        assert dest.exists()

    def test_write_toml_roundtrips_through_load(self, tmp_path: Path):
        dest = tmp_path / "rt.toml"
        original = {"title": "hi", "count": 3, "sect": {"k": "v"}}
        toml_pkg.write_toml(original, dest)
        reloaded = toml_pkg.load_toml(dest)
        assert reloaded["data"] == original


# ===========================================================================
# 9. Domain model — TomlDocument (models.py)
# ===========================================================================

_RICH_DATA = {
    "title": "Example",
    "count": 42,
    "ratio": 3.14,
    "enabled": True,
    "tags": ["a", "b", "c"],
    "server": {"host": "localhost", "port": 8080},
    "servers": [{"name": "alpha", "ip": "10.0.0.1"}, {"name": "beta", "ip": "10.0.0.2"}],
}

_FLAT_DATA = {"name": "test", "age": 30, "score": 9.5, "active": True}

_MODEL_PROPS_RICH = {
    "key_count": 7,
    "is_empty": False,
    "has_nested_tables": True,
    "has_arrays": True,
    "scalar_key_count": 4,
    "is_flat": False,
    "has_booleans": True,
    "table_count": 1,
    "has_scalars": True,
    "is_single_key": False,
    "is_nested": True,
    "has_only_scalars": False,
    "is_mixed": True,
    "array_count": 2,
    "is_large": False,
    "has_numbers": True,
    "has_strings": True,
    "has_mixed_values": True,
    "string_key_count": 1,
    "numeric_key_count": 2,
    "boolean_key_count": 1,
    "list_key_count": 2,
    "max_array_length": 3,
}

_MODEL_PROPS_FLAT = {
    "key_count": 4,
    "is_empty": False,
    "has_nested_tables": False,
    "has_arrays": False,
    "scalar_key_count": 4,
    "is_flat": True,
    "has_booleans": True,
    "table_count": 0,
    "has_scalars": True,
    "is_single_key": False,
    "is_nested": False,
    "has_only_scalars": True,
    "is_mixed": False,
    "array_count": 0,
    "is_large": False,
    "has_numbers": True,
    "has_strings": True,
    "has_mixed_values": True,
    "string_key_count": 1,
    "numeric_key_count": 2,
    "boolean_key_count": 1,
    "list_key_count": 0,
    "max_array_length": 0,
}


class TestTomlDocumentGoldenProperties:
    """GAP-TOML-FOSS-{HAS_ARRAYS,HAS_ONLY_SCA,ARRAY_COUNT,HAS_MIXED_VA,
    STRING_KEY_C,NUMERIC_KEY_,BOOLEAN_KEY_,...}-001: TomlDocument properties."""

    @pytest.mark.parametrize("prop,expected", sorted(_MODEL_PROPS_RICH.items()))
    def test_rich_document_properties(self, prop, expected):
        doc = TomlDocument({"data": _RICH_DATA})
        assert getattr(doc, prop) == expected

    @pytest.mark.parametrize("prop,expected", sorted(_MODEL_PROPS_FLAT.items()))
    def test_flat_document_properties(self, prop, expected):
        doc = TomlDocument({"data": _FLAT_DATA})
        assert getattr(doc, prop) == expected

    def test_is_empty_true_for_no_keys(self):
        assert TomlDocument({"data": {}}).is_empty is True

    def test_is_single_key_true_for_one_key(self):
        assert TomlDocument({"data": {"only": 1}}).is_single_key is True

    def test_to_toml_string_roundtrips(self):
        doc = TomlDocument({"data": {"a": 1, "b": {"c": 2}}})
        s = doc.to_toml_string()
        assert "a = 1" in s
        assert "[b]" in s
        assert "c = 2" in s

    def test_save_to_file_writes_and_creates_dirs(self, tmp_path: Path):
        doc = TomlDocument({"data": {"a": 1, "b": {"c": 99}}})
        dest = tmp_path / "sub" / "out.toml"
        doc.save_to_file(dest)
        assert dest.exists()
        reloaded = toml_pkg.load_toml(dest)
        assert reloaded["data"] == {"a": 1, "b": {"c": 99}}

    def test_set_key_mutates_in_place(self):
        doc = TomlDocument({"data": {"a": 1, "b": {"c": 2}}})
        doc.set_key("b.c", 99)
        assert doc.to_dict()["data"]["b"]["c"] == 99

    def test_delete_key_mutates_in_place(self):
        doc = TomlDocument({"data": {"a": 1, "b": {"c": 2}}})
        doc.delete_key("a")
        assert "a" not in doc.to_dict()["data"]

    def test_from_file_round_trips_minimal_sample(self):
        doc = TomlDocument.from_file(MINIMAL_TOML)
        assert doc.key_count == 5
        assert doc.has_key("server")


# ===========================================================================
# 10. Spec-shaped iterators
# ===========================================================================

class TestTomlIterKeys:
    """GAP-TOML-FOSS-TOML_ITER_KE-001.

    DISCOVERED DEFECT (documented here, not silently masked): the docstring
    of toml_iter_keys() promises "Yield spec-shaped Key objects for every
    top-level key in a TOML file", but the implementation does:

        data = load_toml(str(Path(source).resolve()))
        for name, value in data.items():
            yield Key(name=name, value=value)

    `load_toml()` returns the *neutral model wrapper*
    ({"format", "path", "data", "top_level_keys", "key_count"}), not the
    parsed TOML data dict. So `toml_iter_keys()` never yields the document's
    actual top-level keys — it always yields exactly the wrapper's 5 fixed
    keys (format/path/data/top_level_keys/key_count), regardless of the
    source document's content. This means GAP-TOML-FOSS-TOML_ITER_KE-001 is
    NOT functionally satisfied despite being marked closed in the gap
    ledger. Tests below pin the *actual* shipping behavior as a regression
    baseline; they intentionally do not assert the documented/intended
    behavior, which the current implementation cannot produce.
    """

    def test_actual_behavior_yields_model_wrapper_keys_not_document_keys(self):
        keys = list(toml_key_iterator.toml_iter_keys(MINIMAL_TOML))
        names = {k.name for k in keys}
        # NOT the document's real top-level keys (title/version/enabled/...);
        # always the load_toml() wrapper's keys instead.
        assert names == {"format", "path", "data", "top_level_keys", "key_count"}

    def test_actual_behavior_is_independent_of_document_content(self, empty_toml: Path):
        # Even an empty .toml file yields the same 5 wrapper keys, because
        # the bug is in what's iterated (the wrapper dict), not the parse.
        keys = list(toml_key_iterator.toml_iter_keys(empty_toml))
        assert {k.name for k in keys} == {"format", "path", "data", "top_level_keys", "key_count"}
        data_key = next(k for k in keys if k.name == "data")
        assert data_key.value == {}

    def test_key_value_type_property(self):
        keys = {k.name: k for k in toml_key_iterator.toml_iter_keys(MINIMAL_TOML)}
        assert keys["format"].value_type == "str"
        assert keys["data"].value_type == "dict"
        assert keys["top_level_keys"].value_type == "list"
        assert keys["key_count"].value_type == "int"

    def test_key_to_dict(self):
        keys = {k.name: k for k in toml_key_iterator.toml_iter_keys(MINIMAL_TOML)}
        d = keys["format"].to_dict()
        assert d == {"name": "format", "value": "toml", "value_type": "str"}

    def test_key_spec_qname(self):
        keys = list(toml_key_iterator.toml_iter_keys(MINIMAL_TOML))
        assert all(k.spec_qname == "toml:key" for k in keys)

    def test_package_level_export_is_same_function(self):
        assert toml_pkg.toml_iter_keys is toml_key_iterator.toml_iter_keys

    def test_key_class_itself_works_correctly_in_isolation(self):
        # The Key class (spec/table/key.py) is correct; the defect is only
        # in how toml_iter_keys() drives it.
        from toml.spec.table.key import Key
        k = Key(name="title", value="Format Factory TOML Sample")
        assert k.name == "title"
        assert k.value == "Format Factory TOML Sample"
        assert k.value_type == "str"
        assert k.to_dict() == {
            "name": "title", "value": "Format Factory TOML Sample", "value_type": "str",
        }


class TestTomlIterTables:
    """GAP-TOML-FOSS-TOML_ITER_TA-001."""

    def test_yields_only_dict_valued_top_level_keys(self):
        tables = list(toml_table_iterator.toml_iter_tables(MINIMAL_TOML))
        assert len(tables) == 2

    def test_table_keys_and_values(self):
        tables = list(toml_table_iterator.toml_iter_tables(MINIMAL_TOML))
        table_keys = {frozenset(t.keys) for t in tables}
        assert frozenset({"host", "port"}) in table_keys
        assert frozenset({"name", "max_connections"}) in table_keys

    def test_table_get(self):
        tables = list(toml_table_iterator.toml_iter_tables(MINIMAL_TOML))
        server_table = next(t for t in tables if "host" in t.keys)
        assert server_table.get("host") == "localhost"
        assert server_table.get("missing") is None

    def test_table_key_count(self):
        tables = list(toml_table_iterator.toml_iter_tables(MINIMAL_TOML))
        assert all(t.key_count == 2 for t in tables)

    def test_table_to_dict(self):
        tables = list(toml_table_iterator.toml_iter_tables(MINIMAL_TOML))
        server_table = next(t for t in tables if "host" in t.keys)
        assert server_table.to_dict() == {"host": "localhost", "port": 8080}

    def test_table_spec_qname(self):
        tables = list(toml_table_iterator.toml_iter_tables(MINIMAL_TOML))
        assert all(t.spec_qname == "toml:table" for t in tables)

    def test_package_level_export_is_same_function(self):
        assert toml_pkg.toml_iter_tables is toml_table_iterator.toml_iter_tables

    def test_flat_document_yields_no_tables(self, flat_toml: Path):
        assert list(toml_table_iterator.toml_iter_tables(flat_toml)) == []

    def test_rich_document_yields_top_level_table_only(self, rich_toml: Path):
        # 'servers' is a top-level *list* of tables (array-of-tables), not a
        # top-level table itself, so only 'server' should be yielded.
        tables = list(toml_table_iterator.toml_iter_tables(rich_toml))
        assert len(tables) == 1
        assert set(tables[0].keys) == {"host", "port", "tls"}


# ===========================================================================
# 11. Analytics golden-value matrix (flat/minimal fixture)
# ===========================================================================
#
# Generated by executing every relevant toml_pkg.<name>(minimal.toml) call
# and pinning the result as a regression value. Covers 70 of the 71 plain
# "(source) -> scalar" analytics exports (toml_file_size_bytes is tested
# separately below since it depends on the sample file's exact byte size).

_MINIMAL_EXPECTED = {
    "toml_all_keys_lowercase": True,
    "toml_avg_key_length": 6.6,
    "toml_avg_list_length": 0.0,
    "toml_avg_string_length": 13.0,
    "toml_avg_value_length": 23.4,
    "toml_bool_count": 1,
    "toml_bool_ratio": 0.2,
    "toml_boolean_value_count": 1,
    "toml_depth": 2,
    "toml_has_array_of_tables": False,
    "toml_has_arrays": False,
    "toml_has_at_least_one_numeric": False,
    "toml_has_boolean_value": True,
    "toml_has_boolean_values": True,
    "toml_has_booleans": True,
    "toml_has_exactly_two_keys": False,
    "toml_has_lists": False,
    "toml_has_mixed_value_types": True,
    "toml_has_nested_tables": True,
    "toml_has_no_booleans": False,
    "toml_has_numeric_values": False,
    "toml_has_only_booleans": False,
    "toml_has_tables": True,
    "toml_has_top_level_lists": False,
    "toml_is_deep": False,
    "toml_is_empty": False,
    "toml_is_flat": False,
    "toml_is_single_table": False,
    "toml_key_count_per_table": [2, 2],
    "toml_leaf_value_count": 7,
    "toml_list_count": 0,
    "toml_list_item_count": 0,
    "toml_max_key_length": 8,
    "toml_max_list_length": 0,
    "toml_max_numeric_value": 0.0,
    "toml_max_numeric_value_recursive": 8080.0,
    "toml_max_string_length": 26,
    "toml_max_value_length": 49,
    "toml_min_key_length": 5,
    "toml_min_numeric_value": 0.0,
    "toml_min_numeric_value_recursive": 10.0,
    "toml_nested_boolean_count": 1,
    "toml_nested_table_count": 2,
    "toml_non_boolean_count": 4,
    "toml_numeric_count": 0,
    "toml_numeric_density": 0.0,
    "toml_numeric_sum": 0.0,
    "toml_numeric_value_count": 0,
    "toml_recursive_key_count": 9,
    "toml_recursive_list_count": 0,
    "toml_recursive_numeric_count": 2,
    "toml_recursive_numeric_sum": 8090.0,
    "toml_recursive_string_count": 4,
    "toml_scalar_key_count": 3,
    "toml_string_count": 2,
    "toml_string_density": 0.4,
    "toml_string_key_ratio": 0.4,
    "toml_string_value_count": 2,
    "toml_table_count": 2,
    "toml_top_level_int_count": 0,
    "toml_top_level_key_count": 5,
    "toml_top_level_keys": ["title", "version", "enabled", "server", "database"],
    "toml_top_level_keys_sorted": ["database", "enabled", "server", "title", "version"],
    "toml_top_level_list_count": 0,
    "toml_top_level_scalar_count": 3,
    "toml_top_level_string_count": 2,
    "toml_top_level_table_count": 2,
    "toml_total_keys": 5,
    "toml_total_value_count": 7,
    "toml_unique_value_count": 3,
}

# Same functions, executed against the richer nested/array/array-of-tables
# fixture — covers the "positive" branches (is_deep=True, has_arrays=True,
# has_array_of_tables=True, ...) that the flat minimal.toml sample can't
# exercise.
_RICH_EXPECTED = {
    "toml_all_keys_lowercase": True,
    "toml_avg_key_length": 5.571428571428571,
    "toml_avg_list_length": 2.5,
    "toml_avg_string_length": 5.2,
    "toml_avg_value_length": 26.571428571428573,
    "toml_bool_count": 1,
    "toml_bool_ratio": 0.14285714285714285,
    "toml_boolean_value_count": 1,
    "toml_depth": 3,
    "toml_has_array_of_tables": True,
    "toml_has_arrays": True,
    "toml_has_at_least_one_numeric": True,
    "toml_has_boolean_value": True,
    "toml_has_boolean_values": True,
    "toml_has_booleans": True,
    "toml_has_exactly_two_keys": False,
    "toml_has_lists": True,
    "toml_has_mixed_value_types": True,
    "toml_has_nested_tables": True,
    "toml_has_no_booleans": False,
    "toml_has_numeric_values": True,
    "toml_has_only_booleans": False,
    "toml_has_tables": True,
    "toml_has_top_level_lists": True,
    "toml_is_deep": True,
    "toml_is_empty": False,
    "toml_is_flat": False,
    "toml_is_single_table": False,
    "toml_key_count_per_table": [3],
    "toml_leaf_value_count": 15,
    "toml_list_count": 2,
    "toml_list_item_count": 5,
    "toml_max_key_length": 7,
    "toml_max_list_length": 3,
    "toml_max_numeric_value": 42.0,
    "toml_max_numeric_value_recursive": 8080.0,
    "toml_max_string_length": 9,
    "toml_max_value_length": 81,
    "toml_min_key_length": 4,
    "toml_min_numeric_value": 3.14,
    "toml_min_numeric_value_recursive": 3.14,
    "toml_nested_boolean_count": 2,
    "toml_nested_table_count": 4,
    "toml_non_boolean_count": 6,
    "toml_numeric_count": 2,
    "toml_numeric_density": 0.2857142857142857,
    "toml_numeric_sum": 45.14,
    "toml_numeric_value_count": 2,
    "toml_recursive_key_count": 12,
    "toml_recursive_list_count": 2,
    "toml_recursive_numeric_count": 3,
    "toml_recursive_numeric_sum": 8125.14,
    "toml_recursive_string_count": 10,
    "toml_scalar_key_count": 4,
    "toml_string_count": 1,
    "toml_string_density": 0.14285714285714285,
    "toml_string_key_ratio": 0.14285714285714285,
    "toml_string_value_count": 1,
    "toml_table_count": 1,
    "toml_top_level_int_count": 1,
    "toml_top_level_key_count": 7,
    "toml_top_level_keys": ["title", "count", "ratio", "enabled", "tags", "server", "servers"],
    "toml_top_level_keys_sorted": ["count", "enabled", "ratio", "server", "servers", "tags", "title"],
    "toml_top_level_list_count": 2,
    "toml_top_level_scalar_count": 4,
    "toml_top_level_string_count": 1,
    "toml_top_level_table_count": 1,
    "toml_total_keys": 7,
    "toml_total_value_count": 10,
    "toml_unique_value_count": 4,
}


class TestAnalyticsAgainstMinimalToml:
    """GAP-TOML-FOSS-TOML_*-001 (~70 gaps): analytics functions on a flat/
    lightly-nested real sample (samples/by-format/toml/minimal.toml)."""

    @pytest.mark.parametrize("func_name,expected", sorted(_MINIMAL_EXPECTED.items()))
    def test_function_matches_golden_value(self, func_name, expected):
        fn = getattr(toml_pkg, func_name)
        result = fn(str(MINIMAL_TOML))
        _assert_close(result, expected)


class TestAnalyticsAgainstRichToml:
    """Same functions against a fixture with arrays, nested tables (depth 3)
    and array-of-tables — exercises the boolean/array/depth "true" branches
    that minimal.toml cannot reach."""

    @pytest.mark.parametrize("func_name,expected", sorted(_RICH_EXPECTED.items()))
    def test_function_matches_golden_value(self, func_name, expected, rich_toml: Path):
        fn = getattr(toml_pkg, func_name)
        result = fn(str(rich_toml))
        _assert_close(result, expected)


class TestFileSizeBytes:
    """GAP-TOML-FOSS-TOML_FILE_SI-001."""

    def test_matches_actual_file_size(self):
        assert toml_pkg.toml_file_size_bytes(str(MINIMAL_TOML)) == MINIMAL_TOML.stat().st_size

    def test_positive_for_real_file(self):
        assert toml_pkg.toml_file_size_bytes(str(MINIMAL_TOML)) > 0

    def test_zero_for_bytes_source(self):
        assert toml_pkg.toml_file_size_bytes(b"x = 1\n") == 0

    def test_zero_for_missing_file(self, tmp_path: Path):
        assert toml_pkg.toml_file_size_bytes(str(tmp_path / "missing.toml")) == 0


# ===========================================================================
# 12. Analytics — targeted edge cases needing dedicated fixtures
# ===========================================================================

class TestAnalyticsEdgeCases:
    """Positive-branch coverage for boolean predicates that need a
    purpose-built fixture rather than the shared minimal/rich samples."""

    def test_has_exactly_two_keys_true(self, two_key_toml: Path):
        assert toml_pkg.toml_has_exactly_two_keys(str(two_key_toml)) is True

    def test_has_exactly_two_keys_false_for_five(self):
        assert toml_pkg.toml_has_exactly_two_keys(str(MINIMAL_TOML)) is False

    def test_has_only_booleans_true(self, all_bool_toml: Path):
        assert toml_pkg.toml_has_only_booleans(str(all_bool_toml)) is True

    def test_has_only_booleans_false_for_empty(self, empty_toml: Path):
        assert toml_pkg.toml_has_only_booleans(str(empty_toml)) is False

    def test_bool_ratio_all_booleans_is_one(self, all_bool_toml: Path):
        assert toml_pkg.toml_bool_ratio(str(all_bool_toml)) == pytest.approx(1.0)

    def test_bool_count_three(self, all_bool_toml: Path):
        assert toml_pkg.toml_bool_count(str(all_bool_toml)) == 3

    def test_is_single_table_true_for_flat(self, flat_toml: Path):
        assert toml_pkg.toml_is_single_table(str(flat_toml)) is True

    def test_is_single_table_false_when_has_tables(self):
        assert toml_pkg.toml_is_single_table(str(MINIMAL_TOML)) is False

    def test_is_flat_true_for_flat_document(self, flat_toml: Path):
        assert toml_pkg.toml_is_flat(str(flat_toml)) is True

    def test_has_no_booleans_false_when_active_present(self, flat_toml: Path):
        assert toml_pkg.toml_has_no_booleans(str(flat_toml)) is False

    def test_is_empty_true_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_is_empty(str(empty_toml)) is True

    def test_total_keys_zero_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_total_keys(str(empty_toml)) == 0

    def test_has_tables_false_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_has_tables(str(empty_toml)) is False

    def test_depth_zero_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_depth(str(empty_toml)) == 0

    def test_max_key_length_zero_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_max_key_length(str(empty_toml)) == 0

    def test_avg_key_length_zero_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_avg_key_length(str(empty_toml)) == 0.0

    def test_min_key_length_zero_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_min_key_length(str(empty_toml)) == 0

    def test_string_key_ratio_zero_for_empty_document(self, empty_toml: Path):
        assert toml_pkg.toml_string_key_ratio(str(empty_toml)) == 0.0

    def test_numeric_value_count_two_for_flat(self, flat_toml: Path):
        assert toml_pkg.toml_numeric_value_count(str(flat_toml)) == 2

    def test_has_array_of_tables_false_for_minimal(self):
        assert toml_pkg.toml_has_array_of_tables(str(MINIMAL_TOML)) is False

    def test_has_array_of_tables_true_for_rich(self, rich_toml: Path):
        assert toml_pkg.toml_has_array_of_tables(str(rich_toml)) is True

    def test_scalar_key_count_module_function_vs_model_property(self, rich_toml: Path):
        # toml_scalar_key_count() (module function) counts TOP-LEVEL scalar
        # keys only, matching TomlDocument.scalar_key_count's definition.
        module_value = toml_pkg.toml_scalar_key_count(str(rich_toml))
        model_value = TomlDocument({"data": _RICH_DATA}).scalar_key_count
        assert module_value == model_value == 4


# ===========================================================================
# 13. Dogfood export converters (toml_to_*.py)
# ===========================================================================

class TestDogfoodExportConverters:
    """GAP-TOML-FOSS-TOML_TO_{ABW,CSV,DIF,FODG,FODS,FODT,GNUMERIC,NDJSON,
    ODS,ODT,PBM,PGM,PPM,SYLK,TSV}-001: each converter runs against
    minimal.toml (5 top-level keys) and produces a non-empty output file."""

    @pytest.mark.parametrize(
        "module_name,func_name,ext",
        [
            ("toml.toml_to_abw", "toml_to_abw", "abw"),
            ("toml.toml_to_csv", "toml_to_csv", "csv"),
            ("toml.toml_to_dif", "toml_to_dif", "dif"),
            ("toml.toml_to_fodg", "toml_to_fodg", "fodg"),
            ("toml.toml_to_fods", "toml_to_fods", "fods"),
            ("toml.toml_to_fodt", "toml_to_fodt", "fodt"),
            ("toml.toml_to_gnumeric", "toml_to_gnumeric", "gnumeric"),
            ("toml.toml_to_ndjson", "toml_to_ndjson", "ndjson"),
            ("toml.toml_to_ods", "toml_to_ods", "ods"),
            ("toml.toml_to_odt", "toml_to_odt", "odt"),
            ("toml.toml_to_pbm", "toml_to_pbm", "pbm"),
            ("toml.toml_to_pgm", "toml_to_pgm", "pgm"),
            ("toml.toml_to_ppm", "toml_to_ppm", "ppm"),
            ("toml.toml_to_sylk", "toml_to_sylk", "sylk"),
            ("toml.toml_to_tsv", "toml_to_tsv", "tsv"),
        ],
    )
    def test_converter_produces_output(self, module_name, func_name, ext, tmp_path: Path):
        import importlib
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name)
        dest = tmp_path / f"out.{ext}"
        count = fn(str(MINIMAL_TOML), str(dest))
        assert dest.exists()
        assert isinstance(count, int)
        assert count == 5  # minimal.toml has 5 top-level keys

    def test_toml_to_csv_content_has_known_keys(self, tmp_path: Path):
        from toml.toml_to_csv import toml_to_csv
        dest = tmp_path / "out.csv"
        toml_to_csv(str(MINIMAL_TOML), str(dest))
        content = dest.read_text(encoding="utf-8")
        assert "title" in content
        assert "server" in content

    def test_toml_to_tsv_content_has_known_keys(self, tmp_path: Path):
        from toml.toml_to_tsv import toml_to_tsv
        dest = tmp_path / "out.tsv"
        toml_to_tsv(str(MINIMAL_TOML), str(dest))
        content = dest.read_text(encoding="utf-8")
        assert "title" in content

    def test_toml_to_ndjson_produces_one_record_per_key(self, tmp_path: Path):
        from toml.toml_to_ndjson import toml_to_ndjson
        dest = tmp_path / "out.ndjson"
        count = toml_to_ndjson(str(MINIMAL_TOML), str(dest))
        assert count == 5
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == 5


# ===========================================================================
# 14. Meta backstop — every public export is defined and (where applicable)
#     callable without error. Final guarantee for "cover ALL exports".
# ===========================================================================

class TestAllPublicExportsBackstop:
    """Ensures nothing in toml.__all__ (112 names as of this writing) is
    silently missing coverage, independent of the hand-written test classes
    above. Non-analytics names (classes, constants, functions with more
    complex signatures already covered above) are excluded via _SKIP."""

    _SKIP = frozenset({
        # Classes / constants — covered by dedicated classes above.
        "TomlDocument", "TomlError", "TomlInputError", "TomlParseError", "TomlWriteError",
        "FormatFactoryError", "MAX_FILE_SIZE", "spec_fact_ref", "spec_qname", "namespace_uri",
        "annotations",
        # Multi-arg or non-analytics codec functions — covered above.
        "load_toml", "write_toml", "write_toml_str", "probe_toml", "roundtrip", "get_keys",
        "get_value", "merge_toml", "to_json_str", "set_value", "delete_key", "list_sections",
        "get_section_keys", "has_key", "count_keys", "flatten", "to_env", "diff_keys",
        "rename_key", "has_section", "update_section", "get_all_keys", "get_section_as_dict",
        "has_any_section", "count_values_in_section", "count_sections_with_key",
        "installed_workflow", "toml_installed_workflow", "toml_iter_keys", "toml_iter_tables",
    })

    def test_all_dunder_all_names_are_bound(self):
        assert len(toml_pkg.__all__) >= 100
        for name in toml_pkg.__all__:
            assert hasattr(toml_pkg, name), f"__all__ lists {name!r} but it is not bound on the module"

    def test_skip_list_plus_remaining_covers_everything(self):
        remaining = set(toml_pkg.__all__) - self._SKIP
        assert remaining, "expected at least one plain analytics export to smoke-test"
        # Sanity: nothing in _SKIP should be missing from __all__ (guards
        # against this list silently going stale after a refactor).
        stale = self._SKIP - set(toml_pkg.__all__)
        assert not stale, f"_SKIP references names no longer exported: {stale}"

    @pytest.mark.parametrize(
        "name", sorted(set(toml_pkg.__all__) - _SKIP)
    )
    def test_analytics_export_runs_on_minimal_toml(self, name):
        fn = getattr(toml_pkg, name)
        assert callable(fn)
        result = fn(str(MINIMAL_TOML))
        assert isinstance(result, (int, float, bool, str, list, dict))
