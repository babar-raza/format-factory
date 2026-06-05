# R98 Train Q: SYLK installed workflow + roundtrip tests
# Governed skill: /add-roundtrip-test
# Ledger: R98-GOVERNED-PYTHON-SYLK-ROUNDTRIP-001
# Priority: 4 (installed workflow proof)

import tempfile
from pathlib import Path

import pytest

from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    parse_sylk_strict,
    write_sylk,
    sylk_to_csv,
)

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "sylk"


def _find_sample():
    """Find a valid SYLK sample file."""
    valid_dir = SAMPLES_DIR / "valid"
    if valid_dir.exists():
        for f in sorted(valid_dir.iterdir()):
            if f.suffix.lower() == ".sylk":
                return f
    if SAMPLES_DIR.exists():
        for f in sorted(SAMPLES_DIR.iterdir()):
            if f.suffix.lower() == ".sylk":
                return f
    return None


def _make_doc():
    """Create a minimal SylkDocument for testing."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="Name"),
        SylkCell(row=1, col=2, value="Score"),
        SylkCell(row=2, col=1, value="Alice"),
        SylkCell(row=2, col=2, value="95"),
        SylkCell(row=3, col=1, value="Bob"),
        SylkCell(row=3, col=2, value="87"),
    ]
    doc.rows = 3
    doc.cols = 2
    return doc


def test_write_then_parse_roundtrip():
    """Write a SYLK doc and parse it back; cells match."""
    doc = _make_doc()
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        assert reloaded.rows >= 3
        assert reloaded.cols >= 2
        # Find the cells we wrote
        values = {(c.row, c.col): c.value for c in reloaded.cells}
        assert values.get((1, 1)) == "Name"
        assert values.get((2, 1)) == "Alice"
        # Numeric values may be parsed as int
        assert str(values.get((3, 2))) == "87"
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_write_then_csv_export():
    """Write SYLK, then export to CSV; exported text contains cell values."""
    doc = _make_doc()
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "Alice" in csv
        assert "87" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_edit_cell_then_write_roundtrip():
    """Modify a cell value, write, parse back — edit persists."""
    doc = _make_doc()
    # Edit Alice's score
    for c in doc.cells:
        if c.row == 2 and c.col == 2:
            c.value = "99"
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = {(c.row, c.col): c.value for c in reloaded.cells}
        # Numeric values may be parsed as int by the parser
        assert str(values.get((2, 2))) == "99"
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_sample_parse_if_available():
    """Parse a real SYLK sample file if available."""
    sample = _find_sample()
    if sample is None:
        pytest.skip("No SYLK sample files found")
    doc = parse_sylk_strict(str(sample))
    assert len(doc.cells) > 0


def test_sample_csv_export_if_available():
    """Export a real sample to CSV if available."""
    sample = _find_sample()
    if sample is None:
        pytest.skip("No SYLK sample files found")
    csv = sylk_to_csv(str(sample))
    assert len(csv) > 0


def test_empty_document_roundtrip():
    """Empty SYLK document writes and parses without error."""
    doc = SylkDocument()
    doc.cells = []
    doc.rows = 0
    doc.cols = 0
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        assert len(reloaded.cells) == 0
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_write_sylk_file_starts_with_id():
    """Written SYLK file starts with 'ID;' marker."""
    doc = _make_doc()
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        content = Path(tmp).read_text(encoding="utf-8")
        assert content.startswith("ID;")
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_write_sylk_file_ends_with_e():
    """Written SYLK file ends with 'E' record."""
    doc = _make_doc()
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        content = Path(tmp).read_text(encoding="utf-8").strip()
        assert content.endswith("E")
    finally:
        Path(tmp).unlink(missing_ok=True)
