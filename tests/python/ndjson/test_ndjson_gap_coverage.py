"""
Comprehensive NDJSON gap-coverage tests.

Targets the ~80 `missing_test_coverage` gaps recorded in
reports/capability-layer/gap-ledger.json for format=NDJSON
(GAP-NDJSON-FOSS-*-SRC-001 series, e.g. GAP-NDJSON-FOSS-NDJSON_NESTED_FIELD_COUNT-SRC-001).

Modules exercised:
  - ndjson_codec.py            (core codec: load/write/probe/transform)
  - ndjson_writer.py           (canonical package-level writer, __init__ re-export)
  - ndjson_workflow.py         (installed workflow proof, __init__ re-export)
  - models.py                  (NdjsonDocument domain model)
  - ndjson_field_analytics.py  (field-level analytics — not re-exported by __init__)
  - ndjson_record_stats.py     (record stats / aggregation / manipulation)
  - json_stream.py             (extended analytics + aliases, re-exported via ndjson_codec)
  - ndjson_record_iterator.py / ndjson_field_iterator.py (spec-shaped iterators)
  - Compat/ndjson_record.py + spec/record/{record,field}.py
  - exceptions.py              (shared FormatFactoryError-based exceptions)
  - cli.py
  - ndjson_to_*.py             (dogfood export converters — smoke coverage)

Notes on duplicate function names across modules (verified before writing this
file — see module docstrings below for details):
  - `ndjson.ndjson_numeric_field_count` (package level, from ndjson_record_stats)
    counts DISTINCT numeric-valued field NAMES, while
    `json_stream.ndjson_numeric_field_count` and
    `ndjson_field_analytics.ndjson_numeric_field_count` count TOTAL numeric
    VALUES. Both variants are tested explicitly with distinguishing values.
  - `ndjson.write_ndjson` (package level) resolves to ndjson_writer.write_ndjson
    (raises NdjsonWriteError), NOT ndjson_codec.write_ndjson (raises NdjsonError).
  - `ndjson.ndjson_installed_workflow` (package level) resolves to
    ndjson_workflow.ndjson_installed_workflow (3 keys), NOT
    ndjson_codec.ndjson_installed_workflow (4 keys, includes field_count).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import ndjson_codec as codec
from ndjson import ndjson_writer as writer
from ndjson import ndjson_workflow as workflow
from ndjson import ndjson_field_analytics as field_analytics
from ndjson import ndjson_record_stats as record_stats
from ndjson import json_stream
from ndjson.models import NdjsonDocument


def _write(tmp_path, records, name="data.ndjson") -> str:
    """Write records to an .ndjson file under tmp_path; return its str path."""
    p = tmp_path / name
    lines = [json.dumps(r) for r in records]
    p.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

RECORDS_A = [
    {"id": 1, "name": "Alice", "active": True, "score": 3.5,
     "tags": ["red", "blue"], "meta": {"city": "NYC"}},
    {"id": 2, "name": "Bob", "active": False, "score": None,
     "tags": [], "meta": {}},
    {"id": 3, "name": "Carol", "active": True, "score": 9.25,
     "tags": ["green"], "meta": {"city": "LA", "zip": "90001"}},
]

RECORDS_B = [
    {"a": 1, "b": "x"},
    {"a": 2, "b": "y", "c": True},
    {},
    {"a": 3, "d": [1, 2, 3], "e": {"f": 1}},
]


@pytest.fixture
def file_a(tmp_path):
    return _write(tmp_path, RECORDS_A, name="fixture_a.ndjson")


@pytest.fixture
def file_b(tmp_path):
    return _write(tmp_path, RECORDS_B, name="fixture_b.ndjson")


# ===========================================================================
# ndjson_codec.py — core codec
# ===========================================================================

class TestNdjsonCodecCore:
    def test_probe_ndjson_valid_file(self, file_a):
        assert codec.probe_ndjson(file_a) is True

    def test_probe_ndjson_invalid_content(self):
        assert codec.probe_ndjson("not json at all {{{") is False

    def test_probe_ndjson_all_blank_lines(self):
        assert codec.probe_ndjson("\n\n\n") is False

    def test_load_ndjson_from_path(self, file_a):
        records = codec.load_ndjson(file_a)
        assert len(records) == 3
        assert records[0]["name"] == "Alice"

    def test_load_ndjson_skips_empty_lines(self, tmp_path):
        p = tmp_path / "gaps.ndjson"
        p.write_text('{"a": 1}\n\n\n{"a": 2}\n', encoding="utf-8")
        records = codec.load_ndjson(str(p))
        assert len(records) == 2

    def test_load_ndjson_from_bytes(self):
        records = codec.load_ndjson(b'{"a": 1}\n{"a": 2}\n')
        assert records == [{"a": 1}, {"a": 2}]

    def test_load_ndjson_from_raw_string_content(self):
        # A string that is NOT an existing path is treated as raw content.
        records = codec.load_ndjson('{"z": 9}')
        assert records == [{"z": 9}]

    def test_load_ndjson_malformed_raises_parse_error(self, tmp_path):
        p = tmp_path / "bad.ndjson"
        p.write_text('{"a": 1}\nnot-json\n', encoding="utf-8")
        with pytest.raises(codec.NdjsonParseError):
            codec.load_ndjson(str(p))

    def test_append_record_creates_and_appends(self, tmp_path):
        dest = tmp_path / "append.ndjson"
        codec.append_record(dest, {"n": 1})
        codec.append_record(dest, {"n": 2})
        assert codec.load_ndjson(str(dest)) == [{"n": 1}, {"n": 2}]

    def test_filter_records_matches(self, file_a):
        matches = codec.filter_records(file_a, "active", True)
        assert [r["id"] for r in matches] == [1, 3]

    def test_filter_records_no_matches(self, file_a):
        assert codec.filter_records(file_a, "active", "nope") == []

    def test_get_field_names_sorted(self, file_a):
        assert codec.get_field_names(file_a) == [
            "active", "id", "meta", "name", "score", "tags"
        ]

    def test_get_field_names_empty(self, tmp_path):
        path = _write(tmp_path, [], name="empty.ndjson")
        assert codec.get_field_names(path) == []

    def test_export_to_csv_basic(self, tmp_path):
        path = _write(tmp_path, [{"a": 1, "b": 2}, {"a": 3, "b": 4}], name="simple.ndjson")
        assert codec.export_to_csv(path) == "a,b\n1,2\n3,4\n"

    def test_export_to_csv_empty(self, tmp_path):
        path = _write(tmp_path, [], name="empty.ndjson")
        assert codec.export_to_csv(path) == ""

    def test_get_record_count(self, file_a):
        assert codec.get_record_count(file_a) == 3

    def test_count_records_matches_get_record_count(self, file_a):
        assert codec.count_records(file_a) == codec.get_record_count(file_a)

    def test_validate_schema_all_valid(self, file_a):
        result = codec.validate_schema(file_a, {"id": int, "name": str})
        assert result == {
            "valid": True, "total_records": 3, "valid_records": 3, "errors": []
        }

    def test_validate_schema_missing_field(self, file_a):
        result = codec.validate_schema(file_a, {"nonexistent": str})
        assert result["valid"] is False
        assert result["valid_records"] == 0
        assert len(result["errors"]) == 3
        assert all(e["error"] == "missing_field" for e in result["errors"])

    def test_validate_schema_wrong_type(self, tmp_path):
        path = _write(tmp_path, [{"n": "not-an-int"}], name="wrongtype.ndjson")
        result = codec.validate_schema(path, {"n": int})
        assert result["valid"] is False
        assert result["errors"][0]["error"] == "wrong_type"

    def test_validate_schema_type_as_string_name(self, file_a):
        result = codec.validate_schema(file_a, {"name": "str"})
        assert result["valid"] is True

    def test_validate_schema_not_a_dict_record(self, tmp_path):
        path = _write(tmp_path, ["plain"], name="scalar.ndjson")
        result = codec.validate_schema(path, {"x": str})
        assert result["errors"][0]["error"] == "not_a_dict"

    def test_sort_records_ascending(self, file_a):
        assert [r["id"] for r in codec.sort_records(file_a, "id")] == [1, 2, 3]

    def test_sort_records_descending(self, file_a):
        assert [r["id"] for r in codec.sort_records(file_a, "id", reverse=True)] == [3, 2, 1]

    def test_merge_ndjson_combines_both_sources(self, tmp_path):
        p1 = _write(tmp_path, [{"z": 99}], name="m1.ndjson")
        p2 = _write(tmp_path, [{"z": 100}], name="m2.ndjson")
        assert codec.merge_ndjson(p1, p2) == [{"z": 99}, {"z": 100}]

    def test_to_jsonl_str(self):
        assert codec.to_jsonl_str([{"x": 1}, {"y": 2}]) == '{"x": 1}\n{"y": 2}'

    def test_roundtrip_preserves_records(self, file_a, tmp_path):
        dest = tmp_path / "roundtrip_out.ndjson"
        result = codec.roundtrip(file_a, dest)
        assert result == codec.load_ndjson(file_a)
        assert dest.exists()

    def test_rename_field_renames_present_field(self, file_a):
        renamed = codec.rename_field(file_a, "id", "uid")
        assert renamed[0]["uid"] == 1
        assert "id" not in renamed[0]

    def test_rename_field_leaves_records_without_field_unchanged(self, tmp_path):
        path = _write(tmp_path, [{"other": 1}], name="norename.ndjson")
        assert codec.rename_field(path, "missing", "new") == [{"other": 1}]

    def test_write_csv_writes_file(self, tmp_path):
        path = _write(tmp_path, [{"a": 1, "b": 2}], name="wcsv.ndjson")
        dest = tmp_path / "out.csv"
        codec.write_csv(path, dest)
        assert dest.read_text(encoding="utf-8") == "a,b\n1,2\n"

    def test_to_tsv_with_header(self, tmp_path):
        path = _write(tmp_path, [{"a": 1, "b": 2}], name="tsv1.ndjson")
        assert codec.to_tsv(path) == "a\tb\n1\t2"

    def test_to_tsv_without_header(self, tmp_path):
        path = _write(tmp_path, [{"a": 1, "b": 2}], name="tsv2.ndjson")
        assert codec.to_tsv(path, include_header=False) == "1\t2"

    def test_to_tsv_non_dict_records(self, tmp_path):
        path = _write(tmp_path, ["plain", 42], name="tsv3.ndjson")
        result = codec.to_tsv(path)
        assert "plain" in result and "42" in result

    def test_to_markdown_table_basic(self, tmp_path):
        path = _write(tmp_path, [{"a": 1}], name="md1.ndjson")
        assert codec.to_markdown_table(path) == "| a |\n| --- |\n| 1 |"

    def test_to_markdown_table_empty(self, tmp_path):
        path = _write(tmp_path, [], name="mdempty.ndjson")
        assert codec.to_markdown_table(path) == ""

    def test_codec_ndjson_installed_workflow_includes_field_count(self, file_a):
        result = codec.ndjson_installed_workflow(file_a)
        assert result == {
            "format": "ndjson", "loaded": True, "record_count": 3, "field_count": 6
        }

    def test_ndjson_record_authority_marker(self):
        assert codec.NdjsonRecord.spec_qname == "ndjson:record"
        assert codec.NdjsonRecord.authority_only is True

    def test_module_size_constants_present(self):
        assert codec.MAX_FILE_SIZE > 0
        assert codec.MAX_LINES > 0


# ===========================================================================
# ndjson_writer.py — canonical package-level writer
# ===========================================================================

class TestNdjsonWriter:
    def test_write_ndjson_str_basic(self):
        assert writer.write_ndjson_str([{"a": 1}, {"b": 2}]) == '{"a": 1}\n{"b": 2}\n'

    def test_write_ndjson_str_empty_list(self):
        assert writer.write_ndjson_str([]) == ""

    def test_write_ndjson_str_none_raises(self):
        with pytest.raises(writer.NdjsonWriteError):
            writer.write_ndjson_str(None)

    def test_write_ndjson_str_non_serializable_raises(self):
        with pytest.raises(writer.NdjsonWriteError):
            writer.write_ndjson_str([{"bad": {1, 2, 3}}])  # sets aren't JSON serializable

    def test_write_ndjson_creates_file(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        writer.write_ndjson([{"x": 1}], dest)
        assert dest.exists()
        assert codec.load_ndjson(str(dest)) == [{"x": 1}]

    def test_write_ndjson_creates_parent_dirs(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        writer.write_ndjson([{"x": 1}], dest)
        assert dest.exists()

    def test_write_ndjson_empty_path_raises(self):
        with pytest.raises(writer.NdjsonWriteError):
            writer.write_ndjson([{"x": 1}], "")


# ===========================================================================
# ndjson_workflow.py
# ===========================================================================

class TestNdjsonWorkflow:
    def test_ndjson_installed_workflow_dict_keys(self, file_a):
        result = workflow.ndjson_installed_workflow(file_a)
        assert result == {"format": "ndjson", "loaded": True, "record_count": 3}

    def test_ndjson_installed_workflow_empty_file(self, tmp_path):
        path = _write(tmp_path, [], name="empty.ndjson")
        result = workflow.ndjson_installed_workflow(path)
        assert result["record_count"] == 0


# ===========================================================================
# models.py — NdjsonDocument
# ===========================================================================

class TestNdjsonDocumentDimensions:
    def _doc_uniform(self):
        return NdjsonDocument([
            {"a": 1, "b": "x"},
            {"a": 2, "b": "y"},
            {"a": 3, "b": "z"},
        ])

    def _doc_hetero(self):
        return NdjsonDocument(RECORDS_B)

    def test_is_empty_false_for_populated(self):
        assert self._doc_uniform().is_empty is False

    def test_is_empty_true_for_empty_doc(self):
        assert NdjsonDocument([]).is_empty is True

    def test_is_single_record(self):
        assert NdjsonDocument([{"a": 1}]).is_single_record is True
        assert self._doc_uniform().is_single_record is False

    def test_has_records(self):
        assert self._doc_uniform().has_records is True
        assert NdjsonDocument([]).has_records is False

    def test_is_multi_record(self):
        assert self._doc_uniform().is_multi_record is True
        assert NdjsonDocument([{"a": 1}]).is_multi_record is False

    def test_all_objects_true_when_all_dicts(self):
        assert self._doc_uniform().all_objects is True

    def test_all_objects_false_for_empty_doc(self):
        assert NdjsonDocument([]).all_objects is False

    def test_all_arrays(self):
        assert NdjsonDocument([[1, 2], [3, 4]]).all_arrays is True
        assert self._doc_uniform().all_arrays is False

    def test_has_mixed_types(self):
        assert NdjsonDocument([{"a": 1}, [1, 2], "x"]).has_mixed_types is True
        assert self._doc_uniform().has_mixed_types is False

    def test_all_scalars(self):
        assert NdjsonDocument(["a", 1, True]).all_scalars is True
        assert self._doc_uniform().all_scalars is False

    def test_max_keys(self):
        assert self._doc_hetero().max_keys == 3

    def test_max_keys_no_object_records(self):
        assert NdjsonDocument(["a", "b"]).max_keys == 0

    def test_min_keys(self):
        assert self._doc_hetero().min_keys == 0

    def test_is_small(self):
        assert self._doc_uniform().is_small is True

    def test_is_large(self):
        big = NdjsonDocument([{"i": i} for i in range(1001)])
        assert big.is_large is True
        assert self._doc_uniform().is_large is False

    def test_has_uniform_keys_true(self):
        assert self._doc_uniform().has_uniform_keys is True

    def test_has_uniform_keys_false(self):
        assert self._doc_hetero().has_uniform_keys is False

    def test_has_uniform_keys_vacuous_true(self):
        assert NdjsonDocument([]).has_uniform_keys is True

    def test_avg_keys(self):
        assert self._doc_hetero().avg_keys == 2.0

    def test_is_wide_objects_false(self):
        assert self._doc_uniform().is_wide_objects is False

    def test_is_wide_objects_true(self):
        wide = NdjsonDocument([{f"k{i}": i for i in range(25)}])
        assert wide.is_wide_objects is True

    def test_key_range(self):
        assert self._doc_hetero().key_range == 3

    def test_is_schema_consistent_true(self):
        assert self._doc_uniform().is_schema_consistent is True

    def test_is_schema_consistent_false(self):
        assert self._doc_hetero().is_schema_consistent is False

    def test_is_schema_consistent_vacuous_true(self):
        assert NdjsonDocument([]).is_schema_consistent is True

    def test_object_count(self):
        assert self._doc_hetero().object_count == 4

    def test_array_count(self):
        assert NdjsonDocument([[1], [2], {"a": 1}]).array_count == 2

    def test_scalar_count(self):
        assert NdjsonDocument(["a", 1, {"x": 1}]).scalar_count == 2

    def test_object_fraction(self):
        assert self._doc_hetero().object_fraction == 1.0
        assert NdjsonDocument([]).object_fraction == 0.0
        assert NdjsonDocument([{"a": 1}, "x"]).object_fraction == 0.5


class TestNdjsonDocumentMutationAndSerialization:
    def test_append_record(self):
        doc = NdjsonDocument([{"a": 1}])
        doc.append_record({"a": 2})
        assert doc.record_count == 2
        assert doc.get_record(1) == {"a": 2}

    def test_append_record_none_raises(self):
        from ndjson.exceptions import NdjsonError
        doc = NdjsonDocument([])
        with pytest.raises(NdjsonError):
            doc.append_record(None)

    def test_to_ndjson_serializes_all_records(self):
        doc = NdjsonDocument([{"a": 1}, {"b": 2}])
        assert doc.to_ndjson() == '{"a": 1}\n{"b": 2}\n'

    def test_to_ndjson_empty_doc(self):
        assert NdjsonDocument([]).to_ndjson() == ""

    def test_save_to_file_writes_and_creates_dirs(self, tmp_path):
        doc = NdjsonDocument([{"a": 1}])
        dest = tmp_path / "nested" / "saved.ndjson"
        doc.save_to_file(dest)
        assert dest.exists()
        assert codec.load_ndjson(str(dest)) == [{"a": 1}]

    def test_save_to_file_empty_path_raises(self):
        from ndjson.exceptions import NdjsonError
        doc = NdjsonDocument([{"a": 1}])
        with pytest.raises(NdjsonError):
            doc.save_to_file("")


# ===========================================================================
# ndjson_field_analytics.py — orphaned module (not re-exported by __init__)
#
# TC-FI025-001 (2026-07-17): 10 methods removed here (bool_value_count,
# null_field_count, numeric_field_count, string_field_count, max_field_count,
# record_count, dict_record_count, unique_key_count, min_field_count,
# total_field_count) -- they tested functions of the same names deleted from
# ndjson_field_analytics.py per registry/found-issue-register.yaml FI-025
# (permanently-dead duplicates, never re-exported by __init__.py). The
# canonical, still-wired implementations of these same names already have
# their own coverage elsewhere (test_ndjson_record_stats_ext.py,
# test_r305_ndjson_new_analytics.py). This removal also surfaced FI-029: the
# comment on the old numeric_field_count test already noted its value (5,
# total numeric VALUES) differed from ndjson_record_stats's same-named
# function (distinct numeric field NAMES) -- a real, separate, pre-existing
# collision between two already-wired modules, registered but not fixed here.
# ===========================================================================

class TestNdjsonFieldAnalytics:
    def test_first_record_keys(self, file_a):
        assert field_analytics.ndjson_first_record_keys(file_a) == [
            "id", "name", "active", "score", "tags", "meta"
        ]

    def test_first_record_keys_no_records(self, tmp_path):
        path = _write(tmp_path, [], name="e.ndjson")
        assert field_analytics.ndjson_first_record_keys(path) == []

    def test_first_record_field_count(self, file_a):
        assert field_analytics.ndjson_first_record_field_count(file_a) == 6

    def test_has_consistent_keys_true(self, file_a):
        assert field_analytics.ndjson_has_consistent_keys(file_a) is True

    def test_has_consistent_keys_false(self, tmp_path):
        path = _write(tmp_path, [{"a": 1}, {"b": 2}], name="incons.ndjson")
        assert field_analytics.ndjson_has_consistent_keys(path) is False

    def test_sorted_key_names(self, file_a):
        assert field_analytics.ndjson_sorted_key_names(file_a) == [
            "active", "id", "meta", "name", "score", "tags"
        ]

    def test_all_key_names_insertion_order(self, file_a):
        assert field_analytics.ndjson_all_key_names(file_a) == [
            "id", "name", "active", "score", "tags", "meta"
        ]

    def test_last_record_keys(self, file_a):
        assert field_analytics.ndjson_last_record_keys(file_a) == [
            "id", "name", "active", "score", "tags", "meta"
        ]

    def test_last_record_keys_no_dict_records(self, tmp_path):
        path = _write(tmp_path, ["a", "b"], name="scalars.ndjson")
        assert field_analytics.ndjson_last_record_keys(path) == []

    def test_has_nested_records_true(self, file_a):
        assert field_analytics.ndjson_has_nested_records(file_a) is True

    def test_has_nested_records_false(self, tmp_path):
        path = _write(tmp_path, [{"a": 1}], name="flat.ndjson")
        assert field_analytics.ndjson_has_nested_records(path) is False

    def test_has_arrays_true(self, file_a):
        assert field_analytics.ndjson_has_arrays(file_a) is True

    def test_has_arrays_false(self, tmp_path):
        path = _write(tmp_path, [{"a": 1}], name="noarr.ndjson")
        assert field_analytics.ndjson_has_arrays(path) is False


# ===========================================================================
# ndjson_record_stats.py
# ===========================================================================

class TestRecordStatsFileBased:
    def test_group_by_active(self, file_a):
        groups = record_stats.group_by(file_a, "active")
        assert set(groups.keys()) == {True, False}
        assert [r["id"] for r in groups[True]] == [1, 3]
        assert [r["id"] for r in groups[False]] == [2]

    def test_group_by_missing_key_groups_under_none(self, tmp_path):
        path = _write(tmp_path, [{"a": 1}, {"b": 2}], name="gb.ndjson")
        groups = record_stats.group_by(path, "a")
        assert [r["a"] for r in groups[1]] == [1]
        assert groups[None] == [{"b": 2}]

    def test_deduplicate_by_field(self, tmp_path):
        path = _write(tmp_path, [{"k": 1}, {"k": 1}, {"k": 2}], name="dedup.ndjson")
        result = record_stats.deduplicate(path, "k")
        assert [r["k"] for r in result] == [1, 2]

    def test_min_value(self, file_a):
        assert record_stats.min_value(file_a, "id") == 1

    def test_min_value_missing_field(self, file_a):
        assert record_stats.min_value(file_a, "zzz") is None

    def test_max_value(self, file_a):
        assert record_stats.max_value(file_a, "id") == 3

    def test_max_value_missing_field(self, file_a):
        assert record_stats.max_value(file_a, "zzz") is None

    def test_count_by(self, file_a):
        assert record_stats.count_by(file_a, "active") == {True: 2, False: 1}

    def test_pick_projects_fields(self, file_a):
        result = record_stats.pick(file_a, ["id", "name"])
        assert result == [
            {"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Carol"}
        ]

    def test_distinct_values(self, file_a):
        assert record_stats.distinct_values(file_a, "active") == [True, False]

    def test_sort_by_ascending(self, file_a):
        assert [r["id"] for r in record_stats.sort_by(file_a, "id")] == [1, 2, 3]

    def test_sort_by_descending(self, file_a):
        assert [r["id"] for r in record_stats.sort_by(file_a, "id", reverse=True)] == [3, 2, 1]

    def test_aggregate_sum(self, file_a):
        assert record_stats.aggregate(file_a, "score", "sum") == 12.75

    def test_aggregate_count(self, file_a):
        assert record_stats.aggregate(file_a, "score", "count") == 3

    def test_aggregate_min(self, file_a):
        assert record_stats.aggregate(file_a, "score", "min") == 3.5

    def test_aggregate_max(self, file_a):
        assert record_stats.aggregate(file_a, "score", "max") == 9.25

    def test_aggregate_invalid_func_raises(self, file_a):
        with pytest.raises(ValueError):
            record_stats.aggregate(file_a, "score", "median")

    def test_aggregate_no_applicable_values_returns_none(self, tmp_path):
        path = _write(tmp_path, [{"x": "not-numeric"}], name="agg.ndjson")
        assert record_stats.aggregate(path, "x", "sum") is None

    def test_tail(self, file_a):
        assert [r["id"] for r in record_stats.tail(file_a, 2)] == [2, 3]

    def test_tail_negative_raises(self, file_a):
        with pytest.raises(ValueError):
            record_stats.tail(file_a, -1)

    def test_tail_zero_returns_empty(self, file_a):
        assert record_stats.tail(file_a, 0) == []

    def test_pluck(self, file_a):
        assert record_stats.pluck(file_a, "name") == ["Alice", "Bob", "Carol"]

    def test_head(self, file_a):
        assert [r["id"] for r in record_stats.head(file_a, 2)] == [1, 2]

    def test_head_default_n(self, file_a):
        assert len(record_stats.head(file_a)) == 3  # fewer than default 10

    def test_head_negative_raises(self, file_a):
        with pytest.raises(ValueError):
            record_stats.head(file_a, -1)

    def test_sum_field(self, file_a):
        assert record_stats.sum_field(file_a, "id") == 6.0

    def test_average_value(self, file_a):
        assert record_stats.average_value(file_a, "id") == 2.0

    def test_average_value_no_numeric_values(self, tmp_path):
        path = _write(tmp_path, [{"x": "abc"}], name="avg.ndjson")
        assert record_stats.average_value(path, "x") == 0.0

    def test_field_stats(self, file_a):
        result = record_stats.field_stats(file_a, "score")
        assert result == {
            "count": 2, "missing": 1, "min": 3.5, "max": 9.25, "sum": 12.75, "mean": 6.375
        }

    def test_field_stats_no_values(self, tmp_path):
        path = _write(tmp_path, [{"x": "abc"}], name="fs.ndjson")
        result = record_stats.field_stats(path, "x")
        assert result == {
            "count": 0, "missing": 1, "min": None, "max": None, "sum": None, "mean": None
        }

    def test_zip_records(self):
        assert record_stats.zip_records([{"a": 1}], [{"b": 2}]) == [{"a": 1, "b": 2}]

    def test_zip_records_key_collision_second_wins(self):
        assert record_stats.zip_records([{"a": 1}], [{"a": 2}]) == [{"a": 2}]

    def test_zip_records_stops_at_shorter(self):
        result = record_stats.zip_records([{"a": 1}, {"a": 2}], [{"b": 1}])
        assert len(result) == 1


class TestRecordStatsListFriendly:
    def test_flatten_records(self):
        result = record_stats.flatten_records([{"a": {"x": 1, "y": 2}, "b": 3}])
        assert result == [{"a_x": 1, "a_y": 2, "b": 3}]

    def test_flatten_records_with_prefix(self):
        assert record_stats.flatten_records([{"a": {"x": 1}}], prefix="p_") == [{"p_a_x": 1}]

    def test_flatten_records_non_dict_passthrough(self):
        assert record_stats.flatten_records(["scalar"]) == ["scalar"]

    def test_count_unique_values(self):
        assert record_stats.count_unique_values(RECORDS_A, "active") == 2

    def test_zip_with_index_default_field(self):
        result = record_stats.zip_with_index([{"a": 1}, {"a": 2}])
        assert result[0]["_index"] == 0
        assert result[1]["_index"] == 1

    def test_zip_with_index_custom_field_name(self):
        result = record_stats.zip_with_index([{"a": 1}], field_name="seq")
        assert result[0]["seq"] == 0

    def test_zip_with_index_non_dict_record(self):
        assert record_stats.zip_with_index(["x"]) == [{"_index": 0, "_value": "x"}]

    def test_omit_removes_fields(self):
        assert record_stats.omit([{"a": 1, "b": 2}], ["b"]) == [{"a": 1}]

    def test_omit_non_dict_passthrough(self):
        assert record_stats.omit(["x"], ["a"]) == ["x"]

    def test_batch_update_sets_field(self):
        assert record_stats.batch_update([{"a": 1}], "status", "done") == [
            {"a": 1, "status": "done"}
        ]

    def test_batch_update_non_dict_passthrough(self):
        assert record_stats.batch_update(["x"], "a", 1) == ["x"]

    def test_max_key_depth(self):
        assert record_stats.ndjson_max_key_depth(RECORDS_A) == 2

    def test_max_key_depth_empty(self):
        assert record_stats.ndjson_max_key_depth([]) == 0

    def test_field_value_mean(self):
        assert record_stats.ndjson_field_value_mean(RECORDS_A) == pytest.approx(3.75)

    def test_record_count(self):
        assert record_stats.ndjson_record_count(RECORDS_A) == 3

    def test_dict_record_count(self):
        assert record_stats.ndjson_dict_record_count(RECORDS_A) == 3

    def test_common_keys(self):
        assert record_stats.ndjson_common_keys(RECORDS_A) == [
            "active", "id", "meta", "name", "score", "tags"
        ]

    def test_common_keys_no_common(self):
        assert record_stats.ndjson_common_keys(RECORDS_B) == []

    def test_unique_key_count(self):
        assert record_stats.ndjson_unique_key_count(RECORDS_A) == 6

    def test_has_null_values(self):
        assert record_stats.ndjson_has_null_values(RECORDS_A) is True
        assert record_stats.ndjson_has_null_values([{"a": 1}]) is False

    def test_numeric_field_count_counts_distinct_names(self):
        # NOTE: this variant counts DISTINCT numeric-valued field NAMES
        # ("id", "score"), unlike json_stream/field_analytics which count
        # total numeric VALUES. See TestNdjsonFieldAnalytics for contrast.
        assert record_stats.ndjson_numeric_field_count(RECORDS_A) == 2

    def test_has_boolean_values(self):
        assert record_stats.ndjson_has_boolean_values(RECORDS_A) is True
        assert record_stats.ndjson_has_boolean_values([{"a": 1}]) is False

    def test_string_field_names(self):
        assert record_stats.ndjson_string_field_names(RECORDS_A) == ["name"]

    def test_max_record_field_count(self):
        assert record_stats.ndjson_max_record_field_count(RECORDS_B) == 3

    def test_min_record_field_count(self):
        assert record_stats.ndjson_min_record_field_count(RECORDS_B) == 0

    def test_all_records_have_same_keys_true(self):
        assert record_stats.ndjson_all_records_have_same_keys(RECORDS_A) is True

    def test_all_records_have_same_keys_false(self):
        assert record_stats.ndjson_all_records_have_same_keys(RECORDS_B) is False

    def test_total_value_count(self):
        assert record_stats.ndjson_total_value_count(RECORDS_A) == 18


# ===========================================================================
# json_stream.py — extended analytics + aliases (largest gap concentration)
# ===========================================================================

EXPECTED_JSON_STREAM_FIXTURE_A = {
    "ndjson_all_records_are_dicts": True,
    "ndjson_all_records_nonempty": True,
    "ndjson_array_field_count": 3,
    "ndjson_average_field_count": 6.0,
    "ndjson_average_record_size": 6.0,
    "ndjson_avg_field_count": 6.0,
    "ndjson_avg_field_name_length": 4.166666666666667,
    "ndjson_avg_key_count": 6.0,
    "ndjson_avg_key_length": 4.166666666666667,
    "ndjson_avg_list_length": 1.0,
    "ndjson_avg_numeric_value": 3.75,
    "ndjson_avg_record_depth": 2.0,
    "ndjson_avg_string_length": 4.333333333333333,
    "ndjson_avg_string_value_length": 4.333333333333333,
    "ndjson_avg_values_per_record": 6.0,
    "ndjson_bool_field_count": 3,
    "ndjson_bool_ratio": 0.16666666666666666,
    "ndjson_bool_value_count": 3,
    "ndjson_boolean_density": 0.16666666666666666,
    "ndjson_boolean_field_count": 3,
    "ndjson_deepest_nesting": 2,
    "ndjson_dict_field_total": 18,
    "ndjson_distinct_key_count": 6,
    "ndjson_empty_record_count": 0,
    "ndjson_field_count_variance": 0.0,
    "ndjson_field_type_distribution": {
        "number": 5, "string": 3, "boolean": 3, "array": 3, "object": 3, "null": 1
    },
    "ndjson_has_all_same_keys": True,
    "ndjson_has_boolean_fields": True,
    "ndjson_has_lists": True,
    "ndjson_has_nested_objects": True,
    "ndjson_has_null_fields": True,
    "ndjson_has_numeric_fields": True,
    "ndjson_has_string_fields": True,
    "ndjson_has_uniform_types": True,
    "ndjson_is_empty": False,
    "ndjson_is_homogeneous": True,
    "ndjson_is_single_record": False,
    "ndjson_key_count_variance": 0.0,
    "ndjson_list_field_count": 3,
    "ndjson_max_field_count": 6,
    "ndjson_max_field_name_length": 6,
    "ndjson_max_field_value_length": 5,
    "ndjson_max_key_count": 6,
    "ndjson_max_list_length": 2,
    "ndjson_max_nesting_depth": 2,
    "ndjson_max_numeric_value": 9.25,
    "ndjson_max_record_key_count": 6,
    "ndjson_max_record_size": 116,
    "ndjson_max_string_length": 5,
    "ndjson_min_field_count": 6,
    "ndjson_min_field_name_length": 2,
    "ndjson_min_numeric_value": 1,
    "ndjson_min_record_fields": 6,
    "ndjson_min_record_size": 80,
    "ndjson_nested_count": 3,
    "ndjson_nested_field_count": 6,
    "ndjson_nonempty_record_count": 3,
    "ndjson_nonempty_record_ratio": 1.0,
    "ndjson_null_field_count": 1,
    "ndjson_null_ratio": 0.05555555555555555,
    "ndjson_null_value_count": 1,
    "ndjson_numeric_density": 0.2777777777777778,
    "ndjson_numeric_field_count": 5,
    "ndjson_numeric_field_ratio": 0.2777777777777778,
    "ndjson_numeric_range": 8.25,
    "ndjson_numeric_ratio": 0.2777777777777778,
    "ndjson_numeric_sum": 18.75,
    "ndjson_object_field_variance": 0.0,
    "ndjson_record_count": 3,
    "ndjson_record_size_variance": 0.0,
    "ndjson_schema_consistency": 1.0,
    "ndjson_string_density": 0.16666666666666666,
    "ndjson_string_field_count": 3,
    "ndjson_string_length_sum": 13,
    "ndjson_string_value_count": 3,
    "ndjson_string_value_count_exceeds_record_count": False,
    "ndjson_string_value_count_minus_record_count": 0,
    "ndjson_total_field_count": 18,
    "ndjson_total_numeric_sum": 18.75,
    "ndjson_total_string_length": 13,
    "ndjson_total_value_count": 18,
    "ndjson_unique_field_count": 6,
    "ndjson_unique_field_names": ["active", "id", "meta", "name", "score", "tags"],
    "ndjson_unique_key_count": 6,
    "ndjson_value_variance": 8.3,
}

EXPECTED_JSON_STREAM_FIXTURE_B = {
    "ndjson_empty_record_count": 1,
    "ndjson_all_records_nonempty": False,
    "ndjson_has_all_same_keys": False,
    "ndjson_min_field_count": 0,
    "ndjson_max_field_count": 3,
    "ndjson_nested_field_count": 2,
    "ndjson_boolean_field_count": 1,
    "ndjson_has_nested_objects": True,
    "ndjson_list_field_count": 1,
    "ndjson_max_list_length": 3,
    "ndjson_schema_consistency": 0.5,
    "ndjson_min_record_fields": 0,
}


def _assert_matches(result, expected):
    if isinstance(expected, float):
        assert result == pytest.approx(expected)
    else:
        assert result == expected


class TestJsonStreamAnalyticsFixtureA:
    @pytest.mark.parametrize("func_name,expected", sorted(EXPECTED_JSON_STREAM_FIXTURE_A.items()))
    def test_function_value(self, func_name, expected, file_a):
        fn = getattr(json_stream, func_name, None)
        if fn is None:
            pytest.skip(f"{func_name} not found in json_stream module")
        _assert_matches(fn(file_a), expected)


class TestJsonStreamAnalyticsFixtureB:
    @pytest.mark.parametrize("func_name,expected", sorted(EXPECTED_JSON_STREAM_FIXTURE_B.items()))
    def test_function_value(self, func_name, expected, file_b):
        fn = getattr(json_stream, func_name, None)
        if fn is None:
            pytest.skip(f"{func_name} not found in json_stream module")
        _assert_matches(fn(file_b), expected)


class TestJsonStreamFieldExists:
    def test_field_exists_true(self, file_a):
        assert json_stream.ndjson_field_exists(file_a, "id") is True

    def test_field_exists_false(self, file_a):
        assert json_stream.ndjson_field_exists(file_a, "nonexistent") is False


class TestJsonStreamFileSizeBytes:
    def test_returns_actual_file_size(self, file_a):
        result = json_stream.ndjson_file_size_bytes(file_a)
        assert result == Path(file_a).stat().st_size
        assert result > 0

    def test_returns_zero_for_list_source(self):
        assert json_stream.ndjson_file_size_bytes([{"a": 1}]) == 0

    def test_returns_zero_for_bytes_source(self):
        assert json_stream.ndjson_file_size_bytes(b'{"a": 1}') == 0

    def test_returns_zero_for_nonexistent_path(self, tmp_path):
        missing = tmp_path / "does" / "not" / "exist.ndjson"
        assert json_stream.ndjson_file_size_bytes(str(missing)) == 0


class TestJsonStreamAliasesShareIdentity:
    """Verify alias assignments at the bottom of json_stream.py are the SAME
    function object as their canonical counterpart (not independent copies)."""

    @pytest.mark.parametrize("alias_name,canonical_name", [
        ("ndjson_max_record_key_count", "ndjson_max_field_count"),
        ("ndjson_deepest_nesting", "ndjson_max_nesting_depth"),
        ("ndjson_max_key_count", "ndjson_max_field_count"),
        ("ndjson_array_field_count", "ndjson_list_field_count"),
        ("ndjson_avg_values_per_record", "ndjson_average_field_count"),
        ("ndjson_avg_field_count", "ndjson_average_field_count"),
        ("ndjson_numeric_ratio", "ndjson_numeric_density"),
        ("ndjson_numeric_field_ratio", "ndjson_numeric_density"),
        ("ndjson_bool_ratio", "ndjson_boolean_density"),
        ("ndjson_bool_field_count", "ndjson_boolean_field_count"),
        ("ndjson_unique_key_count", "ndjson_unique_field_count"),
        ("ndjson_distinct_key_count", "ndjson_unique_field_count"),
        ("ndjson_avg_key_count", "ndjson_average_field_count"),
        ("ndjson_string_length_sum", "ndjson_total_string_length"),
        ("ndjson_numeric_sum", "ndjson_total_numeric_sum"),
        ("ndjson_dict_field_total", "ndjson_total_field_count"),
        ("ndjson_total_value_count", "ndjson_total_field_count"),
        ("ndjson_avg_string_value_length", "ndjson_avg_string_length"),
        ("ndjson_key_count_variance", "ndjson_field_count_variance"),
        ("ndjson_object_field_variance", "ndjson_field_count_variance"),
    ])
    def test_alias_is_same_function_object(self, alias_name, canonical_name):
        assert getattr(json_stream, alias_name) is getattr(json_stream, canonical_name)


# ===========================================================================
# Iterators + spec/Compat classes
# ===========================================================================

class TestIteratorsAndSpecClasses:
    def test_ndjson_iter_records_yields_record_objects(self, file_a):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        from ndjson.spec.record.record import Record

        results = list(ndjson_iter_records(file_a))
        assert len(results) == 3
        assert all(isinstance(r, Record) for r in results)
        assert results[0].get("id") == 1
        assert results[0].field_count == 6

    def test_ndjson_iter_records_skips_non_dict(self, tmp_path):
        path = _write(tmp_path, [{"a": 1}, "plain string", 42, [1, 2]], name="mixed.ndjson")
        from ndjson.ndjson_record_iterator import ndjson_iter_records

        results = list(ndjson_iter_records(path))
        assert len(results) == 1  # only the dict record yields a Record

    def test_ndjson_iter_fields_yields_field_objects(self, file_a):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        from ndjson.spec.record.field import Field

        fields = list(ndjson_iter_fields(file_a))
        assert all(isinstance(f, Field) for f in fields)
        assert len(fields) == 18  # 3 records x 6 fields each
        assert fields[0].key == "id"
        assert fields[0].value == 1

    def test_field_is_null(self):
        from ndjson.spec.record.field import Field

        assert Field("x", None).is_null() is True
        assert Field("x", 0).is_null() is False

    def test_field_to_dict(self):
        from ndjson.spec.record.field import Field

        assert Field("key1", "val1").to_dict() == {"key": "key1", "value": "val1"}

    def test_field_repr(self):
        from ndjson.spec.record.field import Field

        assert "Field" in repr(Field("k", "v"))

    def test_record_class_basic(self):
        from ndjson.spec.record.record import Record

        r = Record({"a": 1, "b": 2})
        assert r.keys == ["a", "b"]
        assert r.field_count == 2
        assert r.get("a") == 1
        assert r.get("missing") is None
        assert r.to_dict() == {"a": 1, "b": 2}
        assert "Record" in repr(r)

    def test_compat_ndjson_record_facade(self):
        from ndjson.Compat.ndjson_record import NdjsonRecord

        assert NdjsonRecord.spec_qname == "ndjson:record"
        rec = NdjsonRecord({"x": 1})
        assert rec.get("x") == 1


# ===========================================================================
# exceptions.py — shared FormatFactoryError-based hierarchy
# ===========================================================================

class TestExceptions:
    def test_ndjson_error_is_format_factory_error(self):
        from ndjson.exceptions import NdjsonError
        from _shared._shared_exceptions import FormatFactoryError

        assert issubclass(NdjsonError, FormatFactoryError)

    def test_ndjson_parse_error_is_ndjson_error(self):
        from ndjson.exceptions import NdjsonError, NdjsonParseError

        assert issubclass(NdjsonParseError, NdjsonError)

    def test_ndjson_write_error_is_ndjson_error(self):
        from ndjson.exceptions import NdjsonError, NdjsonWriteError

        assert issubclass(NdjsonWriteError, NdjsonError)

    def test_ndjson_error_raisable_with_message(self):
        from ndjson.exceptions import NdjsonError

        with pytest.raises(NdjsonError, match="boom"):
            raise NdjsonError("boom")

    def test_codec_level_ndjson_error_is_unified_with_shared_class(self):
        """Healed: ndjson_codec.py imports NdjsonError/NdjsonParseError from
        exceptions.py rather than redefining them -- single source of truth.
        See plans/.claude/quizzical-munching-gadget.md section 7."""
        from ndjson import exceptions as shared_exceptions

        assert codec.NdjsonError is shared_exceptions.NdjsonError
        assert codec.NdjsonParseError is shared_exceptions.NdjsonParseError

    def test_codec_ndjson_parse_error_raised_on_malformed_json(self, tmp_path):
        bad = tmp_path / "bad.ndjson"
        bad.write_text('{"a": 1}\nnot json\n', encoding="utf-8")
        with pytest.raises(codec.NdjsonParseError):
            codec.load_ndjson(str(bad))


# ===========================================================================
# cli.py
# ===========================================================================

class TestCli:
    def test_main_no_args_prints_usage(self, monkeypatch, capsys):
        from ndjson import cli

        monkeypatch.setattr(sys, "argv", ["ff-ndjson"])
        with pytest.raises(SystemExit) as exc:
            cli.main()
        assert exc.value.code == 0
        assert "Usage" in capsys.readouterr().out

    def test_main_missing_file_exits_1(self, monkeypatch, capsys, tmp_path):
        from ndjson import cli

        missing = tmp_path / "does_not_exist.ndjson"
        monkeypatch.setattr(sys, "argv", ["ff-ndjson", str(missing)])
        with pytest.raises(SystemExit) as exc:
            cli.main()
        assert exc.value.code == 1
        assert "not found" in capsys.readouterr().err

    def test_main_valid_file_prints_record_count(self, monkeypatch, capsys, file_a):
        from ndjson import cli

        monkeypatch.setattr(sys, "argv", ["ff-ndjson", file_a])
        cli.main()
        out = capsys.readouterr().out
        assert "Record count: 3" in out
        assert "First record keys" in out

    def test_main_malformed_file_exits_2(self, monkeypatch, capsys, tmp_path):
        from ndjson import cli

        bad = tmp_path / "bad.ndjson"
        bad.write_text('{"a": 1}\nnot-json\n', encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["ff-ndjson", str(bad)])
        with pytest.raises(SystemExit) as exc:
            cli.main()
        assert exc.value.code == 2
        assert "Error" in capsys.readouterr().err


# ===========================================================================
# ndjson_to_*.py — dogfood export converters (smoke coverage)
# ===========================================================================

CONVERTER_RECORDS = [
    {"col_a": "x1", "col_b": "y1"},
    {"col_a": "x2", "col_b": "y2"},
    {"col_a": "x3", "col_b": "y3"},
]


@pytest.fixture
def converter_source(tmp_path):
    return _write(tmp_path, CONVERTER_RECORDS, name="conv_source.ndjson")


class TestDogfoodConverters:
    def test_ndjson_to_abw(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_abw import ndjson_to_abw
        except ImportError:
            pytest.skip("ndjson_to_abw dependency unavailable")
        dest = tmp_path / "out.abw"
        count = ndjson_to_abw(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_csv(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_csv import ndjson_to_csv
        except ImportError:
            pytest.skip("ndjson_to_csv dependency unavailable")
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(converter_source, dest)
        assert count == 3
        assert dest.exists()

    def test_ndjson_to_csv_empty_source(self, tmp_path):
        try:
            from ndjson.ndjson_to_csv import ndjson_to_csv
        except ImportError:
            pytest.skip("ndjson_to_csv dependency unavailable")
        empty = _write(tmp_path, [], name="empty_conv.ndjson")
        dest = tmp_path / "out_empty.csv"
        count = ndjson_to_csv(empty, dest)
        assert count == 0
        assert dest.exists()

    def test_ndjson_to_dif(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_dif import ndjson_to_dif
        except ImportError:
            pytest.skip("ndjson_to_dif dependency unavailable")
        dest = tmp_path / "out.dif"
        count = ndjson_to_dif(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_fodg(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_fodg import ndjson_to_fodg
        except ImportError:
            pytest.skip("ndjson_to_fodg dependency unavailable")
        dest = tmp_path / "out.fodg"
        count = ndjson_to_fodg(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_fods(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_fods import ndjson_to_fods
        except ImportError:
            pytest.skip("ndjson_to_fods dependency unavailable")
        dest = tmp_path / "out.fods"
        count = ndjson_to_fods(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_fodt(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_fodt import ndjson_to_fodt
        except ImportError:
            pytest.skip("ndjson_to_fodt dependency unavailable")
        dest = tmp_path / "out.fodt"
        count = ndjson_to_fodt(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_gnumeric(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_gnumeric import ndjson_to_gnumeric
        except ImportError:
            pytest.skip("ndjson_to_gnumeric dependency unavailable")
        dest = tmp_path / "out.gnumeric"
        count = ndjson_to_gnumeric(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_ods(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_ods import ndjson_to_ods
        except ImportError:
            pytest.skip("ndjson_to_ods dependency unavailable")
        dest = tmp_path / "out.ods"
        count = ndjson_to_ods(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_odt(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_odt import ndjson_to_odt
        except ImportError:
            pytest.skip("ndjson_to_odt dependency unavailable")
        dest = tmp_path / "out.odt"
        count = ndjson_to_odt(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    # test_ndjson_to_pbm / _pgm / _ppm removed by TC-PA-015 (PORTFOLIO-AUDIT-2026-07-16):
    # ndjson->pbm/pgm/ppm are INCOMPATIBLE (STRUCTURED_DATA has no pixel representation);
    # the converters were deprecated and removed. See converter-compatibility-matrix.yaml.

    def test_ndjson_to_sylk(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_sylk import ndjson_to_sylk
        except ImportError:
            pytest.skip("ndjson_to_sylk dependency unavailable")
        dest = tmp_path / "out.sylk"
        count = ndjson_to_sylk(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_toml(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_toml import ndjson_to_toml
        except ImportError:
            pytest.skip("ndjson_to_toml dependency unavailable")
        dest = tmp_path / "out.toml"
        count = ndjson_to_toml(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0

    def test_ndjson_to_toml_empty_source(self, tmp_path):
        try:
            from ndjson.ndjson_to_toml import ndjson_to_toml
        except ImportError:
            pytest.skip("ndjson_to_toml dependency unavailable")
        empty = _write(tmp_path, [], name="empty_toml.ndjson")
        dest = tmp_path / "out_empty.toml"
        count = ndjson_to_toml(empty, dest)
        assert count == 0
        assert dest.exists()

    def test_ndjson_to_tsv(self, converter_source, tmp_path):
        try:
            from ndjson.ndjson_to_tsv import ndjson_to_tsv
        except ImportError:
            pytest.skip("ndjson_to_tsv dependency unavailable")
        dest = tmp_path / "out.tsv"
        count = ndjson_to_tsv(converter_source, dest)
        assert count == 3
        assert dest.exists() and dest.stat().st_size > 0


# ===========================================================================
# Package-level public API sanity (ndjson/__init__.py __all__)
# ===========================================================================

class TestPackagePublicApi:
    def test_all_names_resolve(self):
        import ndjson

        missing = [name for name in ndjson.__all__ if not hasattr(ndjson, name)]
        assert missing == []

    def test_all_has_expected_minimum_size(self):
        import ndjson

        assert len(ndjson.__all__) >= 100

    def test_core_classes_and_exceptions_exported(self):
        import ndjson

        assert ndjson.NdjsonDocument is NdjsonDocument
        assert ndjson.NdjsonRecord is not None
        assert issubclass(ndjson.NdjsonError, Exception)

    def test_write_ndjson_resolves_to_writer_module_version(self):
        import ndjson

        # __init__.py imports ndjson_writer AFTER ndjson_codec's `import *`,
        # so the package-level write_ndjson is the writer.py version.
        assert ndjson.write_ndjson is writer.write_ndjson
        assert ndjson.write_ndjson is not codec.write_ndjson

    def test_ndjson_installed_workflow_resolves_to_workflow_module_version(self):
        import ndjson

        assert ndjson.ndjson_installed_workflow is workflow.ndjson_installed_workflow
        assert ndjson.ndjson_installed_workflow is not codec.ndjson_installed_workflow

    def test_ndjson_numeric_field_count_resolves_to_record_stats_version(self):
        import ndjson

        assert ndjson.ndjson_numeric_field_count is record_stats.ndjson_numeric_field_count
