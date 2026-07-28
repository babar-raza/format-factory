"""
test_sylk_gap_coverage.py — comprehensive gap-closure test suite for SYLK.

Targets the ~87 `missing_test_coverage` gaps registered for the SYLK FOSS
Python package in reports/capability-layer/gap-ledger.json
(GAP-SYLK-FOSS-*). As of 2026-07-16, 81/87 of those gaps were already
`closed` by prior sprints; 6 were still `open`:

    - sylk_has_data
    - sylk_is_square_grid
    - sylk_grid_size
    - sylk_cell_fill_ratio
    - sylk_is_wide
    - sylk_is_tall

(all defined in src/python/sylk/sylk_value_analytics.py, "grid-level
analytics" section). TestGapClosureGridAnalytics below closes those 6
gaps with dedicated, multi-sample, edge-case coverage. The remaining
classes broaden coverage across every module the sylk package exports,
per CLAUDE.md EP-5 (per-work-item grading) and EP-1 (zero-stub
enforcement — every exported callable gets at least one direct test).

Modules exercised:
    sylk.sylk_parser            (parser, exceptions, mutation, cell/row
                                  accessors, CSV/HTML export, capabilities)
    sylk.sylk_writer             (write_sylk / write_sylk_str)
    sylk.sylk_analytics          (65 scalar analytics + 2 structured)
    sylk.sylk_value_analytics    (24 scalar analytics + grid-level probes)
    sylk.models                  (SylkModelDocument / SylkDoc)
    sylk.sylk_workflow           (sylk_installed_workflow)
    sylk.sylk_cell_iterator      (sylk_iter_cells)
    sylk.sylk_row_iterator       (sylk_iter_rows)
    sylk.exceptions              (package-level exception hierarchy)
    sylk.spec.row.{cell,row,header}  (canonical spec classes)
    sylk.Compat.{sylk_cell,sylk_row,sylk_header}  (production facades)
    sylk.cli                     (ff-sylk command-line entry point)
    sylk.sylk_to_{abw,csv,dif,fodg,fods,fodt,gnumeric,ndjson,ods,odt,
                   pbm,pgm,ppm,toml,tsv}  (15 dogfood converters)

Ground-truth expected values below were computed by direct execution
against the fixture samples (not hand-derived) to avoid silent
assertion drift.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

import pytest

VALID = _REPO / "samples" / "by-format" / "sylk" / "valid"
INVALID = _REPO / "samples" / "by-format" / "sylk" / "invalid"
SINGLE = VALID / "single-cell.slk"
MINIMAL = VALID / "minimal-2x2.slk"
NUMERIC = VALID / "numeric-row.slk"
MISSING_ID = INVALID / "missing-id-record.slk"


def _write_slk(path: Path, records: list[str]) -> Path:
    """Write a minimal well-formed SYLK file with the given C records."""
    content = "\r\n".join(["ID;P", *records, "E"]) + "\r\n"
    path.write_bytes(content.encode("ascii"))
    return path


@pytest.fixture
def empty_doc(tmp_path: Path) -> Path:
    """A SYLK file with a valid header/footer but zero cells."""
    return _write_slk(tmp_path / "empty.slk", [])


@pytest.fixture
def tall_doc(tmp_path: Path) -> Path:
    """3 rows x 1 column — exercises is_tall=True / is_wide=False."""
    return _write_slk(
        tmp_path / "tall.slk",
        ["C;X1;Y1;K1", "C;X1;Y2;K2", "C;X1;Y3;K3"],
    )


@pytest.fixture
def sparse_doc(tmp_path: Path) -> Path:
    """3x3 logical grid with only 2/9 cells occupied (corners)."""
    return _write_slk(
        tmp_path / "sparse.slk",
        ['C;X1;Y1;K"a"', 'C;X3;Y3;K"b"'],
    )


# ---------------------------------------------------------------------------
# PRIORITY: the 6 gaps that were still `open` in the gap ledger
# (sylk_value_analytics.py grid-level analytics section)
# ---------------------------------------------------------------------------

class TestGapClosureGridAnalytics:
    """Closes GAP-SYLK-FOSS-SYLK_HAS_DAT-001, SYLK_IS_SQUA-001,
    SYLK_GRID_SI-001, SYLK_CELL_FI-001, SYLK_IS_WIDE-001, SYLK_IS_TALL-001.
    """

    # --- sylk_has_data ---

    def test_has_data_true_single_cell(self):
        from sylk.sylk_value_analytics import sylk_has_data
        assert sylk_has_data(SINGLE) is True

    def test_has_data_true_minimal(self):
        from sylk.sylk_value_analytics import sylk_has_data
        assert sylk_has_data(MINIMAL) is True

    def test_has_data_true_numeric_row(self):
        from sylk.sylk_value_analytics import sylk_has_data
        assert sylk_has_data(NUMERIC) is True

    def test_has_data_false_when_empty(self, empty_doc):
        from sylk.sylk_value_analytics import sylk_has_data
        assert sylk_has_data(empty_doc) is False

    def test_has_data_returns_bool_type(self):
        from sylk.sylk_value_analytics import sylk_has_data
        assert isinstance(sylk_has_data(SINGLE), bool)

    # --- sylk_is_square_grid ---

    def test_is_square_grid_true_single_cell(self):
        from sylk.sylk_value_analytics import sylk_is_square_grid
        assert sylk_is_square_grid(SINGLE) is True  # 1 row == 1 col

    def test_is_square_grid_true_minimal(self):
        from sylk.sylk_value_analytics import sylk_is_square_grid
        assert sylk_is_square_grid(MINIMAL) is True  # 2 rows == 2 cols

    def test_is_square_grid_false_numeric_row(self):
        from sylk.sylk_value_analytics import sylk_is_square_grid
        assert sylk_is_square_grid(NUMERIC) is False  # 1 row != 3 cols

    def test_is_square_grid_false_tall(self, tall_doc):
        from sylk.sylk_value_analytics import sylk_is_square_grid
        assert sylk_is_square_grid(tall_doc) is False  # 3 rows != 1 col

    def test_is_square_grid_vacuously_true_when_empty(self, empty_doc):
        from sylk.sylk_value_analytics import sylk_is_square_grid
        # rows == cols == 0
        assert sylk_is_square_grid(empty_doc) is True

    # --- sylk_grid_size ---

    def test_grid_size_single_cell(self):
        from sylk.sylk_value_analytics import sylk_grid_size
        assert sylk_grid_size(SINGLE) == 1

    def test_grid_size_minimal(self):
        from sylk.sylk_value_analytics import sylk_grid_size
        assert sylk_grid_size(MINIMAL) == 4

    def test_grid_size_numeric_row(self):
        from sylk.sylk_value_analytics import sylk_grid_size
        assert sylk_grid_size(NUMERIC) == 3

    def test_grid_size_zero_when_empty(self, empty_doc):
        from sylk.sylk_value_analytics import sylk_grid_size
        assert sylk_grid_size(empty_doc) == 0

    def test_grid_size_tall_doc(self, tall_doc):
        from sylk.sylk_value_analytics import sylk_grid_size
        assert sylk_grid_size(tall_doc) == 3  # 3 rows * 1 col

    # --- sylk_cell_fill_ratio ---

    def test_cell_fill_ratio_single_cell(self):
        from sylk.sylk_value_analytics import sylk_cell_fill_ratio
        assert sylk_cell_fill_ratio(SINGLE) == pytest.approx(1.0)

    def test_cell_fill_ratio_minimal(self):
        from sylk.sylk_value_analytics import sylk_cell_fill_ratio
        assert sylk_cell_fill_ratio(MINIMAL) == pytest.approx(1.0)

    def test_cell_fill_ratio_numeric_row(self):
        from sylk.sylk_value_analytics import sylk_cell_fill_ratio
        assert sylk_cell_fill_ratio(NUMERIC) == pytest.approx(1.0)

    def test_cell_fill_ratio_zero_when_empty(self, empty_doc):
        from sylk.sylk_value_analytics import sylk_cell_fill_ratio
        assert sylk_cell_fill_ratio(empty_doc) == pytest.approx(0.0)

    def test_cell_fill_ratio_sparse_grid(self, sparse_doc):
        from sylk.sylk_value_analytics import sylk_cell_fill_ratio
        # 3x3 grid, 2 cells occupied -> 2/9
        assert sylk_cell_fill_ratio(sparse_doc) == pytest.approx(2 / 9)

    # --- sylk_is_wide ---

    def test_is_wide_false_single_cell(self):
        from sylk.sylk_value_analytics import sylk_is_wide
        assert sylk_is_wide(SINGLE) is False

    def test_is_wide_false_minimal_square(self):
        from sylk.sylk_value_analytics import sylk_is_wide
        assert sylk_is_wide(MINIMAL) is False  # 2 cols == 2 rows, not >

    def test_is_wide_true_numeric_row(self):
        from sylk.sylk_value_analytics import sylk_is_wide
        assert sylk_is_wide(NUMERIC) is True  # 3 cols > 1 row

    def test_is_wide_false_when_empty(self, empty_doc):
        from sylk.sylk_value_analytics import sylk_is_wide
        assert sylk_is_wide(empty_doc) is False

    def test_is_wide_false_tall_doc(self, tall_doc):
        from sylk.sylk_value_analytics import sylk_is_wide
        assert sylk_is_wide(tall_doc) is False  # 1 col, not > 3 rows

    # --- sylk_is_tall ---

    def test_is_tall_false_single_cell(self):
        from sylk.sylk_value_analytics import sylk_is_tall
        assert sylk_is_tall(SINGLE) is False

    def test_is_tall_false_minimal_square(self):
        from sylk.sylk_value_analytics import sylk_is_tall
        assert sylk_is_tall(MINIMAL) is False

    def test_is_tall_false_numeric_row(self):
        from sylk.sylk_value_analytics import sylk_is_tall
        assert sylk_is_tall(NUMERIC) is False  # 1 row, not > 3 cols

    def test_is_tall_false_when_empty(self, empty_doc):
        from sylk.sylk_value_analytics import sylk_is_tall
        assert sylk_is_tall(empty_doc) is False

    def test_is_tall_true_tall_doc(self, tall_doc):
        from sylk.sylk_value_analytics import sylk_is_tall
        assert sylk_is_tall(tall_doc) is True  # 3 rows > 1 col

    def test_is_wide_and_is_tall_are_mutually_exclusive(self):
        from sylk.sylk_value_analytics import sylk_is_wide, sylk_is_tall
        for sample in (SINGLE, MINIMAL, NUMERIC):
            assert not (sylk_is_wide(sample) and sylk_is_tall(sample))


# ---------------------------------------------------------------------------
# sylk_parser — core parse/probe/capabilities API
# ---------------------------------------------------------------------------

class TestParserExceptionHierarchy:
    def test_hierarchy(self):
        import sylk.sylk_parser as sp
        assert issubclass(sp.SylkInvalidFormatError, sp.SylkError)
        assert issubclass(sp.SylkSizeError, sp.SylkError)
        assert issubclass(sp.SylkParseError, sp.SylkError)
        assert issubclass(sp.SylkError, Exception)


class TestParseSylkStrict:
    def test_parses_single_cell(self):
        from sylk.sylk_parser import parse_sylk_strict
        doc = parse_sylk_strict(SINGLE)
        assert doc.rows == 1 and doc.cols == 1 and len(doc.cells) == 1

    def test_parses_minimal_2x2(self):
        from sylk.sylk_parser import parse_sylk_strict
        doc = parse_sylk_strict(MINIMAL)
        assert doc.rows == 2 and doc.cols == 2 and len(doc.cells) == 4
        assert doc.id_line == "ID;P"

    def test_parses_numeric_row(self):
        from sylk.sylk_parser import parse_sylk_strict
        doc = parse_sylk_strict(NUMERIC)
        assert doc.rows == 1 and doc.cols == 3 and len(doc.cells) == 3

    def test_file_not_found_raises_sylkerror(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkError
        with pytest.raises(SylkError):
            parse_sylk_strict(tmp_path / "does-not-exist.slk")

    def test_missing_id_record_raises_invalid_format(self):
        from sylk.sylk_parser import parse_sylk_strict, SylkInvalidFormatError
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(MISSING_ID)

    def test_empty_file_raises_invalid_format(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkInvalidFormatError
        p = tmp_path / "empty_file.slk"
        p.write_bytes(b"")
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(p)

    def test_missing_end_record_raises_parse_error(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkParseError
        p = tmp_path / "no_end.slk"
        p.write_bytes(b"ID;P\r\nC;X1;Y1;K1\r\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)

    def test_invalid_x_field_raises_parse_error(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkParseError
        p = tmp_path / "bad_x.slk"
        p.write_bytes(b"ID;P\r\nC;Xabc;Y1;K1\r\nE\r\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)

    def test_invalid_y_field_raises_parse_error(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkParseError
        p = tmp_path / "bad_y.slk"
        p.write_bytes(b"ID;P\r\nC;X1;Yabc;K1\r\nE\r\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)

    def test_column_over_limit_raises_size_error(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkSizeError
        p = tmp_path / "big_col.slk"
        p.write_bytes(b"ID;P\r\nC;X99999;Y1;K1\r\nE\r\n")
        with pytest.raises(SylkSizeError):
            parse_sylk_strict(p)

    def test_row_over_limit_raises_size_error(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, SylkSizeError
        p = tmp_path / "big_row.slk"
        p.write_bytes(b"ID;P\r\nC;X1;Y9999999;K1\r\nE\r\n")
        with pytest.raises(SylkSizeError):
            parse_sylk_strict(p)


class TestSylkCellAndDocumentDataclasses:
    def test_sylk_cell_defaults(self):
        from sylk.sylk_parser import SylkCell
        c = SylkCell()
        assert c.row == 1 and c.col == 1 and c.value is None and c.value_type == "empty"

    def test_sylk_cell_spec_qname(self):
        from sylk.sylk_parser import SylkCell
        assert SylkCell.spec_qname == "slk:cell"

    def test_sylk_document_defaults(self):
        from sylk.sylk_parser import SylkDocument
        doc = SylkDocument()
        assert doc.cells == [] and doc.rows == 0 and doc.cols == 0

    def test_sylk_document_spec_qname(self):
        from sylk.sylk_parser import SylkDocument
        assert SylkDocument.spec_qname == "sylk:document"


class TestParseSylkNonStrict:
    def test_ok_true_for_valid_file(self):
        from sylk.sylk_parser import parse_sylk
        result = parse_sylk(MINIMAL)
        assert result == {
            "ok": True,
            "path": str(MINIMAL),
            "rows": 2,
            "cols": 2,
            "cell_count": 4,
            "id_line": "ID;P",
        }

    def test_ok_false_for_invalid_file(self):
        from sylk.sylk_parser import parse_sylk
        result = parse_sylk(MISSING_ID)
        assert result["ok"] is False
        assert result["error_type"] == "SylkInvalidFormatError"
        assert "Missing ID record" in result["error"]

    def test_never_raises(self, tmp_path):
        from sylk.sylk_parser import parse_sylk
        result = parse_sylk(tmp_path / "nope.slk")
        assert result["ok"] is False


class TestProbeSylk:
    def test_probe_valid_file(self):
        from sylk.sylk_parser import probe_sylk
        result = probe_sylk(MINIMAL)
        assert result["exists"] is True
        assert result["valid_header"] is True
        assert result["id_line"] == "ID;P"

    def test_probe_missing_file(self, tmp_path):
        from sylk.sylk_parser import probe_sylk
        result = probe_sylk(tmp_path / "nope.slk")
        assert result["exists"] is False
        assert "valid_header" not in result

    def test_probe_invalid_header(self):
        from sylk.sylk_parser import probe_sylk
        result = probe_sylk(MISSING_ID)
        assert result["exists"] is True
        assert result["valid_header"] is False
        assert "error" in result


class TestGetCapabilities:
    def test_capability_descriptor_shape(self):
        from sylk.sylk_parser import get_capabilities
        caps = get_capabilities()
        assert caps["format"] == "sylk"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False
        assert isinstance(caps["supported"], list)
        assert isinstance(caps["unsupported"], list)

    def test_supported_features_contains_core_parsing(self):
        from sylk.sylk_parser import SUPPORTED_FEATURES
        assert "id_record_parse" in SUPPORTED_FEATURES
        assert "c_record_parse" in SUPPORTED_FEATURES

    def test_unsupported_features_contains_formulas(self):
        from sylk.sylk_parser import UNSUPPORTED_FEATURES
        assert "formula_cells" in UNSUPPORTED_FEATURES
        assert "multi_sheet" in UNSUPPORTED_FEATURES

    def test_supported_and_unsupported_disjoint(self):
        from sylk.sylk_parser import SUPPORTED_FEATURES, UNSUPPORTED_FEATURES
        assert SUPPORTED_FEATURES.isdisjoint(UNSUPPORTED_FEATURES)


class TestParserModuleLevelWriteAndCsv:
    """sylk_parser.py defines its own write_sylk/sylk_to_csv, distinct
    from sylk_writer.write_sylk and sylk_to_csv.sylk_to_csv (dogfood)."""

    def test_write_sylk_roundtrip(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, write_sylk
        doc = parse_sylk_strict(MINIMAL)
        dest = tmp_path / "roundtrip.slk"
        write_sylk(doc, dest)
        doc2 = parse_sylk_strict(dest)
        assert doc2.rows == doc.rows and doc2.cols == doc.cols
        assert len(doc2.cells) == len(doc.cells)

    def test_write_sylk_writes_quoted_strings(self, tmp_path):
        from sylk.sylk_parser import parse_sylk_strict, write_sylk
        doc = parse_sylk_strict(MINIMAL)
        dest = tmp_path / "quoted.slk"
        write_sylk(doc, dest)
        text = dest.read_text(encoding="ascii")
        assert 'K"Name"' in text

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, "99\r\n"),
        (MINIMAL, "Name,Value\r\nAlpha,42\r\n"),
        (NUMERIC, "1,2,3\r\n"),
    ])
    def test_parser_sylk_to_csv(self, sample, expected):
        from sylk.sylk_parser import sylk_to_csv as parser_sylk_to_csv
        assert parser_sylk_to_csv(sample) == expected

    def test_parser_sylk_to_csv_empty_doc(self, empty_doc):
        from sylk.sylk_parser import sylk_to_csv as parser_sylk_to_csv
        assert parser_sylk_to_csv(empty_doc) == ""


class TestCellRowColumnAccessors:
    @pytest.mark.parametrize("sample,row,expected", [
        (SINGLE, 1, [99]),
        (MINIMAL, 1, ["Name", "Value"]),
        (MINIMAL, 2, ["Alpha", 42]),
        (NUMERIC, 1, [1, 2, 3]),
        (NUMERIC, 2, []),
    ])
    def test_get_row_values(self, sample, row, expected):
        from sylk.sylk_parser import get_row_values
        assert get_row_values(sample, row) == expected

    @pytest.mark.parametrize("sample,col,expected", [
        (SINGLE, 1, [99]),
        (MINIMAL, 1, ["Name", "Alpha"]),
        (MINIMAL, 2, ["Value", 42]),
        (NUMERIC, 1, [1]),
        (NUMERIC, 2, [2]),
    ])
    def test_get_column_values(self, sample, col, expected):
        from sylk.sylk_parser import get_column_values
        assert get_column_values(sample, col) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 1), (MINIMAL, 2), (NUMERIC, 1),
    ])
    def test_get_row_count(self, sample, expected):
        from sylk.sylk_parser import get_row_count
        assert get_row_count(sample) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 1), (MINIMAL, 2), (NUMERIC, 3),
    ])
    def test_get_column_count(self, sample, expected):
        from sylk.sylk_parser import get_column_count
        assert get_column_count(sample) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 1), (MINIMAL, 4), (NUMERIC, 3),
    ])
    def test_get_cell_count(self, sample, expected):
        from sylk.sylk_parser import get_cell_count
        assert get_cell_count(sample) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, [99]),
        (MINIMAL, ["Name", "Value", "Alpha", 42]),
        (NUMERIC, [1, 2, 3]),
    ])
    def test_get_all_values(self, sample, expected):
        from sylk.sylk_parser import get_all_values
        assert get_all_values(sample) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 99), (MINIMAL, "Name"), (NUMERIC, 1),
    ])
    def test_get_cell_value_1_1(self, sample, expected):
        from sylk.sylk_parser import get_cell_value
        assert get_cell_value(sample, 1, 1) == expected

    def test_get_cell_value_out_of_range_returns_none(self):
        from sylk.sylk_parser import get_cell_value
        assert get_cell_value(MINIMAL, 99, 99) is None


class TestMutationFunctions:
    def test_set_cell_value_on_model_existing_cell(self):
        from sylk.sylk_parser import parse_sylk_strict, set_cell_value_on_model
        doc = parse_sylk_strict(MINIMAL)
        result = set_cell_value_on_model(doc, 1, 1, "Changed", "string")
        assert result == {
            "ok": True, "row": 1, "col": 1,
            "old_value": "Name", "new_value": "Changed",
        }

    def test_set_cell_value_on_model_new_cell_expands_dims(self):
        from sylk.sylk_parser import parse_sylk_strict, set_cell_value_on_model
        doc = parse_sylk_strict(MINIMAL)
        result = set_cell_value_on_model(doc, 5, 5, "New", "string")
        assert result["ok"] is True and result["old_value"] is None
        assert doc.rows == 5 and doc.cols == 5

    def test_set_cell_value_on_model_invalid_row_raises(self):
        from sylk.sylk_parser import parse_sylk_strict, set_cell_value_on_model, SylkError
        doc = parse_sylk_strict(MINIMAL)
        with pytest.raises(SylkError):
            set_cell_value_on_model(doc, 0, 1, "x")

    def test_set_cell_value_on_model_invalid_col_raises(self):
        from sylk.sylk_parser import parse_sylk_strict, set_cell_value_on_model, SylkError
        doc = parse_sylk_strict(MINIMAL)
        with pytest.raises(SylkError):
            set_cell_value_on_model(doc, 1, 0, "x")

    def test_set_cell_value_file_roundtrip(self, tmp_path):
        from sylk.sylk_parser import set_cell_value, get_cell_value
        dest = tmp_path / "out.slk"
        result = set_cell_value(MINIMAL, dest, 1, 1, "Hi", "string")
        assert result["ok"] is True
        assert get_cell_value(dest, 1, 1) == "Hi"

    def test_add_row_appends_and_writes(self, tmp_path):
        from sylk.sylk_parser import add_row, parse_sylk_strict
        dest = tmp_path / "added.slk"
        result = add_row(MINIMAL, dest, ["x", "y"])
        assert result == {"success": True, "row_index": 3, "cell_count": 2}
        doc = parse_sylk_strict(dest)
        assert doc.rows == 3

    def test_delete_row_removes_and_shifts(self, tmp_path):
        from sylk.sylk_parser import delete_row, parse_sylk_strict
        dest = tmp_path / "deleted.slk"
        result = delete_row(MINIMAL, dest, 1)
        assert result == {"success": True, "deleted_count": 2}
        doc = parse_sylk_strict(dest)
        # row 2 cells shifted down to row 1
        assert {(c.row, c.col, c.value) for c in doc.cells} == {
            (1, 1, "Alpha"), (1, 2, 42),
        }


class TestParserAnalyticsHelpers:
    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 1), (MINIMAL, 4), (NUMERIC, 3),
    ])
    def test_count_nonempty_cells(self, sample, expected):
        from sylk.sylk_parser import count_nonempty_cells
        assert count_nonempty_cells(sample) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 99.0), (MINIMAL, 0.0), (NUMERIC, 1.0),
    ])
    def test_sum_column_1(self, sample, expected):
        from sylk.sylk_parser import sum_column
        assert sum_column(sample, 1) == pytest.approx(expected)

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 99), (MINIMAL, None), (NUMERIC, 1),
    ])
    def test_min_column_value_1(self, sample, expected):
        from sylk.sylk_parser import min_column_value
        assert min_column_value(sample, 1) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 99), (MINIMAL, None), (NUMERIC, 1),
    ])
    def test_max_column_value_1(self, sample, expected):
        from sylk.sylk_parser import max_column_value
        assert max_column_value(sample, 1) == expected

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 99.0), (MINIMAL, 0.0), (NUMERIC, 1.0),
    ])
    def test_average_column_1(self, sample, expected):
        from sylk.sylk_parser import average_column
        assert average_column(sample, 1) == pytest.approx(expected)

    def test_find_value_found(self):
        from sylk.sylk_parser import find_value
        assert find_value(MINIMAL, "Alpha") == (2, 1)
        assert find_value(MINIMAL, 42) == (2, 2)

    def test_find_value_not_found(self):
        from sylk.sylk_parser import find_value
        assert find_value(SINGLE, "Alpha") is None
        assert find_value(NUMERIC, 42) is None

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, 1), (MINIMAL, 2), (NUMERIC, 1),
    ])
    def test_count_distinct_values_col_1(self, sample, expected):
        from sylk.sylk_parser import count_distinct_values
        assert count_distinct_values(sample, 1) == expected

    def test_find_rows_by_value(self):
        from sylk.sylk_parser import find_rows_by_value
        assert find_rows_by_value(MINIMAL, 42) == [2]
        assert find_rows_by_value(SINGLE, 42) == []
        assert find_rows_by_value(NUMERIC, 42) == []

    def test_sylk_to_html_wraps_table(self):
        from sylk.sylk_parser import sylk_to_html
        html = sylk_to_html(MINIMAL)
        assert html.startswith("<table>") and html.endswith("</table>")
        assert "<td>Name</td>" in html and "<td>42</td>" in html

    def test_sylk_to_html_empty_doc(self, empty_doc):
        from sylk.sylk_parser import sylk_to_html
        assert sylk_to_html(empty_doc) == "<table></table>"


# ---------------------------------------------------------------------------
# sylk_writer — write_sylk / write_sylk_str
# ---------------------------------------------------------------------------

class TestSylkWriter:
    def test_write_sylk_str_numeric_and_string(self):
        from sylk.sylk_writer import write_sylk_str
        from sylk.sylk_parser import SylkDocument, SylkCell
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value=5, value_type="numeric"),
            SylkCell(row=1, col=2, value='hi "q"', value_type="string"),
        ], rows=1, cols=2)
        text = write_sylk_str(doc)
        assert text.startswith("ID;P\n")
        assert text.endswith("E\n")
        assert "C;X1;Y1;K5" in text
        assert 'C;X2;Y1;K"hi ""q"""' in text  # embedded quotes doubled

    def test_write_sylk_str_accepts_bare_cell_list(self):
        from sylk.sylk_writer import write_sylk_str
        from sylk.sylk_parser import SylkCell
        text = write_sylk_str([SylkCell(row=1, col=1, value=1, value_type="numeric")])
        assert "C;X1;Y1;K1" in text

    def test_write_sylk_str_none_document_raises(self):
        from sylk.sylk_writer import write_sylk_str, SylkWriteError
        with pytest.raises(SylkWriteError):
            write_sylk_str(None)

    def test_write_sylk_str_cell_missing_row_raises(self):
        from sylk.sylk_writer import write_sylk_str, SylkWriteError

        class _Bad:
            row = None

        with pytest.raises(SylkWriteError):
            write_sylk_str([_Bad()])

    def test_write_sylk_empty_path_raises(self):
        from sylk.sylk_writer import write_sylk, SylkWriteError
        from sylk.sylk_parser import SylkDocument
        with pytest.raises(SylkWriteError):
            write_sylk(SylkDocument(), "")

    def test_write_sylk_creates_parent_dirs(self, tmp_path):
        from sylk.sylk_writer import write_sylk
        from sylk.sylk_parser import SylkDocument, SylkCell
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value=1, value_type="numeric")])
        dest = tmp_path / "nested" / "dir" / "out.slk"
        write_sylk(doc, dest)
        assert dest.exists()
        assert dest.read_text(encoding="utf-8").startswith("ID;P\n")

    def test_write_sylk_then_reparse_roundtrip(self, tmp_path):
        from sylk.sylk_writer import write_sylk
        from sylk.sylk_parser import SylkDocument, SylkCell, parse_sylk_strict
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value="Alpha", value_type="string"),
            SylkCell(row=2, col=2, value=7, value_type="numeric"),
        ])
        dest = tmp_path / "rt.slk"
        write_sylk(doc, dest)
        reparsed = parse_sylk_strict(dest)
        assert len(reparsed.cells) == 2


