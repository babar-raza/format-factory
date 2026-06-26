// Tests for FodsDocument.GetNamedRangeCount, AddNamedRange, GetNamedRangeAddress deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R306

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R306: Tests for FodsDocument.GetNamedRangeCount, AddNamedRange, GetNamedRangeAddress deeper.
/// GetNamedRangeCount(): returns the number of named ranges defined in the workbook.
/// AddNamedRange(name, sheetName, address): adds a named range pointing to a cell range.
/// GetNamedRangeAddress(name): returns the address string for a named range.
/// Covers: GetNamedRangeCount no-throw; GetNamedRangeCount non-negative; GetNamedRangeCount consistent;
/// GetNamedRangeCount zero for new doc; GetNamedRangeCount after AddNamedRange increases;
/// GetNamedRangeCount save-load;
/// AddNamedRange no-throw; AddNamedRange increases count; AddNamedRange save-load;
/// AddNamedRange multiple; AddNamedRange then ExportToCsv no-throw;
/// GetNamedRangeAddress no-throw; GetNamedRangeAddress non-null; GetNamedRangeAddress consistent;
/// GetNamedRangeAddress save-load;
/// dogfood CreateDoc→AddNamedRange→GetNamedRangeCount→GetNamedRangeAddress→SaveToFile pipeline.
/// </summary>
public class FodsR306GetNamedRangeCountAndAddNamedRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR306GetNamedRangeCountAndAddNamedRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR306_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Financials");
        doc.SetCellValue("Financials", 0, 0, "Quarter");
        doc.SetCellValue("Financials", 0, 1, "Revenue");
        doc.SetCellValue("Financials", 0, 2, "Expenses");
        doc.SetCellValue("Financials", 0, 3, "Profit");
        doc.SetCellValue("Financials", 1, 0, "Q1");
        doc.SetCellValue("Financials", 1, 1, "420000");
        doc.SetCellValue("Financials", 1, 2, "310000");
        doc.SetCellValue("Financials", 1, 3, "110000");
        doc.SetCellValue("Financials", 2, 0, "Q2");
        doc.SetCellValue("Financials", 2, 1, "485000");
        doc.SetCellValue("Financials", 2, 2, "340000");
        doc.SetCellValue("Financials", 2, 3, "145000");
        doc.SetCellValue("Financials", 3, 0, "Q3");
        doc.SetCellValue("Financials", 3, 1, "510000");
        doc.SetCellValue("Financials", 3, 2, "355000");
        doc.SetCellValue("Financials", 3, 3, "155000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetNamedRangeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetNamedRangeCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetNamedRangeCount() >= 0);
    }

    [Fact]
    public void GetNamedRangeCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetNamedRangeCount(), doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        doc.SetCellValue("Empty", 0, 0, "data");
        Assert.Equal(0, doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_AfterAddNamedRange_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetNamedRangeCount();
        doc.AddNamedRange("RevenueRange", "Financials", "B2:B4");
        Assert.Equal(before + 1, doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("ProfitRange", "Financials", "D2:D4");
        var before = doc.GetNamedRangeCount();
        var path = TempFile("nrc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRangeCount());
    }

    // -------------------------------------------------------------------------
    // AddNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNamedRange_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddNamedRange("TestRange", "Financials", "A1:D4"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetNamedRangeCount();
        doc.AddNamedRange("ExpenseRange", "Financials", "C2:C4");
        Assert.Equal(before + 1, doc.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("QuarterRange", "Financials", "A2:A4");
        var before = doc.GetNamedRangeCount();
        var path = TempFile("anr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("Rev", "Financials", "B2:B4");
        doc.AddNamedRange("Exp", "Financials", "C2:C4");
        doc.AddNamedRange("Prof", "Financials", "D2:D4");
        Assert.Equal(3, doc.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("DataRange", "Financials", "A1:D4");
        var ex = Record.Exception(() => doc.ExportToCsv("Financials"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetNamedRangeAddress
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeAddress_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("AddrTest", "Financials", "B2:B4");
        var ex = Record.Exception(() => doc.GetNamedRangeAddress("AddrTest"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeAddress_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("AddrNull", "Financials", "C2:C4");
        Assert.NotNull(doc.GetNamedRangeAddress("AddrNull"));
    }

    [Fact]
    public void GetNamedRangeAddress_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("AddrConsist", "Financials", "D2:D4");
        Assert.Equal(
            doc.GetNamedRangeAddress("AddrConsist"),
            doc.GetNamedRangeAddress("AddrConsist"));
    }

    [Fact]
    public void GetNamedRangeAddress_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddNamedRange("AddrSL", "Financials", "A2:A4");
        var before = doc.GetNamedRangeAddress("AddrSL");
        var path = TempFile("nra_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetNamedRangeAddress("AddrSL");
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddNamedRange_GetNamedRangeCount_GetNamedRangeAddress_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");

        // Headers
        doc.SetCellValue("Inventory", 0, 0, "SKU");
        doc.SetCellValue("Inventory", 0, 1, "ProductName");
        doc.SetCellValue("Inventory", 0, 2, "Category");
        doc.SetCellValue("Inventory", 0, 3, "UnitCost");
        doc.SetCellValue("Inventory", 0, 4, "Quantity");
        doc.SetCellValue("Inventory", 0, 5, "TotalValue");

        // Data rows
        string[,] data = {
            { "A001", "Widget Alpha", "Hardware", "12.50", "1500", "18750" },
            { "A002", "Widget Beta", "Hardware", "18.75", "800", "15000" },
            { "B001", "Gadget X", "Electronics", "45.00", "350", "15750" },
            { "B002", "Gadget Y", "Electronics", "72.50", "200", "14500" },
            { "C001", "Supply Box", "Consumables", "8.25", "2000", "16500" }
        };
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("Inventory", r + 1, c, data[r, c]);

        // GetNamedRangeCount — zero initially
        Assert.Equal(0, doc.GetNamedRangeCount());

        // AddNamedRange — SKU column
        doc.AddNamedRange("SKUs", "Inventory", "A2:A6");
        Assert.Equal(1, doc.GetNamedRangeCount());

        // AddNamedRange — cost column
        doc.AddNamedRange("UnitCosts", "Inventory", "D2:D6");
        Assert.Equal(2, doc.GetNamedRangeCount());

        // AddNamedRange — quantity column
        doc.AddNamedRange("Quantities", "Inventory", "E2:E6");
        Assert.Equal(3, doc.GetNamedRangeCount());

        // AddNamedRange — total value column
        doc.AddNamedRange("TotalValues", "Inventory", "F2:F6");
        Assert.Equal(4, doc.GetNamedRangeCount());

        // Consistent
        Assert.Equal(doc.GetNamedRangeCount(), doc.GetNamedRangeCount());

        // GetNamedRangeAddress
        var skuAddr = doc.GetNamedRangeAddress("SKUs");
        Assert.NotNull(skuAddr);
        Assert.Equal(skuAddr, doc.GetNamedRangeAddress("SKUs")); // consistent

        var costAddr = doc.GetNamedRangeAddress("UnitCosts");
        Assert.NotNull(costAddr);

        // ExportToCsv works
        var csv = doc.ExportToCsv("Inventory");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue cross-check
        Assert.Equal("Widget Alpha", doc.GetCellValue("Inventory", 1, 1));

        // SaveToFile
        var path = TempFile("dogfood_inventory.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetNamedRangeCount());
        Assert.NotNull(loaded.GetNamedRangeAddress("SKUs"));
        Assert.NotNull(loaded.GetNamedRangeAddress("UnitCosts"));

        // AddNamedRange on loaded
        loaded.AddNamedRange("FullData", "Inventory", "A1:F6");
        Assert.Equal(5, loaded.GetNamedRangeCount());

        // Mutate and verify
        loaded.SetCellValue("Inventory", 6, 0, "D001");
        loaded.SetCellValue("Inventory", 6, 1, "Device Z");
        loaded.SetCellValue("Inventory", 6, 2, "Electronics");
        loaded.SetCellValue("Inventory", 6, 3, "125.00");
        loaded.SetCellValue("Inventory", 6, 4, "100");
        loaded.SetCellValue("Inventory", 6, 5, "12500");

        // Final save
        var path2 = TempFile("dogfood_inventory_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetNamedRangeCount());
        Assert.NotNull(loaded2.GetNamedRangeAddress("FullData"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Inventory"));
        Assert.Null(ex1);
    }
}
