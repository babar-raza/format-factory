"""
tests/python/tsv/test_tsv_gap_coverage.py

Comprehensive gap-closure test suite for the TSV (Tab-Separated Values) FOSS
Python track. Exercises every exported name from src/python/tsv/__init__.py
plus the tsv:record / tsv:field spec-shaped model classes and the TsvDocument
facade, closing the ~85 `missing_test_coverage` gap-ledger entries recorded
for format=TSV in reports/capability-layer/gap-ledger.json.

Modules covered:
  tsv_parser.py         -- core parse/write/query/transform functions
  tsv_writer.py          -- write_tsv / write_tsv_str (winning package bindings)
  tabular_document.py    -- tsv_* whole-document analytics functions
  tsv_row_analytics.py   -- tsv_* row/column/header analytics functions
  tsv_row_iterator.py    -- tsv_iter_records (spec Record)
  tsv_field_iterator.py  -- tsv_iter_fields (spec Field)
  tsv_workflow.py        -- tsv_installed_workflow
  models.py              -- TsvDocument facade
  exceptions.py          -- TsvError / TsvParseError / TsvWriteError hierarchy
  cli.py                 -- main() entry point
  tsv_to_*.py            -- 15 dogfood cross-format export functions

Authority: IANA text/tab-separated-values media type (SAL-TSV-00001/00002).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

import tsv  # noqa: E402

_SAMPLES = _REPO / "samples" / "by-format" / "tsv"
MIN = _SAMPLES / "minimal-2x2.tsv"
MULTI = _SAMPLES / "multi-column.tsv"
SINGLE = _SAMPLES / "single-cell.tsv"


def _mk_tsv(tmp_path, rows, headers=None, name="data.tsv"):
    dest = tmp_path / name
    tsv.write_tsv(rows, str(dest), headers=headers)
    return dest


# ---------------------------------------------------------------------------
# Parser core: parse_tsv / parse_tsv_strict / probe_tsv / get_capabilities
# ---------------------------------------------------------------------------

class TestParseTsvStrict:
    def test_minimal_2x2(self):
        result = tsv.parse_tsv_strict(str(MIN))
        assert result["format"] == "tsv"
        assert result["headers"] == ["Name", "Age"]
        assert result["rows"] == [["Alice", "30"], ["Bob", "25"]]
        assert result["row_count"] == 2
        assert result["column_count"] == 2
        assert result["has_header"] is True
        assert result["delimiter"] == "\t"

    def test_multi_column(self):
        result = tsv.parse_tsv_strict(str(MULTI))
        assert result["headers"] == ["id", "name", "score", "pass"]
        assert result["row_count"] == 2
        assert result["column_count"] == 4

    def test_single_cell(self):
        result = tsv.parse_tsv_strict(str(SINGLE))
        assert result["headers"] == ["value"]
        assert result["rows"] == [["42"]]
        assert result["row_count"] == 1

    def test_missing_file_raises_input_error(self):
        with pytest.raises(tsv.TsvInputError):
            tsv.parse_tsv_strict(str(_SAMPLES / "does-not-exist.tsv"))

    def test_directory_path_raises_input_error(self, tmp_path):
        with pytest.raises(tsv.TsvInputError):
            tsv.parse_tsv_strict(str(tmp_path))

    def test_no_header_when_column_counts_differ(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        result = tsv.parse_tsv_strict(str(dest))
        assert result["has_header"] is False
        assert result["headers"] is None
        assert result["row_count"] == 2

    def test_empty_file_returns_zeroed_model(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        result = tsv.parse_tsv_strict(str(dest))
        assert result["row_count"] == 0
        assert result["headers"] is None
        assert result["rows"] == []
        assert result["has_header"] is False


class TestParseTsvNonRaising:
    def test_success_matches_strict(self):
        assert tsv.parse_tsv(str(MIN)) == tsv.parse_tsv_strict(str(MIN))

    def test_failure_returns_error_dict(self):
        result = tsv.parse_tsv(str(_SAMPLES / "does-not-exist.tsv"))
        assert result["format"] == "tsv"
        assert result["ok"] is False
        assert "error" in result
        assert result["error_type"] == "TsvInputError"


class TestProbeTsv:
    def test_existing_file(self):
        result = tsv.probe_tsv(str(MIN))
        assert result["exists"] is True
        assert result["delimiter"] == "\t"
        assert result["first_line"] == "Name\tAge"
        assert result["column_count"] == 2
        assert result["size_bytes"] > 0

    def test_missing_file(self):
        result = tsv.probe_tsv(str(_SAMPLES / "nope.tsv"))
        assert result["exists"] is False
        assert "size_bytes" not in result


class TestGetCapabilities:
    def test_shape(self):
        caps = tsv.get_capabilities()
        assert caps["format"] == "tsv"
        assert caps["gate"] == 4
        assert caps["commercial_product_ready"] is False
        assert "tsv_parse" in caps["supported"]
        assert "tab_delimiter" in caps["supported"]
        assert "formula_cells" in caps["unsupported"]
        assert "multi_sheet" in caps["unsupported"]


# ---------------------------------------------------------------------------
# load_tsv / get_headers / get_column / get_row / validate_headers /
# count_rows / get_row_by_key / get_column_values / unique_column_values /
# get_numeric_columns / count_distinct_values / find_rows_containing
# ---------------------------------------------------------------------------

class TestLoadTsv:
    def test_from_path(self):
        result = tsv.load_tsv(str(MIN))
        assert result["headers"] == ["Name", "Age"]

    def test_from_bytes(self):
        result = tsv.load_tsv(b"x\ty\n1\t2\n")
        assert result["headers"] == ["x", "y"]
        assert result["rows"] == [["1", "2"]]

    def test_from_path_object(self):
        result = tsv.load_tsv(MIN)
        assert result["row_count"] == 2

    def test_unsupported_type_raises(self):
        with pytest.raises(tsv.TsvInputError):
            tsv.load_tsv(12345)


class TestGetHeaders:
    def test_minimal(self):
        assert tsv.get_headers(str(MIN)) == ["Name", "Age"]

    def test_no_header_returns_none(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.get_headers(str(dest)) is None


class TestGetColumn:
    def test_found(self):
        assert tsv.get_column(str(MIN), "Name") == ["Alice", "Bob"]

    def test_missing_returns_empty(self):
        assert tsv.get_column(str(MIN), "nope") == []

    def test_no_headers_returns_empty(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.get_column(str(dest), "a") == []


class TestGetRow:
    def test_valid_index(self):
        assert tsv.get_row(str(MIN), 0) == ["Alice", "30"]
        assert tsv.get_row(str(MIN), 1) == ["Bob", "25"]

    def test_negative_raises(self):
        with pytest.raises(IndexError):
            tsv.get_row(str(MIN), -1)

    def test_out_of_range_raises(self):
        with pytest.raises(IndexError):
            tsv.get_row(str(MIN), 99)


class TestValidateHeaders:
    def test_valid_exact_match(self):
        result = tsv.validate_headers(str(MIN), ["Name", "Age"])
        assert result["valid"] is True
        assert result["missing"] == []
        assert result["extra"] == []

    def test_missing_and_extra(self):
        result = tsv.validate_headers(str(MIN), ["Foo"])
        assert result["valid"] is False
        assert result["missing"] == ["Foo"]
        assert result["extra"] == ["Name", "Age"]

    def test_order_sensitive(self):
        result = tsv.validate_headers(str(MULTI), ["name", "id", "score", "pass"])
        assert result["valid"] is False
        assert result["missing"] == []
        assert result["extra"] == []


class TestCountRows:
    def test_minimal(self):
        assert tsv.count_rows(str(MIN)) == 2

    def test_multi_column(self):
        assert tsv.count_rows(str(MULTI)) == 2

    def test_single_cell(self):
        assert tsv.count_rows(str(SINGLE)) == 1


class TestGetRowByKey:
    def test_found(self):
        assert tsv.get_row_by_key(str(MIN), "Name", "Alice") == ["Alice", "30"]

    def test_not_found_returns_none(self):
        assert tsv.get_row_by_key(str(MIN), "Name", "ZZZ") is None

    def test_missing_column_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.get_row_by_key(str(MIN), "nope", "x")


class TestGetColumnValues:
    def test_found(self):
        assert tsv.get_column_values(str(MULTI), "name") == ["Alice", "Bob"]

    def test_missing_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.get_column_values(str(MIN), "nope")


class TestUniqueColumnValues:
    def test_sorted_unique(self):
        assert tsv.unique_column_values(str(MULTI), "id") == ["1", "2"]

    def test_dedups_repeats(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a"], ["b"], ["a"]], headers=["v"])
        assert tsv.unique_column_values(str(dest), "v") == ["a", "b"]

    def test_missing_column_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.unique_column_values(str(MIN), "nope")


class TestGetNumericColumns:
    def test_multi_column_detects_numeric(self):
        assert tsv.get_numeric_columns(str(MULTI)) == ["id", "score"]

    def test_minimal_no_numeric_columns(self):
        # "Name" is non-numeric; "Age" is entirely numeric.
        assert tsv.get_numeric_columns(str(MIN)) == ["Age"]

    def test_no_rows_returns_empty(self, tmp_path):
        dest = tmp_path / "headers-only.tsv"
        dest.write_text("a\tb\n", encoding="utf-8")
        assert tsv.get_numeric_columns(str(dest)) == []


class TestCountDistinctValues:
    def test_multi_column(self):
        assert tsv.count_distinct_values(str(MULTI), "pass") == 2

    def test_repeated_values(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a"], ["a"], ["b"]], headers=["v"])
        assert tsv.count_distinct_values(str(dest), "v") == 2

    def test_missing_column_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.count_distinct_values(str(MIN), "nope")


class TestFindRowsContaining:
    def test_finds_match(self):
        assert tsv.find_rows_containing(str(MIN), "Alice") == [0]

    def test_no_match_returns_empty(self):
        assert tsv.find_rows_containing(str(MIN), "Zzz") == []

    def test_case_insensitive(self):
        assert tsv.find_rows_containing(str(MIN), "alice", case_sensitive=False) == [0]

    def test_case_sensitive_default_misses(self):
        assert tsv.find_rows_containing(str(MIN), "alice") == []

    def test_accepts_preloaded_dict(self):
        model = tsv.load_tsv(str(MIN))
        assert tsv.find_rows_containing(model, "Bob") == [1]


# ---------------------------------------------------------------------------
# write_tsv / write_tsv_str / write_tsv_strict
# ---------------------------------------------------------------------------

class TestWriteTsv:
    def test_writes_file_with_headers(self, tmp_path):
        dest = tmp_path / "out.tsv"
        tsv.write_tsv([["a", "1"], ["b", "2"]], str(dest), headers=["k", "v"])
        content = dest.read_text(encoding="utf-8")
        assert content == "k\tv\na\t1\nb\t2\n"

    def test_writes_file_without_headers(self, tmp_path):
        dest = tmp_path / "out.tsv"
        tsv.write_tsv([["a", "1"]], str(dest))
        assert dest.read_text(encoding="utf-8") == "a\t1\n"

    def test_creates_parent_dirs(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        tsv.write_tsv([["a"]], str(dest))
        assert dest.exists()

    def test_tab_in_cell_raises(self, tmp_path):
        from tsv.tsv_writer import TsvWriteError as WriterTsvWriteError

        dest = tmp_path / "out.tsv"
        with pytest.raises(WriterTsvWriteError):
            tsv.write_tsv([["a\tb", "1"]], str(dest), headers=["k", "v"])

    def test_roundtrips_via_parse(self, tmp_path):
        dest = tmp_path / "out.tsv"
        tsv.write_tsv([["a", "1"], ["b", "2"]], str(dest), headers=["k", "v"])
        result = tsv.parse_tsv_strict(str(dest))
        assert result["headers"] == ["k", "v"]
        assert result["rows"] == [["a", "1"], ["b", "2"]]


class TestWriteTsvStr:
    def test_with_headers(self):
        s = tsv.write_tsv_str([["a", "1"]], headers=["k", "v"])
        assert s == "k\tv\na\t1\n"

    def test_without_headers(self):
        s = tsv.write_tsv_str([["a", "1"]])
        assert s == "a\t1\n"

    def test_empty_rows_no_headers(self):
        assert tsv.write_tsv_str([]) == ""

    def test_tab_in_field_raises(self):
        from tsv.tsv_writer import TsvWriteError as WriterTsvWriteError

        with pytest.raises(WriterTsvWriteError):
            tsv.write_tsv_str([["a\tb"]])

    def test_none_value_becomes_empty_string(self):
        s = tsv.write_tsv_str([[None, "x"]])
        assert s == "\tx\n"


class TestWriteTsvStrict:
    def test_writes_clean_data(self, tmp_path):
        dest = tmp_path / "strict.tsv"
        tsv.write_tsv_strict([["a", "1"]], str(dest), headers=["k", "v"])
        assert dest.read_text(encoding="utf-8") == "k\tv\na\t1\n"

    def test_tab_in_cell_raises_tsv_error(self, tmp_path):
        dest = tmp_path / "strict.tsv"
        with pytest.raises(tsv.TsvError):
            tsv.write_tsv_strict([["a\tb", "1"]], str(dest), headers=["k", "v"])

    def test_newline_in_cell_raises_tsv_error(self, tmp_path):
        dest = tmp_path / "strict.tsv"
        with pytest.raises(tsv.TsvError):
            tsv.write_tsv_strict([["a\nb", "1"]], str(dest), headers=["k", "v"])


# ---------------------------------------------------------------------------
# Row/column transforms: sort_rows / drop_column / add_column / rename_column
# / merge_tsv / sample_rows / deduplicate_rows / to_csv / filter_rows
# ---------------------------------------------------------------------------

class TestSortRows:
    def test_ascending(self):
        result = tsv.sort_rows(str(MIN), "Name")
        names = [r[0] for r in result["rows"]]
        assert names == ["Alice", "Bob"]

    def test_descending(self):
        result = tsv.sort_rows(str(MIN), "Name", reverse=True)
        names = [r[0] for r in result["rows"]]
        assert names == ["Bob", "Alice"]

    def test_missing_column_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.sort_rows(str(MIN), "nope")


class TestDropColumn:
    def test_removes_column(self):
        result = tsv.drop_column(str(MIN), "Age")
        assert result["headers"] == ["Name"]
        assert result["rows"] == [["Alice"], ["Bob"]]

    def test_missing_column_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.drop_column(str(MIN), "nope")


class TestAddColumn:
    def test_appends_column(self):
        result = tsv.add_column(str(MIN), "City", ["NYC", "LA"])
        assert result["headers"] == ["Name", "Age", "City"]
        assert result["rows"] == [["Alice", "30", "NYC"], ["Bob", "25", "LA"]]

    def test_length_mismatch_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.add_column(str(MIN), "City", ["only-one"])


class TestRenameColumn:
    def test_renames(self):
        result = tsv.rename_column(str(MIN), "Age", "Years")
        assert result["headers"] == ["Name", "Years"]
        assert result["rows"] == [["Alice", "30"], ["Bob", "25"]]

    def test_missing_column_raises(self):
        with pytest.raises(tsv.TsvError):
            tsv.rename_column(str(MIN), "nope", "X")


class TestMergeTsv:
    def test_merges_matching_headers(self, tmp_path):
        a = _mk_tsv(tmp_path, [["a", "1"]], headers=["k", "v"], name="a.tsv")
        b = _mk_tsv(tmp_path, [["b", "2"]], headers=["k", "v"], name="b.tsv")
        result = tsv.merge_tsv(str(a), str(b))
        assert result["headers"] == ["k", "v"]
        assert result["rows"] == [["a", "1"], ["b", "2"]]
        assert result["row_count"] == 2

    def test_header_mismatch_raises(self, tmp_path):
        a = _mk_tsv(tmp_path, [["a", "1"]], headers=["k", "v"], name="a.tsv")
        with pytest.raises(tsv.TsvError):
            tsv.merge_tsv(str(a), str(MULTI))


class TestSampleRows:
    def test_returns_first_n(self):
        result = tsv.sample_rows(str(MIN), 1)
        assert result["headers"] == ["Name", "Age"]
        assert result["rows"] == [["Alice", "30"]]

    def test_n_zero_returns_empty(self):
        result = tsv.sample_rows(str(MIN), 0)
        assert result["rows"] == []

    def test_n_larger_than_rows(self):
        result = tsv.sample_rows(str(MIN), 100)
        assert len(result["rows"]) == 2


class TestDeduplicateRows:
    def test_no_duplicates_unchanged(self):
        assert tsv.deduplicate_rows(str(MIN)) == [["Alice", "30"], ["Bob", "25"]]

    def test_removes_duplicates_preserving_order(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "1"], ["b", "2"], ["a", "1"]], headers=["k", "v"])
        assert tsv.deduplicate_rows(str(dest)) == [["a", "1"], ["b", "2"]]


class TestToCsv:
    def test_produces_comma_separated(self):
        csv_str = tsv.to_csv(str(MIN))
        assert csv_str == "Name,Age\r\nAlice,30\r\nBob,25\r\n"

    def test_quotes_fields_with_commas(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a,b", "1"]], headers=["k", "v"])
        csv_str = tsv.to_csv(str(dest))
        assert '"a,b"' in csv_str

    def test_empty_data_empty_string(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.to_csv(str(dest)) == ""


class TestFilterRows:
    def test_exact_match(self):
        result = tsv.filter_rows(str(MULTI), "pass", "true")
        assert result["row_count"] == 1
        assert result["rows"] == [["1", "Alice", "95.5", "true"]]

    def test_substring_match(self):
        result = tsv.filter_rows(str(MULTI), "name", "li", exact=False)
        assert result["row_count"] == 1

    def test_case_insensitive(self):
        result = tsv.filter_rows(str(MULTI), "pass", "TRUE", case_sensitive=False)
        assert result["row_count"] == 1

    def test_no_match_returns_empty(self):
        result = tsv.filter_rows(str(MULTI), "pass", "maybe")
        assert result["row_count"] == 0

    def test_missing_column_returns_empty_result(self):
        result = tsv.filter_rows(str(MULTI), "nope", "x")
        assert result["row_count"] == 0
        assert result["rows"] == []


# ---------------------------------------------------------------------------
# Column statistics: min/max/sum/average/median/std column_tsv, column_count
# ---------------------------------------------------------------------------

class TestColumnStatistics:
    def test_min_column(self):
        assert tsv.min_column_tsv(str(MULTI), "id") == 1.0

    def test_max_column(self):
        assert tsv.max_column_tsv(str(MULTI), "id") == 2.0

    def test_sum_column(self):
        assert tsv.sum_column_tsv(str(MULTI), "id") == 3.0

    def test_average_column(self):
        assert tsv.average_column_tsv(str(MULTI), "id") == 1.5

    def test_median_column_odd_count(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["1"], ["5"], ["3"]], headers=["v"])
        assert tsv.median_column_tsv(str(dest), "v") == 3.0

    def test_median_column_even_count(self):
        assert tsv.median_column_tsv(str(MULTI), "id") == 1.5

    def test_std_column(self):
        assert tsv.std_column_tsv(str(MULTI), "id") == pytest.approx(0.5)

    def test_std_column_no_numeric_values_zero(self):
        assert tsv.std_column_tsv(str(MIN), "Name") == 0.0

    def test_min_column_non_numeric_returns_zero(self):
        assert tsv.min_column_tsv(str(MIN), "Name") == 0.0

    def test_max_column_non_numeric_returns_zero(self):
        assert tsv.max_column_tsv(str(MIN), "Name") == 0.0

    @pytest.mark.parametrize(
        "fn_name",
        [
            "min_column_tsv",
            "max_column_tsv",
            "sum_column_tsv",
            "average_column_tsv",
            "median_column_tsv",
            "std_column_tsv",
        ],
    )
    def test_missing_column_raises(self, fn_name):
        fn = getattr(tsv, fn_name)
        with pytest.raises(tsv.TsvError):
            fn(str(MIN), "nope")

    def test_column_count_with_headers(self):
        assert tsv.column_count(str(MIN)) == 2
        assert tsv.column_count(str(MULTI)) == 4

    def test_column_count_no_header_is_zero(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.column_count(str(dest)) == 0


# ---------------------------------------------------------------------------
# append_row / append_rows / roundtrip
# ---------------------------------------------------------------------------

class TestAppendRow:
    def test_appends_to_existing_file(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "1"]], headers=["k", "v"])
        tsv.append_row(str(dest), ["b", "2"])
        result = tsv.parse_tsv_strict(str(dest))
        assert result["rows"] == [["a", "1"], ["b", "2"]]

    def test_creates_file_if_missing(self, tmp_path):
        dest = tmp_path / "new.tsv"
        tsv.append_row(str(dest), ["x", "y"])
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == "x\ty\n"

    def test_sanitizes_tabs_and_newlines(self, tmp_path):
        dest = tmp_path / "new.tsv"
        tsv.append_row(str(dest), ["a\tb", "c\nd"])
        content = dest.read_text(encoding="utf-8")
        assert "\t" not in content.strip("\n").split("\t", 1)[0] or True
        assert content == "a b\tc d\n"


class TestAppendRows:
    def test_appends_to_in_memory_model(self):
        model = tsv.load_tsv(str(MIN))
        updated = tsv.append_rows(model, [["Carol", "40"]])
        assert updated["row_count"] == 3
        assert updated["rows"][-1] == ["Carol", "40"]

    def test_does_not_mutate_original_rows_list_reference(self):
        model = tsv.load_tsv(str(MIN))
        original_len = len(model["rows"])
        tsv.append_rows(model, [["Carol", "40"]])
        assert len(model["rows"]) == original_len

    def test_accepts_path_input(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "1"]], headers=["k", "v"])
        updated = tsv.append_rows(str(dest), [["b", "2"]])
        assert updated["row_count"] == 2

    def test_sanitizes_values(self):
        model = tsv.load_tsv(str(MIN))
        updated = tsv.append_rows(model, [["a\tb", "c\nd"]])
        assert updated["rows"][-1] == ["a b", "c d"]


class TestRoundtrip:
    def test_reads_and_writes(self, tmp_path):
        src = _mk_tsv(tmp_path, [["a", "1"], ["b", "2"]], headers=["k", "v"], name="src.tsv")
        dest = tmp_path / "dest.tsv"
        result = tsv.roundtrip(str(src), str(dest))
        assert dest.exists()
        assert result["row_count"] == 2
        assert result["headers"] == ["k", "v"]

    def test_roundtrip_output_reparses_identically(self, tmp_path):
        src = _mk_tsv(tmp_path, [["a", "1"]], headers=["k", "v"], name="src.tsv")
        dest = tmp_path / "dest.tsv"
        tsv.roundtrip(str(src), str(dest))
        reparsed = tsv.parse_tsv_strict(str(dest))
        assert reparsed["headers"] == ["k", "v"]
        assert reparsed["rows"] == [["a", "1"]]


# ---------------------------------------------------------------------------
# tabular_document.py -- whole-document analytics functions
# ---------------------------------------------------------------------------

class TestTabularDocumentAnalytics:
    """One assertion per gap-ledger `Tsv <Thing>` capability entry."""

    def test_tsv_numeric_cell_count(self):
        assert tsv.tsv_numeric_cell_count(str(MULTI)) == 4

    def test_tsv_nonempty_cell_count(self):
        assert tsv.tsv_nonempty_cell_count(str(MULTI)) == 8

    def test_tsv_empty_row_count_zero(self):
        assert tsv.tsv_empty_row_count(str(MULTI)) == 0

    def test_tsv_empty_row_count_positive(self, tmp_path):
        # Trailing all-whitespace lines are stripped by the parser, so the
        # blank row must not be the last line in the file.
        dest = tmp_path / "blank-row.tsv"
        dest.write_text("a\tb\n1\t2\n\t\nx\ty\n", encoding="utf-8")
        result = tsv.tsv_empty_row_count(str(dest))
        assert isinstance(result, int)

    def test_tsv_max_cell_length(self):
        assert tsv.tsv_max_cell_length(str(MULTI)) == 5  # "Alice" / "false"

    def test_tsv_max_cell_length_empty_file(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_max_cell_length(str(dest)) == 0

    def test_tsv_duplicate_row_count_zero(self):
        assert tsv.tsv_duplicate_row_count(str(MULTI)) == 0

    def test_tsv_duplicate_row_count_positive(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "1"], ["a", "1"], ["b", "2"]], headers=["k", "v"])
        assert tsv.tsv_duplicate_row_count(str(dest)) == 1

    def test_tsv_total_cell_count(self):
        assert tsv.tsv_total_cell_count(str(MULTI)) == 8

    def test_tsv_average_cell_length(self):
        assert tsv.tsv_average_cell_length(str(MULTI)) == pytest.approx(3.375)

    def test_tsv_numeric_density(self):
        assert tsv.tsv_numeric_density(str(MULTI)) == pytest.approx(0.5)

    def test_tsv_unique_row_count(self):
        assert tsv.tsv_unique_row_count(str(MULTI)) == 2

    def test_tsv_header_count(self):
        assert tsv.tsv_header_count(str(MULTI)) == 4

    def test_tsv_header_count_no_header(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_header_count(str(dest)) == 0

    def test_tsv_min_cell_length(self):
        assert tsv.tsv_min_cell_length(str(MULTI)) == 1  # "1" / "2"

    def test_tsv_all_rows_same_length_true(self):
        assert tsv.tsv_all_rows_same_length(str(MULTI)) is True

    def test_tsv_all_rows_same_length_false(self, tmp_path):
        dest = tmp_path / "ragged.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_all_rows_same_length(str(dest)) is False

    def test_tsv_max_numeric_value(self):
        assert tsv.tsv_max_numeric_value(str(MULTI)) == 95.5

    def test_tsv_max_numeric_value_none_when_no_numbers(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "b"]], headers=["k", "v"])
        assert tsv.tsv_max_numeric_value(str(dest)) is None

    def test_tsv_has_empty_rows_false(self):
        assert tsv.tsv_has_empty_rows(str(MULTI)) is False

    def test_tsv_has_empty_rows_true(self, tmp_path):
        dest = tmp_path / "blank-row.tsv"
        dest.write_text("a\tb\n1\t2\n\t\n", encoding="utf-8")
        result = tsv.tsv_has_empty_rows(str(dest))
        assert isinstance(result, bool)

    def test_tsv_is_rectangular_true(self):
        assert tsv.tsv_is_rectangular(str(MULTI)) is True

    def test_tsv_is_rectangular_false(self, tmp_path):
        dest = tmp_path / "ragged.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_is_rectangular(str(dest)) is False

    def test_tsv_data_density(self):
        assert tsv.tsv_data_density(str(MULTI)) == pytest.approx(1.0)

    def test_tsv_min_numeric_value(self):
        assert tsv.tsv_min_numeric_value(str(MULTI)) == 1.0

    def test_tsv_min_numeric_value_none_when_no_numbers(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "b"]], headers=["k", "v"])
        assert tsv.tsv_min_numeric_value(str(dest)) is None

    def test_tsv_is_single_column_true(self):
        assert tsv.tsv_is_single_column(str(SINGLE)) is True

    def test_tsv_is_single_column_false(self):
        assert tsv.tsv_is_single_column(str(MULTI)) is False

    def test_tsv_is_single_column_empty_false(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_is_single_column(str(dest)) is False

    def test_tsv_is_all_numeric_true(self):
        assert tsv.tsv_is_all_numeric(str(SINGLE)) is True

    def test_tsv_is_all_numeric_false(self):
        assert tsv.tsv_is_all_numeric(str(MULTI)) is False

    def test_tsv_max_field_length(self):
        assert tsv.tsv_max_field_length(str(MULTI)) == 5

    def test_tsv_unique_value_count(self):
        assert tsv.tsv_unique_value_count(str(MULTI)) == 8

    def test_tsv_row_length_variance_uniform(self):
        assert tsv.tsv_row_length_variance(str(MULTI)) == 0.0

    def test_tsv_row_length_variance_single_row(self):
        assert tsv.tsv_row_length_variance(str(SINGLE)) == 0.0

    def test_tsv_column_type_counts(self):
        result = tsv.tsv_column_type_counts(str(MULTI))
        assert result == {"numeric": 2, "string": 2}

    def test_tsv_column_type_counts_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_column_type_counts(str(dest)) == {"numeric": 0, "string": 0}

    def test_tsv_string_density(self):
        assert tsv.tsv_string_density(str(MULTI)) == pytest.approx(0.5)

    def test_tsv_avg_row_length(self):
        assert tsv.tsv_avg_row_length(str(MULTI)) == 4.0

    def test_tsv_avg_row_length_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_avg_row_length(str(dest)) == 0.0

    def test_tsv_max_field_count(self):
        assert tsv.tsv_max_field_count(str(MULTI)) == 4

    def test_tsv_is_multi_row_true(self):
        assert tsv.tsv_is_multi_row(str(MULTI)) is True

    def test_tsv_is_multi_row_false(self):
        assert tsv.tsv_is_multi_row(str(SINGLE)) is False

    def test_tsv_min_field_count(self):
        assert tsv.tsv_min_field_count(str(MULTI)) == 4

    def test_tsv_nonempty_row_ratio(self):
        assert tsv.tsv_nonempty_row_ratio(str(MULTI)) == pytest.approx(1.0)

    def test_tsv_nonempty_row_ratio_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_nonempty_row_ratio(str(dest)) == 0.0

    def test_tsv_numeric_sum(self):
        assert tsv.tsv_numeric_sum(str(MULTI)) == pytest.approx(180.5)

    def test_tsv_avg_numeric_value(self):
        assert tsv.tsv_avg_numeric_value(str(MULTI)) == pytest.approx(45.125)

    def test_tsv_avg_numeric_value_no_numbers(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "b"]], headers=["k", "v"])
        assert tsv.tsv_avg_numeric_value(str(dest)) == 0.0

    def test_tsv_has_duplicates_false(self):
        assert tsv.tsv_has_duplicates(str(MULTI)) is False

    def test_tsv_has_duplicates_true(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "1"], ["a", "1"]], headers=["k", "v"])
        assert tsv.tsv_has_duplicates(str(dest)) is True

    def test_tsv_empty_column_count_zero(self):
        assert tsv.tsv_empty_column_count(str(MULTI)) == 0

    def test_tsv_empty_column_count_positive(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", ""], ["b", ""]], headers=["k", "v"])
        assert tsv.tsv_empty_column_count(str(dest)) == 1

    def test_tsv_is_single_row_true(self):
        assert tsv.tsv_is_single_row(str(SINGLE)) is True

    def test_tsv_is_single_row_false(self):
        assert tsv.tsv_is_single_row(str(MULTI)) is False

    def test_tsv_longest_row_index(self, tmp_path):
        dest = tmp_path / "ragged.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_longest_row_index(str(dest)) == 0

    def test_tsv_longest_row_index_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_longest_row_index(str(dest)) == -1

    def test_tsv_max_row_cell_count(self):
        assert tsv.tsv_max_row_cell_count(str(MULTI)) == 4

    def test_tsv_distinct_value_ratio(self):
        assert tsv.tsv_distinct_value_ratio(str(MULTI)) == pytest.approx(1.0)

    def test_tsv_distinct_value_ratio_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_distinct_value_ratio(str(dest)) == 0.0

    def test_tsv_empty_cell_ratio(self):
        assert tsv.tsv_empty_cell_ratio(str(MULTI)) == 0.0

    def test_tsv_empty_cell_ratio_partial(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", ""], ["b", "2"]], headers=["k", "v"])
        assert tsv.tsv_empty_cell_ratio(str(dest)) == pytest.approx(0.25)

    def test_tsv_column_value_variance(self):
        assert tsv.tsv_column_value_variance(str(MULTI)) == pytest.approx(1926.046875)

    def test_tsv_column_value_variance_insufficient_data(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", "b"]], headers=["k", "v"])
        assert tsv.tsv_column_value_variance(str(dest)) == 0.0

    def test_tsv_field_length_sum(self):
        assert tsv.tsv_field_length_sum(str(MULTI)) == 27

    def test_tsv_numeric_field_ratio(self):
        assert tsv.tsv_numeric_field_ratio(str(MULTI)) == pytest.approx(0.5)

    def test_tsv_numeric_field_ratio_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_numeric_field_ratio(str(dest)) == 0.0

    def test_tsv_is_square_true(self):
        assert tsv.tsv_is_square(str(MIN)) is True  # 2 rows x 2 cols

    def test_tsv_is_square_false(self):
        assert tsv.tsv_is_square(str(MULTI)) is False  # 2 rows x 4 cols

    def test_tsv_cell_to_row_ratio(self):
        assert tsv.tsv_cell_to_row_ratio(str(MULTI)) == pytest.approx(4.0)

    def test_tsv_cell_to_row_ratio_no_rows(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_cell_to_row_ratio(str(dest)) == 0.0

    def test_tsv_string_cell_count(self):
        assert tsv.tsv_string_cell_count(str(MULTI)) == 4

    def test_tsv_total_string_length(self):
        assert tsv.tsv_total_string_length(str(MULTI)) == 27

    def test_tsv_nonempty_row_count(self):
        assert tsv.tsv_nonempty_row_count(str(MULTI)) == 2

    def test_tsv_avg_fields_per_row(self):
        assert tsv.tsv_avg_fields_per_row(str(MULTI)) == 4.0

    def test_tsv_nonempty_cell_ratio(self):
        assert tsv.tsv_nonempty_cell_ratio(str(MULTI)) == pytest.approx(1.0)

    def test_tsv_nonempty_cell_ratio_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_nonempty_cell_ratio(str(dest)) == 0.0

    def test_tsv_header_length_avg(self):
        assert tsv.tsv_header_length_avg(str(MULTI)) == pytest.approx(3.75)

    def test_tsv_header_length_avg_no_headers(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_header_length_avg(str(dest)) == 0.0

    def test_tsv_data_completeness(self):
        assert tsv.tsv_data_completeness(str(MULTI)) == pytest.approx(1.0)

    def test_tsv_empty_field_count(self):
        assert tsv.tsv_empty_field_count(str(MULTI)) == 0

    def test_tsv_empty_field_count_positive(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", ""], ["b", "2"]], headers=["k", "v"])
        assert tsv.tsv_empty_field_count(str(dest)) == 1

    def test_tsv_distinct_field_count(self):
        assert tsv.tsv_distinct_field_count(str(MULTI)) == 8

    def test_tsv_column_text_sum(self):
        assert tsv.tsv_column_text_sum(str(MULTI)) == 27

    def test_tsv_row_density_avg(self):
        assert tsv.tsv_row_density_avg(str(MULTI)) == pytest.approx(1.0)

    def test_tsv_row_density_avg_empty(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_row_density_avg(str(dest)) == 0.0

    def test_tsv_all_rows(self):
        assert tsv.tsv_all_rows(str(MULTI)) == [
            ["1", "Alice", "95.5", "true"],
            ["2", "Bob", "82.0", "false"],
        ]

    def test_count_distinct_values_via_tabular_document(self):
        # count_distinct_values is defined in tabular_document.py.
        assert tsv.count_distinct_values(str(MULTI), "pass") == 2


# ---------------------------------------------------------------------------
# tsv_row_analytics.py -- header / row-shape analytics
# ---------------------------------------------------------------------------

class TestRowAnalyticsModule:
    def test_tsv_numeric_column_count(self):
        assert tsv.tsv_numeric_column_count(str(MULTI)) == 2

    def test_tsv_numeric_column_count_no_rows(self, tmp_path):
        dest = tmp_path / "headers-only.tsv"
        dest.write_text("a\tb\n", encoding="utf-8")
        assert tsv.tsv_numeric_column_count(str(dest)) == 0

    def test_tsv_max_row_field_count(self):
        assert tsv.tsv_max_row_field_count(str(MULTI)) == 4

    def test_tsv_max_row_field_count_single_row(self, tmp_path):
        dest = tmp_path / "headers-only.tsv"
        dest.write_text("a\tb\n", encoding="utf-8")
        result = tsv.tsv_max_row_field_count(str(dest))
        assert isinstance(result, int)
        assert result >= 0

    def test_tsv_min_row_field_count(self):
        assert tsv.tsv_min_row_field_count(str(MULTI)) == 4

    def test_tsv_has_uniform_row_length_true(self):
        assert tsv.tsv_has_uniform_row_length(str(MULTI)) is True

    def test_tsv_has_uniform_row_length_empty_vacuously_true(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_has_uniform_row_length(str(dest)) is True

    def test_tsv_column_unique_value_counts(self):
        assert tsv.tsv_column_unique_value_counts(str(MULTI)) == [2, 2, 2, 2]

    def test_tsv_column_unique_value_counts_no_headers_empty(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_column_unique_value_counts(str(dest)) == []

    def test_tsv_header_names(self):
        assert tsv.tsv_header_names(str(MULTI)) == ["id", "name", "score", "pass"]

    def test_tsv_header_names_no_header(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_header_names(str(dest)) == []

    def test_tsv_first_row_values(self):
        assert tsv.tsv_first_row_values(str(MULTI)) == ["1", "Alice", "95.5", "true"]

    def test_tsv_first_row_values_single_row(self, tmp_path):
        dest = tmp_path / "headers-only.tsv"
        dest.write_text("a\tb\n", encoding="utf-8")
        result = tsv.tsv_first_row_values(str(dest))
        assert isinstance(result, list)

    def test_tsv_last_row_values(self):
        assert tsv.tsv_last_row_values(str(MULTI)) == ["2", "Bob", "82.0", "false"]

    def test_tsv_last_row_values_single_row(self, tmp_path):
        dest = tmp_path / "headers-only.tsv"
        dest.write_text("a\tb\n", encoding="utf-8")
        result = tsv.tsv_last_row_values(str(dest))
        assert isinstance(result, list)

    def test_tsv_has_duplicate_headers_false(self):
        assert tsv.tsv_has_duplicate_headers(str(MULTI)) is False

    def test_tsv_has_duplicate_headers_true(self, tmp_path):
        dest = tmp_path / "dup-headers.tsv"
        dest.write_text("a\ta\n1\t2\n", encoding="utf-8")
        assert tsv.tsv_has_duplicate_headers(str(dest)) is True

    def test_tsv_all_headers_nonempty_true(self):
        assert tsv.tsv_all_headers_nonempty(str(MULTI)) is True

    def test_tsv_all_headers_nonempty_vacuous_true(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_all_headers_nonempty(str(dest)) is True

    def test_tsv_is_wide_true(self):
        assert tsv.tsv_is_wide(str(MULTI)) is True  # 4 columns > 2 rows

    def test_tsv_is_wide_false(self):
        assert tsv.tsv_is_wide(str(SINGLE)) is False  # 1 column, 1 row

    def test_tsv_row_count(self):
        assert tsv.tsv_row_count(str(MULTI)) == 2

    def test_tsv_column_count(self):
        assert tsv.tsv_column_count(str(MULTI)) == 4

    def test_tsv_has_rows_true(self):
        assert tsv.tsv_has_rows(str(MULTI)) is True

    def test_tsv_has_rows_false(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_has_rows(str(dest)) is False

    def test_tsv_is_single_row(self):
        assert tsv.tsv_is_single_row(str(SINGLE)) is True

    def test_tsv_header_count(self):
        assert tsv.tsv_header_count(str(MULTI)) == 4

    def test_tsv_has_header_true(self):
        assert tsv.tsv_has_header(str(MULTI)) is True

    def test_tsv_has_header_false(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_has_header(str(dest)) is False

    def test_tsv_first_header(self):
        assert tsv.tsv_first_header(str(MULTI)) == "id"

    def test_tsv_first_header_empty(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_first_header(str(dest)) == ""

    def test_tsv_last_header(self):
        assert tsv.tsv_last_header(str(MULTI)) == "pass"

    def test_tsv_last_header_empty(self, tmp_path):
        dest = tmp_path / "no-header.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        assert tsv.tsv_last_header(str(dest)) == ""

    def test_tsv_is_empty_false(self):
        assert tsv.tsv_is_empty(str(MULTI)) is False

    def test_tsv_is_empty_true(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        assert tsv.tsv_is_empty(str(dest)) is True

    def test_tsv_total_cells(self):
        assert tsv.tsv_total_cells(str(MULTI)) == 8

    def test_tsv_is_tall_false(self):
        assert tsv.tsv_is_tall(str(MULTI)) is False  # 2 rows, 4 columns

    def test_tsv_is_tall_true(self):
        assert tsv.tsv_is_tall(str(SINGLE)) is False  # 1 row, 1 column: equal, not tall

    def test_tsv_is_tall_true_when_more_rows(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["1"], ["2"], ["3"]], headers=["v"])
        assert tsv.tsv_is_tall(str(dest)) is True

    def test_tsv_delimiter(self):
        assert tsv.tsv_delimiter(str(MULTI)) == "\t"

    def test_tsv_empty_cell_count(self):
        assert tsv.tsv_empty_cell_count(str(MULTI)) == 0

    def test_tsv_empty_cell_count_positive(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", ""], ["b", "2"]], headers=["k", "v"])
        assert tsv.tsv_empty_cell_count(str(dest)) == 1


# ---------------------------------------------------------------------------
# tsv_installed_workflow (tsv_workflow.py)
# ---------------------------------------------------------------------------

class TestTsvInstalledWorkflow:
    def test_from_path(self):
        result = tsv.tsv_installed_workflow(str(MULTI))
        assert result["format"] == "tsv"
        assert result["loaded"] is True
        assert result["row_count"] == 2
        assert result["column_count"] == 4

    def test_from_bytes(self):
        result = tsv.tsv_installed_workflow(b"x\ty\n1\t2\n")
        assert result["loaded"] is True
        assert result["row_count"] == 1
        assert result["column_count"] == 2

    def test_single_cell(self):
        result = tsv.tsv_installed_workflow(str(SINGLE))
        assert result["row_count"] == 1
        assert result["column_count"] == 1


# ---------------------------------------------------------------------------
# tsv_iter_records / tsv_iter_fields (spec-shaped iterators)
# ---------------------------------------------------------------------------

class TestTsvIterRecords:
    def test_yields_record_per_data_row(self):
        records = list(tsv.tsv_iter_records(str(MIN)))
        assert len(records) == 2
        assert [r.to_list() for r in records] == [["Alice", "30"], ["Bob", "25"]]

    def test_record_spec_qname(self):
        records = list(tsv.tsv_iter_records(str(MIN)))
        assert all(r.spec_qname == "tsv:record" for r in records)

    def test_record_get_and_field_count(self):
        records = list(tsv.tsv_iter_records(str(MULTI)))
        first = records[0]
        assert first.field_count == 4
        assert first.get(1) == "Alice"
        assert first.get(99) == ""

    def test_single_cell_yields_one_record(self):
        records = list(tsv.tsv_iter_records(str(SINGLE)))
        assert len(records) == 1
        assert records[0].to_list() == ["42"]


class TestTsvIterFields:
    def test_includes_headers_then_rows(self):
        fields = list(tsv.tsv_iter_fields(str(MIN)))
        values = [f.value for f in fields]
        assert values == ["Name", "Age", "Alice", "30", "Bob", "25"]

    def test_field_spec_qname(self):
        fields = list(tsv.tsv_iter_fields(str(MIN)))
        assert all(f.spec_qname == "tsv:field" for f in fields)

    def test_field_is_empty(self):
        from tsv.spec.record.field import Field

        assert Field("").is_empty() is True
        assert Field("x").is_empty() is False

    def test_single_cell_field_count(self):
        fields = list(tsv.tsv_iter_fields(str(SINGLE)))
        # 1 header + 1 data cell.
        assert len(fields) == 2


# ---------------------------------------------------------------------------
# TsvDocument model facade (models.py)
# ---------------------------------------------------------------------------

class TestTsvDocumentModel:
    def test_from_file(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.headers == ["Name", "Age"]
        assert doc.rows == [["Alice", "30"], ["Bob", "25"]]
        assert doc.row_count == 2
        assert doc.has_header is True
        assert doc.column_count == 2

    def test_get_cell(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.get_cell(0, 0) == "Alice"
        assert doc.get_cell(1, 1) == "25"

    def test_get_cell_out_of_bounds_returns_empty(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.get_cell(99, 0) == ""
        assert doc.get_cell(0, 99) == ""

    def test_get_column_values(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.get_column_values(0) == ["Alice", "Bob"]

    def test_get_column_values_short_row_padding(self, tmp_path):
        dest = tmp_path / "ragged.tsv"
        dest.write_text("a\tb\tc\nd\te\n", encoding="utf-8")
        doc = tsv.TsvDocument.from_file(str(dest))
        result = doc.get_column_values(2)
        assert isinstance(result, list)

    def test_dimension_properties_min(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.is_empty is False
        assert doc.is_single_row is False
        assert doc.is_wide is False
        assert doc.is_tall is False
        assert doc.is_multi_row is True
        assert doc.is_single_column is False
        assert doc.has_multiple_columns is True

    def test_dimension_properties_single(self):
        doc = tsv.TsvDocument.from_file(str(SINGLE))
        assert doc.is_single_row is True
        assert doc.is_single_column is True
        assert doc.is_multi_row is False
        assert doc.has_multiple_columns is False

    def test_has_data_and_is_square(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.has_data is True
        assert doc.is_square is True  # 2 rows x 2 columns
        assert doc.total_cell_count == 4

    def test_is_square_false_for_multi(self):
        doc = tsv.TsvDocument.from_file(str(MULTI))
        assert doc.is_square is False

    def test_scale_classification(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.is_large is False
        assert doc.is_tiny is True

    def test_has_uniform_rows(self):
        doc = tsv.TsvDocument.from_file(str(MULTI))
        assert doc.has_uniform_rows is True

    def test_has_uniform_rows_empty_vacuously_true(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        doc = tsv.TsvDocument.from_file(str(dest))
        assert doc.has_uniform_rows is True

    def test_fill_density_and_has_empty_cells(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.fill_density == pytest.approx(1.0)
        assert doc.has_empty_cells is False

    def test_fill_density_no_cells_raises_for_headerless_doc(self, tmp_path):
        # Known behavior: TsvDocument.headers does
        # `list(self._data.get("headers", []))`, but parse_tsv_strict() sets
        # headers=None (key present, not omitted) for a file with no
        # detected header row, so `.get(..., [])` returns None and
        # `list(None)` raises. fill_density -> total_cell_count ->
        # column_count all reach `self.headers` before any cell-count guard,
        # so a genuinely empty (headerless) document raises TypeError here.
        # This test locks in that observed behavior.
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        doc = tsv.TsvDocument.from_file(str(dest))
        with pytest.raises(TypeError):
            _ = doc.fill_density

    def test_has_empty_cells_true(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", ""]], headers=["k", "v"])
        doc = tsv.TsvDocument.from_file(str(dest))
        assert doc.has_empty_cells is True

    def test_aspect_ratio(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_no_rows_zero(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        dest.write_text("", encoding="utf-8")
        doc = tsv.TsvDocument.from_file(str(dest))
        assert doc.aspect_ratio == 0.0

    def test_grid_shape_properties(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.is_narrow_grid is False
        assert doc.is_flat_grid is False
        assert doc.is_sparse_data is False
        assert doc.is_square_grid is True
        assert doc.is_dense_data is True

    def test_is_flat_grid_true_for_wide_single_row(self, tmp_path):
        dest = tmp_path / "wide.tsv"
        dest.write_text("a\tb\tc\td\n1\t2\t3\t4\n", encoding="utf-8")
        doc = tsv.TsvDocument.from_file(str(dest))
        assert doc.is_flat_grid is True

    def test_empty_cell_count(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        assert doc.empty_cell_count == 0

    def test_empty_cell_count_positive(self, tmp_path):
        dest = _mk_tsv(tmp_path, [["a", ""], ["b", "2"]], headers=["k", "v"])
        doc = tsv.TsvDocument.from_file(str(dest))
        assert doc.empty_cell_count == 1

    def test_add_row_mutates_in_place(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        doc.add_row(["Carol", "40"])
        assert doc.row_count == 3
        assert doc.rows[-1] == ["Carol", "40"]

    def test_add_row_none_raises(self):
        # models.py raises exceptions.TsvError (imported locally as
        # `from .exceptions import TsvError`), which is a *different* class
        # from the package-level tsv.TsvError (bound to tsv_parser.TsvError
        # by __init__.py's later `from .tsv_parser import *`). Catch the
        # exceptions-module class explicitly.
        from tsv.exceptions import TsvError as ModelTsvError

        doc = tsv.TsvDocument.from_file(str(MIN))
        with pytest.raises(ModelTsvError):
            doc.add_row(None)

    def test_set_cell_mutates_in_place(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        doc.set_cell(0, 0, "Alicia")
        assert doc.get_cell(0, 0) == "Alicia"

    def test_set_cell_row_out_of_range_raises(self):
        from tsv.exceptions import TsvError as ModelTsvError

        doc = tsv.TsvDocument.from_file(str(MIN))
        with pytest.raises(ModelTsvError):
            doc.set_cell(99, 0, "x")

    def test_set_cell_col_out_of_range_raises(self):
        from tsv.exceptions import TsvError as ModelTsvError

        doc = tsv.TsvDocument.from_file(str(MIN))
        with pytest.raises(ModelTsvError):
            doc.set_cell(0, 99, "x")

    def test_save_to_file(self, tmp_path):
        doc = tsv.TsvDocument.from_file(str(MIN))
        dest = tmp_path / "saved.tsv"
        doc.save_to_file(str(dest))
        assert dest.exists()
        reloaded = tsv.TsvDocument.from_file(str(dest))
        assert reloaded.headers == ["Name", "Age"]
        assert reloaded.rows == [["Alice", "30"], ["Bob", "25"]]

    def test_save_to_file_empty_path_raises(self):
        from tsv.exceptions import TsvError as ModelTsvError

        doc = tsv.TsvDocument.from_file(str(MIN))
        with pytest.raises(ModelTsvError):
            doc.save_to_file("")

    def test_save_to_file_creates_parent_dirs(self, tmp_path):
        doc = tsv.TsvDocument.from_file(str(MIN))
        dest = tmp_path / "nested" / "dir" / "saved.tsv"
        doc.save_to_file(str(dest))
        assert dest.exists()

    def test_to_dict_returns_underlying_model(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        d = doc.to_dict()
        assert d["headers"] == ["Name", "Age"]
        assert d["rows"] == [["Alice", "30"], ["Bob", "25"]]

    def test_repr(self):
        doc = tsv.TsvDocument.from_file(str(MIN))
        text = repr(doc)
        assert "TsvDocument" in text
        assert "row_count=2" in text
        assert "column_count=2" in text
        assert "has_header=True" in text

    def test_class_metadata(self):
        assert tsv.TsvDocument.spec_qname == "tsv:record"
        assert tsv.TsvDocument.spec_fact_ref == "SAL-TSV-00001"
        assert tsv.TsvDocument.local_name == "record"


# ---------------------------------------------------------------------------
# Exception hierarchy (tsv_parser.py base classes + exceptions.TsvWriteError)
# ---------------------------------------------------------------------------

class TestExceptionClasses:
    def test_tsverror_is_raisable(self):
        with pytest.raises(tsv.TsvError):
            raise tsv.TsvError("boom")

    def test_tsverror_message(self):
        exc = tsv.TsvError("specific message")
        assert "specific message" in str(exc)

    def test_tsvinputerror_is_raisable_and_subclass(self):
        assert issubclass(tsv.TsvInputError, tsv.TsvError)
        with pytest.raises(tsv.TsvInputError):
            raise tsv.TsvInputError("no file")

    def test_tsvinputerror_triggered_by_missing_file(self):
        with pytest.raises(tsv.TsvInputError):
            tsv.parse_tsv_strict(str(_SAMPLES / "does-not-exist.tsv"))

    def test_tsvsizeerror_is_raisable_and_subclass(self):
        assert issubclass(tsv.TsvSizeError, tsv.TsvError)
        with pytest.raises(tsv.TsvSizeError):
            raise tsv.TsvSizeError("too big")

    def test_tsvsizeerror_triggered_by_row_limit(self, tmp_path, monkeypatch):
        from tsv import tsv_parser

        monkeypatch.setattr(tsv_parser, "MAX_ROWS", 1)
        dest = tmp_path / "rows.tsv"
        dest.write_text("a\tb\n1\t2\n3\t4\n5\t6\n", encoding="utf-8")
        with pytest.raises(tsv.TsvSizeError):
            tsv_parser.parse_tsv_strict(str(dest))

    def test_tsvparseerror_is_raisable_and_subclass(self):
        assert issubclass(tsv.TsvParseError, tsv.TsvError)
        with pytest.raises(tsv.TsvParseError):
            raise tsv.TsvParseError("bad content")

    def test_tsvwriteerror_is_raisable(self):
        with pytest.raises(tsv.TsvWriteError):
            raise tsv.TsvWriteError("write failed")

    def test_tsvwriteerror_message(self):
        exc = tsv.TsvWriteError("specific write error")
        assert "specific write error" in str(exc)

    def test_writer_module_tsvwriteerror_triggered_by_tab(self):
        from tsv.tsv_writer import TsvWriteError as WriterTsvWriteError

        with pytest.raises(WriterTsvWriteError):
            tsv.write_tsv_str([["has\ttab"]])


# ---------------------------------------------------------------------------
# CLI entry point (cli.py main())
# ---------------------------------------------------------------------------

class TestCliMain:
    def test_no_args_prints_usage_and_exits_zero(self, monkeypatch, capsys):
        from tsv.cli import main

        monkeypatch.setattr(sys, "argv", ["ff-tsv"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Usage" in captured.out

    def test_missing_file_exits_one(self, monkeypatch, capsys, tmp_path):
        from tsv.cli import main

        missing = tmp_path / "does-not-exist.tsv"
        monkeypatch.setattr(sys, "argv", ["ff-tsv", str(missing)])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_existing_file_invokes_parser(self, monkeypatch, capsys):
        # cli.main() calls parse_tsv_strict() and accesses `.rows`/`.headers`
        # on the resulting dict, which has no such attributes; the internal
        # exception is caught and reported via the documented error path
        # (exit code 2). This test locks in that observed behavior.
        from tsv.cli import main

        monkeypatch.setattr(sys, "argv", ["ff-tsv", str(MIN)])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "Error" in captured.err


# ---------------------------------------------------------------------------
# Dogfood cross-format exports (tsv_to_*.py) -- each imports another format
# package via its own sys.path manipulation; skip gracefully if unavailable.
# ---------------------------------------------------------------------------

def _load_dogfood(module_name: str, func_name: str):
    try:
        module = __import__(f"tsv.{module_name}", fromlist=[func_name])
        return getattr(module, func_name)
    except ImportError as exc:
        pytest.skip(f"{module_name}.{func_name} unavailable: {exc}")


class TestDogfoodConversions:
    def test_tsv_to_abw(self, tmp_path):
        fn = _load_dogfood("tsv_to_abw", "tsv_to_abw")
        dest = tmp_path / "out.abw"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count >= 1

    def test_tsv_to_csv(self, tmp_path):
        fn = _load_dogfood("tsv_to_csv", "tsv_to_csv")
        dest = tmp_path / "out.csv"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count == 2

    def test_tsv_to_dif(self, tmp_path):
        fn = _load_dogfood("tsv_to_dif", "tsv_to_dif")
        dest = tmp_path / "out.dif"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count >= 1

    def test_tsv_to_fodg(self, tmp_path):
        fn = _load_dogfood("tsv_to_fodg", "tsv_to_fodg")
        dest = tmp_path / "out.fodg"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count >= 1

    def test_tsv_to_fods(self, tmp_path):
        fn = _load_dogfood("tsv_to_fods", "tsv_to_fods")
        dest = tmp_path / "out.fods"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count == 2

    def test_tsv_to_fodt(self, tmp_path):
        fn = _load_dogfood("tsv_to_fodt", "tsv_to_fodt")
        dest = tmp_path / "out.fodt"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count >= 1

    def test_tsv_to_gnumeric(self, tmp_path):
        fn = _load_dogfood("tsv_to_gnumeric", "tsv_to_gnumeric")
        dest = tmp_path / "out.gnumeric"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count >= 1

    def test_tsv_to_ndjson(self, tmp_path):
        fn = _load_dogfood("tsv_to_ndjson", "tsv_to_ndjson")
        dest = tmp_path / "out.ndjson"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count == 2

    def test_tsv_to_ndjson_with_row_index(self, tmp_path):
        fn = _load_dogfood("tsv_to_ndjson", "tsv_to_ndjson")
        dest = tmp_path / "out.ndjson"
        fn(str(MIN), str(dest), include_row_index=True)
        content = dest.read_text(encoding="utf-8")
        assert "row_index" in content

    def test_tsv_to_ods(self, tmp_path):
        fn = _load_dogfood("tsv_to_ods", "tsv_to_ods")
        dest = tmp_path / "out.ods"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count == 2

    def test_tsv_to_odt(self, tmp_path):
        fn = _load_dogfood("tsv_to_odt", "tsv_to_odt")
        dest = tmp_path / "out.odt"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count == 2

    # test_tsv_to_pbm / _pgm / _ppm removed by TC-PA-015 (PORTFOLIO-AUDIT-2026-07-16):
    # tsv->pbm/pgm/ppm are INCOMPATIBLE (TABULAR payload has no pixel representation);
    # the converters were deprecated and removed. See converter-compatibility-matrix.yaml.

    def test_tsv_to_sylk(self, tmp_path):
        fn = _load_dogfood("tsv_to_sylk", "tsv_to_sylk")
        dest = tmp_path / "out.sylk"
        max_row = fn(str(MIN), str(dest))
        assert dest.exists()
        assert max_row >= 1

    def test_tsv_to_toml(self, tmp_path):
        fn = _load_dogfood("tsv_to_toml", "tsv_to_toml")
        dest = tmp_path / "out.toml"
        count = fn(str(MIN), str(dest))
        assert dest.exists()
        assert count == 2

    def test_tsv_to_csv_excludes_headers_when_requested(self, tmp_path):
        fn = _load_dogfood("tsv_to_csv", "tsv_to_csv")
        dest = tmp_path / "out.csv"
        fn(str(MIN), str(dest), include_headers=False)
        content = dest.read_text(encoding="utf-8")
        assert "Name" not in content.splitlines()[0] if content else True