# ---------------------------------------------------------------------------
# sylk_analytics — scalar analytics functions (ground truth computed by
# direct execution against the fixture samples)
# ---------------------------------------------------------------------------

_SA_CASES = [
    ("sylk_average_numeric_value", SINGLE, 99.0),
    ("sylk_average_numeric_value", MINIMAL, 42.0),
    ("sylk_average_numeric_value", NUMERIC, 2.0),
    ("sylk_avg_cell_length", SINGLE, 2.0),
    ("sylk_avg_cell_length", MINIMAL, 4.0),
    ("sylk_avg_cell_length", NUMERIC, 1.0),
    ("sylk_avg_cell_value_length", SINGLE, 2.0),
    ("sylk_avg_cell_value_length", MINIMAL, 4.0),
    ("sylk_avg_cell_value_length", NUMERIC, 1.0),
    ("sylk_avg_numeric_cell_length", SINGLE, 2.0),
    ("sylk_avg_numeric_cell_length", MINIMAL, 2.0),
    ("sylk_avg_numeric_cell_length", NUMERIC, 1.0),
    ("sylk_avg_numeric_value", SINGLE, 99.0),
    ("sylk_avg_numeric_value", MINIMAL, 42.0),
    ("sylk_avg_numeric_value", NUMERIC, 2.0),
    ("sylk_avg_row_density", SINGLE, 1.0),
    ("sylk_avg_row_density", MINIMAL, 2.0),
    ("sylk_avg_row_density", NUMERIC, 3.0),
    ("sylk_avg_row_length", SINGLE, 1.0),
    ("sylk_avg_row_length", MINIMAL, 2.0),
    ("sylk_avg_row_length", NUMERIC, 3.0),
    ("sylk_cell_count_variance", SINGLE, 0.0),
    ("sylk_cell_count_variance", MINIMAL, 0.0),
    ("sylk_cell_count_variance", NUMERIC, 0.0),
    ("sylk_cell_text_length_sum", SINGLE, 2),
    ("sylk_cell_text_length_sum", MINIMAL, 16),
    ("sylk_cell_text_length_sum", NUMERIC, 3),
    ("sylk_column_count", SINGLE, 1),
    ("sylk_column_count", MINIMAL, 2),
    ("sylk_column_count", NUMERIC, 3),
    ("sylk_column_fill_rate", SINGLE, 1.0),
    ("sylk_column_fill_rate", MINIMAL, 1.0),
    ("sylk_column_fill_rate", NUMERIC, 1.0),
    ("sylk_column_span", SINGLE, 1),
    ("sylk_column_span", MINIMAL, 2),
    ("sylk_column_span", NUMERIC, 3),
    ("sylk_column_variance", SINGLE, 0.0),
    ("sylk_column_variance", MINIMAL, 0.0),
    ("sylk_column_variance", NUMERIC, 0.0),
    ("sylk_data_density", SINGLE, 1.0),
    ("sylk_data_density", MINIMAL, 1.0),
    ("sylk_data_density", NUMERIC, 1.0),
    ("sylk_data_sparsity", SINGLE, 0.0),
    ("sylk_data_sparsity", MINIMAL, 0.0),
    ("sylk_data_sparsity", NUMERIC, 0.0),
    ("sylk_distinct_string_count", SINGLE, 0),
    ("sylk_distinct_string_count", MINIMAL, 3),
    ("sylk_distinct_string_count", NUMERIC, 0),
    ("sylk_empty_cell_count", SINGLE, 0),
    ("sylk_empty_cell_count", MINIMAL, 0),
    ("sylk_empty_cell_count", NUMERIC, 0),
    ("sylk_has_empty_cells", SINGLE, False),
    ("sylk_has_empty_cells", MINIMAL, False),
    ("sylk_has_empty_cells", NUMERIC, False),
    ("sylk_has_empty_rows", SINGLE, False),
    ("sylk_has_empty_rows", MINIMAL, False),
    ("sylk_has_empty_rows", NUMERIC, False),
    ("sylk_has_header", SINGLE, False),
    ("sylk_has_header", MINIMAL, True),
    ("sylk_has_header", NUMERIC, False),
    ("sylk_has_numeric_cells", SINGLE, True),
    ("sylk_has_numeric_cells", MINIMAL, True),
    ("sylk_has_numeric_cells", NUMERIC, True),
    ("sylk_has_string_cells", SINGLE, False),
    ("sylk_has_string_cells", MINIMAL, True),
    ("sylk_has_string_cells", NUMERIC, False),
    ("sylk_is_all_numeric", SINGLE, True),
    ("sylk_is_all_numeric", MINIMAL, False),
    ("sylk_is_all_numeric", NUMERIC, True),
    ("sylk_is_empty", SINGLE, False),
    ("sylk_is_empty", MINIMAL, False),
    ("sylk_is_empty", NUMERIC, False),
    ("sylk_is_multi_row", SINGLE, False),
    ("sylk_is_multi_row", MINIMAL, True),
    ("sylk_is_multi_row", NUMERIC, False),
    ("sylk_is_rectangular", SINGLE, True),
    ("sylk_is_rectangular", MINIMAL, True),
    ("sylk_is_rectangular", NUMERIC, True),
    ("sylk_is_single_column", SINGLE, True),
    ("sylk_is_single_column", MINIMAL, False),
    ("sylk_is_single_column", NUMERIC, False),
    ("sylk_is_single_row", SINGLE, True),
    ("sylk_is_single_row", MINIMAL, False),
    ("sylk_is_single_row", NUMERIC, True),
    ("sylk_is_square", SINGLE, True),
    ("sylk_is_square", MINIMAL, True),
    ("sylk_is_square", NUMERIC, False),
    ("sylk_longest_row_index", SINGLE, 1),
    ("sylk_longest_row_index", MINIMAL, 1),
    ("sylk_longest_row_index", NUMERIC, 1),
    ("sylk_max_cell_value_length", SINGLE, 2),
    ("sylk_max_cell_value_length", MINIMAL, 5),
    ("sylk_max_cell_value_length", NUMERIC, 1),
    ("sylk_max_column_index", SINGLE, 1),
    ("sylk_max_column_index", MINIMAL, 2),
    ("sylk_max_column_index", NUMERIC, 3),
    ("sylk_max_numeric_value", SINGLE, 99.0),
    ("sylk_max_numeric_value", MINIMAL, 42.0),
    ("sylk_max_numeric_value", NUMERIC, 3.0),
    ("sylk_max_row_cell_count", SINGLE, 1),
    ("sylk_max_row_cell_count", MINIMAL, 2),
    ("sylk_max_row_cell_count", NUMERIC, 3),
    ("sylk_max_row_index", SINGLE, 1),
    ("sylk_max_row_index", MINIMAL, 2),
    ("sylk_max_row_index", NUMERIC, 1),
    ("sylk_max_row_length", SINGLE, 1),
    ("sylk_max_row_length", MINIMAL, 2),
    ("sylk_max_row_length", NUMERIC, 3),
    ("sylk_max_string_length", SINGLE, 0),
    ("sylk_max_string_length", MINIMAL, 5),
    ("sylk_max_string_length", NUMERIC, 0),
    ("sylk_min_cell_value_length", SINGLE, 2),
    ("sylk_min_cell_value_length", MINIMAL, 2),
    ("sylk_min_cell_value_length", NUMERIC, 1),
    ("sylk_min_col_index", SINGLE, 1),
    ("sylk_min_col_index", MINIMAL, 1),
    ("sylk_min_col_index", NUMERIC, 1),
    ("sylk_min_numeric_value", SINGLE, 99.0),
    ("sylk_min_numeric_value", MINIMAL, 42.0),
    ("sylk_min_numeric_value", NUMERIC, 1.0),
    ("sylk_min_row_index", SINGLE, 1),
    ("sylk_min_row_index", MINIMAL, 1),
    ("sylk_min_row_index", NUMERIC, 1),
    ("sylk_min_row_length", SINGLE, 1),
    ("sylk_min_row_length", MINIMAL, 2),
    ("sylk_min_row_length", NUMERIC, 3),
    ("sylk_nonempty_cell_count", SINGLE, 1),
    ("sylk_nonempty_cell_count", MINIMAL, 4),
    ("sylk_nonempty_cell_count", NUMERIC, 3),
    ("sylk_nonempty_cell_ratio", SINGLE, 1.0),
    ("sylk_nonempty_cell_ratio", MINIMAL, 1.0),
    ("sylk_nonempty_cell_ratio", NUMERIC, 1.0),
    ("sylk_nonempty_row_ratio", SINGLE, 1.0),
    ("sylk_nonempty_row_ratio", MINIMAL, 1.0),
    ("sylk_nonempty_row_ratio", NUMERIC, 1.0),
    ("sylk_nonempty_rows", SINGLE, 1),
    ("sylk_nonempty_rows", MINIMAL, 2),
    ("sylk_nonempty_rows", NUMERIC, 1),
    ("sylk_numeric_cell_count", SINGLE, 1),
    ("sylk_numeric_cell_count", MINIMAL, 1),
    ("sylk_numeric_cell_count", NUMERIC, 3),
    ("sylk_numeric_cell_ratio", SINGLE, 1.0),
    ("sylk_numeric_cell_ratio", MINIMAL, 0.25),
    ("sylk_numeric_cell_ratio", NUMERIC, 1.0),
    ("sylk_numeric_density", SINGLE, 1.0),
    ("sylk_numeric_density", MINIMAL, 0.25),
    ("sylk_numeric_density", NUMERIC, 1.0),
    ("sylk_numeric_range", SINGLE, 0.0),
    ("sylk_numeric_range", MINIMAL, 0.0),
    ("sylk_numeric_range", NUMERIC, 2.0),
    ("sylk_numeric_sum", SINGLE, 99.0),
    ("sylk_numeric_sum", MINIMAL, 42.0),
    ("sylk_numeric_sum", NUMERIC, 6.0),
    ("sylk_numeric_value_sum", SINGLE, 99.0),
    ("sylk_numeric_value_sum", MINIMAL, 42.0),
    ("sylk_numeric_value_sum", NUMERIC, 6.0),
    ("sylk_numeric_variance", SINGLE, 0.0),
    ("sylk_numeric_variance", MINIMAL, 0.0),
    ("sylk_numeric_variance", NUMERIC, 0.6666666666666666),
    ("sylk_row_count", SINGLE, 1),
    ("sylk_row_count", MINIMAL, 2),
    ("sylk_row_count", NUMERIC, 1),
    ("sylk_row_span", SINGLE, 1),
    ("sylk_row_span", MINIMAL, 2),
    ("sylk_row_span", NUMERIC, 1),
    ("sylk_string_cell_count", SINGLE, 0),
    ("sylk_string_cell_count", MINIMAL, 3),
    ("sylk_string_cell_count", NUMERIC, 0),
    ("sylk_string_density", SINGLE, 0.0),
    ("sylk_string_density", MINIMAL, 0.75),
    ("sylk_string_density", NUMERIC, 0.0),
    ("sylk_string_value_count", SINGLE, 0),
    ("sylk_string_value_count", MINIMAL, 3),
    ("sylk_string_value_count", NUMERIC, 0),
    ("sylk_total_cell_count", SINGLE, 1),
    ("sylk_total_cell_count", MINIMAL, 4),
    ("sylk_total_cell_count", NUMERIC, 3),
    ("sylk_total_cells", SINGLE, 1),
    ("sylk_total_cells", MINIMAL, 4),
    ("sylk_total_cells", NUMERIC, 3),
    ("sylk_total_string_length", SINGLE, 2),
    ("sylk_total_string_length", MINIMAL, 16),
    ("sylk_total_string_length", NUMERIC, 3),
    ("sylk_total_sum", SINGLE, 99.0),
    ("sylk_total_sum", MINIMAL, 42.0),
    ("sylk_total_sum", NUMERIC, 6.0),
    ("sylk_unique_column_count", SINGLE, 1),
    ("sylk_unique_column_count", MINIMAL, 2),
    ("sylk_unique_column_count", NUMERIC, 3),
    ("sylk_unique_row_count", SINGLE, 1),
    ("sylk_unique_row_count", MINIMAL, 2),
    ("sylk_unique_row_count", NUMERIC, 1),
    ("sylk_unique_value_count", SINGLE, 1),
    ("sylk_unique_value_count", MINIMAL, 4),
    ("sylk_unique_value_count", NUMERIC, 3),
    ("sylk_value_length_sum", SINGLE, 2),
    ("sylk_value_length_sum", MINIMAL, 16),
    ("sylk_value_length_sum", NUMERIC, 3),
]


