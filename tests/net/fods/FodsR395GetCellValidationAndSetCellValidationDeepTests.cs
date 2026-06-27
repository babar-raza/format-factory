// Tests for FodsDocument.GetCellValidation, SetCellValidation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R395

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R395: Tests for FodsDocument.GetCellValidation, SetCellValidation deeper.
/// GetCellValidation(sheet, row, col): returns the validation rule description for a cell.
/// SetCellValidation(sheet, row, col, type, rule): sets a data validation constraint on a cell.
/// Covers: GetCellValidation no-throw; GetCellValidation null for unvalidated;
/// GetCellValidation consistent; GetCellValidation save-load;
/// SetCellValidation no-throw; SetCellValidation then GetCellValidation non-null;
/// SetCellValidation value unchanged; SetCellValidation sheet count unchanged;
/// SetCellValidation then ExportToHtml no-throw; SetCellValidation override;
/// SetCellValidation save-load; SetCellValidation multiple cells;
/// dogfood CreateDoc→SetCellValidation→GetCellValidation→SaveToFile pipeline.
/// </summary>
public class FodsR395GetCellValidationAndSetCellValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR395GetCellValidationAndSetCellValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR395_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Risk Register");
        doc.SetCellValue("Risk Register", 0, 0, "Risk ID");
        doc.SetCellValue("Risk Register", 0, 1, "Description");
        doc.SetCellValue("Risk Register", 0, 2, "Likelihood");
        doc.SetCellValue("Risk Register", 0, 3, "Impact");
        doc.SetCellValue("Risk Register", 0, 4, "Score");
        doc.SetCellValue("Risk Register", 0, 5, "Owner");
        string[,] risks = {
            { "RSK-001", "Regulatory capital breach", "2", "5", "10", "CRO" },
            { "RSK-002", "Cyber incident — data exfiltration", "3", "5", "15", "CISO" },
            { "RSK-003", "Liquidity stress", "2", "4", "8", "CFO" },
            { "RSK-004", "Conduct risk — mis-selling", "3", "4", "12", "CCO" },
            { "RSK-005", "Model risk — VaR breach", "2", "3", "6", "CRO" }
        };
        for (int i = 0; i < risks.GetLength(0); i++)
            for (int j = 0; j < risks.GetLength(1); j++)
                doc.SetCellValue("Risk Register", i + 1, j, risks[i, j]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValidation_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        var ex = Record.Exception(() => doc.GetCellValidation("Risk Register", 1, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellValidation_Null_ForUnvalidated()
    {
        var doc = CreateRiskDoc();
        // No validation set on column 0 (Risk ID)
        Assert.Null(doc.GetCellValidation("Risk Register", 1, 0));
    }

    [Fact]
    public void GetCellValidation_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        Assert.Equal(doc.GetCellValidation("Risk Register", 1, 2),
                     doc.GetCellValidation("Risk Register", 1, 2));
    }

    [Fact]
    public void GetCellValidation_SaveLoad_Consistent()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 1, 3, "integer", "between:1:5");
        var before = doc.GetCellValidation("Risk Register", 1, 3);
        var path = TempFile("gcv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellValidation("Risk Register", 1, 3));
    }

    // -------------------------------------------------------------------------
    // SetCellValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValidation_NoThrow()
    {
        var doc = CreateRiskDoc();
        var ex = Record.Exception(() =>
            doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellValidation_Then_GetCellValidation_NonNull()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        Assert.NotNull(doc.GetCellValidation("Risk Register", 1, 2));
    }

    [Fact]
    public void SetCellValidation_ValueUnchanged()
    {
        var doc = CreateRiskDoc();
        var before = doc.GetCellValue("Risk Register", 1, 2);
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        Assert.Equal(before, doc.GetCellValue("Risk Register", 1, 2));
    }

    [Fact]
    public void SetCellValidation_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateRiskDoc();
        var before = doc.GetSheetCount();
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetCellValidation_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellValidation_Override()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:3");
        doc.SetCellValidation("Risk Register", 1, 2, "integer", "between:1:5");
        Assert.NotNull(doc.GetCellValidation("Risk Register", 1, 2));
    }

    [Fact]
    public void SetCellValidation_SaveLoad_Persists()
    {
        var doc = CreateRiskDoc();
        doc.SetCellValidation("Risk Register", 2, 2, "integer", "between:1:5");
        var path = TempFile("scv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellValidation("Risk Register", 2, 2));
    }

    [Fact]
    public void SetCellValidation_MultipleCells()
    {
        var doc = CreateRiskDoc();
        // Validate Likelihood (col 2) and Impact (col 3) for all data rows
        for (int row = 1; row <= 5; row++)
        {
            doc.SetCellValidation("Risk Register", row, 2, "integer", "between:1:5");
            doc.SetCellValidation("Risk Register", row, 3, "integer", "between:1:5");
        }
        for (int row = 1; row <= 5; row++)
        {
            Assert.NotNull(doc.GetCellValidation("Risk Register", row, 2));
            Assert.NotNull(doc.GetCellValidation("Risk Register", row, 3));
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellValidation_SetCellValidation_SaveToFile_Pipeline()
    {
        // Risk management — UK Prudential Regulation Authority (PRA) ICAAP/ILAAP
        // Internal stress test workbook with data validation rules
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Stress Scenarios");
        doc.AddSheet("Capital Projections");
        doc.AddSheet("Liquidity Projections");

        // Stress Scenarios sheet
        doc.SetCellValue("Stress Scenarios", 0, 0, "Scenario ID");
        doc.SetCellValue("Stress Scenarios", 0, 1, "Scenario Name");
        doc.SetCellValue("Stress Scenarios", 0, 2, "Severity (1-5)");
        doc.SetCellValue("Stress Scenarios", 0, 3, "GDP Shock (%)");
        doc.SetCellValue("Stress Scenarios", 0, 4, "HPI Shock (%)");
        doc.SetCellValue("Stress Scenarios", 0, 5, "Unemployment Shock (pp)");
        doc.SetCellValue("Stress Scenarios", 0, 6, "Approved");

        string[,] scenarios = {
            { "SCN-001", "Base Case", "1", "0.0", "0.0", "0.0", "Yes" },
            { "SCN-002", "Mild Stress", "2", "-2.5", "-5.0", "1.5", "Yes" },
            { "SCN-003", "Moderate Stress (PRA Ref)", "3", "-5.0", "-15.0", "3.0", "Yes" },
            { "SCN-004", "Severe Stress", "4", "-8.5", "-30.0", "5.5", "Yes" },
            { "SCN-005", "Exploratory (Systemic)", "5", "-12.0", "-45.0", "8.0", "No" }
        };
        for (int i = 0; i < scenarios.GetLength(0); i++)
            for (int j = 0; j < scenarios.GetLength(1); j++)
                doc.SetCellValue("Stress Scenarios", i + 1, j, scenarios[i, j]);

        // Apply validations to Stress Scenarios
        for (int row = 1; row <= 5; row++)
        {
            doc.SetCellValidation("Stress Scenarios", row, 2, "integer", "between:1:5");
            doc.SetCellValidation("Stress Scenarios", row, 6, "list", "Yes,No");
        }

        // Verify validations set
        for (int row = 1; row <= 5; row++)
        {
            Assert.NotNull(doc.GetCellValidation("Stress Scenarios", row, 2));
            Assert.NotNull(doc.GetCellValidation("Stress Scenarios", row, 6));
        }
        // Unvalidated cells
        Assert.Null(doc.GetCellValidation("Stress Scenarios", 0, 0)); // header row
        Assert.Null(doc.GetCellValidation("Stress Scenarios", 1, 1)); // text column

        // Capital Projections sheet
        doc.SetCellValue("Capital Projections", 0, 0, "Scenario ID");
        doc.SetCellValue("Capital Projections", 0, 1, "Year");
        doc.SetCellValue("Capital Projections", 0, 2, "CET1 Ratio (%)");
        doc.SetCellValue("Capital Projections", 0, 3, "Total Capital Ratio (%)");
        doc.SetCellValue("Capital Projections", 0, 4, "Leverage Ratio (%)");
        doc.SetCellValue("Capital Projections", 0, 5, "RWA (£bn)");
        string[,] capData = {
            { "SCN-003", "2025", "13.2", "17.8", "5.1", "42.5" },
            { "SCN-003", "2026", "12.1", "16.4", "4.8", "45.2" },
            { "SCN-003", "2027", "10.8", "14.9", "4.3", "48.1" },
            { "SCN-004", "2025", "11.5", "15.6", "4.5", "44.3" },
            { "SCN-004", "2026", "9.8", "13.2", "3.9", "47.8" }
        };
        for (int i = 0; i < capData.GetLength(0); i++)
            for (int j = 0; j < capData.GetLength(1); j++)
                doc.SetCellValue("Capital Projections", i + 1, j, capData[i, j]);

        // Validate CET1 ratio (col 2) — must be positive
        for (int row = 1; row <= 5; row++)
            doc.SetCellValidation("Capital Projections", row, 2, "decimal", "greaterThan:0");

        for (int row = 1; row <= 5; row++)
            Assert.NotNull(doc.GetCellValidation("Capital Projections", row, 2));

        Assert.Equal(3, doc.GetSheetCount());
        Assert.Equal("13.2", doc.GetCellValue("Capital Projections", 1, 2));

        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        var path1 = TempFile("dogfood_pra_icaap.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(3, loaded.GetSheetCount());
        for (int row = 1; row <= 5; row++)
        {
            Assert.NotNull(loaded.GetCellValidation("Stress Scenarios", row, 2));
            Assert.NotNull(loaded.GetCellValidation("Stress Scenarios", row, 6));
        }
        Assert.Null(loaded.GetCellValidation("Stress Scenarios", 0, 0));

        // Override validation on SCN-005 severity
        loaded.SetCellValidation("Stress Scenarios", 5, 2, "integer", "between:1:5");
        Assert.NotNull(loaded.GetCellValidation("Stress Scenarios", 5, 2));

        // Add Liquidity validation
        loaded.SetCellValue("Liquidity Projections", 0, 0, "Scenario ID");
        loaded.SetCellValue("Liquidity Projections", 0, 1, "LCR (%)");
        loaded.SetCellValue("Liquidity Projections", 1, 0, "SCN-003");
        loaded.SetCellValue("Liquidity Projections", 1, 1, "125");
        loaded.SetCellValidation("Liquidity Projections", 1, 1, "decimal", "greaterThan:0");
        Assert.NotNull(loaded.GetCellValidation("Liquidity Projections", 1, 1));

        var path2 = TempFile("dogfood_pra_icaap_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.NotNull(final.GetCellValidation("Stress Scenarios", 1, 2));
        Assert.NotNull(final.GetCellValidation("Liquidity Projections", 1, 1));

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.SetCellValidation("Stress Scenarios", 1, 4, "decimal", "between:-50:0"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
