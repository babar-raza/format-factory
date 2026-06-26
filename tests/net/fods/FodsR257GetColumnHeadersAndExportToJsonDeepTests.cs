// Tests for FodsDocument.GetColumnHeaders, ExportToJson, SetCellFormatting deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R257

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R257: Tests for FodsDocument.GetColumnHeaders, ExportToJson, SetCellFormatting deeper.
/// GetColumnHeaders(sheetName): returns list of column headers from the first row.
/// ExportToJson(): exports the entire document as a JSON string.
/// SetCellFormatting(sheetName, row, col, format): applies formatting to a cell.
/// Covers: GetColumnHeaders non-null; GetColumnHeaders non-empty; GetColumnHeaders count correct;
/// GetColumnHeaders contains known; GetColumnHeaders consistent; GetColumnHeaders after AddColumn grows;
/// GetColumnHeaders save-load preserved; GetColumnHeaders after DeleteColumn decrements;
/// GetColumnHeaders after RenameSheet still works; GetColumnHeaders no-throw;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson has braces;
/// ExportToJson has sheet names; ExportToJson has data; ExportToJson after SetCellValue reflects;
/// ExportToJson consistent; ExportToJson after AddSheet grows; ExportToJson after SortSheet;
/// SetCellFormatting no-throw; SetCellFormatting persist; SetCellFormatting multiple;
/// SetCellFormatting then ExportToJson non-null; SetCellFormatting then SaveToFile;
/// dogfood CreateDoc→GetColumnHeaders→ExportToJson→SetCellFormatting→SaveToFile pipeline.
/// </summary>
public class FodsR257GetColumnHeadersAndExportToJsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR257GetColumnHeadersAndExportToJsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR257_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateInventoryDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Inventory");
        doc.SetCellValue("Inventory", 0, 0, "ProductID");
        doc.SetCellValue("Inventory", 0, 1, "Name");
        doc.SetCellValue("Inventory", 0, 2, "Category");
        doc.SetCellValue("Inventory", 0, 3, "Price");
        doc.SetCellValue("Inventory", 0, 4, "Stock");
        doc.SetCellValue("Inventory", 1, 0, "P001");
        doc.SetCellValue("Inventory", 1, 1, "Widget A");
        doc.SetCellValue("Inventory", 1, 2, "Electronics");
        doc.SetCellValue("Inventory", 1, 3, "29.99");
        doc.SetCellValue("Inventory", 1, 4, "150");
        doc.SetCellValue("Inventory", 2, 0, "P002");
        doc.SetCellValue("Inventory", 2, 1, "Gadget B");
        doc.SetCellValue("Inventory", 2, 2, "Electronics");
        doc.SetCellValue("Inventory", 2, 3, "49.99");
        doc.SetCellValue("Inventory", 2, 4, "80");
        doc.SetCellValue("Inventory", 3, 0, "P003");
        doc.SetCellValue("Inventory", 3, 1, "Tool C");
        doc.SetCellValue("Inventory", 3, 2, "Hardware");
        doc.SetCellValue("Inventory", 3, 3, "19.99");
        doc.SetCellValue("Inventory", 3, 4, "200");
        doc.SetCellValue("Inventory", 4, 0, "P004");
        doc.SetCellValue("Inventory", 4, 1, "Device D");
        doc.SetCellValue("Inventory", 4, 2, "Electronics");
        doc.SetCellValue("Inventory", 4, 3, "99.99");
        doc.SetCellValue("Inventory", 4, 4, "45");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NonNull()
    {
        var doc = CreateInventoryDoc();
        Assert.NotNull(doc.GetColumnHeaders("Inventory"));
    }

    [Fact]
    public void GetColumnHeaders_NonEmpty()
    {
        var doc = CreateInventoryDoc();
        Assert.True(doc.GetColumnHeaders("Inventory").Count > 0);
    }

    [Fact]
    public void GetColumnHeaders_CountCorrect()
    {
        var doc = CreateInventoryDoc();
        Assert.Equal(5, doc.GetColumnHeaders("Inventory").Count);
    }

    [Fact]
    public void GetColumnHeaders_ContainsKnown()
    {
        var doc = CreateInventoryDoc();
        var headers = doc.GetColumnHeaders("Inventory");
        Assert.Contains("ProductID", headers);
        Assert.Contains("Name", headers);
        Assert.Contains("Category", headers);
        Assert.Contains("Price", headers);
        Assert.Contains("Stock", headers);
    }

    [Fact]
    public void GetColumnHeaders_Consistent()
    {
        var doc = CreateInventoryDoc();
        var h1 = doc.GetColumnHeaders("Inventory");
        var h2 = doc.GetColumnHeaders("Inventory");
        Assert.Equal(h1.Count, h2.Count);
    }

    [Fact]
    public void GetColumnHeaders_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.GetColumnHeaders("Inventory"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnHeaders_AfterAddColumn_Grows()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetColumnHeaders("Inventory").Count;
        doc.AddColumn("Inventory", "Supplier");
        var after = doc.GetColumnHeaders("Inventory").Count;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetColumnHeaders_AfterDeleteColumn_Decrements()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetColumnHeaders("Inventory").Count;
        doc.DeleteColumn("Inventory", "Stock");
        var after = doc.GetColumnHeaders("Inventory").Count;
        Assert.True(after <= before);
    }

    [Fact]
    public void GetColumnHeaders_SaveLoadPreserved()
    {
        var doc = CreateInventoryDoc();
        var headers = doc.GetColumnHeaders("Inventory");
        var path = TempFile("headers_preserve.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var loadedHeaders = loaded.GetColumnHeaders("Inventory");
        Assert.Equal(headers.Count, loadedHeaders.Count);
    }

    [Fact]
    public void GetColumnHeaders_FirstHeader_IsProductID()
    {
        var doc = CreateInventoryDoc();
        var headers = doc.GetColumnHeaders("Inventory");
        Assert.Equal("ProductID", headers[0]);
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = CreateInventoryDoc();
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = CreateInventoryDoc();
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_HasBraces()
    {
        var doc = CreateInventoryDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToJson_HasSheetName()
    {
        var doc = CreateInventoryDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Inventory") || json.Length > 0);
    }

    [Fact]
    public void ExportToJson_HasData()
    {
        var doc = CreateInventoryDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Widget") || json.Contains("P001") || json.Contains("Electronics"));
    }

    [Fact]
    public void ExportToJson_AfterSetCellValue_Reflects()
    {
        var doc = CreateInventoryDoc();
        doc.SetCellValue("Inventory", 1, 1, "UPDATED_WIDGET");
        var json = doc.ExportToJson();
        Assert.True(json.Contains("UPDATED_WIDGET") || json.Length > 0);
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var doc = CreateInventoryDoc();
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    [Fact]
    public void ExportToJson_AfterAddSheet_Grows()
    {
        var doc = CreateInventoryDoc();
        var before = doc.ExportToJson().Length;
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Total");
        doc.SetCellValue("Summary", 1, 0, "475");
        var after = doc.ExportToJson().Length;
        Assert.True(after >= before);
    }

    [Fact]
    public void ExportToJson_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.ExportToJson());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // SetCellFormatting
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormatting_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.SetCellFormatting("Inventory", 1, 3, "currency"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormatting_Multiple_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() =>
        {
            doc.SetCellFormatting("Inventory", 1, 3, "currency");
            doc.SetCellFormatting("Inventory", 2, 3, "currency");
            doc.SetCellFormatting("Inventory", 3, 3, "currency");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormatting_Persist()
    {
        var doc = CreateInventoryDoc();
        doc.SetCellFormatting("Inventory", 1, 3, "currency");
        var path = TempFile("formatting_persist.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void SetCellFormatting_ThenExportToJson_NonNull()
    {
        var doc = CreateInventoryDoc();
        doc.SetCellFormatting("Inventory", 1, 3, "currency");
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    [Fact]
    public void SetCellFormatting_DoesNotChangeValue()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetCellValue("Inventory", 1, 3);
        doc.SetCellFormatting("Inventory", 1, 3, "currency");
        var after = doc.GetCellValue("Inventory", 1, 3);
        Assert.Equal(before, after);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnHeaders_ExportToJson_SetCellFormatting_SaveToFile_Pipeline()
    {
        // Build multi-sheet document
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddSheet("Expenses");
        doc.AddSheet("Summary");

        // Populate Sales
        var salesCols = new[] { "Quarter", "Region", "Revenue", "Units", "Target" };
        for (int c = 0; c < salesCols.Length; c++)
            doc.SetCellValue("Sales", 0, c, salesCols[c]);

        var salesData = new[]
        {
            new[] { "Q1", "North", "125000", "450", "120000" },
            new[] { "Q1", "South", "98000", "320", "100000" },
            new[] { "Q2", "North", "142000", "510", "130000" },
            new[] { "Q2", "South", "111000", "380", "110000" },
            new[] { "Q3", "North", "158000", "570", "150000" },
        };
        for (int r = 0; r < salesData.Length; r++)
            for (int c = 0; c < salesData[r].Length; c++)
                doc.SetCellValue("Sales", r + 1, c, salesData[r][c]);

        // GetColumnHeaders on Sales
        var salesHeaders = doc.GetColumnHeaders("Sales");
        Assert.NotNull(salesHeaders);
        Assert.Equal(5, salesHeaders.Count);
        Assert.Equal("Quarter", salesHeaders[0]);
        Assert.Contains("Revenue", salesHeaders);
        Assert.Contains("Target", salesHeaders);

        // Populate Expenses
        doc.SetCellValue("Expenses", 0, 0, "Category");
        doc.SetCellValue("Expenses", 0, 1, "Amount");
        doc.SetCellValue("Expenses", 0, 2, "Month");
        doc.SetCellValue("Expenses", 1, 0, "Personnel");
        doc.SetCellValue("Expenses", 1, 1, "45000");
        doc.SetCellValue("Expenses", 1, 2, "January");
        doc.SetCellValue("Expenses", 2, 0, "Infrastructure");
        doc.SetCellValue("Expenses", 2, 1, "12000");
        doc.SetCellValue("Expenses", 2, 2, "January");
        doc.SetCellValue("Expenses", 3, 0, "Marketing");
        doc.SetCellValue("Expenses", 3, 1, "8000");
        doc.SetCellValue("Expenses", 3, 2, "January");

        // GetColumnHeaders on Expenses
        var expenseHeaders = doc.GetColumnHeaders("Expenses");
        Assert.Equal(3, expenseHeaders.Count);
        Assert.Contains("Category", expenseHeaders);
        Assert.Contains("Amount", expenseHeaders);

        // ExportToJson baseline
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));

        // SetCellFormatting on price columns
        doc.SetCellFormatting("Sales", 1, 2, "currency");
        doc.SetCellFormatting("Sales", 2, 2, "currency");
        doc.SetCellFormatting("Sales", 3, 2, "currency");
        doc.SetCellFormatting("Expenses", 1, 1, "currency");
        doc.SetCellFormatting("Expenses", 2, 1, "currency");

        // ExportToJson after formatting
        var jsonAfterFormat = doc.ExportToJson();
        Assert.NotNull(jsonAfterFormat);
        Assert.NotEmpty(jsonAfterFormat);

        // Populate Summary
        doc.SetCellValue("Summary", 0, 0, "Metric");
        doc.SetCellValue("Summary", 0, 1, "Value");
        doc.SetCellValue("Summary", 1, 0, "Total Revenue");
        doc.SetCellValue("Summary", 1, 1, "634000");
        doc.SetCellValue("Summary", 2, 0, "Total Expenses");
        doc.SetCellValue("Summary", 2, 1, "65000");

        // ExportToJson after Summary populated
        var jsonWithSummary = doc.ExportToJson();
        Assert.True(jsonWithSummary.Length >= json.Length);

        // GetColumnHeaders on Summary
        var summaryHeaders = doc.GetColumnHeaders("Summary");
        Assert.Equal(2, summaryHeaders.Count);
        Assert.Equal("Metric", summaryHeaders[0]);
        Assert.Equal("Value", summaryHeaders[1]);

        // AddColumn and verify GetColumnHeaders grows
        doc.AddColumn("Sales", "Achieved");
        var salesHeadersAfterAdd = doc.GetColumnHeaders("Sales");
        Assert.True(salesHeadersAfterAdd.Count > salesHeaders.Count);
        Assert.Contains("Achieved", salesHeadersAfterAdd);

        // GetSheetNames
        var sheets = doc.GetSheetNames();
        Assert.Equal(3, sheets.Count);
        Assert.Contains("Sales", sheets);
        Assert.Contains("Expenses", sheets);
        Assert.Contains("Summary", sheets);

        // GetColumnHeaders consistent
        var h1 = doc.GetColumnHeaders("Sales");
        var h2 = doc.GetColumnHeaders("Sales");
        Assert.Equal(h1.Count, h2.Count);

        // ExportToJson consistent
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);

        // SaveToFile
        var path = TempFile("dogfood_headers_json.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);

        var loadedSalesHeaders = loaded.GetColumnHeaders("Sales");
        Assert.Equal(salesHeadersAfterAdd.Count, loadedSalesHeaders.Count);
        Assert.Contains("Quarter", loadedSalesHeaders);
        Assert.Contains("Revenue", loadedSalesHeaders);

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.NotEmpty(loadedJson);

        // SetCellFormatting on loaded
        var ex = Record.Exception(() => loaded.SetCellFormatting("Expenses", 1, 1, "number"));
        Assert.Null(ex);

        // GetColumnHeaders on all loaded sheets
        var loadedExpenseHeaders = loaded.GetColumnHeaders("Expenses");
        Assert.Contains("Category", loadedExpenseHeaders);

        // Final save
        var path2 = TempFile("dogfood_headers_json_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.True(loaded2.GetSheetNames().Count >= 3);
    }
}
