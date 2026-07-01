"""
tests/skills/test_fodt_gate4_prototype.py

Gate 4 prototype validation tests for FODT (Flat OpenDocument Text) format.
Tests the prototypes/by-format/fodt/fodt_parser.py prototype.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "fodt"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fodt"

sys.path.insert(0, str(PROTO_DIR))
from fodt_parser import parse_fodt


def test_parse_fodt_minimal_ok():
    result = parse_fodt(str(SAMPLES_DIR / "minimal-document.fodt"))
    assert result.get("error") is None, f"Unexpected error: {result.get('error')}"
    # fodt_parser returns mime_type; verify format identity via mime_type
    assert "opendocument.text-flat-xml" in result.get("mime_type", "")


def test_parse_fodt_returns_paragraphs():
    result = parse_fodt(str(SAMPLES_DIR / "minimal-document.fodt"))
    assert "paragraphs" in result
    assert isinstance(result["paragraphs"], list)


def test_parse_fodt_headings_and_paragraphs():
    result = parse_fodt(str(SAMPLES_DIR / "headings-and-paragraphs.fodt"))
    assert result.get("error") is None
    paras = result.get("paragraphs", [])
    # fodt_parser uses "element" key for heading/paragraph discrimination
    headings = [p for p in paras if p.get("element") == "heading"]
    assert len(headings) >= 1, "Expected at least one heading"


def test_parse_fodt_table():
    result = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
    assert result.get("error") is None
    assert len(result.get("tables", [])) >= 1


def test_parse_fodt_list():
    result = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
    assert result.get("error") is None


def test_parse_fodt_file_not_found():
    result = parse_fodt(str(REPO_ROOT / "nonexistent.fodt"))
    assert result.get("error") is not None


def test_parse_fodt_invalid_xml():
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w") as f:
        f.write("not xml <<<")
        tmp = f.name
    try:
        result = parse_fodt(tmp)
        assert result.get("error") is not None
    finally:
        os.unlink(tmp)


def test_all_corpus_samples_parse():
    """All FODT corpus samples parse without error."""
    samples = list(SAMPLES_DIR.glob("*.fodt"))
    assert len(samples) >= 3, f"Expected >=3 samples, got {len(samples)}"
    for sample in samples:
        result = parse_fodt(str(sample))
        assert result.get("error") is None, f"{sample.name}: {result.get('error')}"
        assert "opendocument" in result.get("mime_type", "")
