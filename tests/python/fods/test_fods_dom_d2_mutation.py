"""FODS DOM D2 mutation roundtrip test — TC-PCL-005-05.

Verifies that cell value mutations persist through write → re-parse cycle.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from fods.models import FodsDocument

SAMPLES_DIR = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fods"
_SAMPLE = SAMPLES_DIR / "minimal-spreadsheet.fods"


def test_cell_value_mutation_persists_through_roundtrip(tmp_path):
    """Mutate cell (0,0) value; write to disk; re-parse; assert mutation persisted."""
    doc = FodsDocument.from_file(_SAMPLE)
    sheet = doc.sheets()[0]
    original_value = sheet.cell_at(0, 0).value
    sheet.cell_at(0, 0).value = "MUTATED_BY_TEST"
    out = tmp_path / "mutated.fods"
    doc.to_file(out)
    reparsed = FodsDocument.from_file(out)
    assert reparsed.sheets()[0].cell_at(0, 0).value == "MUTATED_BY_TEST"
    assert reparsed.sheets()[0].cell_at(0, 0).value != original_value


def test_to_file_creates_valid_fods(tmp_path):
    """to_file() produces a file that can be re-parsed without error."""
    doc = FodsDocument.from_file(_SAMPLE)
    out = tmp_path / "roundtrip.fods"
    doc.to_file(out)
    assert out.exists()
    reparsed = FodsDocument.from_file(out)
    assert reparsed.sheet_count >= 1
