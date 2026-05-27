"""R67 Train I: ODS track advancement tests."""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ods.ods_stats import ods_data_validation_count


def _minimal_ods_doc():
    return {
        "sheets": [{"name": "Sheet1", "cells": []}],
        "metadata": {},
    }


class TestOdsDataValidationCount:
    def test_returns_int_on_empty_doc(self):
        doc = _minimal_ods_doc()
        result = ods_data_validation_count(doc)
        assert isinstance(result, int)

    def test_zero_for_empty_doc(self):
        doc = _minimal_ods_doc()
        assert ods_data_validation_count(doc) == 0

    def test_handles_none_doc(self):
        result = ods_data_validation_count({})
        assert isinstance(result, int)
