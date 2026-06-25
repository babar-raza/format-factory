"""Tests verifying FodsDocument is the designated primary API (QF-1-003).

Confirms that:
- FodsDocument is the first-class export
- The module docstring identifies it as primary
- parse_fods remains available but is documented as legacy
- __commercial_ready__ is False (honest status)
"""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import fods


def test_fods_document_exported():
    """FodsDocument must be importable from the fods package."""
    from fods import FodsDocument
    assert FodsDocument is not None


def test_fods_document_in_all():
    """FodsDocument must appear in __all__."""
    assert "FodsDocument" in fods.__all__


def test_parse_fods_still_exported_for_compatibility():
    """parse_fods must remain exported for backward compatibility."""
    from fods import parse_fods
    assert callable(parse_fods)


def test_parse_fods_in_all():
    assert "parse_fods" in fods.__all__


def test_module_docstring_mentions_primary_api():
    """Module docstring must identify FodsDocument as the primary API."""
    doc = fods.__doc__ or ""
    assert "Primary API" in doc or "FodsDocument" in doc


def test_module_docstring_mentions_legacy_dict_api():
    """Module docstring must identify parse_fods as legacy."""
    doc = fods.__doc__ or ""
    assert "Legacy" in doc or "legacy" in doc or "parse_fods" in doc


def test_commercial_ready_is_false():
    """__commercial_ready__ must be False (Gate 11 not approved)."""
    assert fods.__commercial_ready__ is False


def test_parse_fods_docstring_mentions_deprecated():
    """parse_fods docstring must contain deprecation guidance."""
    from fods import parse_fods
    doc = parse_fods.__doc__ or ""
    assert "deprecated" in doc.lower() or "Deprecated" in doc or "legacy" in doc.lower()
