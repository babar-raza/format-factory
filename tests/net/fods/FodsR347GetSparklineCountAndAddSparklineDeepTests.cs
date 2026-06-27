// Tests for FodsDocument.GetSparklineCount, AddSparkline, GetSparklineType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R347

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R347: Tests for FodsDocument.GetSparklineCount, AddSparkline, GetSparklineType deeper.
/// GetSparklineCount(): returns the number of sparklines defined in the document.
/// AddSparkline(sheetName, dataRange, targetCell, sparklineType): adds a sparkline chart.
/// GetSparklineType(index): returns the type of the sparkline at the given index.
/// Covers: GetSparklineCount no-throw; GetSparklineCount non-negative; GetSparklineCount consistent;
/// GetSparklineCount zero for new doc; GetSparklineCount after AddSparkline increases;
/// GetSparklineCount save-load;
/// AddSparkline no-throw; AddSparkline increases count; AddSparkline save-load;
/// AddSparkline multiple; AddSparkline then ExportToHtml no-throw;
/// AddSparkline then GetCellValue no-throw;
/// GetSparklineType no-throw; GetSparklineType non-null; GetSparklineType consistent;
/// GetSparklineType save-load;
/// dogfood CreateDoc→AddSparkline→GetSparklineCount→GetSparklineType→SaveToFile pipeline.
/// </summary>
public class FodsR347GetSparklineCountAndAddSparklineDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR347GetSparklineCountAndAddSparklineDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR347_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateTrendDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("MonthlyData");
        doc.SetCellValue("MonthlyData", 0, 0, "Metric");
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("MonthlyData", 0, m, $"M{m:D2}");
        doc.SetCellValue("MonthlyData", 1, 0, "Revenue");
        doc.SetCellValue("MonthlyData", 2, 0, "Units");
        doc.SetCellValue("MonthlyData", 3, 0, "Margin");
        for (int m = 1; m <= 12; m++)
        {
            doc.SetCellValue("MonthlyData", 1, m, (100000 + m * 5000).ToString());
            doc.SetCellValue("MonthlyData", 2, m, (500 + m * 20).ToString());
            doc.SetCellValue("MonthlyData", 3, m, (0.25m + m * 0.005m).ToString("F3"));
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSparklineCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSparklineCount_NoThrow()
    {
        var doc = CreateTrendDataDoc();
        var ex = Record.Exception(() => doc.GetSparklineCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSparklineCount_NonNegative()
    {
        var doc = CreateTrendDataDoc();
        Assert.True(doc.GetSparklineCount() >= 0);
    }

    [Fact]
    public void GetSparklineCount_Consistent()
    {
        var doc = CreateTrendDataDoc();
        Assert.Equal(doc.GetSparklineCount(), doc.GetSparklineCount());
    }

    [Fact]
    public void GetSparklineCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.Equal(0, doc.GetSparklineCount());
    }

    [Fact]
    public void GetSparklineCount_AfterAddSparkline_Increases()
    {
        var doc = CreateTrendDataDoc();
        var before = doc.GetSparklineCount();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "line");
        Assert.Equal(before + 1, doc.GetSparklineCount());
    }

    [Fact]
    public void GetSparklineCount_SaveLoad_Consistent()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "column");
        var before = doc.GetSparklineCount();
        var path = TempFile("sc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSparklineCount());
    }

    // -------------------------------------------------------------------------
    // AddSparkline
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSparkline_NoThrow()
    {
        var doc = CreateTrendDataDoc();
        var ex = Record.Exception(() => doc.AddSparkline("MonthlyData", "B3:M3", "N3", "line"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSparkline_Increases_Count()
    {
        var doc = CreateTrendDataDoc();
        var before = doc.GetSparklineCount();
        doc.AddSparkline("MonthlyData", "B4:M4", "N4", "winloss");
        Assert.Equal(before + 1, doc.GetSparklineCount());
    }

    [Fact]
    public void AddSparkline_SaveLoad_Persists()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "line");
        var before = doc.GetSparklineCount();
        var path = TempFile("asl_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSparklineCount());
    }

    [Fact]
    public void AddSparkline_Multiple()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "line");
        doc.AddSparkline("MonthlyData", "B3:M3", "N3", "column");
        doc.AddSparkline("MonthlyData", "B4:M4", "N4", "winloss");
        Assert.Equal(3, doc.GetSparklineCount());
    }

    [Fact]
    public void AddSparkline_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "line");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSparkline_Then_GetCellValue_NoThrow()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "column");
        var ex = Record.Exception(() => doc.GetCellValue("MonthlyData", 1, 1));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetSparklineType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSparklineType_NoThrow()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "line");
        var ex = Record.Exception(() => doc.GetSparklineType(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSparklineType_NonNull()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B3:M3", "N3", "column");
        Assert.NotNull(doc.GetSparklineType(0));
    }

    [Fact]
    public void GetSparklineType_Consistent()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B2:M2", "N2", "winloss");
        Assert.Equal(doc.GetSparklineType(0), doc.GetSparklineType(0));
    }

    [Fact]
    public void GetSparklineType_SaveLoad_Consistent()
    {
        var doc = CreateTrendDataDoc();
        doc.AddSparkline("MonthlyData", "B4:M4", "N4", "line");
        var path = TempFile("slt_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetSparklineType(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSparkline_GetSparklineCount_GetSparklineType_SaveToFile_Pipeline()
    {
        // Executive dashboard — KPI performance monitoring workbook with sparkline trend indicators
        var doc = FodsDocument.CreateEmpty();

        // ---- KPI Data sheet ----
        doc.AddSheet("KPIData");
        string[] kpis = { "Revenue_GBP", "Units_Sold", "Gross_Margin_Pct", "Customer_Acq_Cost", "NPS_Score", "Churn_Rate_Pct" };
        doc.SetCellValue("KPIData", 0, 0, "KPI");
        doc.SetCellValue("KPIData", 0, 13, "Trend");
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 0, m, $"Q{(m - 1) / 3 + 1}M{(m - 1) % 3 + 1}");

        // Revenue: increasing trend
        doc.SetCellValue("KPIData", 1, 0, kpis[0]);
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 1, m, (800000 + m * 25000).ToString());

        // Units Sold: seasonal with Q4 peak
        doc.SetCellValue("KPIData", 2, 0, kpis[1]);
        int[] units = { 1200, 1100, 1350, 1400, 1300, 1450, 1250, 1200, 1500, 1600, 1900, 2200 };
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 2, m, units[m - 1].ToString());

        // Gross Margin: stable around 38%
        doc.SetCellValue("KPIData", 3, 0, kpis[2]);
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 3, m, (0.375m + (m % 3) * 0.005m).ToString("F3"));

        // Customer Acquisition Cost: decreasing (improving)
        doc.SetCellValue("KPIData", 4, 0, kpis[3]);
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 4, m, (480 - m * 8).ToString());

        // NPS: volatile
        doc.SetCellValue("KPIData", 5, 0, kpis[4]);
        int[] nps = { 42, 45, 38, 52, 48, 55, 43, 50, 58, 52, 61, 65 };
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 5, m, nps[m - 1].ToString());

        // Churn Rate: decreasing (improving)
        doc.SetCellValue("KPIData", 6, 0, kpis[5]);
        for (int m = 1; m <= 12; m++)
            doc.SetCellValue("KPIData", 6, m, (0.038m - m * 0.001m).ToString("F3"));

        Assert.Equal(0, doc.GetSparklineCount());

        // AddSparkline — one per KPI row
        doc.AddSparkline("KPIData", "B2:M2", "N2", "line");    // Revenue
        Assert.Equal(1, doc.GetSparklineCount());

        doc.AddSparkline("KPIData", "B3:M3", "N3", "column");  // Units (seasonal)
        Assert.Equal(2, doc.GetSparklineCount());

        doc.AddSparkline("KPIData", "B4:M4", "N4", "line");    // Gross Margin
        Assert.Equal(3, doc.GetSparklineCount());

        doc.AddSparkline("KPIData", "B5:M5", "N5", "line");    // CAC
        Assert.Equal(4, doc.GetSparklineCount());

        doc.AddSparkline("KPIData", "B6:M6", "N6", "winloss"); // NPS (above/below target)
        Assert.Equal(5, doc.GetSparklineCount());

        doc.AddSparkline("KPIData", "B7:M7", "N7", "line");    // Churn
        Assert.Equal(6, doc.GetSparklineCount());

        // Consistent
        Assert.Equal(doc.GetSparklineCount(), doc.GetSparklineCount());

        // GetSparklineType
        var type0 = doc.GetSparklineType(0);
        Assert.NotNull(type0);
        Assert.Equal(type0, doc.GetSparklineType(0)); // consistent

        var type1 = doc.GetSparklineType(1);
        Assert.NotNull(type1);

        var type4 = doc.GetSparklineType(4);
        Assert.NotNull(type4);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCellValue
        Assert.NotNull(doc.GetCellValue("KPIData", 1, 1));

        // SaveToFile
        var path = TempFile("dogfood_kpi_dashboard.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetSparklineCount());
        Assert.NotNull(loaded.GetSparklineType(0));
        Assert.NotNull(loaded.GetSparklineType(5));

        // AddSparkline on loaded — bonus summary row
        loaded.AddSparkline("KPIData", "B2:B7", "B9", "column");
        Assert.Equal(7, loaded.GetSparklineCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_kpi_dashboard_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetSparklineCount());
        Assert.NotNull(loaded2.GetSparklineType(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetSparklineType(6));
        var ex3 = Record.Exception(() => loaded2.AddSparkline("KPIData", "B2:M2", "O2", "line"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
