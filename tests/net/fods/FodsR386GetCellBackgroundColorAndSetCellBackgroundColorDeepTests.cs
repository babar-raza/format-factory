// Tests for FodsDocument.GetCellBackgroundColor, SetCellBackgroundColor deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R386

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R386: Tests for FodsDocument.GetCellBackgroundColor, SetCellBackgroundColor deeper.
/// GetCellBackgroundColor(sheetName, row, col): returns the background fill colour of the cell.
/// SetCellBackgroundColor(sheetName, row, col, color): sets the cell background fill colour.
/// Covers: GetCellBackgroundColor no-throw; GetCellBackgroundColor non-null;
/// GetCellBackgroundColor consistent; GetCellBackgroundColor save-load;
/// SetCellBackgroundColor no-throw; SetCellBackgroundColor then GetCellBackgroundColor updated;
/// SetCellBackgroundColor value unchanged; SetCellBackgroundColor then GetSheetCount unchanged;
/// SetCellBackgroundColor then ExportToHtml no-throw; SetCellBackgroundColor override;
/// SetCellBackgroundColor save-load; SetCellBackgroundColor then GetRowCount unchanged;
/// dogfood CreateDoc→SetCellBackgroundColor→GetCellBackgroundColor→SaveToFile pipeline.
/// </summary>
public class FodsR386GetCellBackgroundColorAndSetCellBackgroundColorDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR386GetCellBackgroundColorAndSetCellBackgroundColorDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR386_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreatePlainDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Dashboard");
        doc.SetCellValue("Dashboard", 0, 0, "KPI");
        doc.SetCellValue("Dashboard", 0, 1, "Target");
        doc.SetCellValue("Dashboard", 0, 2, "Actual");
        doc.SetCellValue("Dashboard", 0, 3, "Status");
        doc.SetCellValue("Dashboard", 1, 0, "SLA Compliance");
        doc.SetCellValue("Dashboard", 1, 1, "98%");
        doc.SetCellValue("Dashboard", 1, 2, "96.2%");
        doc.SetCellValue("Dashboard", 1, 3, "AMBER");
        doc.SetCellValue("Dashboard", 2, 0, "MTTR");
        doc.SetCellValue("Dashboard", 2, 1, "4 hrs");
        doc.SetCellValue("Dashboard", 2, 2, "3.1 hrs");
        doc.SetCellValue("Dashboard", 2, 3, "GREEN");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellBackgroundColor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBackgroundColor_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetCellBackgroundColor("Dashboard", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellBackgroundColor_NonNull()
    {
        var doc = CreatePlainDoc();
        Assert.NotNull(doc.GetCellBackgroundColor("Dashboard", 0, 0));
    }

    [Fact]
    public void GetCellBackgroundColor_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetCellBackgroundColor("Dashboard", 1, 3),
                     doc.GetCellBackgroundColor("Dashboard", 1, 3));
    }

    [Fact]
    public void GetCellBackgroundColor_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.SetCellBackgroundColor("Dashboard", 1, 3, "#FFCC00");
        var before = doc.GetCellBackgroundColor("Dashboard", 1, 3);
        var path = TempFile("gbc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellBackgroundColor("Dashboard", 1, 3));
    }

    // -------------------------------------------------------------------------
    // SetCellBackgroundColor
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBackgroundColor_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.SetCellBackgroundColor("Dashboard", 0, 3, "#4CAF50"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBackgroundColor_Then_GetCellBackgroundColor_Updated()
    {
        var doc = CreatePlainDoc();
        doc.SetCellBackgroundColor("Dashboard", 2, 3, "#4CAF50");
        Assert.Equal("#4CAF50", doc.GetCellBackgroundColor("Dashboard", 2, 3));
    }

    [Fact]
    public void SetCellBackgroundColor_ValueUnchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCellValue("Dashboard", 1, 3);
        doc.SetCellBackgroundColor("Dashboard", 1, 3, "#FFCC00");
        Assert.Equal(before, doc.GetCellValue("Dashboard", 1, 3));
    }

    [Fact]
    public void SetCellBackgroundColor_Then_GetSheetCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetSheetCount();
        doc.SetCellBackgroundColor("Dashboard", 0, 0, "#003366");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetCellBackgroundColor_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetCellBackgroundColor("Dashboard", 1, 3, "#FFCC00");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBackgroundColor_Override()
    {
        var doc = CreatePlainDoc();
        doc.SetCellBackgroundColor("Dashboard", 0, 0, "#FF0000");
        doc.SetCellBackgroundColor("Dashboard", 0, 0, "#0000FF");
        Assert.Equal("#0000FF", doc.GetCellBackgroundColor("Dashboard", 0, 0));
    }

    [Fact]
    public void SetCellBackgroundColor_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.SetCellBackgroundColor("Dashboard", 1, 3, "#FF6600");
        var path = TempFile("sbc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("#FF6600", loaded.GetCellBackgroundColor("Dashboard", 1, 3));
    }

    [Fact]
    public void SetCellBackgroundColor_Then_GetRowCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetRowCount("Dashboard");
        doc.SetCellBackgroundColor("Dashboard", 0, 0, "#FFFFFF");
        Assert.Equal(before, doc.GetRowCount("Dashboard"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellBackgroundColor_SetCellBackgroundColor_SaveToFile_Pipeline()
    {
        // Operational — NHS England NHS 111 Service Performance Dashboard
        // Background-colour heat map for call handling metrics: PASS/FAIL thresholds
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("NHS 111 Performance");
        doc.AddSheet("IUC Metrics");

        // Sheet 1: NHS 111 Call Handling KPIs
        doc.SetCellValue("NHS 111 Performance", 0, 0, "Metric");
        doc.SetCellValue("NHS 111 Performance", 0, 1, "CCG Standard");
        doc.SetCellValue("NHS 111 Performance", 0, 2, "Apr-24");
        doc.SetCellValue("NHS 111 Performance", 0, 3, "May-24");
        doc.SetCellValue("NHS 111 Performance", 0, 4, "Jun-24");
        doc.SetCellValue("NHS 111 Performance", 0, 5, "Trend");

        // RAG header: dark blue
        for (int j = 0; j < 6; j++)
            doc.SetCellBackgroundColor("NHS 111 Performance", 0, j, "#003087");

        string[,] kpiData = {
            { "Calls Answered <60 Secs", "≥95%", "92.1%", "94.8%", "96.3%", "↑" },
            { "Abandoned Call Rate", "<5%", "6.2%", "5.1%", "4.3%", "↓" },
            { "Clinical Callback <60 Mins", "≥95%", "97.1%", "97.8%", "98.2%", "↑" },
            { "Ambulance Dispatch (Cat 3)", "<5%", "4.8%", "4.5%", "4.1%", "↓" },
            { "Call Back Within 60 Secs", "≥95%", "89.4%", "91.2%", "95.4%", "↑" },
            { "DoS Compliance Rate", "≥98%", "97.2%", "97.9%", "98.4%", "↑" },
            { "Average Handling Time (secs)", "<480", "512", "498", "471", "↓" }
        };

        // Colour coding for monthly values: #C8E6C9 (green) / #FFF9C4 (amber) / #FFCDD2 (red)
        // Simple rule: for percentage metrics — met/not met; for AHT — under/over
        bool[,] metTarget = {
            { false, false, true },   // Calls <60s
            { false, false, true },   // Abandoned rate
            { true, true, true },     // Clinical callback
            { true, true, true },     // Ambulance dispatch
            { false, false, true },   // Call back
            { false, false, true },   // DoS compliance
            { false, false, true }    // AHT
        };

        for (int i = 0; i < kpiData.GetLength(0); i++)
        {
            for (int j = 0; j < kpiData.GetLength(1); j++)
                doc.SetCellValue("NHS 111 Performance", i + 1, j, kpiData[i, j]);

            // Colour monthly columns (cols 2, 3, 4)
            for (int m = 0; m < 3; m++)
            {
                string bg = metTarget[i, m] ? "#C8E6C9" : "#FFCDD2";
                doc.SetCellBackgroundColor("NHS 111 Performance", i + 1, m + 2, bg);
            }
        }

        // Verify specific cells
        Assert.Equal("#FFCDD2", doc.GetCellBackgroundColor("NHS 111 Performance", 1, 2)); // Apr-24 failed
        Assert.Equal("#C8E6C9", doc.GetCellBackgroundColor("NHS 111 Performance", 1, 4)); // Jun-24 met
        Assert.Equal("#C8E6C9", doc.GetCellBackgroundColor("NHS 111 Performance", 3, 2)); // Clinical callback met
        Assert.Equal("#003087", doc.GetCellBackgroundColor("NHS 111 Performance", 0, 0)); // Header

        // Sheet 2: IUC Metrics
        doc.SetCellValue("IUC Metrics", 0, 0, "IUC Metric");
        doc.SetCellValue("IUC Metrics", 0, 1, "Standard");
        doc.SetCellValue("IUC Metrics", 0, 2, "Q1 2024/25");
        doc.SetCellValue("IUC Metrics", 0, 3, "Q2 2024/25");

        for (int j = 0; j < 4; j++)
            doc.SetCellBackgroundColor("IUC Metrics", 0, j, "#003087");

        string[,] iucData = {
            { "GP OOH — Definitive Clin Assessment <1hr", "≥85%", "87.2%", "89.1%" },
            { "UTC — 4hr Waiting Standard", "≥95%", "94.3%", "95.8%" },
            { "ED — 12hr Decision to Admit Breaches", "<1%", "0.8%", "0.6%" }
        };
        bool[,] iucMet = { { true, true }, { false, true }, { true, true } };

        for (int i = 0; i < iucData.GetLength(0); i++)
        {
            for (int j = 0; j < iucData.GetLength(1); j++)
                doc.SetCellValue("IUC Metrics", i + 1, j, iucData[i, j]);
            for (int q = 0; q < 2; q++)
            {
                string bg = iucMet[i, q] ? "#C8E6C9" : "#FFCDD2";
                doc.SetCellBackgroundColor("IUC Metrics", i + 1, q + 2, bg);
            }
        }

        Assert.Equal(2, doc.GetSheetCount());
        Assert.Equal("#FFCDD2", doc.GetCellBackgroundColor("IUC Metrics", 2, 2)); // UTC Q1 failed
        Assert.Equal("#C8E6C9", doc.GetCellBackgroundColor("IUC Metrics", 2, 3)); // UTC Q2 met

        // Cell values unchanged
        Assert.Equal("NHS 111 Performance", doc.GetSheetNames()[0]);
        Assert.Equal("92.1%", doc.GetCellValue("NHS 111 Performance", 1, 2));

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("dogfood_nhs111_dashboard.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify colours
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal("#FFCDD2", loaded.GetCellBackgroundColor("NHS 111 Performance", 1, 2));
        Assert.Equal("#C8E6C9", loaded.GetCellBackgroundColor("NHS 111 Performance", 1, 4));
        Assert.Equal("#003087", loaded.GetCellBackgroundColor("NHS 111 Performance", 0, 0));
        Assert.Equal(2, loaded.GetSheetCount());

        // Override: add provisional Jul-24 data
        loaded.AddColumn("NHS 111 Performance", "Jul-24 (P)");
        loaded.SetCellValue("NHS 111 Performance", 0, 6, "Jul-24 (P)");
        loaded.SetCellBackgroundColor("NHS 111 Performance", 0, 6, "#003087");
        // Mark all as provisional (amber background)
        for (int i = 1; i <= kpiData.GetLength(0); i++)
        {
            loaded.SetCellValue("NHS 111 Performance", i, 6, "Pending");
            loaded.SetCellBackgroundColor("NHS 111 Performance", i, 6, "#FFF9C4");
        }
        Assert.Equal("#FFF9C4", loaded.GetCellBackgroundColor("NHS 111 Performance", 1, 6));

        // Final save
        var path2 = TempFile("dogfood_nhs111_dashboard_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var v2 = FodsDocument.LoadFile(path2);
        Assert.Equal("#FFF9C4", v2.GetCellBackgroundColor("NHS 111 Performance", 1, 6));

        var ex1 = Record.Exception(() => v2.ExportToHtml());
        var ex2 = Record.Exception(() => v2.SetCellBackgroundColor("NHS 111 Performance", 0, 0, "#000000"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
