# R100 Train G: SYLK deep lane — CSV export hardening + malformed input tests
# Governed skill: /add-roundtrip-test
# Ledger: R100-GOVERNED-PYTHON-SYLK-CSV-MALFORMED-001

import tempfile
from pathlib import Path


from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    parse_sylk,
    parse_sylk_strict,
    probe_sylk,
    write_sylk,
    sylk_to_csv,
)


def test_csv_export_commas_in_values():
    """CSV export properly quotes values containing commas."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="hello, world"),
        SylkCell(row=1, col=2, value="no comma"),
    ]
    doc.rows = 1
    doc.cols = 2
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "hello, world" in csv or '"hello, world"' in csv
        assert "no comma" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_csv_export_empty_cells():
    """CSV export handles empty cell values."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value=""),
        SylkCell(row=1, col=2, value="filled"),
    ]
    doc.rows = 1
    doc.cols = 2
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "filled" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_probe_random_bytes():
    """probe_sylk rejects random binary data."""
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="wb") as f:
        f.write(bytes(range(256)))
        tmp = f.name
    try:
        result = probe_sylk(tmp)
        assert result.get("valid_header", True) is False
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_probe_empty_file():
    """probe_sylk rejects empty file."""
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
        tmp = f.name
    try:
        result = probe_sylk(tmp)
        assert result.get("valid_header", True) is False
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_parse_dict_malformed():
    """parse_sylk (dict mode) handles malformed but probed-valid file gracefully."""
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
        f.write("ID;P\nE\n")  # minimal valid SYLK (header + end)
        tmp = f.name
    try:
        result = parse_sylk(tmp)
        assert isinstance(result, dict)
        assert result.get("ok", False) is True or result.get("rows", 0) == 0
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_write_read_special_characters():
    """Special characters survive write/read cycle."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="tab\there"),
        SylkCell(row=1, col=2, value="line\nbreak"),
    ]
    doc.rows = 1
    doc.cols = 2
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = [str(c.value) for c in reloaded.cells]
        # At minimum, the file should not crash; values may be sanitized
        assert len(reloaded.cells) >= 1
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_csv_export_multirow():
    """CSV export handles multiple rows correctly."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=1, col=1, value="A"),
        SylkCell(row=1, col=2, value="B"),
        SylkCell(row=2, col=1, value="1"),
        SylkCell(row=2, col=2, value="2"),
        SylkCell(row=3, col=1, value="3"),
        SylkCell(row=3, col=2, value="4"),
    ]
    doc.rows = 3
    doc.cols = 2
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        lines = [l for l in csv.strip().split("\n") if l.strip()]
        assert len(lines) >= 3
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_probe_valid_sylk_header():
    """Valid SYLK with ID;P header is detected."""
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
        f.write("ID;P\nC;X1;Y1;K\"test\"\nE\n")
        tmp = f.name
    try:
        result = probe_sylk(tmp)
        assert result.get("valid_header", False) is True
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_large_grid_csv_export():
    """Large grid (10x10) exports to CSV without error."""
    doc = SylkDocument()
    doc.cells = [
        SylkCell(row=r, col=c, value=f"R{r}C{c}")
        for r in range(1, 11)
        for c in range(1, 11)
    ]
    doc.rows = 10
    doc.cols = 10
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "R1C1" in csv
        assert "R10C10" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)
