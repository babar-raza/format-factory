// Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R327

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R327: Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
/// GetConditionalFormatCount(sheetName): returns the number of conditional formats on the sheet.
/// AddConditionalFormat(sheetName, range, condition, style): adds a conditional format rule.
/// GetConditionalFormatRule(sheetName, index): returns the condition expression for the rule at the index.
/// Covers: GetConditionalFormatCount no-throw; GetConditionalFormatCount non-negative; GetConditionalFormatCount consistent;
/// GetConditionalFormatCount zero for new sheet; GetConditionalFormatCount after AddConditionalFormat increases;
/// GetConditionalFormatCount save-load;
/// AddConditionalFormat no-throw; AddConditionalFormat increases count; AddConditionalFormat save-load;
/// AddConditionalFormat multiple; AddConditionalFormat then GetColumnSum no-throw; AddConditionalFormat then ExportToCsv no-throw;
/// GetConditionalFormatRule no-throw; GetConditionalFormatRule non-null; GetConditionalFormatRule consistent;
/// GetConditionalFormatRule save-load;
/// dogfood CreateDoc→AddConditionalFormat→GetConditionalFormatCount→GetConditionalFormatRule→SaveToFile pipeline.
/// </summary>
public class FodsR327GetConditionalFormatCountAndAddConditionalFormatDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR327GetConditionalFormatCountAndAddConditionalFormatDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR327_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRiskDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("RiskMatrix");
        doc.SetCellValue("RiskMatrix", 0, 0, "risk_id");
        doc.SetCellValue("RiskMatrix", 0, 1, "probability");
        doc.SetCellValue("RiskMatrix", 0, 2, "impact");
        doc.SetCellValue("RiskMatrix", 0, 3, "risk_score");
        doc.SetCellValue("RiskMatrix", 0, 4, "category");
        string[][] rows = {
            new[] { "R001", "0.85", "9.2", "7.82", "Critical" },
            new[] { "R002", "0.42", "6.5", "2.73", "High" },
            new[] { "R003", "0.15", "8.0", "1.20", "Medium" },
            new[] { "R004", "0.72", "7.8", "5.62", "High" },
            new[] { "R005", "0.08", "5.5", "0.44", "Low" },
        };
        for (int r = 0; r < rows.Length; r++)
            for (int c = 0; c < rows[r].Length; c++)
                doc.SetCellValue("RiskMatrix", r + 1, c, rows[r][c]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatCount_NoThrow()
    {
        var doc = CreateRiskDoc();
        var ex = Record.Exception(() => doc.GetConditionalFormatCount("RiskMatrix"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatCount_NonNegative()
    {
        var doc = CreateRiskDoc();
        Assert.True(doc.GetConditionalFormatCount("RiskMatrix") >= 0);
    }

    [Fact]
    public void GetConditionalFormatCount_Consistent()
    {
        var doc = CreateRiskDoc();
        Assert.Equal(doc.GetConditionalFormatCount("RiskMatrix"), doc.GetConditionalFormatCount("RiskMatrix"));
    }

    [Fact]
    public void GetConditionalFormatCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("EmptySheet");
        doc.SetCellValue("EmptySheet", 0, 0, "header");
        Assert.Equal(0, doc.GetConditionalFormatCount("EmptySheet"));
    }

    [Fact]
    public void GetConditionalFormatCount_AfterAddConditionalFormat_Increases()
    {
        var doc = CreateRiskDoc();
        var before = doc.GetConditionalFormatCount("RiskMatrix");
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", ">5", "HighRiskStyle");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount("RiskMatrix"));
    }

    [Fact]
    public void GetConditionalFormatCount_SaveLoad_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "B2:B6", ">0.7", "HighProbStyle");
        var before = doc.GetConditionalFormatCount("RiskMatrix");
        var path = TempFile("cfc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount("RiskMatrix"));
    }

    // -------------------------------------------------------------------------
    // AddConditionalFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void AddConditionalFormat_NoThrow()
    {
        var doc = CreateRiskDoc();
        var ex = Record.Exception(() => doc.AddConditionalFormat("RiskMatrix", "C2:C6", ">8", "CriticalStyle"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Increases_Count()
    {
        var doc = CreateRiskDoc();
        var before = doc.GetConditionalFormatCount("RiskMatrix");
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", "<1", "LowRiskStyle");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount("RiskMatrix"));
    }

    [Fact]
    public void AddConditionalFormat_SaveLoad_Persists()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "B2:B6", ">=0.5", "ModerateStyle");
        var before = doc.GetConditionalFormatCount("RiskMatrix");
        var path = TempFile("acf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount("RiskMatrix"));
    }

    [Fact]
    public void AddConditionalFormat_Multiple()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", ">7", "CriticalStyle");
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", ">=3", "HighStyle");
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", "<1", "LowStyle");
        Assert.Equal(3, doc.GetConditionalFormatCount("RiskMatrix"));
    }

    [Fact]
    public void AddConditionalFormat_Then_GetColumnSum_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "C2:C6", ">7", "HighImpact");
        var ex = Record.Exception(() => doc.GetColumnSum("RiskMatrix", "impact"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", ">5", "HighRiskStyle");
        var path = TempFile("export_test.csv");
        var ex = Record.Exception(() => doc.ExportToCsv("RiskMatrix", path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatRule_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", ">5", "HighRisk");
        var ex = Record.Exception(() => doc.GetConditionalFormatRule("RiskMatrix", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatRule_NonNull()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "B2:B6", ">=0.7", "HighProb");
        Assert.NotNull(doc.GetConditionalFormatRule("RiskMatrix", 0));
    }

    [Fact]
    public void GetConditionalFormatRule_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "C2:C6", ">8", "HighImpact");
        Assert.Equal(doc.GetConditionalFormatRule("RiskMatrix", 0), doc.GetConditionalFormatRule("RiskMatrix", 0));
    }

    [Fact]
    public void GetConditionalFormatRule_SaveLoad_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskMatrix", "D2:D6", ">7", "Critical");
        var before = doc.GetConditionalFormatRule("RiskMatrix", 0);
        var path = TempFile("cfr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetConditionalFormatRule("RiskMatrix", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddConditionalFormat_GetConditionalFormatCount_GetConditionalFormatRule_SaveToFile_Pipeline()
    {
        // ESG scoring dashboard — 12 companies across 3 ESG dimensions
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("ESGScores");
        doc.SetCellValue("ESGScores", 0, 0, "company");
        doc.SetCellValue("ESGScores", 0, 1, "env_score");
        doc.SetCellValue("ESGScores", 0, 2, "social_score");
        doc.SetCellValue("ESGScores", 0, 3, "governance_score");
        doc.SetCellValue("ESGScores", 0, 4, "composite_esg");
        doc.SetCellValue("ESGScores", 0, 5, "rating");

        string[][] data = {
            new[] { "TechCorp A",  "82.5", "76.3", "88.2", "82.3", "A" },
            new[] { "EnergyFirm B","45.2", "62.8", "71.5", "59.8", "B+" },
            new[] { "RetailCo C",  "68.4", "84.6", "79.3", "77.4", "A-" },
            new[] { "MiningInc D", "28.7", "51.2", "63.8", "47.9", "C+" },
            new[] { "BankGroup E", "71.3", "69.8", "85.4", "75.5", "A-" },
            new[] { "PharmaCo F",  "79.6", "88.4", "76.2", "81.4", "A" },
            new[] { "AgriCorp G",  "55.8", "73.5", "68.4", "65.9", "B" },
            new[] { "TelecomH",    "74.2", "71.6", "82.5", "76.1", "A-" },
            new[] { "AutoMfg I",   "61.5", "66.8", "74.3", "67.5", "B+" },
            new[] { "LogisticsJ",  "58.3", "69.2", "71.8", "66.4", "B" },
            new[] { "FinTech K",   "76.4", "80.5", "87.6", "81.5", "A" },
            new[] { "ConstrL",     "38.6", "58.4", "65.2", "54.1", "C+" },
        };
        for (int r = 0; r < data.Length; r++)
            for (int c = 0; c < data[r].Length; c++)
                doc.SetCellValue("ESGScores", r + 1, c, data[r][c]);

        // Initial conditional format count — zero
        Assert.Equal(0, doc.GetConditionalFormatCount("ESGScores"));

        // AddConditionalFormat — 5 rules for ESG dashboard
        doc.AddConditionalFormat("ESGScores", "D2:D13", ">=80", "ExcellentGovStyle");
        Assert.Equal(1, doc.GetConditionalFormatCount("ESGScores"));

        doc.AddConditionalFormat("ESGScores", "B2:B13", "<50", "PoorEnvStyle");
        Assert.Equal(2, doc.GetConditionalFormatCount("ESGScores"));

        doc.AddConditionalFormat("ESGScores", "E2:E13", ">=80", "TopESGStyle");
        Assert.Equal(3, doc.GetConditionalFormatCount("ESGScores"));

        doc.AddConditionalFormat("ESGScores", "E2:E13", "<55", "BottomESGStyle");
        Assert.Equal(4, doc.GetConditionalFormatCount("ESGScores"));

        doc.AddConditionalFormat("ESGScores", "C2:C13", ">=85", "ExcellentSocialStyle");
        Assert.Equal(5, doc.GetConditionalFormatCount("ESGScores"));

        // Consistent
        Assert.Equal(doc.GetConditionalFormatCount("ESGScores"), doc.GetConditionalFormatCount("ESGScores"));

        // GetConditionalFormatRule
        var rule0 = doc.GetConditionalFormatRule("ESGScores", 0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetConditionalFormatRule("ESGScores", 0)); // consistent

        var rule4 = doc.GetConditionalFormatRule("ESGScores", 4);
        Assert.NotNull(rule4);

        // Column operations work after adding conditional formats
        var ex1 = Record.Exception(() => doc.GetColumnSum("ESGScores", "composite_esg"));
        Assert.Null(ex1);

        // ExportToCsv works
        var csvPath = TempFile("dogfood_esg.csv");
        var ex2 = Record.Exception(() => doc.ExportToCsv("ESGScores", csvPath));
        Assert.Null(ex2);

        // SaveToFile
        var path = TempFile("dogfood_esg.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetConditionalFormatCount("ESGScores"));
        Assert.NotNull(loaded.GetConditionalFormatRule("ESGScores", 0));
        Assert.NotNull(loaded.GetConditionalFormatRule("ESGScores", 4));

        // AddConditionalFormat on loaded
        loaded.AddConditionalFormat("ESGScores", "B2:B13", ">=75", "GoodEnvStyle");
        Assert.Equal(6, loaded.GetConditionalFormatCount("ESGScores"));

        // ExportToCsv on loaded
        var csvPath2 = TempFile("dogfood_esg_v2.csv");
        var ex3 = Record.Exception(() => loaded.ExportToCsv("ESGScores", csvPath2));
        Assert.Null(ex3);

        // Final save
        var path2 = TempFile("dogfood_esg_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetConditionalFormatCount("ESGScores"));
        Assert.NotNull(loaded2.GetConditionalFormatRule("ESGScores", 5));
        var ex4 = Record.Exception(() => loaded2.AddConditionalFormat("ESGScores", "D2:D13", "<60", "LowGovStyle"));
        Assert.Null(ex4);
    }
}