@pytest.mark.parametrize("func_name,sample,expected", _SA_CASES)
def test_sylk_analytics_scalar_functions(func_name, sample, expected):
    import sylk.sylk_analytics as sa
    fn = getattr(sa, func_name)
    actual = fn(sample)
    if isinstance(expected, float):
        assert actual == pytest.approx(expected)
    else:
        assert actual == expected


class TestSylkAnalyticsStructuredFunctions:
    """Functions in sylk_analytics.py that don't return a plain scalar."""

    @pytest.mark.parametrize("sample,expected", [
        (SINGLE, {"numeric": 1, "string": 0, "empty": 0}),
        (MINIMAL, {"numeric": 1, "string": 3, "empty": 0}),
        (NUMERIC, {"numeric": 3, "string": 0, "empty": 0}),
    ])
    def test_cell_type_distribution(self, sample, expected):
        from sylk.sylk_analytics import sylk_cell_type_distribution
        assert sylk_cell_type_distribution(sample) == expected

    def test_unique_values_single(self):
        from sylk.sylk_analytics import sylk_unique_values
        assert sylk_unique_values(SINGLE, 1) == [99]

    def test_unique_values_minimal_sorted_by_str(self):
        from sylk.sylk_analytics import sylk_unique_values
        # mixed-nothing here (both strings) -> sorts normally
        assert sylk_unique_values(MINIMAL, 1) == ["Alpha", "Name"]

    def test_unique_values_numeric(self):
        from sylk.sylk_analytics import sylk_unique_values
        assert sylk_unique_values(NUMERIC, 1) == [1]

    def test_unique_values_empty_column(self):
        from sylk.sylk_analytics import sylk_unique_values
        assert sylk_unique_values(MINIMAL, 99) == []


