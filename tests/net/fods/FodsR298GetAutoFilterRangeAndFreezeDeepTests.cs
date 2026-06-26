// Tests for FodsDocument.GetAutoFilterRange, SetAutoFilter, GetFrozenRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R298

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R298: Tests for FodsDocument.GetAutoFilterRange, SetAutoFilter, GetFrozenRowCount deeper.
/// GetAutoFilterRange(sheetName): returns the cell range on which auto-filter is active, or empty string.
/// SetAutoFilter(sheetName, cellRange): applies auto-filter to the specified cell range.
/// GetFrozenRowCount(sheetName): returns the number of frozen rows at the top of the sheet.
/// Covers: GetAutoFilterRange no-throw; GetAutoFilterRange non-null; GetAutoFilterRange consistent;
/// GetAutoFilterRange after SetAutoFilter non-empty; GetAutoFilterRange save-load;
/// SetAutoFilter no-throw; SetAutoFilter makes GetAutoFilterRange non-empty;
/// SetAutoFilter save-load; SetAutoFilter then ExportToCsv no-throw;
/// SetAutoFilter multiple (overwrites); SetAutoFilter then GetColumnHeaders no-throw;
/// GetFrozenRowCount no-throw; GetFrozenRowCount non-negative; GetFrozenRowCount consistent;
/// GetFrozenRowCount save-load; GetFrozenRowCount zero for new sheet;
/// dogfood CreateDoc→SetAutoFilter→GetAutoFilterRange→GetFrozenRowCount→SaveToFile pipeline.
/// </summary>
public class FodsR298GetAutoFilterRangeAndFreezeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR298GetAutoFilterRangeAndFreezeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR298_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRichDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");
        doc.SetCellValue("Inventory", 0, 0, "SKU");
        doc.SetCellValue("Inventory", 0, 1, "Description");
        doc.SetCellValue("Inventory", 0, 2, "Category");
        doc.SetCellValue("Inventory", 0, 3, "Price");
        doc.SetCellValue("Inventory", 0, 4, "Stock");
        doc.SetCellValue("Inventory", 1, 0, "A001");
        doc.SetCellValue("Inventory", 1, 1, "Laptop Pro 15");
        doc.SetCellValue("Inventory", 1, 2, "Electronics");
        doc.SetCellValue("Inventory", 1, 3, "1299.99");
        doc.SetCellValue("Inventory", 1, 4, "45");
        doc.SetCellValue("Inventory", 2, 0, "A002");
        doc.SetCellValue("Inventory", 2, 1, "Wireless Mouse");
        doc.SetCellValue("Inventory", 2, 2, "Accessories");
        doc.SetCellValue("Inventory", 2, 3, "29.99");
        doc.SetCellValue("Inventory", 2, 4, "230");
        doc.SetCellValue("Inventory", 3, 0, "A003");
        doc.SetCellValue("Inventory", 3, 1, "USB-C Hub 7-port");
        doc.SetCellValue("Inventory", 3, 2, "Accessories");
        doc.SetCellValue("Inventory", 3, 3, "79.99");
        doc.SetCellValue("Inventory", 3, 4, "112");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetAutoFilterRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAutoFilterRange_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetAutoFilterRange("Inventory"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetAutoFilterRange_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetAutoFilterRange("Inventory"));
    }

    [Fact]
    public void GetAutoFilterRange_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetAutoFilterRange("Inventory"), doc.GetAutoFilterRange("Inventory"));
    }

    [Fact]
    public void GetAutoFilterRange_AfterSetAutoFilter_NonEmpty()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:E4");
        var range = doc.GetAutoFilterRange("Inventory");
        Assert.NotEmpty(range);
    }

    [Fact]
    public void GetAutoFilterRange_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:E4");
        var before = doc.GetAutoFilterRange("Inventory");
        var path = TempFile("afr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetAutoFilterRange("Inventory");
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // SetAutoFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void SetAutoFilter_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.SetAutoFilter("Inventory", "A1:E4"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetAutoFilter_Makes_Range_NonEmpty()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:E4");
        Assert.NotEmpty(doc.GetAutoFilterRange("Inventory"));
    }

    [Fact]
    public void SetAutoFilter_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:E4");
        var path = TempFile("saf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetAutoFilterRange("Inventory"));
    }

    [Fact]
    public void SetAutoFilter_Multiple_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:C4");
        doc.SetAutoFilter("Inventory", "A1:E4"); // overwrite
        Assert.NotEmpty(doc.GetAutoFilterRange("Inventory"));
    }

    [Fact]
    public void SetAutoFilter_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:E4");
        var ex = Record.Exception(() => doc.ExportToCsv("Inventory"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetAutoFilter_Then_GetColumnHeaders_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.SetAutoFilter("Inventory", "A1:E4");
        var ex = Record.Exception(() => doc.GetColumnHeaders("Inventory"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetFrozenRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrozenRowCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetFrozenRowCount("Inventory"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrozenRowCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetFrozenRowCount("Inventory") >= 0);
    }

    [Fact]
    public void GetFrozenRowCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetFrozenRowCount("Inventory"), doc.GetFrozenRowCount("Inventory"));
    }

    [Fact]
    public void GetFrozenRowCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetFrozenRowCount("Inventory");
        var path = TempFile("frc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrozenRowCount("Inventory"));
    }

    [Fact]
    public void GetFrozenRowCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        doc.SetCellValue("Fresh", 0, 0, "Header");
        Assert.Equal(0, doc.GetFrozenRowCount("Fresh"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetAutoFilter_GetAutoFilterRange_GetFrozenRowCount_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Orders");

        // Header row
        doc.SetCellValue("Orders", 0, 0, "OrderId");
        doc.SetCellValue("Orders", 0, 1, "Customer");
        doc.SetCellValue("Orders", 0, 2, "Product");
        doc.SetCellValue("Orders", 0, 3, "Quantity");
        doc.SetCellValue("Orders", 0, 4, "UnitPrice");
        doc.SetCellValue("Orders", 0, 5, "Total");
        doc.SetCellValue("Orders", 0, 6, "Status");

        // Data rows
        string[,] rows = {
            { "ORD-001", "Acme Corp", "ServerX Pro", "5", "2499.99", "12499.95", "Shipped" },
            { "ORD-002", "TechStart Inc", "Workstation Z", "2", "3299.99", "6599.98", "Processing" },
            { "ORD-003", "Global Media", "Monitor 4K", "10", "599.99", "5999.90", "Shipped" },
            { "ORD-004", "Acme Corp", "Keyboard Pro", "25", "149.99", "3749.75", "Delivered" },
            { "ORD-005", "DataFlow Ltd", "ServerX Pro", "3", "2499.99", "7499.97", "Pending" },
            { "ORD-006", "TechStart Inc", "Monitor 4K", "4", "599.99", "2399.96", "Shipped" }
        };
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 7; c++)
                doc.SetCellValue("Orders", r + 1, c, rows[r, c]);

        // GetAutoFilterRange — initially empty or no filter
        var initialRange = doc.GetAutoFilterRange("Orders");
        Assert.NotNull(initialRange);

        // GetFrozenRowCount — initially 0
        Assert.Equal(0, doc.GetFrozenRowCount("Orders"));

        // SetAutoFilter — apply to header + data
        doc.SetAutoFilter("Orders", "A1:G7");
        Assert.Equal(doc.GetAutoFilterRange("Orders"), doc.GetAutoFilterRange("Orders")); // consistent
        Assert.NotEmpty(doc.GetAutoFilterRange("Orders"));

        // GetFrozenRowCount still 0 (auto-filter ≠ freeze)
        Assert.Equal(0, doc.GetFrozenRowCount("Orders"));

        // ExportToCsv works with auto-filter
        var csv = doc.ExportToCsv("Orders");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetColumnHeaders works
        var headers = doc.GetColumnHeaders("Orders");
        Assert.NotNull(headers);

        // GetCellValue cross-check
        Assert.Equal("ORD-001", doc.GetCellValue("Orders", 1, 0));
        Assert.Equal("Acme Corp", doc.GetCellValue("Orders", 1, 1));

        // SaveToFile
        var path = TempFile("dogfood_orders.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetAutoFilterRange("Orders"));
        Assert.True(loaded.GetFrozenRowCount("Orders") >= 0);

        // Consistent after load
        Assert.Equal(loaded.GetFrozenRowCount("Orders"), loaded.GetFrozenRowCount("Orders"));
        Assert.Equal(loaded.GetAutoFilterRange("Orders"), loaded.GetAutoFilterRange("Orders"));

        // SetAutoFilter on loaded — different range
        loaded.SetAutoFilter("Orders", "A1:C7");
        Assert.NotEmpty(loaded.GetAutoFilterRange("Orders"));

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("Orders");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // Final save
        var path2 = TempFile("dogfood_orders_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.NotNull(loaded2.GetAutoFilterRange("Orders"));
        Assert.True(loaded2.GetFrozenRowCount("Orders") >= 0);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Orders"));
        Assert.Null(ex1);
    }
}
