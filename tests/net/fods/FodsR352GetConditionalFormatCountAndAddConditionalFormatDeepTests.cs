// Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R352

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R352: Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
/// GetConditionalFormatCount(): returns the number of conditional formatting rules in the workbook.
/// AddConditionalFormat(sheetName, rangeAddress, condition, styleClass): adds a conditional format rule.
/// GetConditionalFormatRule(index): returns the condition expression string for the rule at the given index.
/// Covers: GetConditionalFormatCount no-throw; GetConditionalFormatCount non-negative;
/// GetConditionalFormatCount consistent; GetConditionalFormatCount zero for new workbook;
/// GetConditionalFormatCount after AddConditionalFormat increases; GetConditionalFormatCount save-load;
/// AddConditionalFormat no-throw; AddConditionalFormat increases count; AddConditionalFormat save-load;
/// AddConditionalFormat multiple; AddConditionalFormat then ExportToCsv no-throw;
/// AddConditionalFormat then GetCellValue no-throw;
/// GetConditionalFormatRule no-throw; GetConditionalFormatRule non-null; GetConditionalFormatRule consistent;
/// GetConditionalFormatRule save-load;
/// dogfood CreateDoc→AddConditionalFormat→GetConditionalFormatCount→GetConditionalFormatRule pipeline.
/// </summary>
public class FodsR352GetConditionalFormatCountAndAddConditionalFormatDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR352GetConditionalFormatCountAndAddConditionalFormatDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR352_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRiskWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("RiskRegister");
        doc.SetCellValue("RiskRegister", 0, 0, "Risk_ID");
        doc.SetCellValue("RiskRegister", 0, 1, "Category");
        doc.SetCellValue("RiskRegister", 0, 2, "Likelihood");
        doc.SetCellValue("RiskRegister", 0, 3, "Impact");
        doc.SetCellValue("RiskRegister", 0, 4, "Risk_Score");
        string[] categories = { "Operational", "Financial", "Strategic", "Compliance", "Reputational" };
        var rng = new Random(20240501);
        for (int i = 1; i <= 12; i++)
        {
            int likelihood = rng.Next(1, 6);
            int impact = rng.Next(1, 6);
            doc.SetCellValue("RiskRegister", i, 0, $"R{i:D3}");
            doc.SetCellValue("RiskRegister", i, 1, categories[(i - 1) % 5]);
            doc.SetCellValue("RiskRegister", i, 2, likelihood.ToString());
            doc.SetCellValue("RiskRegister", i, 3, impact.ToString());
            doc.SetCellValue("RiskRegister", i, 4, (likelihood * impact).ToString());
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatCount_NoThrow()
    {
        var doc = CreateRiskWorkbook();
        var ex = Record.Exception(() => doc.GetConditionalFormatCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatCount_NonNegative()
    {
        var doc = CreateRiskWorkbook();
        Assert.True(doc.GetConditionalFormatCount() >= 0);
    }

    [Fact]
    public void GetConditionalFormatCount_Consistent()
    {
        var doc = CreateRiskWorkbook();
        Assert.Equal(doc.GetConditionalFormatCount(), doc.GetConditionalFormatCount());
    }

    [Fact]
    public void GetConditionalFormatCount_Zero_ForNewWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        Assert.Equal(0, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void GetConditionalFormatCount_AfterAdd_Increases()
    {
        var doc = CreateRiskWorkbook();
        var before = doc.GetConditionalFormatCount();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">15", "HighRisk");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void GetConditionalFormatCount_SaveLoad_Consistent()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "C2:C13", ">3", "HighLikelihood");
        var before = doc.GetConditionalFormatCount();
        var path = TempFile("cfc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount());
    }

    // -------------------------------------------------------------------------
    // AddConditionalFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void AddConditionalFormat_NoThrow()
    {
        var doc = CreateRiskWorkbook();
        var ex = Record.Exception(() => doc.AddConditionalFormat("RiskRegister", "D2:D13", ">4", "HighImpact"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Increases_Count()
    {
        var doc = CreateRiskWorkbook();
        var before = doc.GetConditionalFormatCount();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">=20", "CriticalRisk");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void AddConditionalFormat_SaveLoad_Persists()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", "<=4", "LowRisk");
        var before = doc.GetConditionalFormatCount();
        var path = TempFile("acf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount());
    }

    [Fact]
    public void AddConditionalFormat_Multiple()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">=20", "Critical");
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">=10", "High");
        doc.AddConditionalFormat("RiskRegister", "E2:E13", "<=4", "Low");
        Assert.Equal(3, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void AddConditionalFormat_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "C2:C13", ">3", "High");
        var ex = Record.Exception(() => doc.ExportToCsv("RiskRegister"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Then_GetCellValue_NoThrow()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">15", "Critical");
        var ex = Record.Exception(() => doc.GetCellValue("RiskRegister", 1, 4));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatRule_NoThrow()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">15", "HighRisk");
        var ex = Record.Exception(() => doc.GetConditionalFormatRule(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatRule_NonNull()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", ">=20", "Critical");
        Assert.NotNull(doc.GetConditionalFormatRule(0));
    }

    [Fact]
    public void GetConditionalFormatRule_Consistent()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "C2:C13", ">3", "High");
        Assert.Equal(doc.GetConditionalFormatRule(0), doc.GetConditionalFormatRule(0));
    }

    [Fact]
    public void GetConditionalFormatRule_SaveLoad_Consistent()
    {
        var doc = CreateRiskWorkbook();
        doc.AddConditionalFormat("RiskRegister", "E2:E13", "<=4", "Low");
        var path = TempFile("cfr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetConditionalFormatRule(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddConditionalFormat_GetConditionalFormatCount_GetConditionalFormatRule_Pipeline()
    {
        // Credit risk monitoring — bank loan portfolio with conditional highlighting for PD/LGD/EAD thresholds
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("LoanPortfolio");
        doc.SetCellValue("LoanPortfolio", 0, 0, "Loan_ID");
        doc.SetCellValue("LoanPortfolio", 0, 1, "Obligor");
        doc.SetCellValue("LoanPortfolio", 0, 2, "PD_Pct");
        doc.SetCellValue("LoanPortfolio", 0, 3, "LGD_Pct");
        doc.SetCellValue("LoanPortfolio", 0, 4, "EAD_GBP");
        doc.SetCellValue("LoanPortfolio", 0, 5, "Expected_Loss_GBP");
        doc.SetCellValue("LoanPortfolio", 0, 6, "Rating");

        string[] obligors = { "AlphaCorp", "BetaLtd", "GammaPlc", "DeltaGroup", "EpsilonInc", "ZetaHoldings" };
        string[] ratings = { "AAA", "AA", "A", "BBB", "BB", "B", "CCC" };
        var rng = new Random(20240501);
        for (int i = 1; i <= 12; i++)
        {
            double pd = rng.NextDouble() * 0.20; // 0-20%
            double lgd = 0.30 + rng.NextDouble() * 0.40; // 30-70%
            double ead = 500000 + rng.NextDouble() * 4500000; // £500K–£5M
            double el = pd * lgd * ead;
            string rating = ratings[Math.Min((int)(pd * 35), 6)];
            doc.SetCellValue("LoanPortfolio", i, 0, $"LOAN{i:D4}");
            doc.SetCellValue("LoanPortfolio", i, 1, obligors[(i - 1) % 6]);
            doc.SetCellValue("LoanPortfolio", i, 2, $"{pd * 100:F2}");
            doc.SetCellValue("LoanPortfolio", i, 3, $"{lgd * 100:F1}");
            doc.SetCellValue("LoanPortfolio", i, 4, $"{ead:F0}");
            doc.SetCellValue("LoanPortfolio", i, 5, $"{el:F0}");
            doc.SetCellValue("LoanPortfolio", i, 6, rating);
        }

        doc.AddSheet("StressTest");
        doc.SetCellValue("StressTest", 0, 0, "Scenario");
        doc.SetCellValue("StressTest", 0, 1, "Stressed_PD_Multiplier");
        doc.SetCellValue("StressTest", 0, 2, "Portfolio_EL_GBP");

        Assert.Equal(0, doc.GetConditionalFormatCount());

        // AddConditionalFormat — PD traffic light (high PD = red flag)
        doc.AddConditionalFormat("LoanPortfolio", "C2:C13", ">10", "HighPD");
        Assert.Equal(1, doc.GetConditionalFormatCount());

        // LGD threshold
        doc.AddConditionalFormat("LoanPortfolio", "D2:D13", ">60", "HighLGD");
        Assert.Equal(2, doc.GetConditionalFormatCount());

        // Expected loss warning
        doc.AddConditionalFormat("LoanPortfolio", "F2:F13", ">200000", "HighEL");
        Assert.Equal(3, doc.GetConditionalFormatCount());

        // Rating alert for sub-investment grade
        doc.AddConditionalFormat("LoanPortfolio", "G2:G13", "\"B\"", "SubIG");
        Assert.Equal(4, doc.GetConditionalFormatCount());

        // Combined EL and rating
        doc.AddConditionalFormat("StressTest", "C2:C5", ">5000000", "CriticalStress");
        Assert.Equal(5, doc.GetConditionalFormatCount());

        // Consistent
        Assert.Equal(doc.GetConditionalFormatCount(), doc.GetConditionalFormatCount());

        // GetConditionalFormatRule
        var rule0 = doc.GetConditionalFormatRule(0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetConditionalFormatRule(0)); // consistent

        var rule2 = doc.GetConditionalFormatRule(2);
        Assert.NotNull(rule2);

        var rule4 = doc.GetConditionalFormatRule(4);
        Assert.NotNull(rule4);

        // ExportToCsv no-throw
        var ex = Record.Exception(() => doc.ExportToCsv("LoanPortfolio"));
        Assert.Null(ex);

        // GetCellValue after conditional format
        Assert.NotNull(doc.GetCellValue("LoanPortfolio", 1, 2));

        // SaveToFile
        var path = TempFile("dogfood_credit_risk.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetConditionalFormatCount());
        Assert.NotNull(loaded.GetConditionalFormatRule(0));
        Assert.NotNull(loaded.GetConditionalFormatRule(4));
        Assert.NotNull(loaded.GetCellValue("LoanPortfolio", 1, 0));

        // AddConditionalFormat on loaded
        loaded.AddConditionalFormat("LoanPortfolio", "E2:E13", ">3000000", "LargeExposure");
        Assert.Equal(6, loaded.GetConditionalFormatCount());

        // Final save
        var path2 = TempFile("dogfood_credit_risk_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetConditionalFormatCount());
        Assert.NotNull(loaded2.GetConditionalFormatRule(0));
        var ex2 = Record.Exception(() => loaded2.ExportToCsv("LoanPortfolio"));
        var ex3 = Record.Exception(() => loaded2.AddConditionalFormat("LoanPortfolio", "C2:C13", ">15", "VeryHighPD"));
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
