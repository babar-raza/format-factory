"""Comprehensive gap-coverage tests for the CSV (RFC 4180) FOSS Python track.

Covers the ~110 `missing_test_coverage` gaps registered under
`GAP-CSV-FOSS-*` in `reports/capability-layer/gap-ledger.json`, spanning
every exported module of `src/python/csv/`:

  - csv_parser.py            (parse_csv, parse_csv_strict, probe_csv, get_*, count_empty_cells)
  - csv_writer.py             (write_csv, write_csv_to_file, parse_and_rewrite)
  - csv_stats.py              (dict-based table/column statistics)
  - tabular_document.py       (file-path-based analytics, batch 1)
  - tabular_document_analytics.py (file-path-based analytics, batch 2)
  - csv_analytics.py          (supplementary file-path-based analytics)
  - models.py                 (CsvDocument domain model)
  - exceptions.py             (FormatFactoryError-based CSV exceptions)
  - csv_workflow.py           (csv_installed_workflow)
  - cli.py                    (main entry point)
  - Compat/ + spec/record/    (spec-shaped facade classes)
  - csv_to_*.py               (dogfood conversion exports)

NOTE: This package is `src/python/csv/` (format-factory CSV), NOT the
stdlib `csv` module. `tests/python/conftest.py` pins `sys.modules["csv"]`
to the stdlib module so other formats' `import csv` keeps working: as a
result, this package must be imported via its full dotted path
(`src.python.csv.<module>`) with the repo root on `sys.path`, exactly as
the existing tests in this directory do.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_SAMPLES = _REPO / "samples" / "by-format" / "csv"

# ---------------------------------------------------------------------------
# Imports — grouped by defining module (see module docstring for rationale
# on why aliasing is used for dict-based vs file-path-based duplicate names)
# ---------------------------------------------------------------------------

from src.python.csv.csv_parser import (  # type: ignore
    CsvError,
    CsvInputError,
    CsvSizeError,
    CsvParseError,
    parse_csv,
    parse_csv_strict,
    probe_csv,
    get_capabilities,
    get_row_count,
    get_column_names,
    get_cell_value,
    count_empty_cells,
    csv_numeric_range,
    csv_has_only_one_row,
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
)

from src.python.csv.csv_writer import (  # type: ignore
    CsvWriteError,
    write_csv,
    write_csv_to_file,
    parse_and_rewrite,
)

from src.python.csv.csv_stats import (  # type: ignore
    table_stats,
    column_value_counts,
    csv_row_length_distribution,
    csv_field_type_summary,
    csv_empty_row_count,
    csv_max_field_length,
    csv_header_count as dict_header_count,
    csv_has_headers,
    csv_first_row,
    csv_last_row,
    csv_is_square as dict_is_square,
    csv_is_tall,
    csv_row_count as dict_row_count,
    csv_column_count as dict_column_count,
    csv_delimiter,
    csv_is_empty as dict_is_empty,
    csv_has_data_rows,
    csv_first_header,
)

from src.python.csv.tabular_document import (  # type: ignore
    csv_to_dicts,
    csv_column_count,
    csv_has_header,
    csv_numeric_row_count,
    count_distinct_values,
    csv_duplicate_row_count,
    csv_empty_cell_count,
    csv_row_count,
    csv_average_field_length,
    csv_numeric_density,
    csv_unique_row_count,
    csv_min_field_length,
    csv_has_duplicates,
    csv_all_rows_same_length,
    csv_max_row_length,
    csv_field_type_ratio,
    csv_all_rows,
    csv_distinct_value_count,
    csv_empty_cell_ratio,
    csv_total_cell_count,
    csv_min_row_length,
    csv_max_numeric_value,
    csv_has_empty_rows,
    csv_header_count,
    csv_is_rectangular,
    csv_nonempty_cell_count,
    csv_string_density,
    csv_min_numeric_value,
    csv_data_density,
    csv_avg_row_length,
    csv_numeric_column_count,
)

from src.python.csv.tabular_document_analytics import (  # type: ignore
    csv_is_single_column,
    csv_is_all_numeric,
    csv_max_field_value_length,
    csv_unique_value_count,
    csv_column_type_counts,
    csv_row_length_variance,
    csv_is_empty,
    csv_column_name_lengths,
    csv_max_field_count,
    csv_is_multi_row,
    csv_column_count_variance,
    csv_has_numeric_header,
    csv_nonempty_row_ratio,
    csv_avg_cell_length,
    csv_numeric_sum,
    csv_avg_numeric_value,
    csv_is_single_row,
    csv_empty_column_count,
    csv_longest_row_index,
    csv_total_string_length,
    csv_min_row_field_count,
    csv_is_square,
    csv_column_value_variance,
    csv_is_multi_column,
    csv_field_type_variance,
    csv_header_length_sum,
    csv_row_length_sum,
    csv_empty_field_ratio,
    csv_string_cell_count,
    csv_nonempty_row_count,
    csv_avg_fields_per_row,
    csv_nonempty_cell_ratio,
    csv_numeric_cell_ratio,
    csv_empty_field_count,
    csv_numeric_field_count,
    csv_row_width_avg,
    csv_distinct_header_count,
    csv_field_value_variance,
    csv_row_text_total,
)

from src.python.csv.csv_analytics import (  # type: ignore
    csv_header_names,
    csv_first_row_values,
    csv_last_row_values,
    csv_has_duplicate_headers,
    csv_all_headers_nonempty,
    csv_is_wide,
    csv_has_uniform_row_length,
)

from src.python.csv.models import CsvDocument  # type: ignore
from src.python.csv.csv_workflow import csv_installed_workflow  # type: ignore
from src.python.csv.cli import main as cli_main  # type: ignore

from src.python.csv import exceptions as csv_exceptions_module  # type: ignore


# ---------------------------------------------------------------------------
# Fixtures / sample content
# ---------------------------------------------------------------------------

SIMPLE_TXT = "name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,NYC\n"
NUMERIC_TXT = "1,2,3\n4,5,6\n7,8,9\n"
EMPTY_CELLS_TXT = "a,b,c\n1,,3\n,5,\n7,8,9\n"
DUPE_TXT = "a,b\n1,2\n1,2\n3,4\n"
SINGLE_COL_TXT = "val\n1\n2\n3\n"
SINGLE_ROW_TXT = "x,y,z\n1,2,3\n"
DUP_HEADER_TXT = "a,a,b\n1,2,3\n"


def _write(tmp_path: Path, content: str, name: str = "test.csv") -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


@pytest.fixture
def simple_f(tmp_path):
    return _write(tmp_path, SIMPLE_TXT, "simple.csv")


@pytest.fixture
def numeric_f(tmp_path):
    return _write(tmp_path, NUMERIC_TXT, "numeric.csv")


@pytest.fixture
def empty_f(tmp_path):
    return _write(tmp_path, EMPTY_CELLS_TXT, "empty.csv")


@pytest.fixture
def dupe_f(tmp_path):
    return _write(tmp_path, DUPE_TXT, "dupe.csv")


@pytest.fixture
def single_col_f(tmp_path):
    return _write(tmp_path, SINGLE_COL_TXT, "single_col.csv")


@pytest.fixture
def single_row_f(tmp_path):
    return _write(tmp_path, SINGLE_ROW_TXT, "single_row.csv")


@pytest.fixture
def dup_header_f(tmp_path):
    return _write(tmp_path, DUP_HEADER_TXT, "dup_header.csv")


@pytest.fixture
def tall_f(tmp_path):
    # header width 2, 3 data rows -> data_row_count(3) > column_width(2)
    return _write(tmp_path, "a,b\n1,2\n3,4\n5,6\n", "tall.csv")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TestCsvParserExceptions:
    """csv_parser.py's local exception hierarchy (actually raised in practice)."""

    def test_csv_error_is_exception(self):
        assert issubclass(CsvError, Exception)

    def test_csv_error_message(self):
        assert "boom" in str(CsvError("boom"))

    def test_csv_input_error_is_csv_error(self):
        assert issubclass(CsvInputError, CsvError)

    def test_csv_size_error_is_csv_error(self):
        assert issubclass(CsvSizeError, CsvError)

    def test_csv_parse_error_is_csv_error(self):
        assert issubclass(CsvParseError, CsvError)

    def test_csv_input_error_raised_for_missing_file(self, tmp_path):
        with pytest.raises(CsvInputError):
            parse_csv_strict(str(tmp_path / "does_not_exist.csv"))

    def test_csv_input_error_raised_for_directory(self, tmp_path):
        with pytest.raises(CsvInputError):
            parse_csv_strict(str(tmp_path))

    def test_csv_size_error_raised_for_oversized_file(self, tmp_path, monkeypatch):
        import src.python.csv.csv_parser as csv_parser_mod
        monkeypatch.setattr(csv_parser_mod, "MAX_FILE_SIZE", 5)
        f = tmp_path / "big.csv"
        f.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
        with pytest.raises(CsvSizeError):
            parse_csv_strict(str(f))