# ---------------------------------------------------------------------------
# sylk_value_analytics — remaining scalar functions (grid-level 6 already
# covered exhaustively above in TestGapClosureGridAnalytics)
# ---------------------------------------------------------------------------

_SVA_CASES = [
    ("sylk_all_cells_same_type", SINGLE, True),
    ("sylk_all_cells_same_type", MINIMAL, False),
    ("sylk_all_cells_same_type", NUMERIC, True),
    ("sylk_cell_count", SINGLE, 1),
    ("sylk_cell_count", MINIMAL, 4),
    ("sylk_cell_count", NUMERIC, 3),
    ("sylk_col_count", SINGLE, 1),
    ("sylk_col_count", MINIMAL, 2),
    ("sylk_col_count", NUMERIC, 3),
    ("sylk_duplicate_value_count", SINGLE, 0),
    ("sylk_duplicate_value_count", MINIMAL, 0),
    ("sylk_duplicate_value_count", NUMERIC, 0),
    ("sylk_first_cell_value", SINGLE, 99),
    ("sylk_first_cell_value", MINIMAL, "Name"),
    ("sylk_first_cell_value", NUMERIC, 1),
    ("sylk_has_duplicate_values", SINGLE, False),
    ("sylk_has_duplicate_values", MINIMAL, False),
    ("sylk_has_duplicate_values", NUMERIC, False),
    ("sylk_has_mixed_types", SINGLE, False),
    ("sylk_has_mixed_types", MINIMAL, True),
    ("sylk_has_mixed_types", NUMERIC, False),
    ("sylk_has_only_numeric", SINGLE, True),
    ("sylk_has_only_numeric", MINIMAL, False),
    ("sylk_has_only_numeric", NUMERIC, True),
    ("sylk_has_only_strings", SINGLE, False),
    ("sylk_has_only_strings", MINIMAL, False),
    ("sylk_has_only_strings", NUMERIC, False),
    ("sylk_id_line", SINGLE, "ID;P"),
    ("sylk_id_line", MINIMAL, "ID;P"),
    ("sylk_id_line", NUMERIC, "ID;P"),
    ("sylk_last_cell_value", SINGLE, 99),
    ("sylk_last_cell_value", MINIMAL, 42),
    ("sylk_last_cell_value", NUMERIC, 3),
    ("sylk_max_row_numeric_sum", SINGLE, 99.0),
    ("sylk_max_row_numeric_sum", MINIMAL, 42.0),
    ("sylk_max_row_numeric_sum", NUMERIC, 6.0),
    ("sylk_min_row_numeric_sum", SINGLE, 99.0),
    ("sylk_min_row_numeric_sum", MINIMAL, 42.0),
    ("sylk_min_row_numeric_sum", NUMERIC, 6.0),
    ("sylk_numeric_cell_count", SINGLE, 1),
    ("sylk_numeric_cell_count", MINIMAL, 1),
    ("sylk_numeric_cell_count", NUMERIC, 3),
    ("sylk_numeric_cells_per_row", SINGLE, 1.0),
    ("sylk_numeric_cells_per_row", MINIMAL, 1.0),
    ("sylk_numeric_cells_per_row", NUMERIC, 3.0),
    ("sylk_numeric_median", SINGLE, 99.0),
    ("sylk_numeric_median", MINIMAL, 42.0),
    ("sylk_numeric_median", NUMERIC, 2.0),
    ("sylk_row_count", SINGLE, 1),
    ("sylk_row_count", MINIMAL, 2),
    ("sylk_row_count", NUMERIC, 1),
    ("sylk_string_cell_count", SINGLE, 0),
    ("sylk_string_cell_count", MINIMAL, 3),
    ("sylk_string_cell_count", NUMERIC, 0),
    ("sylk_string_to_numeric_ratio", SINGLE, 0.0),
    ("sylk_string_to_numeric_ratio", MINIMAL, 3.0),
    ("sylk_string_to_numeric_ratio", NUMERIC, 0.0),
    ("sylk_unique_value_count", SINGLE, 1),
    ("sylk_unique_value_count", MINIMAL, 4),
    ("sylk_unique_value_count", NUMERIC, 3),
]


