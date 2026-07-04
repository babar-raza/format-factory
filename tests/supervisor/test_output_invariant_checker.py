"""
Tests for the Output Invariant Checker (OIC).

7 required tests per plan TC-A1:
  1. test_json_with_literal_newline_fails
  2. test_json_with_escaped_newline_passes
  3. test_html_with_script_tag_fails
  4. test_html_with_escaped_script_passes
  5. test_xml_malformed_fails
  6. test_xml_valid_passes
  7. test_csv_roundtrip_correct_count
"""
import pytest
from tools.assurance.output_invariant_checker import OutputInvariantChecker


@pytest.fixture
def oic() -> OutputInvariantChecker:
    return OutputInvariantChecker()


# ---------------------------------------------------------------------------
# JSON invariant tests
# ---------------------------------------------------------------------------

def test_json_with_literal_newline_fails(oic: OutputInvariantChecker) -> None:
    """
    A JSON string containing a LITERAL newline (not \\n) is invalid per RFC 8259.
    This is exactly the bug produced by the defective _JsonEsc that only escapes
    backslash and double-quote but not control characters.
    """
    # Literal newline inside a JSON string value — this is invalid JSON
    bad_json = '{"key": "line1\nline2"}'
    result = oic.check_json(bad_json, "test_context")
    assert not result.passed, (
        "Expected FAIL: JSON with a literal newline in a string value is invalid"
    )
    assert result.error is not None
    assert "JSONDecodeError" in result.error


def test_json_with_escaped_newline_passes(oic: OutputInvariantChecker) -> None:
    """
    A JSON string where the newline is properly escaped as \\n (two chars: backslash + n)
    is valid JSON and must pass the OIC check.
    """
    # Properly escaped newline — valid JSON
    good_json = '{"key": "line1\\nline2"}'
    result = oic.check_json(good_json, "test_context")
    assert result.passed, (
        f"Expected PASS: properly escaped \\n is valid JSON. Error: {result.error}"
    )


def test_json_with_control_chars_fails(oic: OutputInvariantChecker) -> None:
    """
    JSON strings with literal tab and carriage return characters must also fail.
    This is the full scope of what the fixed _JsonEsc must handle.
    """
    bad_json_tab = '{"key": "col1\tcol2"}'
    result = oic.check_json(bad_json_tab, "test_context")
    assert not result.passed, "Expected FAIL: literal tab in JSON string is invalid"


# ---------------------------------------------------------------------------
# HTML cell safety tests
# ---------------------------------------------------------------------------

def test_html_with_script_tag_fails(oic: OutputInvariantChecker) -> None:
    """
    An HTML table cell containing a raw <script> tag must fail the OIC check.
    This is the exact XSS vector produced by ToHtml() with raw {cell} interpolation.
    """
    bad_html = "<table><tr><td><script>alert(1)</script></td></tr></table>"
    result = oic.check_html_cell_safety(bad_html, "test_context")
    assert not result.passed, (
        "Expected FAIL: <script> tag inside <td> contains raw < > characters"
    )
    assert result.error is not None


def test_html_with_escaped_script_passes(oic: OutputInvariantChecker) -> None:
    """
    An HTML table cell where < > are replaced with &lt; &gt; must pass.
    This is what correctly escaped output from _HtmlEsc produces.
    """
    good_html = "<table><tr><td>&lt;script&gt;alert(1)&lt;/script&gt;</td></tr></table>"
    result = oic.check_html_cell_safety(good_html, "test_context")
    assert result.passed, (
        f"Expected PASS: properly entity-escaped script tag. Error: {result.error}"
    )


def test_html_with_ampersand_in_td_fails(oic: OutputInvariantChecker) -> None:
    """
    A raw & in a <td> (not part of a valid entity) must fail.
    """
    bad_html = "<table><tr><td>AT&T</td></tr></table>"
    result = oic.check_html_cell_safety(bad_html, "test_context")
    assert not result.passed, "Expected FAIL: raw & in <td> is not safe HTML"


def test_html_with_entity_encoded_ampersand_passes(oic: OutputInvariantChecker) -> None:
    """
    &amp; in a <td> is a valid entity and must pass.
    """
    good_html = "<table><tr><td>AT&amp;T</td></tr></table>"
    result = oic.check_html_cell_safety(good_html, "test_context")
    assert result.passed, (
        f"Expected PASS: &amp; is a valid HTML entity. Error: {result.error}"
    )


def test_html_with_th_script_tag_fails(oic: OutputInvariantChecker) -> None:
    """
    Header cells (<th>) are also checked — a raw < inside <th> must fail.
    """
    bad_html = "<table><tr><th><b>Name</th><th>Value</th></tr></table>"
    result = oic.check_html_cell_safety(bad_html, "test_context")
    assert not result.passed, "Expected FAIL: raw < inside <th> is not safe"


# ---------------------------------------------------------------------------
# XML invariant tests
# ---------------------------------------------------------------------------

def test_xml_malformed_fails(oic: OutputInvariantChecker) -> None:
    """
    XML with a missing closing tag must fail the OIC XML check.
    """
    bad_xml = "<root><child>value</root>"  # <child> never closed
    result = oic.check_xml(bad_xml, "test_context")
    assert not result.passed, "Expected FAIL: XML with unclosed <child> tag is malformed"
    assert result.error is not None
    assert "XML ParseError" in result.error


def test_xml_valid_passes(oic: OutputInvariantChecker) -> None:
    """
    Well-formed XML with proper closing tags must pass.
    """
    good_xml = "<root><row><cell>Alice</cell><cell>30</cell></row></root>"
    result = oic.check_xml(good_xml, "test_context")
    assert result.passed, (
        f"Expected PASS: well-formed XML. Error: {result.error}"
    )


# ---------------------------------------------------------------------------
# CSV roundtrip test
# ---------------------------------------------------------------------------

def test_csv_roundtrip_correct_count(oic: OutputInvariantChecker) -> None:
    """
    A 3-row CSV (plus header) must parse back to exactly 3 data rows.
    """
    csv_output = "Name,Age,City\nAlice,30,NYC\nBob,25,LA\nCarol,35,Chicago\n"
    result = oic.check_csv_roundtrip(csv_output, expected_row_count=3, context="test_context")
    assert result.passed, (
        f"Expected PASS: 3-row CSV should roundtrip to 3 rows. Error: {result.error}"
    )


def test_csv_roundtrip_wrong_count_fails(oic: OutputInvariantChecker) -> None:
    """
    If the row count doesn't match the expected value, it must fail.
    """
    csv_output = "Name,Age\nAlice,30\nBob,25\n"  # 2 data rows
    result = oic.check_csv_roundtrip(csv_output, expected_row_count=5, context="test_context")
    assert not result.passed, "Expected FAIL: got 2 rows but expected 5"
