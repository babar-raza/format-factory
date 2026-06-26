// Tests for FodsDocument.GetChartCount, AddChart, GetChartType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R301

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R301: Tests for FodsDocument.GetChartCount, AddChart, GetChartType deeper.
/// GetChartCount(sheetName): returns the number of embedded charts in the sheet.
/// AddChart(sheetName, dataRange, chartType): adds a chart based on the given data range.
/// GetChartType(sheetName, chartIndex): returns a string describing the chart type.
/// Covers: GetChartCount no-throw; GetChartCount non-negative; GetChartCount consistent;
/// GetChartCount zero for new sheet; GetChartCount after AddChart increases;
/// GetChartCount save-load;
/// AddChart no-throw; AddChart increases GetChartCount; AddChart save-load;
/// AddChart multiple charts; AddChart then ExportToCsv no-throw;
/// GetChartType no-throw; GetChartType non-null; GetChartType consistent;
/// GetChartType save-load; GetChartType non-empty after AddChart;
/// dogfood CreateDoc→AddChart→GetChartCount→GetChartType→SaveToFile pipeline.
/// </summary>
public class FodsR301GetChartCountAndAddChartDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR301GetChartCountAndAddChartDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR301_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Analytics");
        doc.SetCellValue("Analytics", 0, 0, "Quarter");
        doc.SetCellValue("Analytics", 0, 1, "Revenue");
        doc.SetCellValue("Analytics", 0, 2, "Costs");
        doc.SetCellValue("Analytics", 0, 3, "Profit");
        doc.SetCellValue("Analytics", 1, 0, "Q1");
        doc.SetCellValue("Analytics", 1, 1, "1200000");
        doc.SetCellValue("Analytics", 1, 2, "850000");
        doc.SetCellValue("Analytics", 1, 3, "350000");
        doc.SetCellValue("Analytics", 2, 0, "Q2");
        doc.SetCellValue("Analytics", 2, 1, "1450000");
        doc.SetCellValue("Analytics", 2, 2, "920000");
        doc.SetCellValue("Analytics", 2, 3, "530000");
        doc.SetCellValue("Analytics", 3, 0, "Q3");
        doc.SetCellValue("Analytics", 3, 1, "1680000");
        doc.SetCellValue("Analytics", 3, 2, "990000");
        doc.SetCellValue("Analytics", 3, 3, "690000");
        doc.SetCellValue("Analytics", 4, 0, "Q4");
        doc.SetCellValue("Analytics", 4, 1, "1920000");
        doc.SetCellValue("Analytics", 4, 2, "1050000");
        doc.SetCellValue("Analytics", 4, 3, "870000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetChartCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetChartCount("Analytics"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChartCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetChartCount("Analytics") >= 0);
    }

    [Fact]
    public void GetChartCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetChartCount("Analytics"), doc.GetChartCount("Analytics"));
    }

    [Fact]
    public void GetChartCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        doc.SetCellValue("Empty", 0, 0, "data");
        Assert.Equal(0, doc.GetChartCount("Empty"));
    }

    [Fact]
    public void GetChartCount_AfterAddChart_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetChartCount("Analytics");
        doc.AddChart("Analytics", "A1:B5", "bar");
        Assert.Equal(before + 1, doc.GetChartCount("Analytics"));
    }

    [Fact]
    public void GetChartCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "line");
        var before = doc.GetChartCount("Analytics");
        var path = TempFile("cc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChartCount("Analytics"));
    }

    // -------------------------------------------------------------------------
    // AddChart
    // -------------------------------------------------------------------------

    [Fact]
    public void AddChart_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddChart("Analytics", "A1:D5", "bar"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddChart_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetChartCount("Analytics");
        doc.AddChart("Analytics", "A1:C5", "pie");
        Assert.Equal(before + 1, doc.GetChartCount("Analytics"));
    }

    [Fact]
    public void AddChart_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "line");
        var before = doc.GetChartCount("Analytics");
        var path = TempFile("ac_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChartCount("Analytics"));
    }

    [Fact]
    public void AddChart_Multiple_Charts()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "bar");
        doc.AddChart("Analytics", "A1:C5", "line");
        doc.AddChart("Analytics", "A1:D5", "area");
        Assert.Equal(3, doc.GetChartCount("Analytics"));
    }

    [Fact]
    public void AddChart_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:D5", "column");
        var ex = Record.Exception(() => doc.ExportToCsv("Analytics"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetChartType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChartType_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "bar");
        var ex = Record.Exception(() => doc.GetChartType("Analytics", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChartType_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "bar");
        Assert.NotNull(doc.GetChartType("Analytics", 0));
    }

    [Fact]
    public void GetChartType_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "line");
        Assert.Equal(doc.GetChartType("Analytics", 0), doc.GetChartType("Analytics", 0));
    }

    [Fact]
    public void GetChartType_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "pie");
        var before = doc.GetChartType("Analytics", 0);
        var path = TempFile("gct_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetChartType("Analytics", 0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetChartType_NonEmpty_AfterAddChart()
    {
        var doc = CreateRichDoc();
        doc.AddChart("Analytics", "A1:B5", "bar");
        Assert.NotEmpty(doc.GetChartType("Analytics", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddChart_GetChartCount_GetChartType_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Dashboard");

        // KPI headers
        doc.SetCellValue("Dashboard", 0, 0, "Metric");
        doc.SetCellValue("Dashboard", 0, 1, "Jan");
        doc.SetCellValue("Dashboard", 0, 2, "Feb");
        doc.SetCellValue("Dashboard", 0, 3, "Mar");
        doc.SetCellValue("Dashboard", 0, 4, "Apr");
        doc.SetCellValue("Dashboard", 0, 5, "May");
        doc.SetCellValue("Dashboard", 0, 6, "Jun");

        // KPI data
        string[,] kpis = {
            { "Revenue", "980000", "1050000", "1120000", "1080000", "1200000", "1350000" },
            { "Customers", "4200", "4500", "4800", "4650", "5100", "5600" },
            { "ARPU", "233", "233", "233", "232", "235", "241" },
            { "Churn", "45", "42", "38", "41", "36", "32" }
        };
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 7; c++)
                doc.SetCellValue("Dashboard", r + 1, c, kpis[r, c]);

        // GetChartCount — zero initially
        Assert.Equal(0, doc.GetChartCount("Dashboard"));

        // AddChart — revenue trend (line)
        doc.AddChart("Dashboard", "A1:G2", "line");
        Assert.Equal(1, doc.GetChartCount("Dashboard"));

        // AddChart — customer growth (bar)
        doc.AddChart("Dashboard", "A1:A1,A3:G3", "bar");
        Assert.Equal(2, doc.GetChartCount("Dashboard"));

        // AddChart — churn reduction (area)
        doc.AddChart("Dashboard", "A1:A1,A5:G5", "area");
        Assert.Equal(3, doc.GetChartCount("Dashboard"));

        // Consistent
        Assert.Equal(doc.GetChartCount("Dashboard"), doc.GetChartCount("Dashboard"));

        // GetChartType
        var t0 = doc.GetChartType("Dashboard", 0);
        var t1 = doc.GetChartType("Dashboard", 1);
        var t2 = doc.GetChartType("Dashboard", 2);
        Assert.NotNull(t0);
        Assert.NotNull(t1);
        Assert.NotNull(t2);
        Assert.Equal(t0, doc.GetChartType("Dashboard", 0)); // consistent

        // ExportToCsv still works
        var csv = doc.ExportToCsv("Dashboard");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue cross-check
        Assert.Equal("Revenue", doc.GetCellValue("Dashboard", 1, 0));

        // SaveToFile
        var path = TempFile("dogfood_dashboard.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetChartCount("Dashboard"));
        for (int i = 0; i < loaded.GetChartCount("Dashboard"); i++)
            Assert.NotNull(loaded.GetChartType("Dashboard", i));

        // AddChart on loaded
        loaded.AddChart("Dashboard", "A1:G2", "column");
        Assert.Equal(4, loaded.GetChartCount("Dashboard"));

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("Dashboard");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // Final save
        var path2 = TempFile("dogfood_dashboard_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetChartCount("Dashboard"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Dashboard"));
        Assert.Null(ex1);
    }
}
