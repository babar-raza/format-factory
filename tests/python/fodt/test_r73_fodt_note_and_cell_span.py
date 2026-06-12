"""
R73 Train D — test_r73_fodt_note_and_cell_span.py

Test FODT R73 improvements:
1. Footnote/endnote detection — WARN_NOTE_ELEMENT emitted for text:note
2. Table cell span preservation — col_span/row_span captured when > 1

ODF 1.3 section 6.3 (text:note), section 9.1.4 (table cell spans)
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import textwrap

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.parser import parse_fodt
from src.python.fodt.constants import WARN_NOTE_ELEMENT


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_fodt(content: str, tmpdir: pathlib.Path) -> pathlib.Path:
    p = tmpdir / "test.fodt"
    p.write_text(content, encoding="utf-8")
    return p


FODT_WITH_FOOTNOTE = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
                 office:version="1.3">
  <office:body>
    <office:text>
      <text:p>Main text here.</text:p>
      <text:note text:id="fn1" text:note-class="footnote">
        <text:note-citation>1</text:note-citation>
        <text:note-body>
          <text:p>Footnote text content.</text:p>
        </text:note-body>
      </text:note>
      <text:p>More text after footnote.</text:p>
    </office:text>
  </office:body>
</office:document>
""")

FODT_WITH_ENDNOTE = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
                 office:version="1.3">
  <office:body>
    <office:text>
      <text:p>Text with endnote reference.</text:p>
      <text:note text:id="en1" text:note-class="endnote">
        <text:note-citation>i</text:note-citation>
        <text:note-body>
          <text:p>Endnote text content.</text:p>
        </text:note-body>
      </text:note>
    </office:text>
  </office:body>
</office:document>
""")

FODT_WITH_TABLE_SPAN = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
                 office:version="1.3">
  <office:body>
    <office:text>
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell table:number-columns-spanned="2">
            <text:p>Merged cell (2 cols)</text:p>
          </table:table-cell>
          <table:table-cell>
            <text:p>Regular cell</text:p>
          </table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell table:number-rows-spanned="2">
            <text:p>Row span cell</text:p>
          </table:table-cell>
          <table:table-cell>
            <text:p>A</text:p>
          </table:table-cell>
          <table:table-cell>
            <text:p>B</text:p>
          </table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell>
            <text:p>C</text:p>
          </table:table-cell>
          <table:table-cell>
            <text:p>D</text:p>
          </table:table-cell>
        </table:table-row>
      </table:table>
    </office:text>
  </office:body>
</office:document>
""")


# ---------------------------------------------------------------------------
# Tests: footnote/endnote detection
# ---------------------------------------------------------------------------

def test_footnote_emits_warn_note_element():
    """text:note with note-class=footnote must emit WARN_NOTE_ELEMENT."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_FOOTNOTE, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    warning_codes = [w["code"] for w in doc["warnings"]]
    assert WARN_NOTE_ELEMENT in warning_codes, (
        f"Footnote must emit {WARN_NOTE_ELEMENT}. Got codes: {warning_codes}"
    )


def test_endnote_emits_warn_note_element():
    """text:note with note-class=endnote must emit WARN_NOTE_ELEMENT."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_ENDNOTE, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    warning_codes = [w["code"] for w in doc["warnings"]]
    assert WARN_NOTE_ELEMENT in warning_codes, (
        f"Endnote must emit {WARN_NOTE_ELEMENT}. Got codes: {warning_codes}"
    )


def test_note_adds_to_unsupported_features():
    """Footnote/endnote must add 'footnote-endnote' to unsupported_features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_FOOTNOTE, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    assert "footnote-endnote" in doc.get("unsupported_features", []), (
        f"Footnote must add 'footnote-endnote' to unsupported_features. "
        f"Got: {doc.get('unsupported_features')}"
    )


def test_no_note_no_warn_note_element():
    """Document without footnotes must NOT emit WARN_NOTE_ELEMENT."""
    fodt_plain = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
                 office:version="1.3">
  <office:body><office:text>
    <text:p>Just a plain paragraph.</text:p>
  </office:text></office:body>
</office:document>
""")
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(fodt_plain, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    warning_codes = [w["code"] for w in doc["warnings"]]
    assert WARN_NOTE_ELEMENT not in warning_codes, (
        f"Plain doc must not emit {WARN_NOTE_ELEMENT}. Got: {warning_codes}"
    )


# ---------------------------------------------------------------------------
# Tests: table cell span preservation
# ---------------------------------------------------------------------------

def test_table_cell_col_span_captured():
    """Table cell with col-span=2 must have col_span=2 in neutral model."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_TABLE_SPAN, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    assert doc["tables"], "Document must have tables"
    table = doc["tables"][0]
    first_row = table["rows"][0]
    merged_cell = first_row["cells"][0]
    assert merged_cell.get("col_span") == 2, (
        f"Cell must have col_span=2. Got: {merged_cell}"
    )


def test_table_cell_row_span_captured():
    """Table cell with row-span=2 must have row_span=2 in neutral model."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_TABLE_SPAN, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    table = doc["tables"][0]
    second_row = table["rows"][1]
    row_span_cell = second_row["cells"][0]
    assert row_span_cell.get("row_span") == 2, (
        f"Cell must have row_span=2. Got: {row_span_cell}"
    )


def test_regular_cell_no_span_fields():
    """Regular table cell (span=1) must not have col_span or row_span keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_TABLE_SPAN, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    table = doc["tables"][0]
    first_row = table["rows"][0]
    regular_cell = first_row["cells"][1]  # second cell, no span
    assert "col_span" not in regular_cell, (
        f"Regular cell must not have col_span. Got: {regular_cell}"
    )
    assert "row_span" not in regular_cell, (
        f"Regular cell must not have row_span. Got: {regular_cell}"
    )


def test_table_cell_text_still_present():
    """Span-enriched cells must still have text field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fodt(FODT_WITH_TABLE_SPAN, pathlib.Path(tmpdir))
        doc = parse_fodt(p)
    assert "error" not in doc
    table = doc["tables"][0]
    for row in table["rows"]:
        for cell in row["cells"]:
            assert "text" in cell, f"Every table cell must have 'text' field. Got: {cell}"
