"""Tests for governance_validators_dotnet_semantic.py (V87, V88, V89).

GI-FODS-NET-001: FODS .NET governance incident — semantic stub detection validators.

Tests: 9 per validator = 27 total.
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
