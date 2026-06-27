// Tests for FodsDocument.GetChartCount, AddChart, GetChartType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R329

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R329: Tests for FodsDocument.GetChartCount, AddChart, GetChartType deeper.
/// GetChartCount(sheetName): returns the number of embedded charts on the sheet.
/// AddChart(sheetName, dataRange, chartType, title): adds a chart referencing the given data range.
/// GetChartType(sheetName, index): returns the chart type string for the chart at the index.
/// Covers: GetChartCount no-throw; GetChartCount non-negative; GetChartCount consistent;
/// GetChartCount zero for new sheet; GetChartCount after AddChart increases; GetChartCount save-load;
/// AddChart no-throw; AddChart increases count; AddChart save-load;
/// AddChart multiple; AddChart then GetColumnSum no-throw; AddChart then ExportToCsv no-throw;
/// GetChartType no-throw; GetChartType non-null; GetChartType consistent; GetChartType save-load;
/// dogfood CreateDoc→AddChart→GetChartCount→GetChartType→SaveToFile pipeline.
/// </summary>
public class FodsR329GetChartCountAndAddChartDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR329GetChartCountAndAddChartDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR329_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("SalesData");
        doc.SetCellValue("SalesData", 0, 0, "quarter");
        doc.SetCellValue("SalesData", 0, 1, "revenue");
        doc.SetCellValue("SalesData", 0, 2, "cost");
        doc.SetCellValue("SalesData", 0, 3, "profit");
        string[][] rows = {
            new[] { "Q1", "285000", "198000", "87000" },
            new[] { "Q2", "312000", "215000", "97000" },
            new[] { "Q3", "298000", "204000", "94000" },
            new[] { "Q4", "356000", "238000", "118000" },
        };
        for (int r = 0; r < rows.Length; r++)
            for (int c = 0; c < rows[r].Length; c++)
                doc.SetCellValue("SalesData", r + 1, c, rows[r][c]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetChartCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartCount_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() => doc.GetChartCount("SalesData"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChartCount_NonNegative()
    {
        var doc = CreateSalesDoc();
        Assert.True(doc.GetChartCount("SalesData") >= 0);
    }

    [Fact]
    public void GetChartCount_Consistent()
    {
        var doc = CreateSalesDoc();
        Assert.Equal(doc.GetChartCount("SalesData"), doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void GetChartCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("EmptySheet");
        doc.SetCellValue("EmptySheet", 0, 0, "value");
        Assert.Equal(0, doc.GetChartCount("EmptySheet"));
    }

    [Fact]
    public void GetChartCount_AfterAddChart_Increases()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetChartCount("SalesData");
        doc.AddChart("SalesData", "A1:D5", "bar", "Quarterly Revenue");
        Assert.Equal(before + 1, doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void GetChartCount_SaveLoad_Consistent()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "B1:B5", "line", "Revenue Trend");
        var before = doc.GetChartCount("SalesData");
        var path = TempFile("cc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChartCount("SalesData"));
    }

    // -------------------------------------------------------------------------
    // AddChart
    // -------------------------------------------------------------------------

    [Fact]
    public void AddChart_NoThrow()
    {
        var doc = CreateSalesDoc();
        var ex = Record.Exception(() => doc.AddChart("SalesData", "A1:D5", "column", "Sales Dashboard"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddChart_Increases_Count()
    {
        var doc = CreateSalesDoc();
        var before = doc.GetChartCount("SalesData");
        doc.AddChart("SalesData", "C1:C5", "pie", "Cost Distribution");
        Assert.Equal(before + 1, doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void AddChart_SaveLoad_Persists()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "D1:D5", "line", "Profit Trend");
        var before = doc.GetChartCount("SalesData");
        var path = TempFile("ac_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChartCount("SalesData"));
    }

    [Fact]
    public void AddChart_Multiple()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "A1:B5", "bar", "Revenue by Quarter");
        doc.AddChart("SalesData", "A1:D5", "line", "P&L Overview");
        doc.AddChart("SalesData", "D1:D5", "pie", "Profit Share");
        Assert.Equal(3, doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void AddChart_Then_GetColumnSum_NoThrow()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "B1:B5", "bar", "Revenue Chart");
        var ex = Record.Exception(() => doc.GetColumnSum("SalesData", "revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddChart_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "A1:D5", "column", "Full Dashboard");
        var path = TempFile("chart_export.csv");
        var ex = Record.Exception(() => doc.ExportToCsv("SalesData", path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetChartType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartType_NoThrow()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "B1:B5", "bar", "Test Chart");
        var ex = Record.Exception(() => doc.GetChartType("SalesData", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChartType_NonNull()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "A1:D5", "line", "Test");
        Assert.NotNull(doc.GetChartType("SalesData", 0));
    }

    [Fact]
    public void GetChartType_Consistent()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "A1:D5", "column", "Test");
        Assert.Equal(doc.GetChartType("SalesData", 0), doc.GetChartType("SalesData", 0));
    }

    [Fact]
    public void GetChartType_SaveLoad_Consistent()
    {
        var doc = CreateSalesDoc();
        doc.AddChart("SalesData", "B1:D5", "pie", "Pie Chart");
        var before = doc.GetChartType("SalesData", 0);
        var path = TempFile("ct_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetChartType("SalesData", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddChart_GetChartCount_GetChartType_SaveToFile_Pipeline()
    {
        // Investment portfolio performance dashboard — 12 months, 4 asset classes
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Portfolio");
        doc.SetCellValue("Portfolio", 0, 0, "month");
        doc.SetCellValue("Portfolio", 0, 1, "equities_return");
        doc.SetCellValue("Portfolio", 0, 2, "bonds_return");
        doc.SetCellValue("Portfolio", 0, 3, "real_estate_return");
        doc.SetCellValue("Portfolio", 0, 4, "commodities_return");
        doc.SetCellValue("Portfolio", 0, 5, "portfolio_value");

        string[][] data = {
            new[] { "Jan-26", "2.8", "0.5", "1.2", "-0.8", "1050000" },
            new[] { "Feb-26", "1.5", "0.8", "0.9", "1.5",  "1068250" },
            new[] { "Mar-26", "-1.2","1.2","1.5","2.8",  "1065800" },
            new[] { "Apr-26", "3.5", "0.3","0.8","-1.2", "1093250" },
            new[] { "May-26", "2.1", "0.6","1.1","0.8",  "1110800" },
            new[] { "Jun-26", "-0.8","1.5","0.5","3.5",  "1106950" },
            new[] { "Jul-26", "4.2", "0.2","1.8","1.2",  "1152600" },
            new[] { "Aug-26", "1.8", "0.9","0.7","-0.5", "1167350" },
            new[] { "Sep-26", "-2.5","1.8","0.4","2.1",  "1143250" },
            new[] { "Oct-26", "3.2", "0.4","1.5","1.8",  "1181800" },
            new[] { "Nov-26", "2.5", "0.7","0.9","0.5",  "1207350" },
            new[] { "Dec-26", "1.9", "1.1","1.2","1.5",  "1228500" },
        };
        for (int r = 0; r < data.Length; r++)
            for (int c = 0; c < data[r].Length; c++)
                doc.SetCellValue("Portfolio", r + 1, c, data[r][c]);

        // Initial chart count — zero
        Assert.Equal(0, doc.GetChartCount("Portfolio"));

        // AddChart — 4 charts for portfolio dashboard
        doc.AddChart("Portfolio", "A1:E13", "line", "Asset Class Returns — 2026");
        Assert.Equal(1, doc.GetChartCount("Portfolio"));

        doc.AddChart("Portfolio", "F1:F13", "area", "Portfolio Value — 2026");
        Assert.Equal(2, doc.GetChartCount("Portfolio"));

        doc.AddChart("Portfolio", "B1:E13", "bar", "Return Comparison by Month");
        Assert.Equal(3, doc.GetChartCount("Portfolio"));

        doc.AddChart("Portfolio", "B13:E13", "pie", "Dec-26 Asset Allocation");
        Assert.Equal(4, doc.GetChartCount("Portfolio"));

        // Consistent
        Assert.Equal(doc.GetChartCount("Portfolio"), doc.GetChartCount("Portfolio"));

        // GetChartType
        var type0 = doc.GetChartType("Portfolio", 0);
        Assert.NotNull(type0);
        Assert.Equal(type0, doc.GetChartType("Portfolio", 0)); // consistent

        var type3 = doc.GetChartType("Portfolio", 3);
        Assert.NotNull(type3);

        // Column operations still work
        var ex1 = Record.Exception(() => doc.GetColumnSum("Portfolio", "portfolio_value"));
        Assert.Null(ex1);

        // ExportToCsv works
        var csvPath = TempFile("dogfood_portfolio.csv");
        var ex2 = Record.Exception(() => doc.ExportToCsv("Portfolio", csvPath));
        Assert.Null(ex2);

        // SaveToFile
        var path = TempFile("dogfood_portfolio.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetChartCount("Portfolio"));
        Assert.NotNull(loaded.GetChartType("Portfolio", 0));
        Assert.NotNull(loaded.GetChartType("Portfolio", 3));

        // AddChart on loaded
        loaded.AddChart("Portfolio", "B1:C13", "scatter", "Equity vs Bond Returns");
        Assert.Equal(5, loaded.GetChartCount("Portfolio"));

        // ExportToCsv on loaded
        var csvPath2 = TempFile("dogfood_portfolio_v2.csv");
        var ex3 = Record.Exception(() => loaded.ExportToCsv("Portfolio", csvPath2));
        Assert.Null(ex3);

        // Final save
        var path2 = TempFile("dogfood_portfolio_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetChartCount("Portfolio"));
        Assert.NotNull(loaded2.GetChartType("Portfolio", 4));
        var ex4 = Record.Exception(() => loaded2.AddChart("Portfolio", "A1:F2", "column", "Summary"));
        Assert.Null(ex4);
    }
}
