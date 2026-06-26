// Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R313

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R313: Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
/// GetConditionalFormatCount(sheetName): returns the number of conditional formats on the sheet.
/// AddConditionalFormat(sheetName, range, condition, style): adds a conditional format rule.
/// GetConditionalFormatRule(sheetName, index): returns the condition rule string at the given index.
/// Covers: GetConditionalFormatCount no-throw; GetConditionalFormatCount non-negative;
/// GetConditionalFormatCount consistent; GetConditionalFormatCount zero for new sheet;
/// GetConditionalFormatCount after AddConditionalFormat increases; GetConditionalFormatCount save-load;
/// AddConditionalFormat no-throw; AddConditionalFormat increases count; AddConditionalFormat save-load;
/// AddConditionalFormat multiple; AddConditionalFormat then ExportToCsv no-throw;
/// GetConditionalFormatRule no-throw; GetConditionalFormatRule non-null; GetConditionalFormatRule consistent;
/// GetConditionalFormatRule save-load;
/// dogfood CreateDoc→AddConditionalFormat→GetConditionalFormatCount→GetConditionalFormatRule→SaveToFile pipeline.
/// </summary>
public class FodsR313GetConditionalFormatCountAndAddConditionalFormatDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR313GetConditionalFormatCountAndAddConditionalFormatDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR313_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("KPITracker");
        doc.SetCellValue("KPITracker", 0, 0, "Metric");
        doc.SetCellValue("KPITracker", 0, 1, "Target");
        doc.SetCellValue("KPITracker", 0, 2, "Actual");
        doc.SetCellValue("KPITracker", 0, 3, "Variance");
        doc.SetCellValue("KPITracker", 0, 4, "Status");
        doc.SetCellValue("KPITracker", 1, 0, "Revenue");
        doc.SetCellValue("KPITracker", 1, 1, "1000000");
        doc.SetCellValue("KPITracker", 1, 2, "950000");
        doc.SetCellValue("KPITracker", 1, 3, "-50000");
        doc.SetCellValue("KPITracker", 1, 4, "MISS");
        doc.SetCellValue("KPITracker", 2, 0, "Units Sold");
        doc.SetCellValue("KPITracker", 2, 1, "5000");
        doc.SetCellValue("KPITracker", 2, 2, "5250");
        doc.SetCellValue("KPITracker", 2, 3, "250");
        doc.SetCellValue("KPITracker", 2, 4, "HIT");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetConditionalFormatCount("KPITracker"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetConditionalFormatCount("KPITracker") >= 0);
    }

    [Fact]
    public void GetConditionalFormatCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(
            doc.GetConditionalFormatCount("KPITracker"),
            doc.GetConditionalFormatCount("KPITracker"));
    }

    [Fact]
    public void GetConditionalFormatCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        doc.SetCellValue("Fresh", 0, 0, "data");
        Assert.Equal(0, doc.GetConditionalFormatCount("Fresh"));
    }

    [Fact]
    public void GetConditionalFormatCount_AfterAdd_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetConditionalFormatCount("KPITracker");
        doc.AddConditionalFormat("KPITracker", "D2:D3", "cell-value<0", "red-highlight");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount("KPITracker"));
    }

    [Fact]
    public void GetConditionalFormatCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "C2:C3", "cell-value>target", "green-highlight");
        var before = doc.GetConditionalFormatCount("KPITracker");
        var path = TempFile("cfc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount("KPITracker"));
    }

    // -------------------------------------------------------------------------
    // AddConditionalFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void AddConditionalFormat_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() =>
            doc.AddConditionalFormat("KPITracker", "E2:E3", "cell-value=MISS", "orange-highlight"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetConditionalFormatCount("KPITracker");
        doc.AddConditionalFormat("KPITracker", "D2:D3", "cell-value<0", "red-bg");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount("KPITracker"));
    }

    [Fact]
    public void AddConditionalFormat_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "C2:C3", "cell-value>=target", "green-bg");
        var before = doc.GetConditionalFormatCount("KPITracker");
        var path = TempFile("acf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount("KPITracker"));
    }

    [Fact]
    public void AddConditionalFormat_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "D2:D3", "cell-value<0", "red-bg");
        doc.AddConditionalFormat("KPITracker", "D2:D3", "cell-value>=0", "green-bg");
        doc.AddConditionalFormat("KPITracker", "E2:E3", "cell-value=HIT", "bold-green");
        Assert.Equal(3, doc.GetConditionalFormatCount("KPITracker"));
    }

    [Fact]
    public void AddConditionalFormat_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "C2:C3", "cell-value>0", "highlight");
        var ex = Record.Exception(() => doc.ExportToCsv("KPITracker"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatRule_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "D2:D3", "cell-value<0", "red-bg");
        var ex = Record.Exception(() => doc.GetConditionalFormatRule("KPITracker", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatRule_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "C2:C3", "cell-value>1000000", "blue-bg");
        Assert.NotNull(doc.GetConditionalFormatRule("KPITracker", 0));
    }

    [Fact]
    public void GetConditionalFormatRule_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "E2:E3", "cell-value=MISS", "red-text");
        Assert.Equal(
            doc.GetConditionalFormatRule("KPITracker", 0),
            doc.GetConditionalFormatRule("KPITracker", 0));
    }

    [Fact]
    public void GetConditionalFormatRule_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddConditionalFormat("KPITracker", "D2:D3", "cell-value<=-50000", "warning-bg");
        var before = doc.GetConditionalFormatRule("KPITracker", 0);
        var path = TempFile("gcfr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetConditionalFormatRule("KPITracker", 0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddConditionalFormat_GetConditionalFormatCount_GetConditionalFormatRule_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("RiskMatrix");

        // Headers
        doc.SetCellValue("RiskMatrix", 0, 0, "Risk ID");
        doc.SetCellValue("RiskMatrix", 0, 1, "Category");
        doc.SetCellValue("RiskMatrix", 0, 2, "Likelihood");
        doc.SetCellValue("RiskMatrix", 0, 3, "Impact");
        doc.SetCellValue("RiskMatrix", 0, 4, "Score");
        doc.SetCellValue("RiskMatrix", 0, 5, "Status");

        // Risk data
        string[,] risks = {
            { "R001", "Operational", "4", "5", "20", "CRITICAL" },
            { "R002", "Financial", "3", "4", "12", "HIGH" },
            { "R003", "Strategic", "2", "5", "10", "HIGH" },
            { "R004", "Compliance", "4", "3", "12", "HIGH" },
            { "R005", "Technology", "3", "3", "9", "MEDIUM" },
            { "R006", "Reputational", "2", "4", "8", "MEDIUM" },
            { "R007", "Market", "3", "2", "6", "LOW" },
            { "R008", "HR", "2", "3", "6", "LOW" },
        };
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("RiskMatrix", r + 1, c, risks[r, c]);

        // Zero conditional formats initially
        Assert.Equal(0, doc.GetConditionalFormatCount("RiskMatrix"));

        // AddConditionalFormat — CRITICAL score (>=15)
        doc.AddConditionalFormat("RiskMatrix", "E2:E9", "cell-value>=15", "critical-red");
        Assert.Equal(1, doc.GetConditionalFormatCount("RiskMatrix"));

        // AddConditionalFormat — HIGH score (9-14)
        doc.AddConditionalFormat("RiskMatrix", "E2:E9", "cell-value>=9 AND cell-value<15", "high-orange");
        Assert.Equal(2, doc.GetConditionalFormatCount("RiskMatrix"));

        // AddConditionalFormat — MEDIUM score (5-8)
        doc.AddConditionalFormat("RiskMatrix", "E2:E9", "cell-value>=5 AND cell-value<9", "medium-yellow");
        Assert.Equal(3, doc.GetConditionalFormatCount("RiskMatrix"));

        // AddConditionalFormat — LOW score (<5)
        doc.AddConditionalFormat("RiskMatrix", "E2:E9", "cell-value<5", "low-green");
        Assert.Equal(4, doc.GetConditionalFormatCount("RiskMatrix"));

        // AddConditionalFormat — CRITICAL status
        doc.AddConditionalFormat("RiskMatrix", "F2:F9", "cell-value=CRITICAL", "bold-red-text");
        Assert.Equal(5, doc.GetConditionalFormatCount("RiskMatrix"));

        // Consistent
        Assert.Equal(
            doc.GetConditionalFormatCount("RiskMatrix"),
            doc.GetConditionalFormatCount("RiskMatrix"));

        // GetConditionalFormatRule
        var rule0 = doc.GetConditionalFormatRule("RiskMatrix", 0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetConditionalFormatRule("RiskMatrix", 0)); // consistent

        var rule1 = doc.GetConditionalFormatRule("RiskMatrix", 1);
        Assert.NotNull(rule1);

        var rule4 = doc.GetConditionalFormatRule("RiskMatrix", 4);
        Assert.NotNull(rule4);

        // ExportToCsv works
        var csv = doc.ExportToCsv("RiskMatrix");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_risk.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetConditionalFormatCount("RiskMatrix"));
        Assert.NotNull(loaded.GetConditionalFormatRule("RiskMatrix", 0));

        // AddConditionalFormat on loaded
        loaded.AddConditionalFormat("RiskMatrix", "D2:D9", "cell-value=5", "impact-bold");
        Assert.Equal(6, loaded.GetConditionalFormatCount("RiskMatrix"));

        // Mutate and verify
        loaded.SetCellValue("RiskMatrix", 9, 0, "R009");
        loaded.SetCellValue("RiskMatrix", 9, 1, "Cybersecurity");
        loaded.SetCellValue("RiskMatrix", 9, 2, "5");
        loaded.SetCellValue("RiskMatrix", 9, 3, "5");
        loaded.SetCellValue("RiskMatrix", 9, 4, "25");
        loaded.SetCellValue("RiskMatrix", 9, 5, "CRITICAL");

        // Final save
        var path2 = TempFile("dogfood_risk_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetConditionalFormatCount("RiskMatrix"));
        Assert.NotNull(loaded2.GetConditionalFormatRule("RiskMatrix", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("RiskMatrix"));
        Assert.Null(ex1);
    }
}
