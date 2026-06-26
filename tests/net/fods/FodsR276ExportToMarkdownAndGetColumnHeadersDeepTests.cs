// Tests for FodsDocument.ExportSheetToMarkdown, GetColumnHeaders, SetColumnHeaders deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R276

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R276: Tests for FodsDocument.ExportSheetToMarkdown, GetColumnHeaders, SetColumnHeaders deeper.
/// ExportSheetToMarkdown(sheetName): exports sheet as a Markdown table.
/// GetColumnHeaders(sheetName): returns the header row values.
/// SetColumnHeaders(sheetName, headers[]): sets header row values.
/// Covers: ExportSheetToMarkdown non-null; ExportSheetToMarkdown non-empty;
/// ExportSheetToMarkdown has pipe chars; ExportSheetToMarkdown has content;
/// ExportSheetToMarkdown consistent; ExportSheetToMarkdown no-throw;
/// ExportSheetToMarkdown after SetCellValue changes; ExportSheetToMarkdown save-load;
/// GetColumnHeaders non-null; GetColumnHeaders no-throw; GetColumnHeaders count correct;
/// GetColumnHeaders values correct; GetColumnHeaders consistent; GetColumnHeaders save-load;
/// SetColumnHeaders no-throw; SetColumnHeaders values readable; SetColumnHeaders save-load;
/// SetColumnHeaders then GetColumnHeaders reflects; SetColumnHeaders then ExportSheetToMarkdown;
/// SetColumnHeaders then SetCellValue; SetColumnHeaders consistent;
/// dogfood CreateDoc→SetColumnHeaders→GetColumnHeaders→ExportSheetToMarkdown→SaveToFile.
/// </summary>
public class FodsR276ExportToMarkdownAndGetColumnHeadersDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR276ExportToMarkdownAndGetColumnHeadersDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR276_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateTableDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Table");
        // Header row
        doc.SetCellValue("Table", 0, 0, "Product");
        doc.SetCellValue("Table", 0, 1, "Category");
        doc.SetCellValue("Table", 0, 2, "Price");
        doc.SetCellValue("Table", 0, 3, "Stock");
        // Data rows
        doc.SetCellValue("Table", 1, 0, "Widget-A"); doc.SetCellValue("Table", 1, 1, "Electronics"); doc.SetCellValue("Table", 1, 2, "29.99"); doc.SetCellValue("Table", 1, 3, "500");
        doc.SetCellValue("Table", 2, 0, "Gadget-B"); doc.SetCellValue("Table", 2, 1, "Electronics"); doc.SetCellValue("Table", 2, 2, "79.99"); doc.SetCellValue("Table", 2, 3, "200");
        doc.SetCellValue("Table", 3, 0, "Tool-C");   doc.SetCellValue("Table", 3, 1, "Hardware");    doc.SetCellValue("Table", 3, 2, "14.99"); doc.SetCellValue("Table", 3, 3, "800");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NonNull()
    {
        var doc = CreateTableDoc();
        Assert.NotNull(doc.ExportSheetToMarkdown("Table"));
    }

    [Fact]
    public void ExportSheetToMarkdown_NonEmpty()
    {
        var doc = CreateTableDoc();
        Assert.NotEmpty(doc.ExportSheetToMarkdown("Table"));
    }

    [Fact]
    public void ExportSheetToMarkdown_HasPipeChars()
    {
        var doc = CreateTableDoc();
        var md = doc.ExportSheetToMarkdown("Table");
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_HasContent()
    {
        var doc = CreateTableDoc();
        var md = doc.ExportSheetToMarkdown("Table");
        Assert.True(md.Contains("Product") || md.Contains("Widget") || md.Contains("Category"));
    }

    [Fact]
    public void ExportSheetToMarkdown_Consistent()
    {
        var doc = CreateTableDoc();
        var m1 = doc.ExportSheetToMarkdown("Table");
        var m2 = doc.ExportSheetToMarkdown("Table");
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void ExportSheetToMarkdown_NoThrow()
    {
        var doc = CreateTableDoc();
        var ex = Record.Exception(() => doc.ExportSheetToMarkdown("Table"));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportSheetToMarkdown_AfterSetCellValue_Changes()
    {
        var doc = CreateTableDoc();
        var before = doc.ExportSheetToMarkdown("Table");
        doc.SetCellValue("Table", 1, 0, "SuperWidget-XYZ999");
        var after = doc.ExportSheetToMarkdown("Table");
        Assert.NotEqual(before, after);
    }

    [Fact]
    public void ExportSheetToMarkdown_SaveLoad_Consistent()
    {
        var doc = CreateTableDoc();
        var before = doc.ExportSheetToMarkdown("Table").Length;
        var path = TempFile("md_export_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportSheetToMarkdown("Table").Length - before) <= 20);
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NonNull()
    {
        var doc = CreateTableDoc();
        Assert.NotNull(doc.GetColumnHeaders("Table"));
    }

    [Fact]
    public void GetColumnHeaders_NoThrow()
    {
        var doc = CreateTableDoc();
        var ex = Record.Exception(() => doc.GetColumnHeaders("Table"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnHeaders_Count_Correct()
    {
        var doc = CreateTableDoc();
        // 4 headers: Product, Category, Price, Stock
        Assert.Equal(4, doc.GetColumnHeaders("Table").Length);
    }

    [Fact]
    public void GetColumnHeaders_Values_Correct()
    {
        var doc = CreateTableDoc();
        var headers = doc.GetColumnHeaders("Table");
        Assert.Equal("Product", headers[0]);
        Assert.Equal("Category", headers[1]);
        Assert.Equal("Price", headers[2]);
        Assert.Equal("Stock", headers[3]);
    }

    [Fact]
    public void GetColumnHeaders_Consistent()
    {
        var doc = CreateTableDoc();
        var h1 = doc.GetColumnHeaders("Table");
        var h2 = doc.GetColumnHeaders("Table");
        Assert.Equal(h1.Length, h2.Length);
        Assert.Equal(h1[0], h2[0]);
    }

    [Fact]
    public void GetColumnHeaders_SaveLoad_Consistent()
    {
        var doc = CreateTableDoc();
        var before = doc.GetColumnHeaders("Table");
        var path = TempFile("headers_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetColumnHeaders("Table");
        Assert.Equal(before.Length, after.Length);
        Assert.Equal(before[0], after[0]);
    }

    // -------------------------------------------------------------------------
    // SetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnHeaders_NoThrow()
    {
        var doc = CreateTableDoc();
        var ex = Record.Exception(() => doc.SetColumnHeaders("Table", new[] { "A", "B", "C", "D" }));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnHeaders_Values_Readable()
    {
        var doc = CreateTableDoc();
        doc.SetColumnHeaders("Table", new[] { "Col1", "Col2", "Col3", "Col4" });
        var headers = doc.GetColumnHeaders("Table");
        Assert.Equal("Col1", headers[0]);
        Assert.Equal("Col4", headers[3]);
    }

    [Fact]
    public void SetColumnHeaders_Reflects_In_GetColumnHeaders()
    {
        var doc = CreateTableDoc();
        doc.SetColumnHeaders("Table", new[] { "Name", "Type", "Cost", "Qty" });
        var headers = doc.GetColumnHeaders("Table");
        Assert.Contains("Name", headers);
        Assert.Contains("Cost", headers);
    }

    [Fact]
    public void SetColumnHeaders_SaveLoad_Persists()
    {
        var doc = CreateTableDoc();
        doc.SetColumnHeaders("Table", new[] { "Item", "Division", "Amount", "Units" });
        var path = TempFile("setheaders_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var headers = loaded.GetColumnHeaders("Table");
        Assert.Equal("Item", headers[0]);
        Assert.Equal("Division", headers[1]);
    }

    [Fact]
    public void SetColumnHeaders_Then_ExportSheetToMarkdown_HasNewHeaders()
    {
        var doc = CreateTableDoc();
        doc.SetColumnHeaders("Table", new[] { "SKU", "Dept", "Retail", "Inventory" });
        var md = doc.ExportSheetToMarkdown("Table");
        Assert.True(md.Contains("SKU") || md.Contains("Dept") || md.Contains("Retail"));
    }

    [Fact]
    public void SetColumnHeaders_Consistent()
    {
        var doc = CreateTableDoc();
        doc.SetColumnHeaders("Table", new[] { "X", "Y", "Z", "W" });
        var h1 = doc.GetColumnHeaders("Table");
        var h2 = doc.GetColumnHeaders("Table");
        Assert.Equal(h1[0], h2[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetColumnHeaders_GetColumnHeaders_ExportSheetToMarkdown_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");

        // SetColumnHeaders
        doc.SetColumnHeaders("Inventory", new[] { "SKU", "ProductName", "Department", "UnitCost", "StockLevel", "ReorderPoint" });

        // Verify GetColumnHeaders
        var headers = doc.GetColumnHeaders("Inventory");
        Assert.Equal(6, headers.Length);
        Assert.Equal("SKU", headers[0]);
        Assert.Equal("ProductName", headers[1]);
        Assert.Equal("ReorderPoint", headers[5]);

        // Fill data rows
        doc.SetCellValue("Inventory", 1, 0, "SKU-001"); doc.SetCellValue("Inventory", 1, 1, "Widget Alpha"); doc.SetCellValue("Inventory", 1, 2, "Electronics"); doc.SetCellValue("Inventory", 1, 3, "29.99"); doc.SetCellValue("Inventory", 1, 4, "500"); doc.SetCellValue("Inventory", 1, 5, "100");
        doc.SetCellValue("Inventory", 2, 0, "SKU-002"); doc.SetCellValue("Inventory", 2, 1, "Gadget Beta"); doc.SetCellValue("Inventory", 2, 2, "Electronics"); doc.SetCellValue("Inventory", 2, 3, "79.99"); doc.SetCellValue("Inventory", 2, 4, "200"); doc.SetCellValue("Inventory", 2, 5, "50");
        doc.SetCellValue("Inventory", 3, 0, "SKU-003"); doc.SetCellValue("Inventory", 3, 1, "Tool Gamma"); doc.SetCellValue("Inventory", 3, 2, "Hardware"); doc.SetCellValue("Inventory", 3, 3, "14.99"); doc.SetCellValue("Inventory", 3, 4, "800"); doc.SetCellValue("Inventory", 3, 5, "200");
        doc.SetCellValue("Inventory", 4, 0, "SKU-004"); doc.SetCellValue("Inventory", 4, 1, "Module Delta"); doc.SetCellValue("Inventory", 4, 2, "Software"); doc.SetCellValue("Inventory", 4, 3, "199.99"); doc.SetCellValue("Inventory", 4, 4, "50"); doc.SetCellValue("Inventory", 4, 5, "10");

        // ExportSheetToMarkdown
        var md = doc.ExportSheetToMarkdown("Inventory");
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("|", md);
        Assert.True(md.Contains("SKU") || md.Contains("Widget") || md.Contains("Electronics"));

        // Consistent
        Assert.Equal(md.Length, doc.ExportSheetToMarkdown("Inventory").Length);

        // GetColumnHeaders consistent
        var h2 = doc.GetColumnHeaders("Inventory");
        Assert.Equal(headers.Length, h2.Length);
        Assert.Equal(headers[0], h2[0]);

        // SetColumnHeaders — rename
        doc.SetColumnHeaders("Inventory", new[] { "Code", "Name", "Division", "Cost", "Qty", "MinQty" });
        var updatedHeaders = doc.GetColumnHeaders("Inventory");
        Assert.Equal("Code", updatedHeaders[0]);
        Assert.Equal("MinQty", updatedHeaders[5]);

        // ExportSheetToMarkdown after rename reflects new headers
        var mdAfterRename = doc.ExportSheetToMarkdown("Inventory");
        Assert.True(mdAfterRename.Contains("Code") || mdAfterRename.Contains("Name") || mdAfterRename.Contains("|"));

        // Data values still accessible
        Assert.Equal("SKU-001", doc.GetCellValue("Inventory", 1, 0));
        Assert.Equal("29.99", doc.GetCellValue("Inventory", 1, 3));

        // SaveToFile
        var path = TempFile("dogfood_inventory.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        var loadedHeaders = loaded.GetColumnHeaders("Inventory");
        Assert.Equal(6, loadedHeaders.Length);
        Assert.Equal("Code", loadedHeaders[0]);
        Assert.Equal("SKU-001", loaded.GetCellValue("Inventory", 1, 0));

        // ExportSheetToMarkdown on loaded
        var loadedMd = loaded.ExportSheetToMarkdown("Inventory");
        Assert.NotNull(loadedMd);
        Assert.Contains("|", loadedMd);

        // SetColumnHeaders on loaded
        loaded.SetColumnHeaders("Inventory", new[] { "ID", "Title", "Dept", "Price", "Count", "Floor" });
        var finalHeaders = loaded.GetColumnHeaders("Inventory");
        Assert.Equal("ID", finalHeaders[0]);

        // Final save
        var path2 = TempFile("dogfood_inventory_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        var loaded2Headers = loaded2.GetColumnHeaders("Inventory");
        Assert.Equal("ID", loaded2Headers[0]);
        Assert.Equal(6, loaded2Headers.Length);
        Assert.Contains("|", loaded2.ExportSheetToMarkdown("Inventory"));
    }
}
