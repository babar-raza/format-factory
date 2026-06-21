"""Tests for fodt_has_multiple_block_types and fodt_punctuation_density (Sprint 76)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_has_multiple_block_types, fodt_punctuation_density

FODT = _REPO / "samples" / "by-format" / "fodt"


# --- fodt_has_multiple_block_types ---

def test_has_multiple_block_types_minimal_false():
    assert fodt_has_multiple_block_types(FODT / "minimal-document.fodt") is False


def test_has_multiple_block_types_headings_true():
    assert fodt_has_multiple_block_types(FODT / "headings-and-paragraphs.fodt") is True


def test_has_multiple_block_types_list_false():
    assert fodt_has_multiple_block_types(FODT / "list-basic.fodt") is False


def test_has_multiple_block_types_returns_bool():
    assert isinstance(fodt_has_multiple_block_types(FODT / "minimal-document.fodt"), bool)


def test_has_multiple_block_types_only_headings_differ():
    vals = [
        fodt_has_multiple_block_types(FODT / "minimal-document.fodt"),
        fodt_has_multiple_block_types(FODT / "headings-and-paragraphs.fodt"),
        fodt_has_multiple_block_types(FODT / "list-basic.fodt"),
    ]
    assert vals.count(True) == 1


# --- fodt_punctuation_density ---

def test_punctuation_density_minimal_one():
    assert abs(fodt_punctuation_density(FODT / "minimal-document.fodt") - 1.0) < 0.01


def test_punctuation_density_headings_low():
    assert abs(fodt_punctuation_density(FODT / "headings-and-paragraphs.fodt") - 0.273) < 0.01


def test_punctuation_density_list_half():
    assert abs(fodt_punctuation_density(FODT / "list-basic.fodt") - 0.5) < 0.01


def test_punctuation_density_returns_float():
    assert isinstance(fodt_punctuation_density(FODT / "minimal-document.fodt"), float)


def test_punctuation_density_nonnegative():
    for name in ["minimal-document.fodt", "headings-and-paragraphs.fodt", "list-basic.fodt"]:
        assert fodt_punctuation_density(FODT / name) >= 0.0
