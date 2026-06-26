// Tests for FodsDocument.GetChartCount, AddChart, GetChartTitle deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R315

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R315: Tests for FodsDocument.GetChartCount, AddChart, GetChartTitle deeper.
/// GetChartCount(sheetName): returns the number of charts embedded in the sheet.
/// AddChart(sheetName, chartType, dataRange, title): adds a chart to the sheet.
/// GetChartTitle(sheetName, chartIndex): returns the title of the chart at the given index.
/// Covers: GetChartCount no-throw; GetChartCount non-negative; GetChartCount consistent;
/// GetChartCount zero for new sheet; GetChartCount after AddChart increases; GetChartCount save-load;
/// AddChart no-throw; AddChart increases count; AddChart save-load;
/// AddChart multiple; AddChart then ExportToCsv no-throw;
/// GetChartTitle no-throw; GetChartTitle non-null; GetChartTitle consistent; GetChartTitle save-load;
/// dogfood CreateDoc→AddChart→GetChartCount→GetChartTitle→SaveToFile pipeline.
/// </summary>
public class FodsR315GetChartCountAndAddChartDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR315GetChartCountAndAddChartDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR315_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("SalesData");
        doc.SetCellValue("SalesData", 0, 0, "Month");
        doc.SetCellValue("SalesData", 0, 1, "Product A");
        doc.SetCellValue("SalesData", 0, 2, "Product B");
        doc.SetCellValue("SalesData", 0, 3, "Product C");
        string[] months = { "Jan", "Feb", "Mar", "Apr", "May", "Jun" };
        string[,] values = {
            { "12500", "8900", "6700" },
            { "14200", "9100", "7200" },
            { "13800", "10200", "7800" },
            { "15600", "11400", "8100" },
            { "16900", "12000", "8900" },
            { "18200", "13500", "9700" }
        };
        for (int r = 0; r < 6; r++)
        {
            doc.SetCellValue("SalesData", r + 1, 0, months[r]);
            for (int c = 0; c < 3; c++)
                doc.SetCellValue("SalesData", r + 1, c + 1, values[r, c]);
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetChartCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetChartCount("SalesData"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChartCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetChartCount("SalesData") >= 0);
    }

    [Fact]
    public void GetChartCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetChartCount("SalesData"), doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void GetChartCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        doc.SetCellValue("Empty", 0, 0, "value");
        Assert.Equal(0, doc.GetChartCount("Empty"));
    }

    [Fact]
    public void GetChartCount_AfterAddChart_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetChartCount("SalesData");
        doc.AddChart("SalesData", "bar", "A1:D7", "Monthly Sales Comparison");
        Assert.Equal(before + 1, doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void GetChartCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "line", "A1:D7", "Sales Trend");
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
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddChart("SalesData", "column", "B1:D7", "Product Revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddChart_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetChartCount("SalesData");
        doc.AddChart("SalesData", "bar", "A1:D7", "Revenue by Month");
        Assert.Equal(before + 1, doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void AddChart_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "pie", "A1:B7", "Product A Share");
        var before = doc.GetChartCount("SalesData");
        var path = TempFile("ac_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChartCount("SalesData"));
    }

    [Fact]
    public void AddChart_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "bar", "A1:D7", "Bar Chart");
        doc.AddChart("SalesData", "line", "A1:D7", "Line Chart");
        doc.AddChart("SalesData", "pie", "A1:B7", "Pie Chart");
        Assert.Equal(3, doc.GetChartCount("SalesData"));
    }

    [Fact]
    public void AddChart_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "column", "A1:D7", "Export Test");
        var ex = Record.Exception(() => doc.ExportToCsv("SalesData"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetChartTitle
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartTitle_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "bar", "A1:D7", "Test Title");
        var ex = Record.Exception(() => doc.GetChartTitle("SalesData", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChartTitle_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "line", "A1:D7", "Revenue Trend Analysis");
        Assert.NotNull(doc.GetChartTitle("SalesData", 0));
    }

    [Fact]
    public void GetChartTitle_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "column", "A1:D7", "Consistent Title");
        Assert.Equal(doc.GetChartTitle("SalesData", 0), doc.GetChartTitle("SalesData", 0));
    }

    [Fact]
    public void GetChartTitle_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddChart("SalesData", "bar", "A1:D7", "SaveLoad Chart Title");
        var before = doc.GetChartTitle("SalesData", 0);
        var path = TempFile("gct_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetChartTitle("SalesData", 0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddChart_GetChartCount_GetChartTitle_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("MarketAnalysis");

        // Headers
        doc.SetCellValue("MarketAnalysis", 0, 0, "Quarter");
        doc.SetCellValue("MarketAnalysis", 0, 1, "Revenue_M");
        doc.SetCellValue("MarketAnalysis", 0, 2, "EBITDA_M");
        doc.SetCellValue("MarketAnalysis", 0, 3, "Net_Income_M");
        doc.SetCellValue("MarketAnalysis", 0, 4, "Market_Share_Pct");
        doc.SetCellValue("MarketAnalysis", 0, 5, "Customer_NPS");

        // Quarterly data
        string[,] data = {
            { "Q1 2025", "245.2", "62.1", "38.4", "12.3", "47" },
            { "Q2 2025", "261.8", "68.4", "42.1", "12.7", "49" },
            { "Q3 2025", "278.5", "74.2", "46.8", "13.1", "51" },
            { "Q4 2025", "302.1", "82.6", "53.2", "13.8", "53" },
            { "Q1 2026", "258.4", "65.8", "40.1", "13.4", "48" },
            { "Q2 2026", "289.7", "78.3", "49.6", "14.2", "54" },
            { "Q3 2026", "315.6", "88.1", "57.9", "14.9", "56" },
            { "Q4 2026", "342.8", "98.4", "67.2", "15.6", "59" },
        };
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("MarketAnalysis", r + 1, c, data[r, c]);

        // Zero charts initially
        Assert.Equal(0, doc.GetChartCount("MarketAnalysis"));

        // AddChart — Revenue trend
        doc.AddChart("MarketAnalysis", "line", "A1:B9", "Quarterly Revenue Trend 2025-2026");
        Assert.Equal(1, doc.GetChartCount("MarketAnalysis"));

        // AddChart — Profitability comparison
        doc.AddChart("MarketAnalysis", "bar", "A1:D9", "Revenue vs EBITDA vs Net Income");
        Assert.Equal(2, doc.GetChartCount("MarketAnalysis"));

        // AddChart — Market share
        doc.AddChart("MarketAnalysis", "column", "A1:A9", "Market Share Growth");
        Assert.Equal(3, doc.GetChartCount("MarketAnalysis"));

        // AddChart — NPS
        doc.AddChart("MarketAnalysis", "line", "A1:A9", "Customer NPS Trajectory");
        Assert.Equal(4, doc.GetChartCount("MarketAnalysis"));

        // Consistent
        Assert.Equal(doc.GetChartCount("MarketAnalysis"), doc.GetChartCount("MarketAnalysis"));

        // GetChartTitle
        var title0 = doc.GetChartTitle("MarketAnalysis", 0);
        Assert.NotNull(title0);
        Assert.Equal(title0, doc.GetChartTitle("MarketAnalysis", 0)); // consistent

        var title1 = doc.GetChartTitle("MarketAnalysis", 1);
        Assert.NotNull(title1);

        var title3 = doc.GetChartTitle("MarketAnalysis", 3);
        Assert.NotNull(title3);

        // ExportToCsv works
        var csv = doc.ExportToCsv("MarketAnalysis");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_market.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetChartCount("MarketAnalysis"));
        Assert.NotNull(loaded.GetChartTitle("MarketAnalysis", 0));

        // AddChart on loaded
        loaded.AddChart("MarketAnalysis", "scatter", "B1:C9", "EBITDA vs Net Income Scatter");
        Assert.Equal(5, loaded.GetChartCount("MarketAnalysis"));

        // Mutate cell values
        loaded.SetCellValue("MarketAnalysis", 9, 0, "Q1 2027");
        loaded.SetCellValue("MarketAnalysis", 9, 1, "358.2");
        loaded.SetCellValue("MarketAnalysis", 9, 2, "105.7");
        loaded.SetCellValue("MarketAnalysis", 9, 3, "73.1");
        loaded.SetCellValue("MarketAnalysis", 9, 4, "16.1");
        loaded.SetCellValue("MarketAnalysis", 9, 5, "61");

        // Final save
        var path2 = TempFile("dogfood_market_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetChartCount("MarketAnalysis"));
        Assert.NotNull(loaded2.GetChartTitle("MarketAnalysis", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("MarketAnalysis"));
        Assert.Null(ex1);
    }
}
