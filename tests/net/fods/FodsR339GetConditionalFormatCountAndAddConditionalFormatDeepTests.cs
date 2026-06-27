// Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R339

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R339: Tests for FodsDocument.GetConditionalFormatCount, AddConditionalFormat, GetConditionalFormatRule deeper.
/// GetConditionalFormatCount(): returns the number of conditional formatting rules in the document.
/// AddConditionalFormat(sheet, range, condition, formatStyle): adds a conditional format rule.
/// GetConditionalFormatRule(index): returns the condition expression of the rule at the given index.
/// Covers: GetConditionalFormatCount no-throw; GetConditionalFormatCount non-negative;
/// GetConditionalFormatCount consistent; GetConditionalFormatCount zero for new doc;
/// GetConditionalFormatCount after AddConditionalFormat increases; GetConditionalFormatCount save-load;
/// AddConditionalFormat no-throw; AddConditionalFormat increases count; AddConditionalFormat save-load;
/// AddConditionalFormat multiple; AddConditionalFormat then ExportToHtml no-throw;
/// AddConditionalFormat then GetCellValue no-throw;
/// GetConditionalFormatRule no-throw; GetConditionalFormatRule non-null; GetConditionalFormatRule consistent;
/// GetConditionalFormatRule save-load;
/// dogfood CreateDoc→AddConditionalFormat→GetConditionalFormatCount→GetConditionalFormatRule→SaveToFile pipeline.
/// </summary>
public class FodsR339GetConditionalFormatCountAndAddConditionalFormatDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR339GetConditionalFormatCountAndAddConditionalFormatDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR339_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("RiskRegister");
        doc.SetCellValue("RiskRegister", 0, 0, "Risk ID");
        doc.SetCellValue("RiskRegister", 0, 1, "Category");
        doc.SetCellValue("RiskRegister", 0, 2, "Likelihood");
        doc.SetCellValue("RiskRegister", 0, 3, "Impact");
        doc.SetCellValue("RiskRegister", 0, 4, "Risk Score");
        doc.SetCellValue("RiskRegister", 0, 5, "Mitigation Status");
        string[] categories = { "Operational", "Financial", "Regulatory", "Reputational", "Strategic" };
        string[] statuses = { "Open", "Mitigated", "Accepted", "Transferred" };
        var rng = new Random(99001);
        for (int i = 1; i <= 8; i++)
        {
            int likelihood = rng.Next(1, 6);
            int impact = rng.Next(1, 6);
            doc.SetCellValue("RiskRegister", i, 0, $"RISK-{i:D3}");
            doc.SetCellValue("RiskRegister", i, 1, categories[i % 5]);
            doc.SetCellValue("RiskRegister", i, 2, likelihood.ToString());
            doc.SetCellValue("RiskRegister", i, 3, impact.ToString());
            doc.SetCellValue("RiskRegister", i, 4, (likelihood * impact).ToString());
            doc.SetCellValue("RiskRegister", i, 5, statuses[i % 4]);
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatCount_NoThrow()
    {
        var doc = CreateRiskDoc();
        var ex = Record.Exception(() => doc.GetConditionalFormatCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatCount_NonNegative()
    {
        var doc = CreateRiskDoc();
        Assert.True(doc.GetConditionalFormatCount() >= 0);
    }

    [Fact]
    public void GetConditionalFormatCount_Consistent()
    {
        var doc = CreateRiskDoc();
        Assert.Equal(doc.GetConditionalFormatCount(), doc.GetConditionalFormatCount());
    }

    [Fact]
    public void GetConditionalFormatCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "No conditional formats");
        Assert.Equal(0, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void GetConditionalFormatCount_AfterAddConditionalFormat_Increases()
    {
        var doc = CreateRiskDoc();
        var before = doc.GetConditionalFormatCount();
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">15", "HighRiskStyle");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void GetConditionalFormatCount_SaveLoad_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">=10", "MediumRiskStyle");
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
        var doc = CreateRiskDoc();
        var ex = Record.Exception(() => doc.AddConditionalFormat("RiskRegister", "C2:C9", ">3", "HighLikelihoodStyle"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Increases_Count()
    {
        var doc = CreateRiskDoc();
        var before = doc.GetConditionalFormatCount();
        doc.AddConditionalFormat("RiskRegister", "D2:D9", ">4", "HighImpactStyle");
        Assert.Equal(before + 1, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void AddConditionalFormat_SaveLoad_Persists()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "F2:F9", "=\"Open\"", "OpenRiskStyle");
        var before = doc.GetConditionalFormatCount();
        var path = TempFile("acf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatCount());
    }

    [Fact]
    public void AddConditionalFormat_Multiple()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">15", "RedStyle");
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">=10", "AmberStyle");
        doc.AddConditionalFormat("RiskRegister", "E2:E9", "<10", "GreenStyle");
        Assert.Equal(3, doc.GetConditionalFormatCount());
    }

    [Fact]
    public void AddConditionalFormat_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "C2:C9", ">3", "TestStyle");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddConditionalFormat_Then_GetCellValue_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">10", "TestStyle");
        var ex = Record.Exception(() => doc.GetCellValue("RiskRegister", 1, 4));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatRule
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatRule_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">15", "Style1");
        var ex = Record.Exception(() => doc.GetConditionalFormatRule(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatRule_NonNull()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "E2:E9", ">=10", "Style2");
        Assert.NotNull(doc.GetConditionalFormatRule(0));
    }

    [Fact]
    public void GetConditionalFormatRule_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "D2:D9", ">3", "Style3");
        Assert.Equal(doc.GetConditionalFormatRule(0), doc.GetConditionalFormatRule(0));
    }

    [Fact]
    public void GetConditionalFormatRule_SaveLoad_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.AddConditionalFormat("RiskRegister", "C2:C9", "<2", "LowLikelihoodStyle");
        var path = TempFile("cfr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetConditionalFormatRule(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddConditionalFormat_GetConditionalFormatCount_GetConditionalFormatRule_SaveToFile_Pipeline()
    {
        // Enterprise risk dashboard — ESG and financial risk heat map workbook
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("ESGRiskHeatMap");
        doc.SetCellValue("ESGRiskHeatMap", 0, 0, "Risk Category");
        doc.SetCellValue("ESGRiskHeatMap", 0, 1, "Sub-Category");
        doc.SetCellValue("ESGRiskHeatMap", 0, 2, "Likelihood (1-5)");
        doc.SetCellValue("ESGRiskHeatMap", 0, 3, "Severity (1-5)");
        doc.SetCellValue("ESGRiskHeatMap", 0, 4, "Inherent Risk");
        doc.SetCellValue("ESGRiskHeatMap", 0, 5, "Residual Risk");
        doc.SetCellValue("ESGRiskHeatMap", 0, 6, "Control Effectiveness");

        string[][] risks = {
            new[] { "Environmental", "Carbon Emissions", "4", "5", "20", "12", "Medium" },
            new[] { "Environmental", "Water Scarcity", "3", "4", "12", "8", "High" },
            new[] { "Social", "Labour Standards", "3", "5", "15", "9", "Medium" },
            new[] { "Social", "Supply Chain Ethics", "4", "4", "16", "10", "Medium" },
            new[] { "Governance", "Board Independence", "2", "4", "8", "4", "High" },
            new[] { "Governance", "Anti-Corruption", "3", "5", "15", "7", "High" },
            new[] { "Financial", "Credit Concentration", "4", "5", "20", "14", "Low" },
            new[] { "Financial", "Liquidity Risk", "3", "5", "15", "11", "Medium" },
            new[] { "Operational", "Cyber Security", "5", "5", "25", "15", "Medium" },
            new[] { "Operational", "Business Continuity", "3", "4", "12", "6", "High" },
        };
        for (int i = 0; i < risks.Length; i++)
            for (int c = 0; c < risks[i].Length; c++)
                doc.SetCellValue("ESGRiskHeatMap", i + 1, c, risks[i][c]);

        Assert.Equal(0, doc.GetConditionalFormatCount());

        // Inherent Risk — traffic light colouring
        doc.AddConditionalFormat("ESGRiskHeatMap", "E2:E11", ">=20", "CriticalRiskRedStyle");
        Assert.Equal(1, doc.GetConditionalFormatCount());

        doc.AddConditionalFormat("ESGRiskHeatMap", "E2:E11", ">=15", "HighRiskAmberStyle");
        Assert.Equal(2, doc.GetConditionalFormatCount());

        doc.AddConditionalFormat("ESGRiskHeatMap", "E2:E11", ">=10", "MediumRiskYellowStyle");
        Assert.Equal(3, doc.GetConditionalFormatCount());

        doc.AddConditionalFormat("ESGRiskHeatMap", "E2:E11", "<10", "LowRiskGreenStyle");
        Assert.Equal(4, doc.GetConditionalFormatCount());

        // Residual Risk — same traffic light
        doc.AddConditionalFormat("ESGRiskHeatMap", "F2:F11", ">=12", "ResidualHighStyle");
        Assert.Equal(5, doc.GetConditionalFormatCount());

        // Control Effectiveness — text-based
        doc.AddConditionalFormat("ESGRiskHeatMap", "G2:G11", "=\"Low\"", "LowControlStyle");
        Assert.Equal(6, doc.GetConditionalFormatCount());

        Assert.Equal(doc.GetConditionalFormatCount(), doc.GetConditionalFormatCount());

        // GetConditionalFormatRule
        var rule0 = doc.GetConditionalFormatRule(0);
        Assert.NotNull(rule0);
        Assert.Equal(rule0, doc.GetConditionalFormatRule(0)); // consistent

        var rule3 = doc.GetConditionalFormatRule(3);
        Assert.NotNull(rule3);

        var rule5 = doc.GetConditionalFormatRule(5);
        Assert.NotNull(rule5);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCellValue preserved
        Assert.Equal("20", doc.GetCellValue("ESGRiskHeatMap", 1, 4)); // Carbon Emissions inherent risk

        // SaveToFile
        var path = TempFile("dogfood_esg_risk.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetConditionalFormatCount());
        Assert.NotNull(loaded.GetConditionalFormatRule(0));
        Assert.NotNull(loaded.GetConditionalFormatRule(5));
        Assert.Equal("20", loaded.GetCellValue("ESGRiskHeatMap", 1, 4));

        // AddConditionalFormat on loaded
        loaded.AddConditionalFormat("ESGRiskHeatMap", "B2:B11", "=\"Governance\"", "GovernanceHighlightStyle");
        Assert.Equal(7, loaded.GetConditionalFormatCount());

        // Second sheet
        loaded.AddSheet("FinancialRisk");
        loaded.SetCellValue("FinancialRisk", 0, 0, "Metric");
        loaded.SetCellValue("FinancialRisk", 0, 1, "Value");
        loaded.SetCellValue("FinancialRisk", 1, 0, "VaR (95%, 1-day)");
        loaded.SetCellValue("FinancialRisk", 1, 1, "2.3");
        loaded.AddConditionalFormat("FinancialRisk", "B2:B10", ">2.0", "VaRBreachStyle");
        Assert.Equal(8, loaded.GetConditionalFormatCount());

        // Final save
        var path2 = TempFile("dogfood_esg_risk_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(8, loaded2.GetConditionalFormatCount());
        Assert.NotNull(loaded2.GetConditionalFormatRule(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.AddConditionalFormat("ESGRiskHeatMap", "A2:A11", "=\"Environmental\"", "EnvStyle"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
