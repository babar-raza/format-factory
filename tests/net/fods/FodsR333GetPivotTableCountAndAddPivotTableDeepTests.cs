// Tests for FodsDocument.GetPivotTableCount, AddPivotTable, GetPivotTableSourceRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R333

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R333: Tests for FodsDocument.GetPivotTableCount, AddPivotTable, GetPivotTableSourceRange deeper.
/// GetPivotTableCount(sheet): returns the number of pivot tables in the given sheet.
/// AddPivotTable(sheet, sourceRange, destCell, rowField, colField, dataField): adds a pivot table.
/// GetPivotTableSourceRange(sheet, index): returns the source data range of the pivot table.
/// Covers: GetPivotTableCount no-throw; GetPivotTableCount non-negative; GetPivotTableCount consistent;
/// GetPivotTableCount zero for new sheet; GetPivotTableCount after AddPivotTable increases;
/// GetPivotTableCount save-load;
/// AddPivotTable no-throw; AddPivotTable increases count; AddPivotTable save-load;
/// AddPivotTable multiple; AddPivotTable then ExportToHtml no-throw; AddPivotTable then ExportToCsv no-throw;
/// AddPivotTable then GetCharCount positive;
/// GetPivotTableSourceRange no-throw; GetPivotTableSourceRange non-null; GetPivotTableSourceRange consistent;
/// GetPivotTableSourceRange save-load;
/// dogfood CreateDoc→AddPivotTable→GetPivotTableCount→GetPivotTableSourceRange→SaveToFile pipeline.
/// </summary>
public class FodsR333GetPivotTableCountAndAddPivotTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR333GetPivotTableCountAndAddPivotTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR333_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSalesDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("RawData");
        doc.SetCellValue("RawData", 0, 0, "Region");
        doc.SetCellValue("RawData", 0, 1, "Product");
        doc.SetCellValue("RawData", 0, 2, "Quarter");
        doc.SetCellValue("RawData", 0, 3, "Revenue");
        string[] regions = { "North", "South", "East", "West" };
        string[] products = { "Widget A", "Widget B", "Widget C" };
        int row = 1;
        for (int r = 0; r < 4; r++)
            for (int p = 0; p < 3; p++)
                for (int q = 1; q <= 4; q++)
                {
                    doc.SetCellValue("RawData", row, 0, regions[r]);
                    doc.SetCellValue("RawData", row, 1, products[p]);
                    doc.SetCellValue("RawData", row, 2, $"Q{q}");
                    doc.SetCellValue("RawData", row, 3, ((r + 1) * (p + 1) * q * 1000).ToString());
                    row++;
                }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPivotTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableCount_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() => doc.GetPivotTableCount("RawData"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPivotTableCount_NonNegative()
    {
        var doc = CreateSalesDoc();
        Assert.True(doc.GetPivotTableCount("RawData") >= 0);
    }

    [Fact]
    public void GetPivotTableCount_Consistent()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(doc.GetPivotTableCount("RawData"), doc.GetPivotTableCount("RawData"));
    }

    [Fact]
    public void GetPivotTableCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        Assert.Equal(0, doc.GetPivotTableCount("Fresh"));
    }

    [Fact]
    public void GetPivotTableCount_AfterAddPivotTable_Increases()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetPivotTableCount("RawData");
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Quarter", "Revenue");
        Assert.Equal(before + 1, doc.GetPivotTableCount("RawData"));
    }

    [Fact]
    public void GetPivotTableCount_SaveLoad_Consistent()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Product", "Quarter", "Revenue");
        var before = doc.GetPivotTableCount("RawData");
        var path = TempFile("ptc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPivotTableCount("RawData"));
    }

    // -------------------------------------------------------------------------
    // AddPivotTable
    // -------------------------------------------------------------------------

    [Fact]
    public void AddPivotTable_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() => doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Product", "Revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddPivotTable_Increases_Count()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetPivotTableCount("RawData");
        doc.AddPivotTable("RawData", "A1:D49", "H1", "Quarter", "Region", "Revenue");
        Assert.Equal(before + 1, doc.GetPivotTableCount("RawData"));
    }

    [Fact]
    public void AddPivotTable_SaveLoad_Persists()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Quarter", "Revenue");
        var before = doc.GetPivotTableCount("RawData");
        var path = TempFile("apt_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPivotTableCount("RawData"));
    }

    [Fact]
    public void AddPivotTable_Multiple()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Quarter", "Revenue");
        doc.AddPivotTable("RawData", "A1:D49", "F10", "Product", "Region", "Revenue");
        doc.AddPivotTable("RawData", "A1:D49", "F20", "Quarter", "Product", "Revenue");
        Assert.Equal(3, doc.GetPivotTableCount("RawData"));
    }

    [Fact]
    public void AddPivotTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Product", "Revenue");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddPivotTable_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Quarter", "Product", "Revenue");
        var path = TempFile("pivot_csv.csv");
        var ex = Record.Exception(() => doc.ExportToCsv("RawData", path));
        Assert.Null(ex);
    }

    [Fact]
    public void AddPivotTable_Then_GetCharCount_Positive()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Quarter", "Revenue");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetPivotTableSourceRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableSourceRange_NoThrow()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Quarter", "Revenue");
        var ex = Record.Exception(() => doc.GetPivotTableSourceRange("RawData", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPivotTableSourceRange_NonNull()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Product", "Quarter", "Revenue");
        Assert.NotNull(doc.GetPivotTableSourceRange("RawData", 0));
    }

    [Fact]
    public void GetPivotTableSourceRange_Consistent()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Product", "Revenue");
        Assert.Equal(doc.GetPivotTableSourceRange("RawData", 0), doc.GetPivotTableSourceRange("RawData", 0));
    }

    [Fact]
    public void GetPivotTableSourceRange_SaveLoad_Consistent()
    {
        var doc = CreateSalesDoc();
        doc.AddPivotTable("RawData", "A1:D49", "F1", "Region", "Quarter", "Revenue");
        var path = TempFile("ptsr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetPivotTableSourceRange("RawData", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddPivotTable_GetPivotTableCount_GetPivotTableSourceRange_SaveToFile_Pipeline()
    {
        // Retail analytics — multi-channel sales performance pivot analysis
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("SalesData");

        // Headers
        doc.SetCellValue("SalesData", 0, 0, "OrderDate");
        doc.SetCellValue("SalesData", 0, 1, "Channel");
        doc.SetCellValue("SalesData", 0, 2, "Category");
        doc.SetCellValue("SalesData", 0, 3, "SubCategory");
        doc.SetCellValue("SalesData", 0, 4, "Region");
        doc.SetCellValue("SalesData", 0, 5, "Revenue");
        doc.SetCellValue("SalesData", 0, 6, "Units");
        doc.SetCellValue("SalesData", 0, 7, "Margin");

        // 12 data rows
        string[] channels = { "Online", "Retail", "Wholesale", "Direct" };
        string[] categories = { "Electronics", "Apparel", "Furniture" };
        string[] regions = { "North", "South", "East" };
        int[] revenues = { 12500, 8900, 45200, 3100, 22000, 15600, 9800, 31400, 7200, 19500, 26800, 11300 };
        for (int i = 0; i < 12; i++)
        {
            doc.SetCellValue("SalesData", i + 1, 0, $"2026-0{(i / 4) + 1}-{(i % 4) * 7 + 1:D2}");
            doc.SetCellValue("SalesData", i + 1, 1, channels[i % 4]);
            doc.SetCellValue("SalesData", i + 1, 2, categories[i % 3]);
            doc.SetCellValue("SalesData", i + 1, 3, $"Sub-{categories[i % 3].Substring(0, 3)}-{(i % 2) + 1}");
            doc.SetCellValue("SalesData", i + 1, 4, regions[i % 3]);
            doc.SetCellValue("SalesData", i + 1, 5, revenues[i].ToString());
            doc.SetCellValue("SalesData", i + 1, 6, (revenues[i] / 85).ToString());
            doc.SetCellValue("SalesData", i + 1, 7, (revenues[i] * 0.28).ToString("F0"));
        }

        // Initial pivot count — zero
        Assert.Equal(0, doc.GetPivotTableCount("SalesData"));

        // AddPivotTable — revenue by channel × region
        doc.AddPivotTable("SalesData", "A1:H13", "J1", "Channel", "Region", "Revenue");
        Assert.Equal(1, doc.GetPivotTableCount("SalesData"));
        Assert.NotNull(doc.GetPivotTableSourceRange("SalesData", 0));

        // AddPivotTable — units by category × channel
        doc.AddPivotTable("SalesData", "A1:H13", "J10", "Category", "Channel", "Units");
        Assert.Equal(2, doc.GetPivotTableCount("SalesData"));

        // AddPivotTable — margin by region × category
        doc.AddPivotTable("SalesData", "A1:H13", "J20", "Region", "Category", "Margin");
        Assert.Equal(3, doc.GetPivotTableCount("SalesData"));

        // Consistent
        Assert.Equal(doc.GetPivotTableCount("SalesData"), doc.GetPivotTableCount("SalesData"));
        Assert.Equal(doc.GetPivotTableSourceRange("SalesData", 0), doc.GetPivotTableSourceRange("SalesData", 0));

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCharCount positive
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_retail_pivot.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetPivotTableCount("SalesData"));
        Assert.NotNull(loaded.GetPivotTableSourceRange("SalesData", 0));
        Assert.NotNull(loaded.GetPivotTableSourceRange("SalesData", 2));

        // AddPivotTable on loaded
        loaded.AddPivotTable("SalesData", "A1:H13", "J30", "SubCategory", "Region", "Revenue");
        Assert.Equal(4, loaded.GetPivotTableCount("SalesData"));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // SetCellValue on loaded
        loaded.SetCellValue("SalesData", 13, 1, "Online");
        loaded.SetCellValue("SalesData", 13, 5, "5600");

        // Final save
        var path2 = TempFile("dogfood_retail_pivot_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetPivotTableCount("SalesData"));
        Assert.NotNull(loaded2.GetPivotTableSourceRange("SalesData", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetPivotTableCount("SalesData"));
        var ex3 = Record.Exception(() => loaded2.AddPivotTable("SalesData", "A1:H14", "J40", "Channel", "Category", "Revenue"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
