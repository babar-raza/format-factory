"""Property-based tests for FODS parser and writer using Hypothesis.

TC-CERT-R2-001 certification hardening.
"""
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from fods import parse_fods, write_fods


# Strategy: generate valid minimal FODS XML content
def _make_fods_xml(sheet_name: str, rows: list[list[str]]) -> str:
    """Build a minimal valid FODS XML string."""
    # Sanitize for XML: escape &, <, > in cell values
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    safe_name = esc(sheet_name.replace('"', "'") or "Sheet1")
    row_xml = []
    for row in rows:
        cells = "".join(
            f'<table:table-cell><text:p>{esc(c)}</text:p></table:table-cell>'
            for c in row
        )
        row_xml.append(f"<table:table-row>{cells}</table:table-row>")
    rows_block = "\n".join(row_xml)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="{safe_name}">
        {rows_block}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>"""


# Strategies
safe_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "Z"),
        blacklist_characters="\x00\ufffe\uffff",
    ),
    min_size=0,
    max_size=50,
)
sheet_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), blacklist_characters='"'),
    min_size=1,
    max_size=20,
)
rows_st = st.lists(st.lists(safe_text, min_size=1, max_size=5), min_size=1, max_size=10)


@given(name=sheet_name_st, rows=rows_st)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_parse_never_crashes_on_valid_fods(name, rows):
    """parse_fods must not crash on any well-formed FODS XML."""
    xml = _make_fods_xml(name, rows)
    tmp = Path(tempfile.mktemp(suffix=".fods"))
    try:
        tmp.write_text(xml, encoding="utf-8")
        result = parse_fods(tmp)
        assert isinstance(result, dict)
    finally:
        tmp.unlink(missing_ok=True)


@given(name=sheet_name_st, rows=rows_st)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_roundtrip_preserves_sheet_count(name, rows):
    """write_fods -> re-parse preserves the number of sheets."""
    xml = _make_fods_xml(name, rows)
    src = Path(tempfile.mktemp(suffix=".fods"))
    dst = Path(tempfile.mktemp(suffix=".fods"))
    try:
        src.write_text(xml, encoding="utf-8")
        model = parse_fods(src)
        write_fods(model, dst)
        reloaded = parse_fods(dst)
        assert len(reloaded.get("sheets", [])) == len(model.get("sheets", []))
    finally:
        src.unlink(missing_ok=True)
        dst.unlink(missing_ok=True)