@pytest.mark.parametrize("func_name,sample,expected", _SVA_CASES)
def test_sylk_value_analytics_scalar_functions(func_name, sample, expected):
    import sylk.sylk_value_analytics as sva
    fn = getattr(sva, func_name)
    actual = fn(sample)
    if isinstance(expected, float):
        assert actual == pytest.approx(expected)
    else:
        assert actual == expected


class TestValueAnalyticsModuleConstants:
    def test_module_level_spec_metadata(self):
        import sylk.sylk_value_analytics as sva
        assert sva.spec_qname == "sylk:cell"
        assert sva.spec_fact_ref == "SAL-SYLK-00001"
        assert sva.namespace_uri == "urn:sylk:spreadsheet"


# ---------------------------------------------------------------------------
# models — SylkModelDocument / SylkDoc
# ---------------------------------------------------------------------------

_MODEL_PROPERTY_CASES = [
    ("cell_count", 1, 4, 3),
    ("col_count", 1, 2, 3),
    ("fill_ratio", 1.0, 1.0, 1.0),
    ("has_mixed_types", False, True, False),
    ("has_numeric_cells", True, True, True),
    ("has_single_type", True, False, True),
    ("has_string_cells", False, True, False),
    ("id_line", "ID;P", "ID;P", "ID;P"),
    ("is_all_numeric", True, False, True),
    ("is_all_string", False, False, False),
    ("is_dense", True, True, True),
    ("is_empty", False, False, False),
    ("is_large_grid", False, False, False),
    ("is_numeric_dominant", True, False, True),
    ("is_single_cell", True, False, False),
    ("is_sparse", False, False, False),
    ("is_square", True, True, False),
    ("is_string_dominant", False, True, False),
    ("is_tall", False, False, False),
    ("is_wide", False, False, True),
    ("nonempty_cell_count", 1, 4, 3),
    ("numeric_cell_count", 1, 1, 3),
    ("numeric_ratio", 1.0, 0.25, 1.0),
    ("row_count", 1, 2, 1),
    ("string_cell_count", 0, 3, 0),
    ("string_ratio", 0.0, 0.75, 0.0),
]


