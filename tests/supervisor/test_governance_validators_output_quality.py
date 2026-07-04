"""
Tests for governance_validators_output_quality.py — V134, V135, V136.

6 required tests per plan TC-B1:
  1. test_v134_catches_manual_json_replace
  2. test_v134_passes_with_json_serializer
  3. test_v135_catches_unescaped_td
  4. test_v135_passes_with_htmlencode
  5. test_v136_catches_python_unescaped_td
  6. test_v136_passes_with_html_escape
"""
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/supervisor is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from governance_validators_output_quality import (
    validate_html_escaping_in_dotnet,
    validate_html_escaping_in_python,
    validate_no_manual_json_escaping_in_dotnet,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_declaration(changed_files: list[str]) -> dict:
    return {"changed_files": changed_files}


def _write_temp_cs(tmp_path: Path, content: str, rel_path: str) -> tuple[Path, str]:
    """Write a .cs file under a simulated src/net/ directory; return (repo_root, rel_path)."""
    full_path = tmp_path / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return tmp_path, rel_path


def _write_temp_py(tmp_path: Path, content: str, rel_path: str) -> tuple[Path, str]:
    """Write a .py file under a simulated src/python/ directory; return (repo_root, rel_path)."""
    full_path = tmp_path / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return tmp_path, rel_path


# ---------------------------------------------------------------------------
# V134: No manual JSON escaping in .NET
# ---------------------------------------------------------------------------

def test_v134_catches_manual_json_replace(tmp_path: Path) -> None:
    """
    A .cs file with a manual Replace chain (escaping \\ and \") but NO System.Text.Json
    import must be flagged as a violation by V134.
    """
    cs_content = '''
using System;
namespace FormatFactory.Csv;
public partial class CsvDocument
{
    // Manual JSON escaping — defective pattern (GAP-CSV-008):
    private static string _JsonEsc(string s) => s.Replace("\\\\", "\\\\\\\\").Replace("\\"", "\\\\\\"");
}
'''
    repo_root, rel_path = _write_temp_cs(tmp_path, cs_content, "src/net/csv/CsvDocument.cs")
    declaration = _make_declaration([rel_path])
    result = validate_no_manual_json_escaping_in_dotnet(declaration, repo_root)

    assert result["result"] in ("WARN", "FAIL"), (
        f"Expected WARN or FAIL for manual JSON escaping without System.Text.Json. Got: {result}"
    )
    assert len(result["items"]) > 0, "Expected at least one violation item"


def test_v134_passes_with_json_serializer(tmp_path: Path) -> None:
    """
    A .cs file that uses JsonSerializer.Serialize() (System.Text.Json) must PASS V134.
    """
    cs_content = '''
using System.Text.Json;
namespace FormatFactory.Csv;
public partial class CsvDocument
{
    public string ToJson() => JsonSerializer.Serialize(Rows);
}
'''
    repo_root, rel_path = _write_temp_cs(tmp_path, cs_content, "src/net/csv/CsvDocument.cs")
    declaration = _make_declaration([rel_path])
    result = validate_no_manual_json_escaping_in_dotnet(declaration, repo_root)

    assert result["result"] == "PASS", (
        f"Expected PASS for file using JsonSerializer. Got: {result}"
    )
    assert len(result["items"]) == 0


# ---------------------------------------------------------------------------
# V135: HTML escaping in .NET
# ---------------------------------------------------------------------------

def test_v135_catches_unescaped_td(tmp_path: Path) -> None:
    """
    A .cs file with raw string interpolation <td>{cell}</td> (no escaping call) must
    be flagged as a violation by V135.
    """
    cs_content = '''
using System.Text;
namespace FormatFactory.Csv;
public partial class CsvDocument
{
    // XSS-vulnerable HTML output — defective pattern (GAP-CSV-009):
    public string ToHtml()
    {
        var sb = new StringBuilder();
        foreach (var cell in Row)
            sb.Append($"<td>{cell}</td>");
        return sb.ToString();
    }
}
'''
    repo_root, rel_path = _write_temp_cs(tmp_path, cs_content, "src/net/csv/CsvDocument.cs")
    declaration = _make_declaration([rel_path])
    result = validate_html_escaping_in_dotnet(declaration, repo_root)

    assert result["result"] in ("WARN", "FAIL"), (
        f"Expected WARN or FAIL for raw <td>{{cell}} interpolation. Got: {result}"
    )
    assert len(result["items"]) > 0


def test_v135_passes_with_htmlencode(tmp_path: Path) -> None:
    """
    A .cs file that uses WebUtility.HtmlEncode() or _HtmlEsc() on cell values must PASS V135.
    """
    cs_content = '''
using System.Net;
using System.Text;
namespace FormatFactory.Csv;
public partial class CsvDocument
{
    public string ToHtml()
    {
        var sb = new StringBuilder();
        foreach (var cell in Row)
            sb.Append($"<td>{WebUtility.HtmlEncode(cell)}</td>");
        return sb.ToString();
    }
}
'''
    repo_root, rel_path = _write_temp_cs(tmp_path, cs_content, "src/net/csv/CsvDocument.cs")
    declaration = _make_declaration([rel_path])
    result = validate_html_escaping_in_dotnet(declaration, repo_root)

    assert result["result"] == "PASS", (
        f"Expected PASS for file using HtmlEncode. Got: {result}"
    )
    assert len(result["items"]) == 0


def test_v135_passes_with_html_esc_helper(tmp_path: Path) -> None:
    """
    A .cs file that uses the _HtmlEsc() helper (as in the fixed CsvDocumentAnalytics.cs)
    must PASS V135.
    """
    cs_content = '''
namespace FormatFactory.Csv;
public partial class CsvDocument
{
    public string ToHtml()
    {
        var sb = new System.Text.StringBuilder();
        foreach (var cell in Row)
            sb.Append($"<td>{_HtmlEsc(cell)}</td>");
        return sb.ToString();
    }
    private static string _HtmlEsc(string s) =>
        s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;");
}
'''
    repo_root, rel_path = _write_temp_cs(tmp_path, cs_content, "src/net/csv/CsvDocument.cs")
    declaration = _make_declaration([rel_path])
    result = validate_html_escaping_in_dotnet(declaration, repo_root)

    assert result["result"] == "PASS", (
        f"Expected PASS for file using _HtmlEsc. Got: {result}"
    )


# ---------------------------------------------------------------------------
# V136: HTML escaping in Python
# ---------------------------------------------------------------------------

def test_v136_catches_python_unescaped_td(tmp_path: Path) -> None:
    """
    A Python source file with f"<td>{value}</td>" (no escaping) must be flagged
    as a violation by V136.
    """
    py_content = '''
def to_html(rows):
    parts = []
    for row in rows:
        for value in row:
            parts.append(f"<td>{value}</td>")  # XSS vulnerability
    return "".join(parts)
'''
    repo_root, rel_path = _write_temp_py(tmp_path, py_content, "src/python/myformat/exporter.py")
    declaration = _make_declaration([rel_path])
    result = validate_html_escaping_in_python(declaration, repo_root)

    assert result["result"] in ("WARN", "FAIL"), (
        f"Expected WARN or FAIL for unescaped <td>{{value}} in Python. Got: {result}"
    )
    assert len(result["items"]) > 0


def test_v136_passes_with_html_escape(tmp_path: Path) -> None:
    """
    A Python source file that uses html.escape() on values before inserting into <td> must PASS V136.
    """
    py_content = '''
import html

def to_html(rows):
    parts = []
    for row in rows:
        for value in row:
            parts.append(f"<td>{html.escape(value)}</td>")
    return "".join(parts)
'''
    repo_root, rel_path = _write_temp_py(tmp_path, py_content, "src/python/myformat/exporter.py")
    declaration = _make_declaration([rel_path])
    result = validate_html_escaping_in_python(declaration, repo_root)

    assert result["result"] == "PASS", (
        f"Expected PASS for file using html.escape(). Got: {result}"
    )
    assert len(result["items"]) == 0


def test_v136_ignores_non_python_src_files(tmp_path: Path) -> None:
    """
    Files outside src/python/ are not checked by V136, even if they contain unescaped <td>.
    """
    py_content = 'output = f"<td>{value}</td>"\n'
    # Put the file outside src/python/
    rel_path = "tests/supervisor/some_test.py"
    full_path = tmp_path / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(py_content, encoding="utf-8")

    declaration = _make_declaration([rel_path])
    result = validate_html_escaping_in_python(declaration, tmp_path)

    assert result["result"] == "PASS", (
        f"Expected PASS: file is outside src/python/, should not be checked. Got: {result}"
    )
