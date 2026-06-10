"""Tests for gnumeric.gnumeric_codec.get_sheet_index() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, get_sheet_index


def _multi_sheet():
    return create_gnumeric([
        {"name": "Alpha", "cells": []},
        {"name": "Beta", "cells": []},
        {"name": "Gamma", "cells": []},
    ])


def test_first_sheet():
    model = _multi_sheet()
    assert get_sheet_index(model, "Alpha") == 0


def test_second_sheet():
    model = _multi_sheet()
    assert get_sheet_index(model, "Beta") == 1


def test_third_sheet():
    model = _multi_sheet()
    assert get_sheet_index(model, "Gamma") == 2


def test_not_found_raises():
    model = _multi_sheet()
    try:
        get_sheet_index(model, "Missing")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_returns_int():
    model = _multi_sheet()
    assert isinstance(get_sheet_index(model, "Alpha"), int)


def test_single_sheet():
    model = create_gnumeric([{"name": "Only", "cells": []}])
    assert get_sheet_index(model, "Only") == 0
