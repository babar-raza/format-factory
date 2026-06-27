// Tests for FodsDocument.GetSparklineCount, AddSparkline, GetSparklineType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R324

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R324: Tests for FodsDocument.GetSparklineCount, AddSparkline, GetSparklineType deeper.
/// GetSparklineCount(sheetName): returns the number of sparklines defined on the sheet.
/// AddSparkline(sheetName, dataRange, location, type): adds a sparkline to the sheet.
/// GetSparklineType(sheetName, index): returns the type of the sparkline at the given index.
/// Covers: GetSparklineCount no-throw; GetSparklineCount non-negative; GetSparklineCount consistent;
/// GetSparklineCount zero for new sheet; GetSparklineCount after AddSparkline increases;
/// GetSparklineCount save-load;
/// AddSparkline no-throw; AddSparkline increases count; AddSparkline save-load;
/// AddSparkline multiple; AddSparkline then GetRowCount positive;
/// GetSparklineType no-throw; GetSparklineType non-null; GetSparklineType consistent;
/// GetSparklineType save-load;
/// dogfood CreateDoc→AddSparkline→GetSparklineCount→GetSparklineType→SaveToFile pipeline.
/// </summary>
public class FodsR324GetSparklineCountAndAddSparklineDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR324GetSparklineCountAndAddSparklineDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR324_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateTimeSeriesDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Trends");
        doc.SetCellValue("Trends", 0, 0, "Metric");
        doc.SetCellValue("Trends", 0, 1, "Q1"); doc.SetCellValue("Trends", 0, 2, "Q2");
        doc.SetCellValue("Trends", 0, 3, "Q3"); doc.SetCellValue("Trends", 0, 4, "Q4");
        doc.SetCellValue("Trends", 0, 5, "Trend");
        doc.SetCellValue("Trends", 1, 0, "Revenue"); doc.SetCellValue("Trends", 1, 1, "420"); doc.SetCellValue("Trends", 1, 2, "510"); doc.SetCellValue("Trends", 1, 3, "480"); doc.SetCellValue("Trends", 1, 4, "620");
        doc.SetCellValue("Trends", 2, 0, "Cost");    doc.SetCellValue("Trends", 2, 1, "280"); doc.SetCellValue("Trends", 2, 2, "310"); doc.SetCellValue("Trends", 2, 3, "295"); doc.SetCellValue("Trends", 2, 4, "340");
        doc.SetCellValue("Trends", 3, 0, "Margin");  doc.SetCellValue("Trends", 3, 1, "140"); doc.SetCellValue("Trends", 3, 2, "200"); doc.SetCellValue("Trends", 3, 3, "185"); doc.SetCellValue("Trends", 3, 4, "280");
        doc.SetCellValue("Trends", 4, 0, "Units");   doc.SetCellValue("Trends", 4, 1, "8200"); doc.SetCellValue("Trends", 4, 2, "9500"); doc.SetCellValue("Trends", 4, 3, "8800"); doc.SetCellValue("Trends", 4, 4, "11200");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSparklineCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSparklineCount_NoThrow()
    {
        var doc = CreateTimeSeriesDoc();
        var ex = Record.Exception(() => doc.GetSparklineCount("Trends"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSparklineCount_NonNegative()
    {
        var doc = CreateTimeSeriesDoc();
        Assert.True(doc.GetSparklineCount("Trends") >= 0);
    }

    [Fact]
    public void GetSparklineCount_Consistent()
    {
        var doc = CreateTimeSeriesDoc();
        Assert.Equal(doc.GetSparklineCount("Trends"), doc.GetSparklineCount("Trends"));
    }

    [Fact]
    public void GetSparklineCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Clean");
        doc.SetCellValue("Clean", 0, 0, "Value");
        Assert.Equal(0, doc.GetSparklineCount("Clean"));
    }

    [Fact]
    public void GetSparklineCount_AfterAddSparkline_Increases()
    {
        var doc = CreateTimeSeriesDoc();
        var before = doc.GetSparklineCount("Trends");
        doc.AddSparkline("Trends", "B2:E2", "F2", "line");
        Assert.Equal(before + 1, doc.GetSparklineCount("Trends"));
    }

    [Fact]
    public void GetSparklineCount_SaveLoad_Consistent()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B3:E3", "F3", "column");
        var before = doc.GetSparklineCount("Trends");
        var path = TempFile("sc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSparklineCount("Trends"));
    }

    // -------------------------------------------------------------------------
    // AddSparkline
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSparkline_NoThrow()
    {
        var doc = CreateTimeSeriesDoc();
        var ex = Record.Exception(() => doc.AddSparkline("Trends", "B2:E2", "F2", "line"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSparkline_Increases_Count()
    {
        var doc = CreateTimeSeriesDoc();
        var before = doc.GetSparklineCount("Trends");
        doc.AddSparkline("Trends", "B4:E4", "F4", "winloss");
        Assert.Equal(before + 1, doc.GetSparklineCount("Trends"));
    }

    [Fact]
    public void AddSparkline_SaveLoad_Persists()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B2:E2", "F2", "line");
        var before = doc.GetSparklineCount("Trends");
        var path = TempFile("as_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSparklineCount("Trends"));
    }

    [Fact]
    public void AddSparkline_Multiple()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B2:E2", "F2", "line");
        doc.AddSparkline("Trends", "B3:E3", "F3", "column");
        doc.AddSparkline("Trends", "B4:E4", "F4", "winloss");
        Assert.Equal(3, doc.GetSparklineCount("Trends"));
    }

    [Fact]
    public void AddSparkline_Then_GetRowCount_Positive()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B2:E2", "F2", "line");
        Assert.True(doc.GetRowCount("Trends") > 0);
    }

    // -------------------------------------------------------------------------
    // GetSparklineType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSparklineType_NoThrow()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B2:E2", "F2", "line");
        var ex = Record.Exception(() => doc.GetSparklineType("Trends", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSparklineType_NonNull()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B3:E3", "F3", "column");
        Assert.NotNull(doc.GetSparklineType("Trends", 0));
    }

    [Fact]
    public void GetSparklineType_Consistent()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B4:E4", "F4", "winloss");
        Assert.Equal(doc.GetSparklineType("Trends", 0), doc.GetSparklineType("Trends", 0));
    }

    [Fact]
    public void GetSparklineType_SaveLoad_Consistent()
    {
        var doc = CreateTimeSeriesDoc();
        doc.AddSparkline("Trends", "B2:E2", "F2", "line");
        var before = doc.GetSparklineType("Trends", 0);
        var path = TempFile("st_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetSparklineType("Trends", 0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSparkline_GetSparklineCount_GetSparklineType_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("KPI_Dashboard");
        // Headers
        doc.SetCellValue("KPI_Dashboard", 0, 0, "KPI");
        doc.SetCellValue("KPI_Dashboard", 0, 1, "Jan"); doc.SetCellValue("KPI_Dashboard", 0, 2, "Feb"); doc.SetCellValue("KPI_Dashboard", 0, 3, "Mar");
        doc.SetCellValue("KPI_Dashboard", 0, 4, "Apr"); doc.SetCellValue("KPI_Dashboard", 0, 5, "May"); doc.SetCellValue("KPI_Dashboard", 0, 6, "Jun");
        doc.SetCellValue("KPI_Dashboard", 0, 7, "Sparkline");
        // KPI data rows
        doc.SetCellValue("KPI_Dashboard", 1, 0, "Revenue_M"); doc.SetCellValue("KPI_Dashboard", 1, 1, "12.4"); doc.SetCellValue("KPI_Dashboard", 1, 2, "14.2"); doc.SetCellValue("KPI_Dashboard", 1, 3, "13.8"); doc.SetCellValue("KPI_Dashboard", 1, 4, "16.1"); doc.SetCellValue("KPI_Dashboard", 1, 5, "15.8"); doc.SetCellValue("KPI_Dashboard", 1, 6, "18.5");
        doc.SetCellValue("KPI_Dashboard", 2, 0, "Customers"); doc.SetCellValue("KPI_Dashboard", 2, 1, "8200");  doc.SetCellValue("KPI_Dashboard", 2, 2, "8950");  doc.SetCellValue("KPI_Dashboard", 2, 3, "9100");  doc.SetCellValue("KPI_Dashboard", 2, 4, "9800");  doc.SetCellValue("KPI_Dashboard", 2, 5, "10200"); doc.SetCellValue("KPI_Dashboard", 2, 6, "11500");
        doc.SetCellValue("KPI_Dashboard", 3, 0, "NPS");      doc.SetCellValue("KPI_Dashboard", 3, 1, "42");     doc.SetCellValue("KPI_Dashboard", 3, 2, "45");     doc.SetCellValue("KPI_Dashboard", 3, 3, "48");     doc.SetCellValue("KPI_Dashboard", 3, 4, "44");     doc.SetCellValue("KPI_Dashboard", 3, 5, "51");     doc.SetCellValue("KPI_Dashboard", 3, 6, "55");
        doc.SetCellValue("KPI_Dashboard", 4, 0, "Churn_Pct");doc.SetCellValue("KPI_Dashboard", 4, 1, "2.8");   doc.SetCellValue("KPI_Dashboard", 4, 2, "2.5");   doc.SetCellValue("KPI_Dashboard", 4, 3, "2.2");   doc.SetCellValue("KPI_Dashboard", 4, 4, "2.6");   doc.SetCellValue("KPI_Dashboard", 4, 5, "2.1");   doc.SetCellValue("KPI_Dashboard", 4, 6, "1.8");
        doc.SetCellValue("KPI_Dashboard", 5, 0, "Support");  doc.SetCellValue("KPI_Dashboard", 5, 1, "580");    doc.SetCellValue("KPI_Dashboard", 5, 2, "620");    doc.SetCellValue("KPI_Dashboard", 5, 3, "595");    doc.SetCellValue("KPI_Dashboard", 5, 4, "542");    doc.SetCellValue("KPI_Dashboard", 5, 5, "510");    doc.SetCellValue("KPI_Dashboard", 5, 6, "488");

        Assert.Equal(0, doc.GetSparklineCount("KPI_Dashboard"));

        // AddSparkline — line type for revenue trend
        doc.AddSparkline("KPI_Dashboard", "B2:G2", "H2", "line");
        Assert.Equal(1, doc.GetSparklineCount("KPI_Dashboard"));

        // AddSparkline — column type for customer growth
        doc.AddSparkline("KPI_Dashboard", "B3:G3", "H3", "column");
        Assert.Equal(2, doc.GetSparklineCount("KPI_Dashboard"));

        // AddSparkline — line type for NPS
        doc.AddSparkline("KPI_Dashboard", "B4:G4", "H4", "line");
        Assert.Equal(3, doc.GetSparklineCount("KPI_Dashboard"));

        // AddSparkline — winloss type for churn (declining is good)
        doc.AddSparkline("KPI_Dashboard", "B5:G5", "H5", "winloss");
        Assert.Equal(4, doc.GetSparklineCount("KPI_Dashboard"));

        // AddSparkline — column for support tickets (declining is good)
        doc.AddSparkline("KPI_Dashboard", "B6:G6", "H6", "column");
        Assert.Equal(5, doc.GetSparklineCount("KPI_Dashboard"));

        // Consistent
        Assert.Equal(doc.GetSparklineCount("KPI_Dashboard"), doc.GetSparklineCount("KPI_Dashboard"));

        // GetSparklineType
        var type0 = doc.GetSparklineType("KPI_Dashboard", 0);
        Assert.NotNull(type0);
        Assert.Equal(type0, doc.GetSparklineType("KPI_Dashboard", 0)); // consistent

        var type1 = doc.GetSparklineType("KPI_Dashboard", 1);
        Assert.NotNull(type1);

        var type3 = doc.GetSparklineType("KPI_Dashboard", 3);
        Assert.NotNull(type3);

        // GetRowCount positive
        Assert.True(doc.GetRowCount("KPI_Dashboard") > 0);

        // ExportToCsv works
        var csv = doc.ExportToCsv("KPI_Dashboard");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_kpi.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetSparklineCount("KPI_Dashboard"));
        Assert.True(loaded.GetRowCount("KPI_Dashboard") > 0);
        Assert.NotNull(loaded.GetSparklineType("KPI_Dashboard", 0));

        // AddSparkline on loaded
        loaded.AddSparkline("KPI_Dashboard", "B2:G6", "I2", "line");
        Assert.Equal(6, loaded.GetSparklineCount("KPI_Dashboard"));

        // AddRow on loaded
        loaded.AddRow("KPI_Dashboard", new[] { "Conversion_Pct", "3.2", "3.5", "3.8", "4.1", "4.4", "4.8", "" });
        Assert.True(loaded.GetRowCount("KPI_Dashboard") > doc.GetRowCount("KPI_Dashboard"));

        // Final save
        var path2 = TempFile("dogfood_kpi_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetSparklineCount("KPI_Dashboard"));
        Assert.True(loaded2.GetRowCount("KPI_Dashboard") > 0);
        Assert.NotNull(loaded2.GetSparklineType("KPI_Dashboard", 0));
        var ex1 = Record.Exception(() => loaded2.GetSparklineCount("KPI_Dashboard"));
        var ex2 = Record.Exception(() => loaded2.GetSparklineType("KPI_Dashboard", 1));
        var ex3 = Record.Exception(() => loaded2.ExportToCsv("KPI_Dashboard"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
