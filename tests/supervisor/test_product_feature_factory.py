"""Tests for product_feature_factory.py.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.product_feature_factory import FeatureFactory, FeatureFactoryError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_CODEC = """\
\"\"\"Minimal test codec.\"\"\"
from __future__ import annotations


def load(source) -> dict:
    return {"rows": [], "headers": []}


def write(model, dest) -> None:
    pass
"""


def make_codec(tmp_path: Path, name: str = "test_codec.py") -> tuple[Path, str]:
    """Create a minimal codec in a temporary directory tree."""
    src_dir = tmp_path / "src" / "python" / "testfmt"
    src_dir.mkdir(parents=True)
    src_file = src_dir / name
    src_file.write_text(MINIMAL_CODEC, encoding="utf-8")
    rel_path = f"src/python/testfmt/{name}"
    return src_file, rel_path


# ---------------------------------------------------------------------------
# _source_to_import helper
# ---------------------------------------------------------------------------

class TestSourceToImport:
    def test_standard_path(self):
        factory = FeatureFactory()
        result = factory._source_to_import("src/python/abw/abw_codec.py")
        assert result == "abw.abw_codec"

    def test_gnumeric_path(self):
        factory = FeatureFactory()
        result = factory._source_to_import("src/python/gnumeric/gnumeric_codec.py")
        assert result == "gnumeric.gnumeric_codec"

    def test_tsv_path(self):
        factory = FeatureFactory()
        result = factory._source_to_import("src/python/tsv/tsv_parser.py")
        assert result == "tsv.tsv_parser"


# ---------------------------------------------------------------------------
# _find_insertion_point
# ---------------------------------------------------------------------------

class TestFindInsertionPoint:
    def test_insert_before_function(self):
        factory = FeatureFactory()
        content = "def load(source):\n    pass\n\ndef write(model, dest):\n    pass\n"
        idx = factory._find_insertion_point(content, insert_before="write")
        assert content[idx:].startswith("def write")

    def test_insert_at_end_when_no_anchor(self):
        factory = FeatureFactory()
        content = "def load(source):\n    pass\n"
        idx = factory._find_insertion_point(content, insert_before=None)
        assert idx == len(content)

    def test_insert_at_end_when_anchor_not_found(self):
        factory = FeatureFactory()
        content = "def load(source):\n    pass\n"
        idx = factory._find_insertion_point(content, insert_before="nonexistent")
        assert idx == len(content)


# ---------------------------------------------------------------------------
# Pattern A: apply_getter
# ---------------------------------------------------------------------------

class TestApplyGetter:
    def test_function_inserted(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        abs_file, rel_path = make_codec(tmp_path)
        factory.apply_getter(
            source_path=rel_path,
            function_name="get_row_count",
            return_type="int",
            docstring="Return number of rows.",
            body_lines=["    return len(model.get('rows', []))"],
        )
        content = abs_file.read_text(encoding="utf-8")
        assert "def get_row_count" in content
        assert "Return number of rows" in content

    def test_returns_test_skeleton_string(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_getter(
            source_path=rel_path,
            function_name="get_row_count",
            return_type="int",
            docstring="Return number of rows.",
            body_lines=["    return len(model.get('rows', []))"],
        )
        assert isinstance(skeleton, str)
        assert "get_row_count" in skeleton

    def test_test_skeleton_is_valid_python(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_getter(
            source_path=rel_path,
            function_name="get_row_count",
            return_type="int",
            docstring="Return number of rows.",
            body_lines=["    return len(model.get('rows', []))"],
        )
        # Should compile without errors
        compile(skeleton, "<test_skeleton>", "exec")

    def test_insert_before_anchor(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        abs_file, rel_path = make_codec(tmp_path)
        factory.apply_getter(
            source_path=rel_path,
            function_name="get_header_count",
            return_type="int",
            docstring="Return header count.",
            body_lines=["    return len(model.get('headers', []))"],
            insert_before="write",
        )
        content = abs_file.read_text(encoding="utf-8")
        get_pos = content.index("def get_header_count")
        write_pos = content.index("def write")
        assert get_pos < write_pos

    def test_source_not_found_raises(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        with pytest.raises(FeatureFactoryError):
            factory.apply_getter(
                source_path="src/python/nonexistent/codec.py",
                function_name="foo",
                return_type="int",
                docstring=".",
                body_lines=["    return 0"],
            )


# ---------------------------------------------------------------------------
# Pattern B: apply_export_csv
# ---------------------------------------------------------------------------

class TestApplyExportCsv:
    def test_function_inserted(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        abs_file, rel_path = make_codec(tmp_path)
        factory.apply_export_csv(
            source_path=rel_path,
            function_name="export_to_csv",
            format_name="TestFmt",
            load_function="load",
            rows_expression="model['rows']",
            headers_expression="model['headers']",
        )
        content = abs_file.read_text(encoding="utf-8")
        assert "def export_to_csv" in content

    def test_returns_test_skeleton(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_export_csv(
            source_path=rel_path,
            function_name="export_to_csv",
            format_name="TestFmt",
            load_function="load",
            rows_expression="model['rows']",
            headers_expression="model['headers']",
        )
        assert "export_to_csv" in skeleton

    def test_skeleton_compiles(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_export_csv(
            source_path=rel_path,
            function_name="export_to_csv",
            format_name="TestFmt",
            load_function="load",
            rows_expression="model['rows']",
            headers_expression="model['headers']",
        )
        compile(skeleton, "<test_skeleton>", "exec")


# ---------------------------------------------------------------------------
# Pattern C: generate_roundtrip_test
# ---------------------------------------------------------------------------

class TestGenerateRoundtripTest:
    def test_returns_string(self):
        factory = FeatureFactory()
        result = factory.generate_roundtrip_test(
            format_name="tsv",
            source_path="src/python/tsv/tsv_parser.py",
            load_function="load_tsv",
            write_function="write_tsv",
            compare_field="headers",
        )
        assert isinstance(result, str)

    def test_contains_load_and_write(self):
        factory = FeatureFactory()
        result = factory.generate_roundtrip_test(
            format_name="tsv",
            source_path="src/python/tsv/tsv_parser.py",
            load_function="load_tsv",
            write_function="write_tsv",
            compare_field="headers",
        )
        assert "load_tsv" in result
        assert "write_tsv" in result

    def test_skeleton_compiles(self):
        factory = FeatureFactory()
        result = factory.generate_roundtrip_test(
            format_name="ndjson",
            source_path="src/python/ndjson/ndjson_codec.py",
            load_function="load_ndjson",
            write_function="write_ndjson",
            compare_field="records",
        )
        compile(result, "<roundtrip_skeleton>", "exec")

    def test_format_name_in_class_name(self):
        factory = FeatureFactory()
        result = factory.generate_roundtrip_test(
            format_name="abw",
            source_path="src/python/abw/abw_codec.py",
            load_function="load_abw",
            write_function="write_abw",
            compare_field="paragraphs",
        )
        assert "TestAbw" in result or "test_roundtrip" in result.lower()


# ---------------------------------------------------------------------------
# Pattern D: apply_append
# ---------------------------------------------------------------------------

class TestApplyAppend:
    def test_function_inserted(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        abs_file, rel_path = make_codec(tmp_path)
        factory.apply_append(
            source_path=rel_path,
            function_name="append_row",
            format_name="TestFmt",
            load_function="load",
            collection_key="rows",
        )
        content = abs_file.read_text(encoding="utf-8")
        assert "def append_row" in content
        assert "rows" in content

    def test_returns_test_skeleton(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_append(
            source_path=rel_path,
            function_name="append_row",
            format_name="TestFmt",
            load_function="load",
            collection_key="rows",
        )
        assert "append_row" in skeleton

    def test_skeleton_compiles(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_append(
            source_path=rel_path,
            function_name="append_row",
            format_name="TestFmt",
            load_function="load",
            collection_key="rows",
        )
        compile(skeleton, "<append_skeleton>", "exec")


# ---------------------------------------------------------------------------
# Pattern E: apply_probe
# ---------------------------------------------------------------------------

class TestApplyProbe:
    def test_function_inserted(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        abs_file, rel_path = make_codec(tmp_path)
        factory.apply_probe(
            source_path=rel_path,
            function_name="probe_testfmt",
            format_name="TestFmt",
            metadata_fields=[("row_count", "0"), ("valid", "True")],
        )
        content = abs_file.read_text(encoding="utf-8")
        assert "def probe_testfmt" in content

    def test_returns_test_skeleton(self, tmp_path):
        factory = FeatureFactory(repo_root=tmp_path)
        _, rel_path = make_codec(tmp_path)
        skeleton = factory.apply_probe(
            source_path=rel_path,
            function_name="probe_testfmt",
            format_name="TestFmt",
            metadata_fields=[],
        )
        assert "probe_testfmt" in skeleton


# ---------------------------------------------------------------------------
# Pattern F: generate_package_proof_command
# ---------------------------------------------------------------------------

class TestGeneratePackageProofCommand:
    def test_contains_package_name(self):
        factory = FeatureFactory()
        cmd = factory.generate_package_proof_command("zstandard")
        assert "zstandard" in cmd

    def test_returns_string(self):
        factory = FeatureFactory()
        cmd = factory.generate_package_proof_command("yaml")
        assert isinstance(cmd, str)

    def test_contains_import(self):
        factory = FeatureFactory()
        cmd = factory.generate_package_proof_command("yaml")
        assert "import yaml" in cmd
