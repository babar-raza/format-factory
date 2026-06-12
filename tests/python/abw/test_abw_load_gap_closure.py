"""
test_abw_load_gap_closure.py -- ABW load/create/write roundtrip tests.

Sprint: REWORK-MEGATRAIN-CONTINUATION-001
Gap: GAP-ABW-FOSS-LOAD-001
Added: 2026-06-10

Verifies: load() returns correct model, create_abw() builds valid XML,
write_abw() persists to disk, full roundtrip preserves content.
"""
from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

from abw.abw_codec import load, create_abw, write_abw


def test_load_from_bytes_minimal():
    """Load ABW from minimal XML bytes."""
    xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<abiword><section><p>Hello world</p></section></abiword>'
    )
    model = load(xml)
    assert model["is_abw"] is True
    assert model["paragraph_count"] >= 1
    assert any("Hello world" in p for p in model["paragraphs"])


def test_load_returns_expected_keys():
    """load() model has required keys."""
    xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<abiword><section><p>Test</p></section></abiword>'
    )
    model = load(xml)
    for key in ("is_abw", "section_count", "paragraph_count", "paragraphs"):
        assert key in model, f"Missing key: {key}"


def test_create_abw_single_paragraph():
    """create_abw() builds a model from paragraph list."""
    model = create_abw(["First paragraph"])
    assert model["is_abw"] is True
    assert model["paragraph_count"] == 1
    assert model["paragraphs"][0] == "First paragraph"


def test_create_abw_multiple_paragraphs():
    """create_abw() with multiple paragraphs."""
    paras = ["Alpha", "Beta", "Gamma"]
    model = create_abw(paras)
    assert model["paragraph_count"] == 3
    assert model["paragraphs"] == paras


def test_write_abw_creates_file():
    """write_abw() writes a file to disk."""
    model = create_abw(["Disk test"])
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "output.abw"
        write_abw(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0


def test_roundtrip_create_write_load():
    """create -> write -> load roundtrip preserves paragraphs."""
    original_paras = ["Line one", "Line two", "Line three"]
    model = create_abw(original_paras)
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "roundtrip.abw"
        write_abw(model, dest)
        reloaded = load(dest)
        assert reloaded["is_abw"] is True
        assert reloaded["paragraph_count"] == 3
        assert reloaded["paragraphs"] == original_paras


def test_load_empty_document():
    """Load ABW with no paragraphs."""
    xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<abiword><section></section></abiword>'
    )
    model = load(xml)
    assert model["is_abw"] is True
    assert model["paragraph_count"] == 0


def test_write_read_preserves_unicode():
    """Roundtrip preserves Unicode content."""
    model = create_abw(["Cafe\u0301 au lait", "\u00fcber cool"])
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "unicode.abw"
        write_abw(model, dest)
        reloaded = load(dest)
        assert reloaded["paragraphs"][1] == "\u00fcber cool"
