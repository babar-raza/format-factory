"""FODT DOM D2 mutation roundtrip tests — TC-PCL-005-06.

Verifies that paragraph text mutations and add_paragraph persist through
write → re-parse cycle.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from fodt.models import FodtDocument

SAMPLES_DIR = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodt"
_SAMPLE = SAMPLES_DIR / "minimal-document.fodt"


def test_paragraph_text_mutation_persists_through_roundtrip(tmp_path):
    """Mutate paragraphs()[0] text; write; re-parse; assert mutation persisted."""
    doc = FodtDocument.from_file(str(_SAMPLE))
    original_count = len(doc.paragraphs())
    doc.paragraphs()[0].set_text("MUTATED_BY_TEST")
    out = tmp_path / "mutated.fodt"
    doc.to_file(out)
    reparsed = FodtDocument.from_file(str(out))
    assert reparsed.paragraphs()[0].text == "MUTATED_BY_TEST"
    assert len(reparsed.paragraphs()) == original_count


def test_add_paragraph_persists_through_roundtrip(tmp_path):
    """add_paragraph appends new block; write; re-parse; new block present."""
    doc = FodtDocument.from_file(str(_SAMPLE))
    original_count = len(doc.paragraphs())
    doc.add_paragraph("NEW_PARAGRAPH_BY_TEST")
    out = tmp_path / "extended.fodt"
    doc.to_file(out)
    reparsed = FodtDocument.from_file(str(out))
    assert len(reparsed.paragraphs()) == original_count + 1
    assert reparsed.paragraphs()[-1].text == "NEW_PARAGRAPH_BY_TEST"
