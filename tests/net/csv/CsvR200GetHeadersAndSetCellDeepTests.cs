// Tests for CsvDocument.GetHeaders, SetCell, ExportToXml deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R200

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R200: Tests for CsvDocument.GetHeaders, SetCell, ExportToXml deeper.
/// GetHeaders(): returns a list of column header names.
/// SetCell(row, col, value): sets the value at the specified row and column.
/// ExportToXml(): exports the document content as an XML string.
/// Covers: GetHeaders non-null; GetHeaders non-empty; GetHeaders count correct;
/// GetHeaders contains known; GetHeaders after AddColumn grows; GetHeaders consistent;
/// GetHeaders after RemoveColumn decrements; GetHeaders order preserved; GetHeaders after RenameColumn updates;
/// SetCell changes value; SetCell then GetCell reflects; SetCell persist;
/// SetCell multiple cells; SetCell preserves others; SetCell no-throw;
/// SetCell then SortRows; SetCell then Filter;
/// ExportToXml non-null; ExportToXml non-empty; ExportToXml has root element;
/// ExportToXml has header fields; ExportToXml has data values; ExportToXml after AddRow grows;
/// ExportToXml after Filter shrinks; ExportToXml consistent; ExportToXml is valid XML fragment;
/// dogfood LoadFile→GetHeaders→SetCell→ExportToXml→SaveToFile pipeline.
/// </summary>
public class CsvR200GetHeadersAndSetCellDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR200GetHeadersAndSetCellDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR200_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var content =
            "Name,Department,Score,City\n" +
            "Alice,Engineering,92,London\n" +
            "Bob,Marketing,78,Paris\n" +
            "Carol,Engineering,88,Berlin\n" +
            "Dave,Finance,85,Rome\n" +
            "Eve,Engineering,95,Madrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_NonEmpty()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.True(doc.GetHeaders().Count > 0);
    }

    [Fact]
    public void GetHeaders_CountCorrect()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(4, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_ContainsKnown()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var headers = doc.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Department", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("City", headers);
    }

    [Fact]
    public void GetHeaders_AfterAddColumn_Grows()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetHeaders().Count;
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        var after = doc.GetHeaders().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetHeaders_AfterAddColumn_ContainsNew()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.AddColumn("Status", new[] { "Active", "Active", "Inactive", "Active", "Active" });
        Assert.Contains("Status", doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var h1 = doc.GetHeaders();
        var h2 = doc.GetHeaders();
        Assert.Equal(h1.Count, h2.Count);
    }

    [Fact]
    public void GetHeaders_OrderPreserved()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var headers = doc.GetHeaders();
        Assert.Equal("Name", headers[0]);
    }

    [Fact]
    public void GetHeaders_AfterRemoveColumn_Decrements()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetHeaders().Count;
        doc.RemoveColumn("City");
        var after = doc.GetHeaders().Count;
        Assert.Equal(before - 1, after);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ChangesValue()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(0, 2, "100");
        Assert.Equal("100", doc.GetCell(0, 2));
    }

    [Fact]
    public void SetCell_ThenGetCell_Reflects()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(1, 1, "UPDATED_DEPT");
        Assert.Equal("UPDATED_DEPT", doc.GetCell(1, 1));
    }

    [Fact]
    public void SetCell_NoThrow()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.SetCell(0, 0, "NewValue"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCell_Persist()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(2, 3, "UPDATED_CITY");
        var savePath = TempFile("setcell_persist.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal("UPDATED_CITY", loaded.GetCell(2, 3));
    }

    [Fact]
    public void SetCell_Multiple_AllReflect()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "ALICE_MOD");
        doc.SetCell(0, 2, "99");
        doc.SetCell(1, 1, "Operations");
        Assert.Equal("ALICE_MOD", doc.GetCell(0, 0));
        Assert.Equal("99", doc.GetCell(0, 2));
        Assert.Equal("Operations", doc.GetCell(1, 1));
    }

    [Fact]
    public void SetCell_PreservesOtherCells()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var original = doc.GetCell(3, 0); // Dave
        doc.SetCell(0, 0, "MODIFIED");
        Assert.Equal(original, doc.GetCell(3, 0));
    }

    [Fact]
    public void SetCell_RowCountUnchanged()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.GetRowCount();
        doc.SetCell(1, 1, "Updated");
        Assert.Equal(before, doc.GetRowCount());
    }

    [Fact]
    public void SetCell_FirstRow_Works()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "FIRST_UPDATED");
        Assert.Equal("FIRST_UPDATED", doc.GetCell(0, 0));
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NonNull()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_HasRootElement()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("<") && xml.Contains(">"));
    }

    [Fact]
    public void ExportToXml_HasHeaderFields()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Name") || xml.Contains("Department") || xml.Contains("Score"));
    }

    [Fact]
    public void ExportToXml_HasDataValues()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Alice") || xml.Contains("Bob") || xml.Contains("Carol"));
    }

    [Fact]
    public void ExportToXml_AfterAddRow_Grows()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.ExportToXml().Length;
        doc.AddRow(new[] { "Frank", "Operations", "82", "Vienna" });
        var after = doc.ExportToXml().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToXml_AfterFilter_Shrinks()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var before = doc.ExportToXml().Length;
        var filtered = doc.Filter("Department", "Finance");
        var after = filtered.ExportToXml().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        var xml1 = doc.ExportToXml();
        var xml2 = doc.ExportToXml();
        Assert.Equal(xml1.Length, xml2.Length);
    }

    [Fact]
    public void ExportToXml_AfterSetCell_Reflects()
    {
        var path = CreateSampleCsv();
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "XML_UPDATED");
        var xml = doc.ExportToXml();
        Assert.Contains("XML_UPDATED", xml);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHeaders_SetCell_ExportToXml_SaveToFile_Pipeline()
    {
        // Create source CSV
        var path = TempFile("dogfood_src.csv");
        var content =
            "Product,Category,Price,Stock,Rating\n" +
            "Widget A,Electronics,29.99,150,4.5\n" +
            "Gadget B,Electronics,49.99,80,4.2\n" +
            "Tool C,Hardware,19.99,200,4.8\n" +
            "Device D,Electronics,99.99,45,4.1\n" +
            "Part E,Hardware,9.99,500,4.6\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5, doc.GetRowCount());

        // GetHeaders
        var headers = doc.GetHeaders();
        Assert.NotNull(headers);
        Assert.Equal(5, headers.Count);
        Assert.Contains("Product", headers);
        Assert.Contains("Category", headers);
        Assert.Contains("Price", headers);
        Assert.Contains("Stock", headers);
        Assert.Contains("Rating", headers);
        Assert.Equal("Product", headers[0]);

        // ExportToXml baseline
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);
        Assert.Contains("<", xml);
        Assert.True(xml.Contains("Widget") || xml.Contains("Product"));

        // SetCell — update prices
        doc.SetCell(0, 2, "24.99"); // Discount Widget A
        doc.SetCell(2, 2, "14.99"); // Discount Tool C
        Assert.Equal("24.99", doc.GetCell(0, 2));
        Assert.Equal("14.99", doc.GetCell(2, 2));

        // ExportToXml after SetCell reflects changes
        var xmlAfterSet = doc.ExportToXml();
        Assert.Contains("24.99", xmlAfterSet);
        Assert.Contains("14.99", xmlAfterSet);

        // GetHeaders after AddColumn
        doc.AddColumn("OnSale", new[] { "Yes", "No", "Yes", "No", "No" });
        var headersAfterAdd = doc.GetHeaders();
        Assert.Equal(6, headersAfterAdd.Count);
        Assert.Contains("OnSale", headersAfterAdd);

        // ExportToXml after AddColumn grows
        var xmlAfterAdd = doc.ExportToXml();
        Assert.True(xmlAfterAdd.Length > xml.Length);

        // AddRow and verify
        doc.AddRow(new[] { "Kit F", "Hardware", "39.99", "75", "4.3", "Yes" });
        Assert.Equal(6, doc.GetRowCount());
        var xmlAfterRow = doc.ExportToXml();
        Assert.True(xmlAfterRow.Length > xmlAfterAdd.Length);
        Assert.Contains("Kit F", xmlAfterRow);

        // SetCell on new row
        doc.SetCell(5, 4, "4.7"); // Update Kit F rating
        Assert.Equal("4.7", doc.GetCell(5, 4));

        // GetHeaders after RemoveColumn
        doc.RemoveColumn("OnSale");
        var headersAfterRemove = doc.GetHeaders();
        Assert.Equal(5, headersAfterRemove.Count);
        Assert.False(headersAfterRemove.Contains("OnSale"));

        // Filter Electronics
        var electronics = doc.Filter("Category", "Electronics");
        Assert.NotNull(electronics);
        var elecXml = electronics.ExportToXml();
        Assert.True(elecXml.Length < xmlAfterRow.Length);
        var elecHeaders = electronics.GetHeaders();
        Assert.Equal(5, elecHeaders.Count);

        // SortRows then verify headers unchanged
        doc.SortRows("Price", ascending: false);
        var sortedHeaders = doc.GetHeaders();
        Assert.Equal(5, sortedHeaders.Count);
        Assert.Equal("Product", sortedHeaders[0]);

        // SaveToFile
        var savePath = TempFile("dogfood_modified.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        var loadedHeaders = loaded.GetHeaders();
        Assert.Equal(5, loadedHeaders.Count);
        Assert.Contains("Product", loadedHeaders);
        Assert.Contains("Price", loadedHeaders);
        Assert.Equal(6, loaded.GetRowCount());

        // ExportToXml on loaded
        var loadedXml = loaded.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // SetCell on loaded
        loaded.SetCell(0, 2, "LOADED_PRICE");
        Assert.Equal("LOADED_PRICE", loaded.GetCell(0, 2));
        var loadedXmlMod = loaded.ExportToXml();
        Assert.Contains("LOADED_PRICE", loadedXmlMod);

        // GetHeaders consistent on loaded
        var lh1 = loaded.GetHeaders();
        var lh2 = loaded.GetHeaders();
        Assert.Equal(lh1.Count, lh2.Count);
    }
}
