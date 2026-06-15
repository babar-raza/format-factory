"""Tests for CSV error class hierarchy — CsvError, CsvInputError, CsvSizeError, CsvParseError, CsvWriteError."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import CsvError, CsvInputError, CsvSizeError, CsvParseError
from src.python.csv.csv_writer import CsvWriteError


class TestCsvErrorHierarchy:
    def test_csv_error_is_exception(self):
        assert issubclass(CsvError, Exception)

    def test_csv_input_error_subclass(self):
        assert issubclass(CsvInputError, CsvError)

    def test_csv_size_error_subclass(self):
        assert issubclass(CsvSizeError, CsvError)

    def test_csv_parse_error_subclass(self):
        assert issubclass(CsvParseError, CsvError)

    def test_csv_write_error_is_exception(self):
        assert issubclass(CsvWriteError, Exception)


class TestCsvErrorRaise:
    def test_raise_csv_error(self):
        with pytest.raises(CsvError, match="base csv error"):
            raise CsvError("base csv error")

    def test_raise_csv_input_error(self):
        with pytest.raises(CsvInputError, match="cannot read"):
            raise CsvInputError("cannot read")

    def test_raise_csv_size_error(self):
        with pytest.raises(CsvSizeError, match="too large"):
            raise CsvSizeError("too large")

    def test_raise_csv_parse_error(self):
        with pytest.raises(CsvParseError, match="malformed"):
            raise CsvParseError("malformed")

    def test_raise_csv_write_error(self):
        with pytest.raises(CsvWriteError, match="write fail"):
            raise CsvWriteError("write fail")


class TestCsvErrorCatch:
    def test_catch_input_as_csv_error(self):
        with pytest.raises(CsvError):
            raise CsvInputError("test")

    def test_catch_size_as_csv_error(self):
        with pytest.raises(CsvError):
            raise CsvSizeError("test")

    def test_catch_parse_as_csv_error(self):
        with pytest.raises(CsvError):
            raise CsvParseError("test")

    def test_csv_error_message_preserved(self):
        err = CsvError("specific detail")
        assert str(err) == "specific detail"

    def test_csv_input_error_message(self):
        err = CsvInputError("file not found")
        assert "file not found" in str(err)

    def test_csv_size_error_message(self):
        err = CsvSizeError("exceeds 10MB")
        assert "exceeds 10MB" in str(err)


class TestCsvErrorInstantiation:
    def test_csv_error_no_args(self):
        err = CsvError()
        assert isinstance(err, Exception)

    def test_csv_input_error_no_args(self):
        err = CsvInputError()
        assert isinstance(err, CsvError)

    def test_csv_size_error_constructed(self):
        err = CsvSizeError("File exceeds MAX_FILE_SIZE")
        assert isinstance(err, CsvError)

    def test_csv_parse_error_constructed(self):
        err = CsvParseError("unexpected token")
        assert isinstance(err, CsvError)