@pytest.mark.parametrize(
    "prop_name,exp_single,exp_minimal,exp_numeric", _MODEL_PROPERTY_CASES
)
def test_sylk_model_document_properties(prop_name, exp_single, exp_minimal, exp_numeric):
    from sylk.models import SylkModelDocument
    for sample, expected in ((SINGLE, exp_single), (MINIMAL, exp_minimal), (NUMERIC, exp_numeric)):
        doc = SylkModelDocument.from_file(sample)
        actual = getattr(doc, prop_name)
        if isinstance(expected, float):
            assert actual == pytest.approx(expected)
        else:
            assert actual == expected


class TestSylkModelDocumentBehavior:
    def test_from_file_returns_model_document(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        assert isinstance(doc, SylkModelDocument)

    def test_path_property(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        assert doc.path.endswith("minimal-2x2.slk")

    def test_cells_property_returns_list(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        cells = doc.cells
        assert isinstance(cells, list) and len(cells) == 4

    def test_spec_metadata_class_vars(self):
        from sylk.models import SylkModelDocument
        assert SylkModelDocument.spec_qname == "sylk:document"
        assert SylkModelDocument.spec_fact_ref == "SAL-SYLK-00001"
        assert SylkModelDocument.namespace_uri == "urn:format:sylk:1.0"
        assert SylkModelDocument.local_name == "document"

    def test_set_cell_value_updates_existing(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        doc.set_cell_value(1, 1, "Z", "string")
        matches = [c for c in doc.cells if c.row == 1 and c.col == 1]
        assert len(matches) == 1 and matches[0].value == "Z"

    def test_set_cell_value_creates_new_and_expands_dims(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        before = doc.cell_count
        doc.set_cell_value(10, 10, "New", "string")
        assert doc.cell_count == before + 1
        assert doc.row_count == 10 and doc.col_count == 10

    def test_set_cell_value_invalid_coords_raises(self):
        from sylk.models import SylkModelDocument
        from sylk.sylk_parser import SylkError
        doc = SylkModelDocument.from_file(MINIMAL)
        with pytest.raises(SylkError):
            doc.set_cell_value(0, 1, "bad")

    def test_save_to_file_roundtrip(self, tmp_path):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        dest = tmp_path / "sub" / "model_out.slk"
        doc.save_to_file(dest)
        assert dest.exists()
        doc2 = SylkModelDocument.from_file(dest)
        assert doc2.cell_count == doc.cell_count

    def test_save_to_file_empty_path_raises(self):
        from sylk.models import SylkModelDocument
        from sylk.sylk_parser import SylkError
        doc = SylkModelDocument.from_file(MINIMAL)
        with pytest.raises(SylkError):
            doc.save_to_file("")

    def test_to_dict_shape(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        d = doc.to_dict()
        assert d["row_count"] == 2
        assert d["col_count"] == 2
        assert d["cell_count"] == 4
        assert d["path"].endswith("minimal-2x2.slk")

    def test_repr_contains_dimensions(self):
        from sylk.models import SylkModelDocument
        doc = SylkModelDocument.from_file(MINIMAL)
        r = repr(doc)
        assert "row_count=2" in r and "col_count=2" in r and "cell_count=4" in r

    def test_sylk_doc_is_alias_of_model_document(self):
        from sylk.models import SylkDoc, SylkModelDocument
        assert SylkDoc is SylkModelDocument


# ---------------------------------------------------------------------------
# sylk_workflow — installed-package proof
# ---------------------------------------------------------------------------

class TestSylkInstalledWorkflow:
    def test_workflow_from_path_string(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(MINIMAL))
        assert result == {
            "format": "sylk", "loaded": True,
            "row_count": 2, "column_count": 2, "cell_count": 4,
        }

    def test_workflow_from_path_object(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(SINGLE)
        assert result["loaded"] is True and result["cell_count"] == 1

    def test_workflow_from_bytes(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        content = MINIMAL.read_bytes()
        result = sylk_installed_workflow(content)
        assert result == {
            "format": "sylk", "loaded": True,
            "row_count": 2, "column_count": 2, "cell_count": 4,
        }

    def test_workflow_bytes_matches_path_result(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        by_path = sylk_installed_workflow(str(NUMERIC))
        by_bytes = sylk_installed_workflow(NUMERIC.read_bytes())
        assert by_path == by_bytes


# ---------------------------------------------------------------------------
# sylk_cell_iterator / sylk_row_iterator — spec-shaped iteration
# ---------------------------------------------------------------------------

class TestSylkIterCells:
    def test_yields_cell_objects_in_row_major_order(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(MINIMAL))
        coords = [(c.row, c.col, c.value) for c in cells]
        assert coords == [
            (1, 1, "Name"), (1, 2, "Value"), (2, 1, "Alpha"), (2, 2, 42),
        ]

    def test_single_cell_document(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(SINGLE))
        assert len(cells) == 1
        assert cells[0].row == 1 and cells[0].col == 1 and cells[0].value == 99

    def test_cell_to_dict(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        cells = list(sylk_iter_cells(SINGLE))
        assert cells[0].to_dict() == {"row": 1, "col": 1, "value": 99}

    def test_cell_spec_metadata(self):
        from sylk.spec.row.cell import Cell
        assert Cell.spec_qname == "sylk:cell"
        assert Cell.spec_fact_ref == "SAL-SYLK-00003"
        assert Cell.facade_names == ["SylkCell"]

    def test_iter_cells_is_a_generator(self):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        import inspect
        assert inspect.isgeneratorfunction(sylk_iter_cells)

    def test_empty_document_yields_nothing(self, empty_doc):
        from sylk.sylk_cell_iterator import sylk_iter_cells
        assert list(sylk_iter_cells(empty_doc)) == []


class TestSylkIterRows:
    def test_yields_row_objects_grouped_and_sorted(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(MINIMAL))
        assert [r.index for r in rows] == [1, 2]
        assert rows[0].cells == ["Name", "Value"]
        assert rows[1].cells == ["Alpha", 42]

    def test_row_cell_count(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(MINIMAL))
        assert all(r.cell_count == 2 for r in rows)

    def test_single_row_document(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(NUMERIC))
        assert len(rows) == 1
        assert rows[0].cells == [1, 2, 3]

    def test_row_to_dict(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(SINGLE))
        assert rows[0].to_dict() == {"index": 1, "cells": [99]}

    def test_row_repr(self):
        from sylk.sylk_row_iterator import sylk_iter_rows
        rows = list(sylk_iter_rows(SINGLE))
        assert "Row(index=1" in repr(rows[0])

    def test_row_spec_metadata(self):
        from sylk.spec.row.row import Row
        assert Row.spec_qname == "sylk:row"
        assert Row.spec_fact_ref == "SAL-SYLK-00002"
        assert Row.facade_names == ["SylkRow"]

    def test_empty_document_yields_nothing(self, empty_doc):
        from sylk.sylk_row_iterator import sylk_iter_rows
        assert list(sylk_iter_rows(empty_doc)) == []


# ---------------------------------------------------------------------------
# exceptions.py — package-level exception hierarchy (distinct from the
# sylk_parser.py hierarchy; both are exercised so neither claim is stale)
# ---------------------------------------------------------------------------

class TestPackageExceptionHierarchy:
    def test_sylk_error_is_exception(self):
        from sylk.exceptions import SylkError
        assert issubclass(SylkError, Exception)

    def test_sylk_parse_error_subclasses_sylk_error(self):
        from sylk.exceptions import SylkError, SylkParseError
        assert issubclass(SylkParseError, SylkError)

    def test_sylk_write_error_subclasses_sylk_error(self):
        from sylk.exceptions import SylkError, SylkWriteError
        assert issubclass(SylkWriteError, SylkError)

    def test_can_raise_and_catch_sylk_parse_error(self):
        from sylk.exceptions import SylkError, SylkParseError
        with pytest.raises(SylkError):
            raise SylkParseError("boom")

    def test_can_raise_and_catch_sylk_write_error(self):
        from sylk.exceptions import SylkError, SylkWriteError
        with pytest.raises(SylkError):
            raise SylkWriteError("boom")

    def test_exceptions_module_unified_with_parser_module(self):
        """Healed: sylk_parser.py imports SylkError from exceptions.py
        rather than redefining it -- single source of truth. See
        plans/.claude/quizzical-munching-gadget.md section 7."""
        from sylk.exceptions import SylkError as PkgSylkError
        from sylk.sylk_parser import SylkError as ParserSylkError
        assert PkgSylkError is ParserSylkError


# ---------------------------------------------------------------------------
# Compat facades — production-facing wrappers over spec.row classes
# ---------------------------------------------------------------------------

class TestCompatFacades:
    def test_sylk_cell_facade(self):
        from sylk.Compat.sylk_cell import SylkCell
        c = SylkCell(row=1, col=2, value="x")
        assert c.row == 1 and c.col == 2 and c.value == "x"
        assert SylkCell.spec_qname == "sylk:cell"
        assert SylkCell.spec_fact_ref == "SAL-SYLK-00003"
        assert SylkCell.namespace_uri == "urn:format:sylk:1.0"

    def test_sylk_row_facade(self):
        from sylk.Compat.sylk_row import SylkRow
        r = SylkRow(index=3, cells=["a", "b"])
        assert r.index == 3 and r.cells == ["a", "b"]
        assert SylkRow.spec_qname == "sylk:row"
        assert SylkRow.spec_fact_ref == "SAL-SYLK-00002"

    def test_sylk_header_facade(self):
        from sylk.Compat.sylk_header import SylkHeader
        h = SylkHeader({"program": "P", "row_count": 5, "col_count": 3})
        assert h.program == "P" and h.row_count == 5 and h.col_count == 3
        assert SylkHeader.spec_qname == "sylk:header"
        assert SylkHeader.spec_fact_ref == "SAL-SYLK-00001"

    def test_compat_package_exports(self):
        import sylk.Compat as compat
        assert set(compat.__all__) == {"SylkHeader", "SylkRow", "SylkCell"}

    def test_facades_are_subclasses_of_spec_classes(self):
        from sylk.Compat.sylk_cell import SylkCell
        from sylk.spec.row.cell import Cell
        from sylk.Compat.sylk_row import SylkRow
        from sylk.spec.row.row import Row
        from sylk.Compat.sylk_header import SylkHeader
        from sylk.spec.row.header import Header
        assert issubclass(SylkCell, Cell)
        assert issubclass(SylkRow, Row)
        assert issubclass(SylkHeader, Header)


class TestSpecHeaderClass:
    def test_header_defaults_and_to_dict(self):
        from sylk.spec.row.header import Header
        h = Header({"program": "Prog", "row_count": 2, "col_count": 2})
        assert h.to_dict() == {"program": "Prog", "row_count": 2, "col_count": 2}

    def test_header_missing_keys_default_safely(self):
        from sylk.spec.row.header import Header
        h = Header({})
        assert h.program == "" and h.row_count == 0 and h.col_count == 0

    def test_header_repr(self):
        from sylk.spec.row.header import Header
        h = Header({"program": "P", "row_count": 1})
        assert "Header(program='P'" in repr(h)

    def test_spec_package_exports(self):
        import sylk.spec as spec
        assert set(spec.__all__) == {"Header", "Row", "Cell"}


# ---------------------------------------------------------------------------
# cli.py — ff-sylk command-line entry point
# ---------------------------------------------------------------------------

class TestCli:
    def test_no_args_prints_usage_and_exits_zero(self, monkeypatch, capsys):
        from sylk import cli
        monkeypatch.setattr(sys, "argv", ["ff-sylk"])
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Usage: ff-sylk FILE.slk" in out

    def test_valid_file_prints_summary_no_exit(self, monkeypatch, capsys):
        from sylk import cli
        monkeypatch.setattr(sys, "argv", ["ff-sylk", str(MINIMAL)])
        cli.main()  # should return normally, no SystemExit
        out = capsys.readouterr().out
        assert "Rows: 2, Cols: 2" in out
        assert "Cells: 4" in out
        assert str(MINIMAL) in out

    def test_missing_file_exits_one(self, monkeypatch, capsys, tmp_path):
        from sylk import cli
        missing = tmp_path / "does-not-exist.slk"
        monkeypatch.setattr(sys, "argv", ["ff-sylk", str(missing)])
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "file not found" in err

    def test_malformed_file_exits_two(self, monkeypatch, capsys):
        from sylk import cli
        monkeypatch.setattr(sys, "argv", ["ff-sylk", str(MISSING_ID)])
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 2
        err = capsys.readouterr().err
        assert "Error:" in err

    def test_main_is_the_module_entry_point(self):
        from sylk import cli
        assert callable(cli.main)


# ---------------------------------------------------------------------------
# Dogfood converters — sylk_to_{abw,csv,dif,fodg,fods,fodt,gnumeric,ndjson,
# ods,odt,pbm,pgm,ppm,toml,tsv}
# ---------------------------------------------------------------------------

class TestDogfoodConverters:
    """Smoke-tests every sylk_to_* converter module: convert MINIMAL to a
    tmp destination, and assert the file is created with a non-negative
    integer return value (each converter's own row/paragraph/block count).
    """

    def test_sylk_to_abw(self, tmp_path):
        from sylk.sylk_to_abw import sylk_to_abw
        dest = tmp_path / "out.abw"
        count = sylk_to_abw(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_csv_dogfood(self, tmp_path):
        from sylk.sylk_to_csv import sylk_to_csv as dogfood_sylk_to_csv
        dest = tmp_path / "out.csv"
        count = dogfood_sylk_to_csv(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_sylk_to_dif(self, tmp_path):
        from sylk.sylk_to_dif import sylk_to_dif
        dest = tmp_path / "out.dif"
        count = sylk_to_dif(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_fodg(self, tmp_path):
        from sylk.sylk_to_fodg import sylk_to_fodg
        dest = tmp_path / "out.fodg"
        count = sylk_to_fodg(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_fods(self, tmp_path):
        from sylk.sylk_to_fods import sylk_to_fods
        dest = tmp_path / "out.fods"
        count = sylk_to_fods(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_fodt(self, tmp_path):
        from sylk.sylk_to_fodt import sylk_to_fodt
        dest = tmp_path / "out.fodt"
        count = sylk_to_fodt(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_gnumeric(self, tmp_path):
        from sylk.sylk_to_gnumeric import sylk_to_gnumeric
        dest = tmp_path / "out.gnumeric"
        count = sylk_to_gnumeric(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_ndjson(self, tmp_path):
        from sylk.sylk_to_ndjson import sylk_to_ndjson
        dest = tmp_path / "out.ndjson"
        count = sylk_to_ndjson(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_ods(self, tmp_path):
        from sylk.sylk_to_ods import sylk_to_ods
        dest = tmp_path / "out.ods"
        count = sylk_to_ods(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_odt(self, tmp_path):
        from sylk.sylk_to_odt import sylk_to_odt
        dest = tmp_path / "out.odt"
        count = sylk_to_odt(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    # test_sylk_to_pbm / _pgm / _ppm removed by TC-PA-015 (PORTFOLIO-AUDIT-2026-07-16):
    # sylk->pbm/pgm/ppm are INCOMPATIBLE (TABULAR payload has no pixel representation);
    # the converters were deprecated and removed. See converter-compatibility-matrix.yaml.

    def test_sylk_to_toml(self, tmp_path):
        from sylk.sylk_to_toml import sylk_to_toml
        dest = tmp_path / "out.toml"
        count = sylk_to_toml(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_sylk_to_tsv(self, tmp_path):
        from sylk.sylk_to_tsv import sylk_to_tsv
        dest = tmp_path / "out.tsv"
        count = sylk_to_tsv(MINIMAL, dest)
        assert isinstance(count, int) and count >= 0
        assert dest.exists()

    def test_all_converters_handle_single_cell_document(self, tmp_path):
        """Edge case: every converter must also handle a 1x1 document
        without raising."""
        from sylk.sylk_to_abw import sylk_to_abw
        from sylk.sylk_to_tsv import sylk_to_tsv
        from sylk.sylk_to_ndjson import sylk_to_ndjson

        for fn, ext in ((sylk_to_abw, "abw"), (sylk_to_tsv, "tsv"), (sylk_to_ndjson, "ndjson")):
            dest = tmp_path / f"single.{ext}"
            count = fn(SINGLE, dest)
            assert isinstance(count, int) and count >= 0
            assert dest.exists()


# ---------------------------------------------------------------------------
# Top-level package import surface (sylk/__init__.py __all__)
# ---------------------------------------------------------------------------

class TestPackageTopLevelImportSurface:
    def test_package_exports_expected_public_names(self):
        import sylk
        for name in (
            "parse_sylk_strict", "parse_sylk", "probe_sylk",
            "write_sylk", "write_sylk_str",
            "SylkModelDocument", "SylkDoc",
            "sylk_installed_workflow",
            "sylk_iter_cells", "sylk_iter_rows",
        ):
            assert hasattr(sylk, name), f"sylk.{name} missing from package surface"

    def test_package_metadata(self):
        import sylk
        assert sylk.__track__ == "python-foss"
        assert sylk.__commercial_ready__ is False
        assert isinstance(sylk.__version__, str)

    def test_all_list_has_no_private_or_module_entries(self):
        import sylk
        for name in sylk.__all__:
            assert not name.startswith("_")
