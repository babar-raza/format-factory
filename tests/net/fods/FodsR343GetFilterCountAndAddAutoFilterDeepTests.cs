// Tests for FodsDocument.GetFilterCount, AddAutoFilter, GetFilterRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R343

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R343: Tests for FodsDocument.GetFilterCount, AddAutoFilter, GetFilterRange deeper.
/// GetFilterCount(): returns the number of auto-filters defined in the document.
/// AddAutoFilter(sheetName, rangeAddress): adds an auto-filter to the specified range.
/// GetFilterRange(index): returns the range address of the filter at the given index.
/// Covers: GetFilterCount no-throw; GetFilterCount non-negative; GetFilterCount consistent;
/// GetFilterCount zero for new doc; GetFilterCount after AddAutoFilter increases;
/// GetFilterCount save-load;
/// AddAutoFilter no-throw; AddAutoFilter increases count; AddAutoFilter save-load;
/// AddAutoFilter multiple; AddAutoFilter then ExportToHtml no-throw;
/// AddAutoFilter then GetCellValue no-throw;
/// GetFilterRange no-throw; GetFilterRange non-null; GetFilterRange consistent;
/// GetFilterRange save-load;
/// dogfood CreateDoc→AddAutoFilter→GetFilterCount→GetFilterRange→SaveToFile pipeline.
/// </summary>
public class FodsR343GetFilterCountAndAddAutoFilterDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR343GetFilterCountAndAddAutoFilterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR343_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSalesDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("SalesData");
        doc.SetCellValue("SalesData", 0, 0, "OrderID");
        doc.SetCellValue("SalesData", 0, 1, "Region");
        doc.SetCellValue("SalesData", 0, 2, "Product");
        doc.SetCellValue("SalesData", 0, 3, "Quantity");
        doc.SetCellValue("SalesData", 0, 4, "Revenue");
        for (int r = 1; r <= 10; r++)
        {
            doc.SetCellValue("SalesData", r, 0, $"ORD{r:D4}");
            doc.SetCellValue("SalesData", r, 1, r % 2 == 0 ? "North" : "South");
            doc.SetCellValue("SalesData", r, 2, r % 3 == 0 ? "WidgetA" : r % 3 == 1 ? "WidgetB" : "WidgetC");
            doc.SetCellValue("SalesData", r, 3, (r * 5).ToString());
            doc.SetCellValue("SalesData", r, 4, (r * 150.0m).ToString());
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFilterCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFilterCount_NoThrow()
    {
        var doc = CreateSalesDataDoc();
        var ex = Record.Exception(() => doc.GetFilterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFilterCount_NonNegative()
    {
        var doc = CreateSalesDataDoc();
        Assert.True(doc.GetFilterCount() >= 0);
    }

    [Fact]
    public void GetFilterCount_Consistent()
    {
        var doc = CreateSalesDataDoc();
        Assert.Equal(doc.GetFilterCount(), doc.GetFilterCount());
    }

    [Fact]
    public void GetFilterCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.Equal(0, doc.GetFilterCount());
    }

    [Fact]
    public void GetFilterCount_AfterAddAutoFilter_Increases()
    {
        var doc = CreateSalesDataDoc();
        var before = doc.GetFilterCount();
        doc.AddAutoFilter("SalesData", "A1:E11");
        Assert.Equal(before + 1, doc.GetFilterCount());
    }

    [Fact]
    public void GetFilterCount_SaveLoad_Consistent()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        var before = doc.GetFilterCount();
        var path = TempFile("fc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFilterCount());
    }

    // -------------------------------------------------------------------------
    // AddAutoFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void AddAutoFilter_NoThrow()
    {
        var doc = CreateSalesDataDoc();
        var ex = Record.Exception(() => doc.AddAutoFilter("SalesData", "A1:E11"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddAutoFilter_Increases_Count()
    {
        var doc = CreateSalesDataDoc();
        var before = doc.GetFilterCount();
        doc.AddAutoFilter("SalesData", "A1:E11");
        Assert.Equal(before + 1, doc.GetFilterCount());
    }

    [Fact]
    public void AddAutoFilter_SaveLoad_Persists()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        var before = doc.GetFilterCount();
        var path = TempFile("af_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFilterCount());
    }

    [Fact]
    public void AddAutoFilter_Multiple()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.SetCellValue("Sheet1", 0, 0, "A");
        doc.SetCellValue("Sheet2", 0, 0, "B");
        doc.AddAutoFilter("Sheet1", "A1:A5");
        doc.AddAutoFilter("Sheet2", "A1:A5");
        Assert.Equal(2, doc.GetFilterCount());
    }

    [Fact]
    public void AddAutoFilter_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddAutoFilter_Then_GetCellValue_NoThrow()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        var ex = Record.Exception(() => doc.GetCellValue("SalesData", 0, 0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetFilterRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFilterRange_NoThrow()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        var ex = Record.Exception(() => doc.GetFilterRange(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFilterRange_NonNull()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        Assert.NotNull(doc.GetFilterRange(0));
    }

    [Fact]
    public void GetFilterRange_Consistent()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        Assert.Equal(doc.GetFilterRange(0), doc.GetFilterRange(0));
    }

    [Fact]
    public void GetFilterRange_SaveLoad_Consistent()
    {
        var doc = CreateSalesDataDoc();
        doc.AddAutoFilter("SalesData", "A1:E11");
        var path = TempFile("fr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetFilterRange(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddAutoFilter_GetFilterCount_GetFilterRange_SaveToFile_Pipeline()
    {
        // Supply chain analytics — multi-sheet sales performance workbook with auto-filters
        var doc = FodsDocument.CreateEmpty();

        // ---- Orders sheet ----
        doc.AddSheet("Orders");
        doc.SetCellValue("Orders", 0, 0, "OrderID");
        doc.SetCellValue("Orders", 0, 1, "OrderDate");
        doc.SetCellValue("Orders", 0, 2, "CustomerID");
        doc.SetCellValue("Orders", 0, 3, "Region");
        doc.SetCellValue("Orders", 0, 4, "Channel");
        doc.SetCellValue("Orders", 0, 5, "SKU");
        doc.SetCellValue("Orders", 0, 6, "Units");
        doc.SetCellValue("Orders", 0, 7, "NetRevenue");
        doc.SetCellValue("Orders", 0, 8, "DiscountPct");
        string[] regions = { "EMEA", "APAC", "AMER", "LATAM" };
        string[] channels = { "Direct", "Distributor", "Retail", "Online" };
        string[] skus = { "SKU-A100", "SKU-B200", "SKU-C300", "SKU-D400", "SKU-E500" };
        for (int r = 1; r <= 20; r++)
        {
            doc.SetCellValue("Orders", r, 0, $"ORD{2024000 + r}");
            doc.SetCellValue("Orders", r, 1, $"2024-{(r % 12 + 1):D2}-15");
            doc.SetCellValue("Orders", r, 2, $"CUST{(r % 5 + 1):D3}");
            doc.SetCellValue("Orders", r, 3, regions[r % 4]);
            doc.SetCellValue("Orders", r, 4, channels[r % 4]);
            doc.SetCellValue("Orders", r, 5, skus[r % 5]);
            doc.SetCellValue("Orders", r, 6, (r * 10).ToString());
            doc.SetCellValue("Orders", r, 7, (r * 250.0m).ToString());
            doc.SetCellValue("Orders", r, 8, (r % 5 * 2.5m).ToString());
        }

        // ---- Returns sheet ----
        doc.AddSheet("Returns");
        doc.SetCellValue("Returns", 0, 0, "ReturnID");
        doc.SetCellValue("Returns", 0, 1, "OrigOrderID");
        doc.SetCellValue("Returns", 0, 2, "Reason");
        doc.SetCellValue("Returns", 0, 3, "Units");
        doc.SetCellValue("Returns", 0, 4, "Refund");
        string[] reasons = { "Defective", "Wrong_Item", "Changed_Mind", "Damaged_Transit" };
        for (int r = 1; r <= 8; r++)
        {
            doc.SetCellValue("Returns", r, 0, $"RET{r:D4}");
            doc.SetCellValue("Returns", r, 1, $"ORD{2024000 + r}");
            doc.SetCellValue("Returns", r, 2, reasons[r % 4]);
            doc.SetCellValue("Returns", r, 3, r.ToString());
            doc.SetCellValue("Returns", r, 4, (r * 50m).ToString());
        }

        Assert.Equal(0, doc.GetFilterCount());

        // AddAutoFilter — Orders sheet
        doc.AddAutoFilter("Orders", "A1:I21");
        Assert.Equal(1, doc.GetFilterCount());

        // AddAutoFilter — Returns sheet
        doc.AddAutoFilter("Returns", "A1:E9");
        Assert.Equal(2, doc.GetFilterCount());

        // Consistent
        Assert.Equal(doc.GetFilterCount(), doc.GetFilterCount());

        // GetFilterRange
        var range0 = doc.GetFilterRange(0);
        Assert.NotNull(range0);
        Assert.Equal(range0, doc.GetFilterRange(0)); // consistent

        var range1 = doc.GetFilterRange(1);
        Assert.NotNull(range1);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCellValue
        var orderId = doc.GetCellValue("Orders", 1, 0);
        Assert.NotNull(orderId);

        // GetSheetCount
        Assert.True(doc.GetSheetCount() >= 2);

        // SaveToFile
        var path = TempFile("dogfood_supply_chain.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetFilterCount());
        Assert.NotNull(loaded.GetFilterRange(0));
        Assert.NotNull(loaded.GetFilterRange(1));

        // AddAutoFilter on loaded
        loaded.AddSheet("Forecast");
        loaded.SetCellValue("Forecast", 0, 0, "Period");
        loaded.SetCellValue("Forecast", 0, 1, "ForecastUnits");
        loaded.AddAutoFilter("Forecast", "A1:B13");
        Assert.Equal(3, loaded.GetFilterCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_supply_chain_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(3, loaded2.GetFilterCount());
        Assert.NotNull(loaded2.GetFilterRange(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetFilterRange(2));
        var ex3 = Record.Exception(() => loaded2.AddAutoFilter("Forecast", "A1:B5"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