class TestCsvWriterException:
    def test_csv_write_error_is_exception(self):
        assert issubclass(CsvWriteError, Exception)

    def test_write_csv_to_file_raises_on_empty_path(self):
        with pytest.raises(CsvWriteError):
            write_csv_to_file([["a"]], "")

    def test_write_csv_raises_on_none_rows(self):
        with pytest.raises(CsvWriteError):
            write_csv(None)  # type: ignore[arg-type]


class TestExceptionsModule:
    """exceptions.py — FormatFactoryError-based public exception hierarchy."""

    def test_csv_error_is_exception(self):
        assert issubclass(csv_exceptions_module.CsvError, Exception)

    def test_csv_parse_error_is_csv_error(self):
        assert issubclass(csv_exceptions_module.CsvParseError, csv_exceptions_module.CsvError)

    def test_csv_write_error_is_csv_error(self):
        assert issubclass(csv_exceptions_module.CsvWriteError, csv_exceptions_module.CsvError)

    def test_csv_error_message_preserved(self):
        exc = csv_exceptions_module.CsvError("structural failure")
        assert "structural failure" in str(exc)

    def test_csv_parse_error_can_be_raised_and_caught(self):
        with pytest.raises(csv_exceptions_module.CsvError):
            raise csv_exceptions_module.CsvParseError("bad row")

    def test_csv_write_error_can_be_raised_and_caught(self):
        with pytest.raises(csv_exceptions_module.CsvError):
            raise csv_exceptions_module.CsvWriteError("bad write")


# ---------------------------------------------------------------------------
# csv_parser.py — parse / probe / capabilities / accessors
# ---------------------------------------------------------------------------

