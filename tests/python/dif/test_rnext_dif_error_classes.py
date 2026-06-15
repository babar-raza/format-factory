"""Tests for DIF error class hierarchy — DifError, DifInvalidFormatError, DifSizeError."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import DifError, DifInvalidFormatError, DifSizeError


class TestDifErrorHierarchy:
    def test_dif_error_is_exception(self):
        assert issubclass(DifError, Exception)

    def test_dif_invalid_format_error_subclass(self):
        assert issubclass(DifInvalidFormatError, DifError)

    def test_dif_size_error_subclass(self):
        assert issubclass(DifSizeError, DifError)


class TestDifErrorRaise:
    def test_raise_dif_error(self):
        with pytest.raises(DifError, match="dif base"):
            raise DifError("dif base")

    def test_raise_dif_invalid_format_error(self):
        with pytest.raises(DifInvalidFormatError, match="bad format"):
            raise DifInvalidFormatError("bad format")

    def test_raise_dif_size_error(self):
        with pytest.raises(DifSizeError, match="too big"):
            raise DifSizeError("too big")


class TestDifErrorCatch:
    def test_catch_invalid_format_as_dif_error(self):
        with pytest.raises(DifError):
            raise DifInvalidFormatError("test")

    def test_catch_size_as_dif_error(self):
        with pytest.raises(DifError):
            raise DifSizeError("test")

    def test_dif_error_message_preserved(self):
        err = DifError("detail here")
        assert str(err) == "detail here"

    def test_dif_invalid_format_message(self):
        err = DifInvalidFormatError("not a DIF file")
        assert "not a DIF file" in str(err)

    def test_dif_size_error_message(self):
        err = DifSizeError("exceeds limit")
        assert "exceeds limit" in str(err)


class TestDifErrorFromModule:
    def test_importable_from_init(self):
        from src.python.dif import DifError as E1, DifInvalidFormatError as E2
        assert issubclass(E2, E1)

    def test_dif_size_error_importable_from_init(self):
        from src.python.dif import DifSizeError as E
        assert issubclass(E, DifError)
