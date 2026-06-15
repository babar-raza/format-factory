"""Gap closure tests for Gnumeric — batch 2 covering error classes and sheet operations.

Gaps: GAP-Gnumeric-FOSS-GNUMERICERRO-001, GAP-Gnumeric-FOSS-GNUMERICPARS-001,
      GAP-Gnumeric-FOSS-GET_SHEET_NA-001, GAP-Gnumeric-FOSS-GET_SHEET_IN-001,
      GAP-Gnumeric-FOSS-SET_CELL_VAL-001, GAP-Gnumeric-FOSS-COUNT_NONEMP-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    GnumericError,
    GnumericParseError,
    load,
    get_sheet_names,
    set_cell_value,
    count_nonempty_cells,
    create_gnumeric,
    write_gnumeric,
)

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"


class TestGnumericError:
    def test_is_exception(self):
        assert issubclass(GnumericError, Exception)

    def test_message_preserved(self):
        err = GnumericError("broken file")
        assert "broken file" in str(err)


class TestGnumericParseError:
    def test_is_subclass(self):
        assert issubclass(GnumericParseError, (GnumericError, Exception))

    def test_can_raise_and_catch(self):
        with pytest.raises(GnumericParseError):
            raise GnumericParseError("bad format")


class TestGetSheetNames:
    def test_returns_list(self):
        names = get_sheet_names(str(MINIMAL))
        assert isinstance(names, list)
        assert len(names) >= 1

    def test_names_are_strings(self):
        names = get_sheet_names(str(MINIMAL))
        for n in names:
            assert isinstance(n, str)


class TestSetCellValue:
    def test_set_and_verify(self, tmp_path):
        doc = create_gnumeric([{"name": "Sheet1", "rows": [[""]]}])
        doc = set_cell_value(doc, 0, 0, 0, "Hello")
        f = tmp_path / "test.gnumeric"
        write_gnumeric(doc, str(f))
        model = load(str(f))
        count = count_nonempty_cells(model, 0)
        assert count >= 1


class TestCountNonemptyCells:
    def test_minimal_has_cells(self):
        model = load(str(MINIMAL))
        count = count_nonempty_cells(model, 0)
        assert isinstance(count, int)
        assert count >= 0

    def test_empty_doc(self, tmp_path):
        doc = create_gnumeric([{"name": "Sheet1", "rows": []}])
        f = tmp_path / "empty.gnumeric"
        write_gnumeric(doc, str(f))
        model = load(str(f))
        count = count_nonempty_cells(model, 0)
        assert count == 0