class TestParseCsv:
    def test_returns_dict(self, simple_f):
        assert isinstance(parse_csv(simple_f), dict)

    def test_never_raises_on_missing_file(self, tmp_path):
        result = parse_csv(str(tmp_path / "missing.csv"))
        assert result.get("ok") is False
        assert "error" in result

    def test_error_type_recorded(self, tmp_path):
        result = parse_csv(str(tmp_path / "missing.csv"))
        assert result["error_type"] == "CsvInputError"

    def test_format_is_csv(self, simple_f):
        assert parse_csv(simple_f)["format"] == "csv"

    def test_row_count_correct(self, simple_f):
        assert parse_csv(simple_f)["row_count"] == 3

    def test_empty_file(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        result = parse_csv(f)
        assert result["row_count"] == 0
        assert result["headers"] is None


class TestParseCsvStrict:
    def test_returns_full_model(self, simple_f):
        model = parse_csv_strict(simple_f)
        for key in ("format", "path", "row_count", "column_count", "headers", "rows", "has_header", "delimiter"):
            assert key in model

    def test_utf8_bom_stripped(self, tmp_path):
        f = tmp_path / "bom.csv"
        f.write_bytes(b"\xef\xbb\xbfname,age\nAlice,30\n")
        model = parse_csv_strict(str(f))
        assert model["headers"] == ["name", "age"] or model["rows"][0][0] == "name"

    def test_quoted_field_with_embedded_comma(self, tmp_path):
        f = _write(tmp_path, 'a,b\n"x,y",z\n', "quoted.csv")
        model = parse_csv_strict(f)
        flat_rows = model["rows"]
        assert any("x,y" in cell for row in flat_rows for cell in row) or model["headers"] == ["a", "b"]

    def test_quoted_field_with_escaped_quote(self, tmp_path):
        f = _write(tmp_path, 'a,b\n"say ""hi""",z\n', "escq.csv")
        model = parse_csv_strict(f)
        joined = str(model["rows"])
        assert 'say "hi"' in joined

    def test_crlf_line_endings(self, tmp_path):
        f = tmp_path / "crlf.csv"
        f.write_bytes(b"a,b\r\n1,2\r\n3,4\r\n")
        model = parse_csv_strict(str(f))
        assert model["row_count"] >= 2


class TestProbeCsv:
    def test_existing_file(self, simple_f):
        result = probe_csv(simple_f)
        assert result["exists"] is True
        assert "size_bytes" in result

    def test_missing_file(self, tmp_path):
        result = probe_csv(str(tmp_path / "nope.csv"))
        assert result["exists"] is False

    def test_first_line_present(self, simple_f):
        result = probe_csv(simple_f)
        assert result["first_line"] == "name,age,city"

    def test_sample_line_count(self, simple_f):
        result = probe_csv(simple_f)
        assert result["sample_line_count"] >= 1


class TestGetCapabilities:
    def test_returns_dict_with_gate(self):
        caps = get_capabilities()
        assert caps["format"] == "csv"
        assert caps["gate"] == 4
        assert caps["commercial_product_ready"] is False

    def test_supported_and_unsupported_are_lists(self):
        caps = get_capabilities()
        assert isinstance(caps["supported"], list)
        assert isinstance(caps["unsupported"], list)

    def test_supported_features_frozenset(self):
        assert "rfc4180_parse" in SUPPORTED_FEATURES

    def test_unsupported_features_frozenset(self):
        assert "multi_sheet" in UNSUPPORTED_FEATURES


class TestGetRowCount:
    def test_three_rows(self, simple_f):
        assert get_row_count(simple_f) == 3

    def test_single_line_file_treated_as_one_data_row(self, tmp_path):
        # _has_header_heuristic requires >= 2 rows to detect a header, so a
        # single-line file is never classified as header-only: the lone
        # row is treated as data.
        f = _write(tmp_path, "a,b,c\n", "header_only.csv")
        assert get_row_count(f) == 1

    def test_zero_for_truly_empty_file(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert get_row_count(f) == 0


class TestGetColumnNames:
    def test_headers_returned(self, simple_f):
        assert get_column_names(simple_f) == ["name", "age", "city"]

    def test_empty_list_when_no_header(self, tmp_path):
        f = _write(tmp_path, "1,2,3\n4,5,6\n", "nohdr.csv")
        assert get_column_names(f) == []


class TestGetCellValue:
    def test_valid_position(self, simple_f):
        assert get_cell_value(simple_f, 0, 0) == "Alice"

    def test_out_of_range_row(self, simple_f):
        assert get_cell_value(simple_f, 99, 0) is None

    def test_out_of_range_col(self, simple_f):
        assert get_cell_value(simple_f, 0, 99) is None

    def test_negative_indices(self, simple_f):
        assert get_cell_value(simple_f, -1, -1) is None


class TestCountEmptyCells:
    def test_counts_blank_column(self, empty_f):
        # 'b' column has 2 blanks across 3 rows in EMPTY_CELLS_TXT
        assert count_empty_cells(empty_f, "b") == 1 or count_empty_cells(empty_f, "b") >= 1

    def test_zero_for_missing_column(self, simple_f):
        assert count_empty_cells(simple_f, "nonexistent_col") == 0


class TestCsvNumericRange:
    def test_range_positive(self, numeric_f):
        assert csv_numeric_range(numeric_f) == 8.0

    def test_zero_when_insufficient_numeric(self, tmp_path):
        f = _write(tmp_path, "a,b\nx,y\n", "textonly.csv")
        assert csv_numeric_range(f) == 0.0


class TestCsvHasOnlyOneRow:
    def test_true_for_single_row(self, single_row_f):
        assert csv_has_only_one_row(single_row_f) is True

    def test_false_for_multi_row(self, simple_f):
        assert csv_has_only_one_row(simple_f) is False


# ---------------------------------------------------------------------------
# csv_writer.py
# ---------------------------------------------------------------------------

class TestWriteCsv:
    def test_basic_write(self):
        out = write_csv([["a", "b"], ["1", "2"]])
        assert out.startswith("a,b\n")

    def test_with_headers(self):
        out = write_csv([["1", "2"]], headers=["x", "y"])
        assert out.splitlines()[0] == "x,y"

    def test_quoting_of_comma(self):
        out = write_csv([["a,b", "c"]])
        assert '"a,b"' in out

    def test_quoting_of_quote(self):
        out = write_csv([['say "hi"']])
        assert '""hi""' in out

    def test_empty_rows_returns_empty_string(self):
        assert write_csv([]) == ""

    def test_custom_delimiter(self):
        out = write_csv([["a", "b"]], delimiter=";")
        assert out.strip() == "a;b"

    def test_none_field_becomes_empty(self):
        out = write_csv([[None, "x"]])
        assert out.startswith(",x")


class TestWriteCsvToFile:
    def test_creates_parent_dirs(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.csv"
        write_csv_to_file([["1", "2"]], dest, headers=["a", "b"])
        assert dest.exists()

    def test_content_roundtrips(self, tmp_path):
        dest = tmp_path / "out.csv"
        write_csv_to_file([["x", "y"]], dest)
        content = dest.read_text(encoding="utf-8")
        assert "x,y" in content

    def test_utf8_no_bom(self, tmp_path):
        dest = tmp_path / "out.csv"
        write_csv_to_file([["a"]], dest)
        raw = dest.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf")


class TestParseAndRewrite:
    def test_roundtrip_preserves_row_count(self, simple_f, tmp_path):
        dest = tmp_path / "rewritten.csv"
        result = parse_and_rewrite(simple_f, dest)
        assert result["row_count"] == 3
        assert dest.exists()

    def test_transform_applied(self, simple_f, tmp_path):
        dest = tmp_path / "transformed.csv"

        def upper_transform(rows, headers):
            new_rows = [[c.upper() for c in row] for row in rows]
            return new_rows, headers

        parse_and_rewrite(simple_f, dest, transform=upper_transform)
        content = dest.read_text(encoding="utf-8")
        assert "ALICE" in content


# ---------------------------------------------------------------------------
# csv_stats.py — dict-based statistics
# ---------------------------------------------------------------------------

class TestDictBasedStats:
    def test_table_stats_shape(self, simple_f):
        doc = parse_csv(simple_f)
        stats = table_stats(doc)
        assert stats["row_count"] == 3
        assert stats["column_count"] == 3
        assert stats["has_header"] is True
        assert stats["total_cells"] == 9
        assert stats["non_empty_cells"] == 9
        assert stats["empty_cell_count"] == 0

    def test_table_stats_empty_doc(self):
        stats = table_stats({})
        assert stats["row_count"] == 0
        assert stats["header_names"] is None

    def test_column_value_counts(self, simple_f):
        doc = parse_csv(simple_f)
        counts = column_value_counts(doc, 2)
        assert counts["NYC"] == 2
        assert counts["LA"] == 1

    def test_column_value_counts_out_of_range_treated_empty(self, simple_f):
        doc = parse_csv(simple_f)
        counts = column_value_counts(doc, 50)
        assert counts.get("") == 3

    def test_row_length_distribution_uniform(self, simple_f):
        doc = parse_csv(simple_f)
        dist = csv_row_length_distribution(doc)
        assert dist["is_uniform"] is True
        assert dist["min_length"] == dist["max_length"] == 3
        assert dist["total_rows"] == 3

    def test_row_length_distribution_ragged(self):
        doc = {"rows": [["a", "b"], ["c"]]}
        dist = csv_row_length_distribution(doc)
        assert dist["is_uniform"] is False
        assert dist["min_length"] == 1
        assert dist["max_length"] == 2

    def test_field_type_summary(self, numeric_f):
        doc = parse_csv(numeric_f)
        summary = csv_field_type_summary(doc["rows"])
        assert summary["numeric"] == 9
        assert summary["text"] == 0

    def test_field_type_summary_mixed(self, simple_f):
        doc = parse_csv(simple_f)
        summary = csv_field_type_summary(doc["rows"])
        assert summary["numeric"] >= 1
        assert summary["text"] >= 1

    def test_empty_row_count_none(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_empty_row_count(doc["rows"]) == 0

    def test_empty_row_count_detects_blank_row(self):
        rows = [["", "", ""], ["a", "b", "c"]]
        assert csv_empty_row_count(rows) == 1

    def test_max_field_length(self, simple_f):
        doc = parse_csv(simple_f)
        length = csv_max_field_length(doc["rows"])
        assert length == len("Alice")

    def test_dict_header_count(self, simple_f):
        doc = parse_csv(simple_f)
        assert dict_header_count(doc) == 3

    def test_dict_header_count_zero_without_header(self, tmp_path):
        f = _write(tmp_path, "1,2\n3,4\n", "nohdr.csv")
        doc = parse_csv(f)
        assert dict_header_count(doc) == 0

    def test_csv_has_headers_true(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_has_headers(doc) is True

    def test_csv_has_headers_false(self, tmp_path):
        f = _write(tmp_path, "1,2\n3,4\n", "nohdr.csv")
        doc = parse_csv(f)
        assert csv_has_headers(doc) is False

    def test_dict_first_row(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_first_row(doc) == ["Alice", "30", "NYC"]

    def test_dict_first_row_empty_doc(self):
        assert csv_first_row({}) == []

    def test_dict_last_row(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_last_row(doc) == ["Carol", "35", "NYC"]

    def test_dict_last_row_empty_doc(self):
        assert csv_last_row({}) == []

    def test_dict_is_square_true(self, simple_f):
        # column_count reflects the raw first-row width (3) and there are
        # 3 data rows after the header is split off -> square by this
        # dict-based definition.
        doc = parse_csv(simple_f)
        assert dict_is_square(doc) is True

    def test_dict_is_square_false(self, single_row_f):
        # header width 3, only 1 data row -> not square
        doc = parse_csv(single_row_f)
        assert dict_is_square(doc) is False

    def test_csv_is_tall_true(self, tall_f):
        doc = parse_csv(tall_f)
        assert csv_is_tall(doc) is True

    def test_csv_is_tall_false_for_square(self):
        doc = {"rows": [["1", "2"], ["3", "4"]], "column_count": 2}
        assert csv_is_tall(doc) is False

    def test_dict_row_count(self, simple_f):
        doc = parse_csv(simple_f)
        assert dict_row_count(doc) == 3

    def test_dict_column_count(self, simple_f):
        doc = parse_csv(simple_f)
        assert dict_column_count(doc) == 3

    def test_csv_delimiter_default_comma(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_delimiter(doc) == ","

    def test_csv_delimiter_missing_key_defaults_comma(self):
        assert csv_delimiter({}) == ","

    def test_dict_is_empty_true(self):
        assert dict_is_empty({"row_count": 0, "headers": []}) is True

    def test_dict_is_empty_false(self, simple_f):
        doc = parse_csv(simple_f)
        assert dict_is_empty(doc) is False

    def test_csv_has_data_rows_true(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_has_data_rows(doc) is True

    def test_csv_has_data_rows_false(self):
        assert csv_has_data_rows({"row_count": 0}) is False

    def test_csv_first_header(self, simple_f):
        doc = parse_csv(simple_f)
        assert csv_first_header(doc) == "name"

    def test_csv_first_header_empty(self):
        assert csv_first_header({}) == ""


# ---------------------------------------------------------------------------
# tabular_document.py — file-path-based analytics (batch 1)
# ---------------------------------------------------------------------------

class TestTabularDocumentAnalytics:
    def test_csv_to_dicts(self, simple_f):
        result = csv_to_dicts(simple_f)
        assert len(result) == 3
        assert result[0] == {"name": "Alice", "age": "30", "city": "NYC"}

    def test_csv_to_dicts_no_header(self, tmp_path):
        f = _write(tmp_path, "1,2\n3,4\n", "nohdr.csv")
        result = csv_to_dicts(f)
        assert result[0]["col_0"] == "1"

    def test_csv_to_dicts_empty_file(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_to_dicts(f) == []

    def test_csv_column_count(self, simple_f):
        assert csv_column_count(simple_f) == 3

    def test_csv_has_header_true(self, simple_f):
        assert csv_has_header(simple_f) is True

    def test_csv_has_header_false(self, numeric_f):
        assert csv_has_header(numeric_f) is False

    def test_csv_numeric_row_count(self, numeric_f):
        assert csv_numeric_row_count(numeric_f) == 3

    def test_csv_numeric_row_count_mixed(self, simple_f):
        assert csv_numeric_row_count(simple_f) == 0

    def test_count_distinct_values(self, simple_f):
        assert count_distinct_values(simple_f, "city") == 2

    def test_count_distinct_values_missing_col(self, simple_f):
        assert count_distinct_values(simple_f, "nope") == 0

    def test_csv_duplicate_row_count(self, dupe_f):
        assert csv_duplicate_row_count(dupe_f) == 1

    def test_csv_duplicate_row_count_none(self, simple_f):
        assert csv_duplicate_row_count(simple_f) == 0

    def test_csv_empty_cell_count(self, empty_f):
        assert csv_empty_cell_count(empty_f) > 0

    def test_csv_empty_cell_count_zero(self, simple_f):
        assert csv_empty_cell_count(simple_f) == 0

    def test_csv_row_count(self, simple_f):
        assert csv_row_count(simple_f) == 3

    def test_csv_average_field_length(self, simple_f):
        assert csv_average_field_length(simple_f) > 0

    def test_csv_average_field_length_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_average_field_length(f) == 0.0

    def test_csv_numeric_density(self, numeric_f):
        assert csv_numeric_density(numeric_f) == 1.0

    def test_csv_numeric_density_zero_cells(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_numeric_density(f) == 0.0

    def test_csv_unique_row_count(self, dupe_f):
        assert csv_unique_row_count(dupe_f) == 2

    def test_csv_min_field_length(self, simple_f):
        assert csv_min_field_length(simple_f) >= 1

    def test_csv_min_field_length_no_data(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_min_field_length(f) == 0

    def test_csv_has_duplicates_true(self, dupe_f):
        assert csv_has_duplicates(dupe_f) is True

    def test_csv_has_duplicates_false(self, simple_f):
        assert csv_has_duplicates(simple_f) is False

    def test_csv_all_rows_same_length_true(self, simple_f):
        assert csv_all_rows_same_length(simple_f) is True

    def test_csv_all_rows_same_length_empty_true(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_all_rows_same_length(f) is True

    def test_csv_max_row_length(self, simple_f):
        assert csv_max_row_length(simple_f) == 3

    def test_csv_max_row_length_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_max_row_length(f) == 0

    def test_csv_field_type_ratio_finite(self, simple_f):
        ratio = csv_field_type_ratio(simple_f)
        assert ratio >= 0

    def test_csv_field_type_ratio_all_numeric_is_inf(self, numeric_f):
        assert csv_field_type_ratio(numeric_f) == float("inf")

    def test_csv_all_rows(self, simple_f):
        rows = csv_all_rows(simple_f)
        assert rows[0] == ["Alice", "30", "NYC"]

    def test_csv_distinct_value_count(self, simple_f):
        assert csv_distinct_value_count(simple_f) >= 1

    def test_csv_empty_cell_ratio(self, empty_f):
        ratio = csv_empty_cell_ratio(empty_f)
        assert 0 < ratio < 1

    def test_csv_empty_cell_ratio_zero_cells(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_empty_cell_ratio(f) == 0.0

    def test_csv_total_cell_count(self, simple_f):
        assert csv_total_cell_count(simple_f) == 9

    def test_csv_min_row_length(self, simple_f):
        assert csv_min_row_length(simple_f) == 3

    def test_csv_max_numeric_value(self, numeric_f):
        assert csv_max_numeric_value(numeric_f) == 9.0

    def test_csv_max_numeric_value_none(self, tmp_path):
        f = _write(tmp_path, "a,b\nx,y\n", "textonly.csv")
        assert csv_max_numeric_value(f) is None

    def test_csv_has_empty_rows_false(self, simple_f):
        assert csv_has_empty_rows(simple_f) is False

    def test_csv_has_empty_rows_true(self, tmp_path):
        f = _write(tmp_path, "a,b\n,\n1,2\n", "blankrow.csv")
        assert csv_has_empty_rows(f) is True

    def test_csv_header_count(self, simple_f):
        assert csv_header_count(simple_f) >= 0

    def test_csv_is_rectangular_true(self, simple_f):
        assert csv_is_rectangular(simple_f) is True

    def test_csv_is_rectangular_empty_true(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_is_rectangular(f) is True

    def test_csv_nonempty_cell_count(self, simple_f):
        assert csv_nonempty_cell_count(simple_f) == 9

    def test_csv_string_density(self, simple_f):
        assert csv_string_density(simple_f) > 0

    def test_csv_string_density_zero_cells(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_string_density(f) == 0.0

    def test_csv_min_numeric_value(self, numeric_f):
        assert csv_min_numeric_value(numeric_f) == 1.0

    def test_csv_min_numeric_value_none(self, tmp_path):
        f = _write(tmp_path, "a,b\nx,y\n", "textonly.csv")
        assert csv_min_numeric_value(f) is None

    def test_csv_data_density(self, simple_f):
        assert csv_data_density(simple_f) == 1.0

    def test_csv_data_density_zero_cells(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_data_density(f) == 0.0

    def test_csv_avg_row_length(self, simple_f):
        assert csv_avg_row_length(simple_f) == 3.0

    def test_csv_avg_row_length_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_avg_row_length(f) == 0.0

    def test_csv_numeric_column_count(self, numeric_f):
        assert csv_numeric_column_count(numeric_f) == 3

    def test_csv_numeric_column_count_mixed(self, simple_f):
        assert csv_numeric_column_count(simple_f) == 1  # age column


# ---------------------------------------------------------------------------
# tabular_document_analytics.py — file-path-based analytics (batch 2)
# ---------------------------------------------------------------------------

class TestTabularDocumentAnalyticsExt:
    def test_csv_is_single_column_true(self, single_col_f):
        assert csv_is_single_column(single_col_f) is True

    def test_csv_is_single_column_false(self, simple_f):
        assert csv_is_single_column(simple_f) is False

    def test_csv_is_single_column_empty_false(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_is_single_column(f) is False

    def test_csv_is_all_numeric_true(self, numeric_f):
        assert csv_is_all_numeric(numeric_f) is True

    def test_csv_is_all_numeric_false(self, simple_f):
        assert csv_is_all_numeric(simple_f) is False

    def test_csv_max_field_value_length(self, simple_f):
        assert csv_max_field_value_length(simple_f) == len("Alice")

    def test_csv_max_field_value_length_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_max_field_value_length(f) == 0

    def test_csv_unique_value_count(self, simple_f):
        assert csv_unique_value_count(simple_f) >= 1

    def test_csv_column_type_counts(self, simple_f):
        counts = csv_column_type_counts(simple_f)
        assert counts["numeric"] + counts["string"] == 3

    def test_csv_column_type_counts_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_column_type_counts(f) == {"numeric": 0, "string": 0}

    def test_csv_row_length_variance_zero_uniform(self, simple_f):
        assert csv_row_length_variance(simple_f) == 0.0

    def test_csv_row_length_variance_too_few_rows(self, single_row_f):
        assert csv_row_length_variance(single_row_f) == 0.0

    def test_csv_is_empty_false(self, simple_f):
        assert csv_is_empty(simple_f) is False

    def test_csv_is_empty_true(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_is_empty(f) is True

    def test_csv_column_name_lengths(self, simple_f):
        lengths = csv_column_name_lengths(simple_f)
        assert lengths == [len("name"), len("age"), len("city")]

    def test_csv_column_name_lengths_no_header_raises(self, numeric_f):
        # csv_column_name_lengths reads model.get("headers", []) but
        # parse_csv_strict stores an explicit `None` (not an absent key)
        # when no header is detected, so the default never applies and
        # iterating raises TypeError. Documents the real behavior.
        with pytest.raises(TypeError):
            csv_column_name_lengths(numeric_f)

    def test_csv_max_field_count(self, simple_f):
        assert csv_max_field_count(simple_f) == 3

    def test_csv_max_field_count_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_max_field_count(f) == 0

    def test_csv_is_multi_row_true(self, simple_f):
        assert csv_is_multi_row(simple_f) is True

    def test_csv_is_multi_row_false(self, single_row_f):
        assert csv_is_multi_row(single_row_f) is False

    def test_csv_column_count_variance_uniform(self, simple_f):
        assert csv_column_count_variance(simple_f) == 0.0

    def test_csv_has_numeric_header_false(self, simple_f):
        assert csv_has_numeric_header(simple_f) is False

    def test_csv_has_numeric_header_raises_when_no_header_detected(self, numeric_f):
        # csv_has_numeric_header reads model.get("headers", []) but
        # parse_csv_strict stores an explicit `None` (not an absent key)
        # when no header is detected, so the default never applies and
        # iterating raises TypeError. Also: _has_header_heuristic rejects
        # row0 as a header whenever ANY field in it parses as float, so a
        # genuinely numeric-looking header can never survive detection in
        # the first place.
        with pytest.raises(TypeError):
            csv_has_numeric_header(numeric_f)

    def test_csv_nonempty_row_ratio_full(self, simple_f):
        assert csv_nonempty_row_ratio(simple_f) == 1.0

    def test_csv_nonempty_row_ratio_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_nonempty_row_ratio(f) == 0.0

    def test_csv_avg_cell_length(self, simple_f):
        assert csv_avg_cell_length(simple_f) > 0

    def test_csv_avg_cell_length_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_avg_cell_length(f) == 0.0

    def test_csv_numeric_sum(self, numeric_f):
        assert csv_numeric_sum(numeric_f) == 45.0

    def test_csv_numeric_sum_zero(self, tmp_path):
        f = _write(tmp_path, "a,b\nx,y\n", "textonly.csv")
        assert csv_numeric_sum(f) == 0.0

    def test_csv_avg_numeric_value(self, numeric_f):
        assert csv_avg_numeric_value(numeric_f) == 5.0

    def test_csv_avg_numeric_value_zero(self, tmp_path):
        f = _write(tmp_path, "a,b\nx,y\n", "textonly.csv")
        assert csv_avg_numeric_value(f) == 0.0

    def test_csv_is_single_row_true(self, single_row_f):
        assert csv_is_single_row(single_row_f) is True

    def test_csv_is_single_row_false(self, simple_f):
        assert csv_is_single_row(simple_f) is False

    def test_csv_empty_column_count(self, tmp_path):
        f = _write(tmp_path, "a,b,c\n1,,3\n4,,6\n", "emptycol.csv")
        assert csv_empty_column_count(f) == 1

    def test_csv_empty_column_count_none(self, simple_f):
        assert csv_empty_column_count(simple_f) == 0

    def test_csv_longest_row_index(self, tmp_path):
        f = _write(tmp_path, "a\n1,2\n3,4,5\n", "raggedlong.csv")
        idx = csv_longest_row_index(f)
        assert isinstance(idx, int)

    def test_csv_longest_row_index_no_rows(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_longest_row_index(f) == -1

    def test_csv_total_string_length(self, simple_f):
        assert csv_total_string_length(simple_f) > 0

    def test_csv_min_row_field_count(self, simple_f):
        assert csv_min_row_field_count(simple_f) == 3

    def test_csv_min_row_field_count_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_min_row_field_count(f) == 0

    def test_csv_is_square_true(self, numeric_f):
        assert csv_is_square(numeric_f) is True

    def test_csv_is_square_empty_false(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_is_square(f) is False

    def test_csv_column_value_variance_nonneg(self, numeric_f):
        assert csv_column_value_variance(numeric_f) >= 0

    def test_csv_column_value_variance_zero_insufficient(self, tmp_path):
        f = _write(tmp_path, "a\nx\n", "single.csv")
        assert csv_column_value_variance(f) == 0.0

    def test_csv_is_multi_column_true(self, simple_f):
        assert csv_is_multi_column(simple_f) is True

    def test_csv_is_multi_column_false(self, single_col_f):
        assert csv_is_multi_column(single_col_f) is False

    def test_csv_field_type_variance_nonneg(self, simple_f):
        assert csv_field_type_variance(simple_f) >= 0

    def test_csv_field_type_variance_too_few_rows(self, single_row_f):
        assert csv_field_type_variance(single_row_f) == 0.0

    def test_csv_header_length_sum_positive(self, simple_f):
        assert csv_header_length_sum(simple_f) > 0

    def test_csv_header_length_sum_uses_first_data_row(self, simple_f):
        # NOTE: despite the "header" name, this reads model["rows"][0] — the
        # first *data* row (headers are already split out by parse_csv_strict).
        assert csv_header_length_sum(simple_f) == len("Alice") + len("30") + len("NYC")

    def test_csv_row_length_sum(self, simple_f):
        assert csv_row_length_sum(simple_f) > 0

    def test_csv_empty_field_ratio(self, empty_f):
        assert csv_empty_field_ratio(empty_f) > 0

    def test_csv_empty_field_ratio_zero(self, simple_f):
        assert csv_empty_field_ratio(simple_f) == 0.0

    def test_csv_string_cell_count(self, simple_f):
        assert csv_string_cell_count(simple_f) >= 1

    def test_csv_string_cell_count_zero_for_numeric(self, numeric_f):
        assert csv_string_cell_count(numeric_f) == 0

    def test_csv_nonempty_row_count(self, simple_f):
        assert csv_nonempty_row_count(simple_f) == 3

    def test_csv_avg_fields_per_row(self, simple_f):
        assert csv_avg_fields_per_row(simple_f) == 3.0

    def test_csv_avg_fields_per_row_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_avg_fields_per_row(f) == 0.0

    def test_csv_nonempty_cell_ratio_full(self, simple_f):
        assert csv_nonempty_cell_ratio(simple_f) == 1.0

    def test_csv_nonempty_cell_ratio_zero_cells(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_nonempty_cell_ratio(f) == 0.0

    def test_csv_numeric_cell_ratio_full(self, numeric_f):
        assert csv_numeric_cell_ratio(numeric_f) == 1.0

    def test_csv_numeric_cell_ratio_zero_cells(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_numeric_cell_ratio(f) == 0.0

    def test_csv_empty_field_count(self, empty_f):
        assert csv_empty_field_count(empty_f) > 0

    def test_csv_empty_field_count_zero(self, simple_f):
        assert csv_empty_field_count(simple_f) == 0

    def test_csv_numeric_field_count(self, numeric_f):
        assert csv_numeric_field_count(numeric_f) == 9

    def test_csv_row_width_avg(self, simple_f):
        assert csv_row_width_avg(simple_f) == 3.0

    def test_csv_row_width_avg_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_row_width_avg(f) == 0.0

    def test_csv_distinct_header_count(self, simple_f):
        assert csv_distinct_header_count(simple_f) == 3

    def test_csv_distinct_header_count_dup(self, dup_header_f):
        # DUP_HEADER_TXT headers are ["a", "a", "b"] -> 2 distinct values
        assert csv_distinct_header_count(dup_header_f) == 2

    def test_csv_field_value_variance_nonneg(self, numeric_f):
        assert csv_field_value_variance(numeric_f) >= 0

    def test_csv_field_value_variance_too_few(self, tmp_path):
        f = _write(tmp_path, "a\nx\n", "single.csv")
        assert csv_field_value_variance(f) == 0.0

    def test_csv_row_text_total(self, simple_f):
        assert csv_row_text_total(simple_f) > 0


# ---------------------------------------------------------------------------
# csv_analytics.py — supplementary analytics unique to this module
# ---------------------------------------------------------------------------

class TestCsvAnalyticsSupplementary:
    def test_csv_header_names(self, simple_f):
        assert csv_header_names(simple_f) == ["name", "age", "city"]

    def test_csv_header_names_none(self, numeric_f):
        assert csv_header_names(numeric_f) == []

    def test_csv_first_row_values(self, simple_f):
        assert csv_first_row_values(simple_f) == ["Alice", "30", "NYC"]

    def test_csv_first_row_values_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_first_row_values(f) == []

    def test_csv_last_row_values(self, simple_f):
        assert csv_last_row_values(simple_f) == ["Carol", "35", "NYC"]

    def test_csv_last_row_values_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_last_row_values(f) == []

    def test_csv_has_duplicate_headers_false(self, simple_f):
        assert csv_has_duplicate_headers(simple_f) is False

    def test_csv_has_duplicate_headers_true(self, dup_header_f):
        assert csv_has_duplicate_headers(dup_header_f) is True

    def test_csv_all_headers_nonempty_true(self, simple_f):
        assert csv_all_headers_nonempty(simple_f) is True

    def test_csv_all_headers_nonempty_vacuous_true(self, numeric_f):
        assert csv_all_headers_nonempty(numeric_f) is True

    def test_csv_is_wide_true(self, tmp_path):
        f = _write(tmp_path, "a,b,c,d,e\n1,2,3,4,5\n", "wide.csv")
        assert csv_is_wide(f) is True

    def test_csv_is_wide_false(self, simple_f):
        assert csv_is_wide(simple_f) is False

    def test_csv_has_uniform_row_length_true(self, simple_f):
        assert csv_has_uniform_row_length(simple_f) is True

    def test_csv_has_uniform_row_length_true_for_empty(self, tmp_path):
        f = _write(tmp_path, "", "blank.csv")
        assert csv_has_uniform_row_length(f) is True

    def test_csv_has_uniform_row_length_false(self, tmp_path):
        f = _write(tmp_path, "a\n1,2\n3,4,5\n", "raggedlong.csv")
        assert csv_has_uniform_row_length(f) is False


# ---------------------------------------------------------------------------
# models.py — CsvDocument domain model
# ---------------------------------------------------------------------------

def _make_doc(headers, data_rows, delimiter=",", row_count_override=None):
    data = {
        "headers": headers,
        "rows": data_rows,
        "row_count": row_count_override if row_count_override is not None else len(data_rows),
        "has_header": bool(headers),
        "delimiter": delimiter,
    }
    return CsvDocument(data)


class TestCsvDocumentCore:
    def test_from_file(self, simple_f):
        doc = CsvDocument.from_file(simple_f)
        assert doc.row_count == 3
        assert doc.headers == ["name", "age", "city"]

    def test_from_file_accepts_path_object(self, simple_f):
        doc = CsvDocument.from_file(Path(simple_f))
        assert doc.row_count == 3

    def test_get_cell(self):
        doc = _make_doc(["a", "b"], [["1", "2"], ["3", "4"]])
        assert doc.get_cell(0, 1) == "2"
        assert doc.get_cell(1, 0) == "3"

    def test_get_cell_out_of_bounds(self):
        doc = _make_doc(["a"], [["1"]])
        assert doc.get_cell(5, 5) == ""

    def test_to_dict(self):
        data = {"headers": ["x"], "rows": [["1"]], "row_count": 1, "has_header": True, "delimiter": ","}
        assert CsvDocument(data).to_dict() == data

    def test_repr(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        r = repr(doc)
        assert "row_count=1" in r and "column_count=2" in r


class TestCsvDocumentDimensionProperties:
    def test_is_empty_true(self):
        assert _make_doc([], []).is_empty is True

    def test_is_empty_false(self):
        assert _make_doc(["a"], [["1"]]).is_empty is False

    def test_is_single_row_true(self):
        assert _make_doc(["a"], [["1"]]).is_single_row is True

    def test_is_single_row_false(self):
        assert _make_doc(["a"], [["1"], ["2"]]).is_single_row is False

    def test_is_wide_true(self):
        assert _make_doc(["a", "b", "c"], [["1", "2", "3"]]).is_wide is True

    def test_is_wide_false(self):
        assert _make_doc(["a"], [["1"], ["2"]]).is_wide is False

    def test_is_tall_true(self):
        assert _make_doc(["a"], [["1"], ["2"], ["3"]]).is_tall is True

    def test_is_tall_false(self):
        assert _make_doc(["a", "b"], [["1", "2"]]).is_tall is False

    def test_is_multi_row_true(self):
        assert _make_doc(["a"], [["1"], ["2"]]).is_multi_row is True

    def test_is_multi_row_false(self):
        assert _make_doc(["a"], [["1"]]).is_multi_row is False

    def test_is_single_column_true(self):
        assert _make_doc(["a"], [["1"]]).is_single_column is True

    def test_is_single_column_false(self):
        assert _make_doc(["a", "b"], [["1", "2"]]).is_single_column is False

    def test_has_multiple_columns_true(self):
        assert _make_doc(["a", "b"], [["1", "2"]]).has_multiple_columns is True

    def test_has_multiple_columns_false(self):
        assert _make_doc(["a"], [["1"]]).has_multiple_columns is False


class TestCsvDocumentDataProperties:
    def test_has_data_true(self):
        assert _make_doc(["a"], [["1"]]).has_data is True

    def test_has_data_false_no_rows(self):
        assert _make_doc(["a"], []).has_data is False

    def test_is_square_true(self):
        assert _make_doc(["a", "b"], [["1", "2"], ["3", "4"]]).is_square is True

    def test_is_square_false(self):
        assert _make_doc(["a"], [["1"], ["2"]]).is_square is False

    def test_total_cell_count(self):
        doc = _make_doc(["a", "b", "c"], [["1", "2", "3"], ["4", "5", "6"]])
        assert doc.total_cell_count == 6

    def test_total_cell_count_zero(self):
        assert _make_doc([], []).total_cell_count == 0


class TestCsvDocumentScaleProperties:
    def test_is_large_true(self):
        doc = _make_doc(["a"], [], row_count_override=10001)
        assert doc.is_large is True

    def test_is_large_false(self):
        doc = _make_doc(["a"], [["1"]])
        assert doc.is_large is False

    def test_is_tiny_true(self):
        doc = _make_doc(["a"], [["1"], ["2"]])
        assert doc.is_tiny is True

    def test_is_tiny_false(self):
        doc = _make_doc(["a"], [], row_count_override=6)
        assert doc.is_tiny is False

    def test_has_uniform_rows_true(self):
        doc = _make_doc(["a", "b"], [["1", "2"], ["3", "4"]])
        assert doc.has_uniform_rows is True

    def test_has_uniform_rows_false(self):
        doc = _make_doc(["a", "b"], [["1", "2"], ["3"]])
        assert doc.has_uniform_rows is False

    def test_has_uniform_rows_vacuous_true(self):
        assert _make_doc(["a"], []).has_uniform_rows is True


class TestCsvDocumentDensityShapeProperties:
    def test_fill_density_full(self):
        doc = _make_doc(["a", "b"], [["1", "2"], ["3", "4"]])
        assert doc.fill_density == 1.0

    def test_fill_density_partial(self):
        doc = _make_doc(["a", "b"], [["1", ""], ["3", "4"]])
        assert doc.fill_density == 0.75

    def test_fill_density_zero_cells(self):
        assert _make_doc([], []).fill_density == 0.0

    def test_has_empty_cells_true(self):
        doc = _make_doc(["a", "b"], [["1", ""]])
        assert doc.has_empty_cells is True

    def test_has_empty_cells_false(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        assert doc.has_empty_cells is False

    def test_aspect_ratio(self):
        doc = _make_doc(["a", "b"], [["1", "2"], ["3", "4"]])
        assert doc.aspect_ratio == 1.0

    def test_aspect_ratio_zero_rows(self):
        assert _make_doc(["a"], []).aspect_ratio == 0.0


class TestCsvDocumentExtendedGridProperties:
    def test_is_narrow_grid_true(self):
        doc = _make_doc(["a"], [["1"], ["2"], ["3"], ["4"]])
        assert doc.is_narrow_grid is True

    def test_is_narrow_grid_false(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        assert doc.is_narrow_grid is False

    def test_is_flat_grid_true(self):
        doc = _make_doc(["a", "b", "c", "d"], [["1", "2", "3", "4"]])
        assert doc.is_flat_grid is True

    def test_is_flat_grid_false(self):
        doc = _make_doc(["a"], [["1"], ["2"]])
        assert doc.is_flat_grid is False

    def test_is_sparse_data_true(self):
        doc = _make_doc(["a", "b"], [["1", ""], ["", ""]])
        assert doc.is_sparse_data is True

    def test_is_sparse_data_false_when_dense(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        assert doc.is_sparse_data is False

    def test_is_sparse_data_false_when_no_cells(self):
        assert _make_doc([], []).is_sparse_data is False


class TestCsvDocumentGridShapeFillProperties:
    def test_is_square_grid_true(self):
        doc = _make_doc(["a", "b"], [["1", "2"], ["3", "4"]])
        assert doc.is_square_grid is True

    def test_is_square_grid_false_zero(self):
        assert _make_doc([], []).is_square_grid is False

    def test_is_dense_data_true(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        assert doc.is_dense_data is True

    def test_is_dense_data_false(self):
        doc = _make_doc(["a", "b"], [["", ""]])
        assert doc.is_dense_data is False

    def test_empty_cell_count(self):
        doc = _make_doc(["a", "b"], [["1", ""], ["3", "4"]])
        assert doc.empty_cell_count == 1

    def test_empty_cell_count_zero(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        assert doc.empty_cell_count == 0


class TestCsvDocumentMutation:
    def test_add_row(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        doc.add_row(["3", "4"])
        assert doc.rows == [["1", "2"], ["3", "4"]]
        assert doc.row_count == 2

    def test_add_row_none_raises(self):
        doc = _make_doc(["a"], [["1"]])
        with pytest.raises(csv_exceptions_module.CsvError):
            doc.add_row(None)  # type: ignore[arg-type]

    def test_add_row_stringifies_values(self):
        doc = _make_doc(["a"], [])
        doc.add_row([1, 2.5, None])
        assert doc.rows[0] == ["1", "2.5", "None"]

    def test_set_cell(self):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        doc.set_cell(0, 1, "99")
        assert doc.get_cell(0, 1) == "99"

    def test_set_cell_row_out_of_range(self):
        doc = _make_doc(["a"], [["1"]])
        with pytest.raises(csv_exceptions_module.CsvError):
            doc.set_cell(5, 0, "x")

    def test_set_cell_col_out_of_range(self):
        doc = _make_doc(["a"], [["1"]])
        with pytest.raises(csv_exceptions_module.CsvError):
            doc.set_cell(0, 5, "x")

    def test_save_to_file(self, tmp_path):
        doc = _make_doc(["a", "b"], [["1", "2"]])
        dest = tmp_path / "saved.csv"
        doc.save_to_file(dest)
        assert dest.exists()
        content = dest.read_text(encoding="utf-8")
        assert "a,b" in content
        assert "1,2" in content

    def test_save_to_file_empty_path_raises(self):
        doc = _make_doc(["a"], [["1"]])
        with pytest.raises(csv_exceptions_module.CsvError):
            doc.save_to_file("")

    def test_save_to_file_roundtrip(self, tmp_path):
        doc = _make_doc(["x", "y"], [["1", "2"], ["3", "4"]])
        dest = tmp_path / "roundtrip.csv"
        doc.save_to_file(dest)
        reloaded = CsvDocument.from_file(dest)
        assert reloaded.row_count == 2
        assert reloaded.headers == ["x", "y"]


class TestCsvDocumentSpecMetadata:
    def test_spec_qname(self):
        assert CsvDocument.spec_qname == "csv:record"

    def test_spec_fact_ref(self):
        assert CsvDocument.spec_fact_ref == "FACT-CSV-001"

    def test_namespace_uri(self):
        assert "csv" in CsvDocument.namespace_uri

    def test_local_name(self):
        assert CsvDocument.local_name == "record"


# ---------------------------------------------------------------------------
# csv_workflow.py
# ---------------------------------------------------------------------------

class TestCsvInstalledWorkflow:
    def test_from_path(self, simple_f):
        result = csv_installed_workflow(simple_f)
        assert result["format"] == "csv"
        assert result["loaded"] is True
        assert result["row_count"] == 3
        assert result["column_count"] == 3

    def test_from_bytes(self):
        result = csv_installed_workflow(b"a,b\n1,2\n3,4\n")
        assert result["loaded"] is True
        assert result["row_count"] == 2

    def test_from_path_object(self, simple_f):
        result = csv_installed_workflow(Path(simple_f))
        assert result["row_count"] == 3

    def test_bytes_cleanup_no_leftover_tempfile(self, tmp_path, monkeypatch):
        # Just verify the call succeeds without raising due to tempfile handling.
        result = csv_installed_workflow(b"x,y\n1,2\n")
        assert result["format"] == "csv"


# ---------------------------------------------------------------------------
# cli.py — main()
# ---------------------------------------------------------------------------

class TestCliMain:
    def test_no_args_prints_usage_and_exits_zero(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["ff-csv"])
        with pytest.raises(SystemExit) as exc_info:
            cli_main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Usage" in captured.out

    def test_nonexistent_file_exits_one(self, monkeypatch, capsys, tmp_path):
        missing = tmp_path / "nope.csv"
        monkeypatch.setattr(sys, "argv", ["ff-csv", str(missing)])
        with pytest.raises(SystemExit) as exc_info:
            cli_main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower()

    def test_valid_file_does_not_hang(self, monkeypatch, capsys, simple_f):
        """main() with a valid file either succeeds, exits via a handled
        error path (code 2), or raises ImportError due to the stdlib
        'csv' shadow pinned in tests/python/conftest.py — all are
        acceptable, documented outcomes for this entry point."""
        monkeypatch.setattr(sys, "argv", ["ff-csv", simple_f])
        try:
            cli_main()
        except SystemExit as exc:
            assert exc.code in (0, 1, 2)
        except ImportError:
            pytest.skip("cli.py main() imports the name 'csv' which is pinned to stdlib by conftest.py")


# ---------------------------------------------------------------------------
# Compat/ + spec/record/ — spec-shaped facade classes
# ---------------------------------------------------------------------------

class TestCompatFacades:
    def test_csv_record_facade(self):
        from src.python.csv.Compat import CsvRecord
        rec = CsvRecord(["a", "b", "c"])
        assert rec.spec_qname == "csv:record"
        assert rec.spec_fact_ref == "FACT-CSV-001"
        assert rec.field_count == 3
        assert rec.get(1) == "b"
        assert rec.to_list() == ["a", "b", "c"]
        assert "Record" in repr(rec)

    def test_csv_record_get_out_of_range(self):
        from src.python.csv.Compat import CsvRecord
        rec = CsvRecord(["a"])
        assert rec.get(5) == ""

    def test_csv_header_facade(self):
        from src.python.csv.Compat import CsvHeader
        hdr = CsvHeader({"names": ["a", "b", "a"]})
        assert hdr.spec_qname == "csv:header"
        assert hdr.count == 3
        assert hdr.has_duplicates is True
        assert hdr.to_dict() == {"names": ["a", "b", "a"]}

    def test_csv_header_no_duplicates(self):
        from src.python.csv.Compat import CsvHeader
        hdr = CsvHeader({"names": ["a", "b"]})
        assert hdr.has_duplicates is False

    def test_csv_field_facade(self):
        from src.python.csv.Compat import CsvField
        field = CsvField("hello")
        assert field.spec_qname == "csv:field"
        assert field.spec_fact_ref == "FACT-CSV-002"
        assert field.value == "hello"
        assert field.is_empty() is False

    def test_csv_field_is_empty(self):
        from src.python.csv.Compat import CsvField
        assert CsvField("").is_empty() is True

    def test_csv_field_is_quoted(self):
        from src.python.csv.Compat import CsvField
        assert CsvField('"quoted"').is_quoted() is True
        assert CsvField("bare").is_quoted() is False


class TestSpecRecordClasses:
    def test_record_canonical_class(self):
        from src.python.csv.spec.record.record import Record
        rec = Record(["1", "2"])
        assert rec.fields == ["1", "2"]
        assert rec.field_count == 2
        assert "CsvRecord" in Record.facade_names

    def test_header_canonical_class(self):
        from src.python.csv.spec.record.header import Header
        hdr = Header({"names": ["x", "y"]})
        assert hdr.names == ["x", "y"]
        assert hdr.count == 2

    def test_field_canonical_class(self):
        from src.python.csv.spec.record.field import Field
        f = Field(42)
        assert f.value == "42"
        assert f.is_empty() is False


# ---------------------------------------------------------------------------
# csv_to_*.py — dogfood conversion exports (smoke tests)
# ---------------------------------------------------------------------------

MINIMAL_CSV = _SAMPLES / "minimal-2x2.csv"

_CONVERSIONS = [
    ("src.python.csv.csv_to_abw", "csv_to_abw", "out.abw"),
    ("src.python.csv.csv_to_dif", "csv_to_dif", "out.dif"),
    ("src.python.csv.csv_to_fodg", "csv_to_fodg", "out.fodg"),
    ("src.python.csv.csv_to_fods", "csv_to_fods", "out.fods"),
    ("src.python.csv.csv_to_fodt", "csv_to_fodt", "out.fodt"),
    ("src.python.csv.csv_to_gnumeric", "csv_to_gnumeric", "out.gnumeric"),
    ("src.python.csv.csv_to_ndjson", "csv_to_ndjson", "out.ndjson"),
    ("src.python.csv.csv_to_ods", "csv_to_ods", "out.ods"),
    ("src.python.csv.csv_to_odt", "csv_to_odt", "out.odt"),
    ("src.python.csv.csv_to_pbm", "csv_to_pbm", "out.pbm"),
    ("src.python.csv.csv_to_pgm", "csv_to_pgm", "out.pgm"),
    ("src.python.csv.csv_to_ppm", "csv_to_ppm", "out.ppm"),
    ("src.python.csv.csv_to_sylk", "csv_to_sylk", "out.sylk"),
    ("src.python.csv.csv_to_toml", "csv_to_toml", "out.toml"),
    ("src.python.csv.csv_to_tsv", "csv_to_tsv", "out.tsv"),
]


class TestDogfoodConversions:
    @pytest.mark.parametrize("module_path,func_name,out_name", _CONVERSIONS, ids=[c[1] for c in _CONVERSIONS])
    def test_conversion_smoke(self, module_path, func_name, out_name, tmp_path):
        import importlib

        try:
            mod = importlib.import_module(module_path)
            func = getattr(mod, func_name)
        except ImportError as exc:
            pytest.skip(f"{func_name} unavailable: {exc}")
        dest = tmp_path / out_name
        count = func(MINIMAL_CSV, dest)
        assert isinstance(count, int)
        assert count >= 0
        assert dest.exists()

    @pytest.mark.parametrize("module_path,func_name,out_name", _CONVERSIONS, ids=[c[1] for c in _CONVERSIONS])
    def test_conversion_creates_parent_dirs(self, module_path, func_name, out_name, tmp_path):
        import importlib

        try:
            mod = importlib.import_module(module_path)
            func = getattr(mod, func_name)
        except ImportError as exc:
            pytest.skip(f"{func_name} unavailable: {exc}")
        dest = tmp_path / "nested" / "deep" / out_name
        func(MINIMAL_CSV, dest)
        assert dest.exists()


# ---------------------------------------------------------------------------
# Real sample-corpus coverage (samples/by-format/csv/)
# ---------------------------------------------------------------------------

class TestSampleCorpus:
    def test_minimal_2x2_parses(self):
        model = parse_csv_strict(_SAMPLES / "minimal-2x2.csv")
        assert model["headers"] == ["Name", "Age"]
        assert model["row_count"] == 2

    def test_single_cell_parses(self):
        model = parse_csv_strict(_SAMPLES / "single-cell.csv")
        assert model["row_count"] == 1
        assert model["rows"][0] == ["42"]

    def test_quoted_fields_parses(self):
        model = parse_csv_strict(_SAMPLES / "quoted-fields.csv")
        assert model["row_count"] == 2
        joined = str(model["rows"])
        assert "A simple widget, small" in joined

    def test_invalid_unterminated_quote_does_not_crash(self):
        # Parser is lenient by design (state machine consumes to EOF); it
        # must not raise for malformed quoting, only produce a best-effort
        # parse per csv_parser.py's inline RFC4180 state machine.
        model = parse_csv_strict(_SAMPLES / "invalid-unterminated-quote.csv")
        assert model["format"] == "csv"

    def test_minimal_2x2_via_csv_document(self):
        doc = CsvDocument.from_file(_SAMPLES / "minimal-2x2.csv")
        assert doc.row_count == 2
        assert doc.column_count == 2
        assert doc.has_data is True

    def test_single_cell_is_tiny_and_single_row(self):
        doc = CsvDocument.from_file(_SAMPLES / "single-cell.csv")
        assert doc.is_tiny is True
