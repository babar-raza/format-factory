"""
tests/skills/test_fods_gate4_prototype.py

Gate 4 prototype validation tests for FODS (Flat OpenDocument Spreadsheet) format.
Tests the prototypes/by-format/fods/fods_parser.py prototype.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "fods"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fods"

sys.path.insert(0, str(PROTO_DIR))
from fods_parser import parse_fods


def test_parse_fods_minimal_ok():
    result = parse_fods(SAMPLES_DIR / "minimal-spreadsheet.fods")
    assert result.get("error") is None, f"Unexpected error: {result.get('error')}"
    # fods_parser returns "format" key (not "format_id")
    assert result.get("format") == "fods"


def test_parse_fods_returns_sheets():
    result = parse_fods(SAMPLES_DIR / "minimal-spreadsheet.fods")
    assert "sheets" in result
    assert isinstance(result["sheets"], list)
    assert len(result["sheets"]) >= 1


def test_parse_fods_multi_sheet():
    result = parse_fods(SAMPLES_DIR / "multi-sheet-basic.fods")
    assert result.get("error") is None
    assert len(result.get("sheets", [])) >= 2


def test_parse_fods_typed_values():
    result = parse_fods(SAMPLES_DIR / "typed-values-basic.fods")
    assert result.get("error") is None
    assert len(result.get("sheets", [])) >= 1


def test_parse_fods_file_not_found():
    result = parse_fods(REPO_ROOT / "nonexistent.fods")
    assert result.get("error") is not None


def test_parse_fods_invalid_xml():
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w") as f:
        f.write("not xml <<<")
        tmp = f.name
    try:
        result = parse_fods(tmp)
        assert result.get("error") is not None
    finally:
        os.unlink(tmp)


def test_parse_fods_wrong_root():
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w") as f:
        f.write("<?xml version='1.0'?><root/>")
        tmp = f.name
    try:
        result = parse_fods(tmp)
        assert result.get("error") is not None
    finally:
        os.unlink(tmp)


def test_all_corpus_samples_parse():
    """All FODS corpus samples parse without error."""
    samples = list(SAMPLES_DIR.glob("*.fods"))
    assert len(samples) >= 3, f"Expected >=3 samples, got {len(samples)}"
    for sample in samples:
        result = parse_fods(sample)
        assert result.get("error") is None, f"{sample.name}: {result.get('error')}"
        assert result.get("format") == "fods"
