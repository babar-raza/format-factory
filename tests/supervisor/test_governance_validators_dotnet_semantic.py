"""Tests for governance_validators_dotnet_semantic.py (V87, V88, V89, V90, V91, V92).

GI-FODS-NET-001: FODS .NET governance incident — semantic stub detection validators.

Tests: 9 per validator = 54 total (27 original + 27 new for V90/V91/V92).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators_dotnet_semantic import (
    validate_dotnet_constant_return_public_api,
    validate_dotnet_detached_dictionary_fields,
    validate_dotnet_missingmethods_filename,
    validate_dotnet_setter_without_xml_write,
    validate_dotnet_getter_without_xml_read,
    validate_dotnet_fods_extended_apis_loc,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decl(changed_files=None, items=None):
    return {
        "changed_files": changed_files or [],
        "planned_work_items": items or [],
    }


def _rg_decl(changed_files=None):
    """Declaration with a RELEASE_GATE item."""
    return {
        "changed_files": changed_files or [],
        "planned_work_items": [{"item_type": "RELEASE_GATE", "item_id": "RG-001"}],
    }


def _product_decl(changed_files=None):
    """Declaration with a PRODUCT_SOURCE item."""
    return {
        "changed_files": changed_files or [],
        "planned_work_items": [{"item_type": "PRODUCT_SOURCE", "item_id": "PS-001"}],
    }


def _write_cs(tmp_path: Path, filename: str, content: str) -> Path:
    """Write a .cs file in tmp_path/src/net/fods/ and return relative path."""
    target_dir = tmp_path / "src" / "net" / "fods"
    target_dir.mkdir(parents=True, exist_ok=True)
    full_path = target_dir / filename
    full_path.write_text(content, encoding="utf-8")
    return Path("src/net/fods") / filename


# ===========================================================================
# V87: validate_dotnet_constant_return_public_api
# ===========================================================================

class TestV87ConstantReturnPublicApi:

    def test_pass_when_no_dotnet_files_in_changed_files(self):
        """V87 should skip and PASS when no .NET files are in changed_files."""
        decl = _decl(changed_files=["src/python/fods/parser.py"])
        result = validate_dotnet_constant_return_public_api(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_pass_for_dom_computed_method(self, tmp_path):
        """V87 should PASS for a method with a real expression body (not a constant)."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public int GetSheetMaxRow(string name)
    {
        var sheet = RequireSheet(name);
        return sheet.Rows.Count;
    }
}
"""
        rel = _write_cs(tmp_path, "FodsTest.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_pass_for_guard_clause_body(self, tmp_path):
        """V87 should PASS for a method that throws an exception (not a constant return)."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public string GetCellValue(string sheet, int row, int col)
    {
        if (sheet is null) throw new ArgumentNullException(nameof(sheet));
        return _cells[sheet, row, col];
    }
}
"""
        rel = _write_cs(tmp_path, "FodsTest.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_for_arrow_zero_return_product_source(self, tmp_path):
        """V87 should WARN (not FAIL) for constant-zero arrow methods in PRODUCT_SOURCE."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public int GetFormulaCount() => 0;
    public int GetImageCount() => 0;
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 2

    def test_fail_and_blocks_for_constant_return_release_gate(self, tmp_path):
        """V87 should FAIL and block sprint for constant-zero methods in RELEASE_GATE."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public int GetFormulaCount() => 0;
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        decl = _rg_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(item["method"] == "GetFormulaCount" for item in result["items"])

    def test_detects_block_body_constant_return(self, tmp_path):
        """V87 should detect multi-line block-body methods returning a constant."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public int GetChartCount(string name)
    {
        return 0;
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert len(result["items"]) >= 1

    def test_detects_string_empty_constant(self, tmp_path):
        """V87 should detect => string.Empty constant returns."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public string GetSheetPrintArea(string name) => string.Empty;
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert any("GetSheetPrintArea" in item["method"] for item in result["items"])

    def test_pass_when_no_constant_returns_found(self, tmp_path):
        """V87 should PASS when all methods in the file have real implementations."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Xml.Linq.XDocument _doc;

    public string GetMimeType()
    {
        return _doc.Root?.Attribute("mimetype")?.Value ?? "";
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_whitelist_suppresses_known_intentional_constant(self, tmp_path):
        """V87 should PASS for a method listed in the whitelist."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    public int GetFormulaCount() => 0;
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        # Write a whitelist that exempts GetFormulaCount
        wl_dir = tmp_path / "registry"
        wl_dir.mkdir(parents=True, exist_ok=True)
        (wl_dir / "dotnet-semantic-stub-whitelist.yaml").write_text(
            "schema_version: '1.0'\nknown_constant_return_ok:\n  - GetFormulaCount\n",
            encoding="utf-8",
        )
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_constant_return_public_api(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"


# ===========================================================================
# V88: validate_dotnet_detached_dictionary_fields
# ===========================================================================

class TestV88DetachedDictionaryFields:

    def test_pass_when_no_dotnet_files(self):
        """V88 should skip and PASS when no .NET files are in changed_files."""
        decl = _decl(changed_files=["src/python/fods/spreadsheet_document.py"])
        result = validate_dotnet_detached_dictionary_fields(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_warn_when_dict_field_has_no_xml_reference(self, tmp_path):
        """V88 should WARN for a Dictionary field with no XML read path in any peer file."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Collections.Generic.Dictionary<string, int> _sheetFreezeRows = new();

    public int GetSheetFreezeRows(string name)
    {
        return _sheetFreezeRows.TryGetValue(name, out var v) ? v : 0;
    }
    public void SetSheetFreezeRows(string name, int rows)
    {
        _sheetFreezeRows[name] = rows;
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocument.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert any("_sheetFreezeRows" in item["field"] for item in result["items"])

    def test_pass_when_dict_field_appears_in_xml_load(self, tmp_path):
        """V88 should PASS when the dict field name co-appears with XDocument.Load( in the file."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Collections.Generic.Dictionary<string, int> _columnWidths = new();
    private System.Xml.Linq.XDocument _doc;

    public FodsDocument(string path)
    {
        _doc = System.Xml.Linq.XDocument.Load(path);
        // _columnWidths populated from parsed XML below
        foreach (var col in _doc.Descendants("col"))
        {
            _columnWidths[col.Attribute("name")?.Value ?? ""] = int.Parse(col.Attribute("width")?.Value ?? "0");
        }
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDoc.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_when_dict_field_appears_in_attribute_call(self, tmp_path):
        """V88 should PASS when the dict field co-appears with Attribute( in the same file."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Collections.Generic.Dictionary<string, string> _styles = new();
    private System.Xml.Linq.XDocument _doc;

    private void ParseStyles()
    {
        foreach (var s in _doc.Descendants("style"))
        {
            var key = s.Attribute("name")?.Value ?? "";
            _styles[key] = s.Attribute("family")?.Value ?? "";
        }
    }
}
"""
        rel = _write_cs(tmp_path, "FodsStyles.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_is_non_blocking(self, tmp_path):
        """V88 warnings must never block the sprint."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Collections.Generic.Dictionary<string, bool> _flags = new();
    public bool GetFlag(string k) => _flags.TryGetValue(k, out var v) && v;
}
"""
        rel = _write_cs(tmp_path, "FodsDoc.cs", content)
        decl = _rg_decl(changed_files=[str(rel)])  # even for RELEASE_GATE
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is False

    def test_pass_when_no_dict_fields_in_file(self, tmp_path):
        """V88 should PASS when the file has no private readonly Dictionary fields."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private System.Xml.Linq.XDocument _doc;
    public string GetMimeType() => _doc.Root?.Attribute("mimetype")?.Value ?? "";
}
"""
        rel = _write_cs(tmp_path, "FodsDoc.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_multiple_detached_dicts_all_reported(self, tmp_path):
        """V88 should report all detached dict fields, not just the first one."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Collections.Generic.Dictionary<string, int> _zoomLevel = new();
    private readonly System.Collections.Generic.Dictionary<string, string> _printArea = new();
}
"""
        rel = _write_cs(tmp_path, "FodsDoc.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        field_names = [item["field"] for item in result["items"]]
        assert "_zoomLevel" in field_names
        assert "_printArea" in field_names

    def test_pass_when_file_does_not_exist(self, tmp_path):
        """V88 should PASS (not crash) when a changed file doesn't exist on disk."""
        decl = _product_decl(changed_files=["src/net/fods/NonExistent.cs"])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_result_contains_remediation_text(self, tmp_path):
        """V88 items should contain remediation guidance."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument
{
    private readonly System.Collections.Generic.Dictionary<string, int> _freezeRows = new();
}
"""
        rel = _write_cs(tmp_path, "FodsDoc.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_detached_dictionary_fields(decl, repo_root=tmp_path)
        if result["result"] == "WARN":
            assert all("remediation" in item for item in result["items"])


# ===========================================================================
# V89: validate_dotnet_missingmethods_filename
# ===========================================================================

class TestV89MissingMethodsFilename:

    def test_pass_when_no_suspicious_files(self, tmp_path):
        """V89 should PASS when no suspicious filenames appear."""
        content = "namespace FormatFactory.Fods; public sealed partial class FodsDocument {}\n"
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_fail_on_missing_methods_addition(self, tmp_path):
        """V89 should FAIL when FodsDocumentMissingMethods.cs exists (addition)."""
        content = "namespace FormatFactory.Fods; public sealed partial class FodsDocument {}\n"
        rel = _write_cs(tmp_path, "FodsDocumentMissingMethods.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_pass_on_missing_methods_deletion(self, tmp_path):
        """V89 should PASS when a suspicious file is DELETED (does not exist on disk)."""
        # File is listed in changed_files but does NOT exist on disk (= deleted)
        rel = Path("src/net/fods/FodsDocumentMissingMethods.cs")
        decl = _product_decl(changed_files=[str(rel)])
        # tmp_path has no such file — so it's a deletion
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "PASS", "Deletion of suspicious file should be allowed"

    def test_fail_on_stubs_filename(self, tmp_path):
        """V89 should FAIL for any *Stubs*.cs file that exists."""
        content = "namespace FormatFactory.Fods; public sealed partial class FodsDocument {}\n"
        rel = _write_cs(tmp_path, "FodsStubs.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_pass_for_non_suspicious_name_with_missing_in_path(self, tmp_path):
        """V89 should PASS for files whose path has 'missing' in a non-product directory."""
        # e.g., tests/net/fods/FodsRoundtripMutationTests.cs — not matching pattern
        content = "// test file\n"
        test_dir = tmp_path / "tests" / "net" / "fods"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "FodsRoundtripMutationTests.cs").write_text(content, encoding="utf-8")
        decl = _product_decl(changed_files=["tests/net/fods/FodsRoundtripMutationTests.cs"])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_when_no_dotnet_files_at_all(self):
        """V89 should PASS when no files match src/net/ pattern."""
        decl = _decl(changed_files=["src/python/fods/parser.py", "README.md"])
        result = validate_dotnet_missingmethods_filename(decl)
        assert result["result"] == "PASS"

    def test_multiple_suspicious_files_all_reported(self, tmp_path):
        """V89 should report all suspicious files, not just the first one."""
        content = "namespace FormatFactory.Fods; public sealed partial class FodsDocument {}\n"
        rel1 = _write_cs(tmp_path, "FodsDocumentMissingMethods.cs", content)
        rel2 = _write_cs(tmp_path, "FodsDocumentStubs.cs", content)
        decl = _product_decl(changed_files=[str(rel1), str(rel2)])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert len(result["items"]) == 2

    def test_fail_items_contain_remediation(self, tmp_path):
        """V89 failure items should include remediation guidance."""
        content = "namespace FormatFactory.Fods; public sealed partial class FodsDocument {}\n"
        rel = _write_cs(tmp_path, "FodsDocumentMissingMethods.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        for item in result["items"]:
            assert "remediation" in item
            assert len(item["remediation"]) > 0

    def test_fail_blocks_sprint(self, tmp_path):
        """V89 FAIL must set blocks_sprint=True."""
        content = "namespace FormatFactory.Fods; public sealed partial class FodsDocument {}\n"
        rel = _write_cs(tmp_path, "FodsStubs.cs", content)
        decl = _rg_decl(changed_files=[str(rel)])
        result = validate_dotnet_missingmethods_filename(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# V90: validate_dotnet_setter_without_xml_write
# ---------------------------------------------------------------------------

class TestV90SetterWithoutXmlWrite:
    def test_pass_no_dotnet_files(self, tmp_path):
        """V90 should pass when no .NET files in changed_files."""
        decl = _decl(changed_files=["README.md"])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_pass_empty_changed_files(self, tmp_path):
        """V90 should pass with empty changed_files."""
        result = validate_dotnet_setter_without_xml_write(_decl(), repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_setter_with_xml_write(self, tmp_path):
        """V90 should pass when setter calls SetAttributeValue."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    public void SetColumnWidth(string sheet, int col, double w) {
        var el = _doc.Descendants("table:table-column").FirstOrDefault();
        el?.SetAttributeValue("width", w);
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_dict_only_setter(self, tmp_path):
        """V90 should warn when setter only writes to dictionary field."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    private readonly Dictionary<string, double> _widths = new();
    public void SetColumnWidth(string sheet, int col, double w) {
        _widths[sheet + col] = w;
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"

    def test_warn_does_not_block_sprint(self, tmp_path):
        """V90 WARN must not block sprint."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    private readonly Dictionary<string, double> _widths = new();
    public void SetColumnWidth(string s, int c, double w) { _widths[s + c] = w; }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is False

    def test_pass_missing_file(self, tmp_path):
        """V90 should pass gracefully when the file does not exist."""
        decl = _product_decl(changed_files=["src/net/fods/NonExistent.cs"])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_items_contain_remediation(self, tmp_path):
        """V90 warning items must include remediation text."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    private readonly Dictionary<string, double> _w = new();
    public void SetWidth(string s, double w) { _w[s] = w; }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        for item in result["items"]:
            assert "remediation" in item
            assert len(item["remediation"]) > 0

    def test_pass_style_editor_setter(self, tmp_path):
        """V90 should pass when setter uses FodsStyleEditor."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    public void SetCellFontColor(string sheet, int r, int c, string color) {
        FodsStyleEditor.SetCellProperty(_doc, sheet, r, c, "color", color);
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_validator_name_in_result(self, tmp_path):
        """V90 result must identify the validator."""
        decl = _decl()
        result = validate_dotnet_setter_without_xml_write(decl, repo_root=tmp_path)
        assert result["validator"] == "validate_dotnet_setter_without_xml_write"


# ---------------------------------------------------------------------------
# V91: validate_dotnet_getter_without_xml_read
# ---------------------------------------------------------------------------

class TestV91GetterWithoutXmlRead:
    def test_pass_no_dotnet_files(self, tmp_path):
        """V91 should pass with no .NET files."""
        decl = _decl(changed_files=["README.md"])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_empty_changed_files(self, tmp_path):
        """V91 should pass with empty changed_files."""
        result = validate_dotnet_getter_without_xml_read(_decl(), repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_getter_with_xml_read(self, tmp_path):
        """V91 should pass when getter uses Attribute(."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    public double GetColumnWidth(string sheet, int col) {
        var el = _doc.Descendants("table:table-column").FirstOrDefault();
        return double.Parse(el?.Attribute("width")?.Value ?? "0");
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_dict_backed_getter(self, tmp_path):
        """V91 should warn when getter reads from dictionary without XML."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    private readonly Dictionary<string, double> _widths = new();
    public double GetColumnWidth(string sheet, int col) {
        _widths.TryGetValue(sheet + col, out var w);
        return w;
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"

    def test_warn_does_not_block_sprint(self, tmp_path):
        """V91 WARN must not block sprint."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    private readonly Dictionary<string, double> _w = new();
    public double GetWidth(string s) { _w.TryGetValue(s, out var v); return v; }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is False

    def test_pass_missing_file(self, tmp_path):
        """V91 should pass when referenced file does not exist."""
        decl = _product_decl(changed_files=["src/net/fods/Missing.cs"])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_items_contain_remediation(self, tmp_path):
        """V91 warning items must include remediation."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    private readonly Dictionary<string, string> _d = new();
    public string GetSheetColor(string s) { _d.TryGetValue(s, out var v); return v ?? ""; }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        for item in result["items"]:
            assert "remediation" in item

    def test_pass_style_resolver_getter(self, tmp_path):
        """V91 should pass when getter uses FodsStyleResolver."""
        content = """\
namespace FormatFactory.Fods;
public sealed partial class FodsDocument {
    public FodsOdfCellStyle? GetResolvedCellStyle(string sheet, int r, int c) {
        return FodsStyleResolver.ResolveCellStyle(_doc, GetCellElement(sheet, r, c));
    }
}
"""
        rel = _write_cs(tmp_path, "FodsDocumentAccessor.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_validator_name_in_result(self, tmp_path):
        """V91 result must identify the validator."""
        decl = _decl()
        result = validate_dotnet_getter_without_xml_read(decl, repo_root=tmp_path)
        assert result["validator"] == "validate_dotnet_getter_without_xml_read"


# ---------------------------------------------------------------------------
# V92: validate_dotnet_fods_extended_apis_loc
# ---------------------------------------------------------------------------

class TestV92ExtendedApisLoc:
    def test_pass_no_extended_apis_file(self, tmp_path):
        """V92 should pass when no ExtendedApis file present."""
        decl = _decl(changed_files=["src/net/fods/FodsDocumentAccessor.cs"])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_empty_changed_files(self, tmp_path):
        """V92 should pass with empty changed_files."""
        result = validate_dotnet_fods_extended_apis_loc(_decl(), repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_within_cap(self, tmp_path):
        """V92 should pass when ExtendedApis file is within 800 LOC."""
        content = "\n".join([f"// line {i}" for i in range(799)]) + "\n"
        rel = _write_cs(tmp_path, "FodsDocumentExtendedApis.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_fail_exceeds_cap(self, tmp_path):
        """V92 should fail when ExtendedApis file exceeds 800 LOC."""
        content = "\n".join([f"// line {i}" for i in range(801)]) + "\n"
        rel = _write_cs(tmp_path, "FodsDocumentExtendedApis.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"

    def test_fail_blocks_sprint(self, tmp_path):
        """V92 FAIL must block sprint."""
        content = "\n".join([f"// line {i}" for i in range(850)]) + "\n"
        rel = _write_cs(tmp_path, "FodsDocumentExtendedApis.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is True

    def test_fail_items_contain_loc_info(self, tmp_path):
        """V92 failure items must include loc and cap."""
        content = "\n".join([f"// line {i}" for i in range(900)]) + "\n"
        rel = _write_cs(tmp_path, "FodsDocumentExtendedApis.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        item = result["items"][0]
        assert "loc" in item
        assert "cap" in item
        assert item["loc"] > item["cap"]

    def test_fail_items_contain_remediation(self, tmp_path):
        """V92 failure items must include remediation guidance."""
        content = "\n".join([f"// line {i}" for i in range(900)]) + "\n"
        rel = _write_cs(tmp_path, "FodsDocumentExtendedApis.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        for item in result["items"]:
            assert "remediation" in item
            assert len(item["remediation"]) > 0

    def test_pass_at_exactly_cap(self, tmp_path):
        """V92 should pass at exactly 800 LOC."""
        content = "\n".join([f"// line {i}" for i in range(800)]) + "\n"
        rel = _write_cs(tmp_path, "FodsDocumentExtendedApis.cs", content)
        decl = _product_decl(changed_files=[str(rel)])
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_validator_name_in_result(self, tmp_path):
        """V92 result must identify the validator."""
        decl = _decl()
        result = validate_dotnet_fods_extended_apis_loc(decl, repo_root=tmp_path)
        assert result["validator"] == "validate_dotnet_fods_extended_apis_loc"
