"""Tests for get_row_count() — Gnumeric row counting.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-GNUMERIC-ROW-COUNT
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import GnumericError, create_gnumeric, get_row_count, set_cell_value


class TestGetRowCount:
    def test_empty_sheet_zero(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        assert get_row_count(m, 0) == 0

    def test_single_row(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        m = set_cell_value(m, 0, 0, 0, "A")
        m = set_cell_value(m, 0, 0, 1, "B")
        assert get_row_count(m, 0) == 1

    def test_two_rows(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        m = set_cell_value(m, 0, 0, 0, "A1")
        m = set_cell_value(m, 0, 1, 0, "A2")
        assert get_row_count(m, 0) == 2

    def test_sparse_rows_counted_correctly(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        m = set_cell_value(m, 0, 0, 0, "r0")
        m = set_cell_value(m, 0, 5, 0, "r5")
        assert get_row_count(m, 0) == 2

    def test_invalid_sheet_index_raises(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        with pytest.raises(GnumericError):
            get_row_count(m, 1)

    def test_negative_index_raises(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        with pytest.raises(GnumericError):
            get_row_count(m, -1)

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            get_row_count("not a dict", 0)

    def test_multiple_cols_same_row_counted_once(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        m = set_cell_value(m, 0, 3, 0, "x")
        m = set_cell_value(m, 0, 3, 1, "y")
        m = set_cell_value(m, 0, 3, 2, "z")
        assert get_row_count(m, 0) == 1

    def test_returns_int(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        assert isinstance(get_row_count(m, 0), int)
