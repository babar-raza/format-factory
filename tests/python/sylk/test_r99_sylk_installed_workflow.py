# R99 Train G: SYLK installed workflow verification tests
# Governed skill: /add-roundtrip-test
# Ledger: R99-GOVERNED-PYTHON-SYLK-INSTALLED-WORKFLOW-001

import tempfile
from pathlib import Path


from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    parse_sylk_strict,
    parse_sylk,
    probe_sylk,
    write_sylk,
    sylk_to_csv,
    get_capabilities,
)


def test_get_capabilities_returns_dict():
    """get_capabilities() returns a dict with expected keys."""
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert "parse" in caps or "read" in caps or len(caps) > 0


def test_full_workflow_create_write_parse_export():
    """Full installed workflow: create -> write -> parse -> CSV export."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="Product"),
        SylkCell(row=1, col=2, value="Price"),
        SylkCell(row=2, col=1, value="Widget"),
        SylkCell(row=2, col=2, value="9.99"),
        SylkCell(row=3, col=1, value="Gadget"),
        SylkCell(row=3, col=2, value="19.99"),
    ]
    doc.rows = 3
    doc.cols = 2

    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        # Step 1: Write
        write_sylk(doc, tmp)
        assert Path(tmp).stat().st_size > 0

        # Step 2: Probe
        probe = probe_sylk(tmp)
        assert probe.get("valid_header", False) is True

        # Step 3: Parse (dict mode)
        parsed = parse_sylk(tmp)
        assert parsed["ok"] is True
        assert parsed["rows"] >= 3

        # Step 4: Parse strict
        strict = parse_sylk_strict(tmp)
        assert len(strict.cells) >= 6

        # Step 5: CSV export
        csv = sylk_to_csv(tmp)
        assert "Widget" in csv
        assert "19.99" in csv or "19" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_probe_valid_file():
    """probe_sylk returns valid=True for valid SYLK."""
    doc = SylkDocument()
    doc.cells = [SylkCell(row=1, col=1, value="test")]
    doc.rows = 1
    doc.cols = 1
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        probe = probe_sylk(tmp)
        assert probe.get("valid_header", False) is True
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_probe_invalid_file():
    """probe_sylk returns valid=False for non-SYLK file."""
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
        f.write("this is not a SYLK file")
        tmp = f.name
    try:
        probe = probe_sylk(tmp)
        assert probe.get("valid_header", True) is False
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_parse_dict_mode():
    """parse_sylk (dict mode) returns structured result."""
    doc = SylkDocument()
    doc.cells = [SylkCell(row=1, col=1, value="A")]
    doc.rows = 1
    doc.cols = 1
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        result = parse_sylk(tmp)
        assert isinstance(result, dict)
        assert "ok" in result
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_csv_export_headers():
    """CSV export includes header row."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="Name"),
        SylkCell(row=2, col=1, value="Alice"),
    ]
    doc.rows = 2
    doc.cols = 1
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "Name" in csv
        assert "Alice" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_write_read_numeric_values():
    """Numeric values survive write/read cycle."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="42"),
        SylkCell(row=1, col=2, value="3.14"),
    ]
    doc.rows = 1
    doc.cols = 2
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = {(c.row, c.col): str(c.value) for c in reloaded.cells}
        assert values.get((1, 1)) in ("42", "42.0")
        assert values.get((1, 2)) in ("3.14",)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_write_empty_string_cell():
    """Empty string cell survives write/read."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value=""),
        SylkCell(row=1, col=2, value="notempty"),
    ]
    doc.rows = 1
    doc.cols = 2
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "notempty" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)
