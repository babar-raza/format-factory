// Tests for FodsDocument.GetSheetProtection, SetSheetProtection deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R400

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R400: Tests for FodsDocument.GetSheetProtection, SetSheetProtection deeper.
/// GetSheetProtection(sheetName): returns whether the sheet has protection enabled (bool).
/// SetSheetProtection(sheetName, enabled): enables or disables sheet protection.
/// Covers: GetSheetProtection no-throw; GetSheetProtection false for new sheet;
/// GetSheetProtection consistent; GetSheetProtection save-load;
/// SetSheetProtection no-throw; SetSheetProtection true then GetSheetProtection true;
/// SetSheetProtection false then GetSheetProtection false; SetSheetProtection value unchanged;
/// SetSheetProtection sheet count unchanged; SetSheetProtection save-load;
/// SetSheetProtection toggle; dogfood CreateDoc→SetSheetProtection→GetSheetProtection pipeline.
/// </summary>
public class FodsR400GetSheetProtectionAndSetSheetProtectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR400GetSheetProtectionAndSetSheetProtectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR400_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateMultiSheetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Summary");
        doc.AddSheet("Assumptions");
        doc.AddSheet("Outputs");
        doc.SetCellValue("Summary", 0, 0, "Report");
        doc.SetCellValue("Summary", 1, 0, "Annual Budget 2025");
        doc.SetCellValue("Assumptions", 0, 0, "Driver");
        doc.SetCellValue("Assumptions", 0, 1, "Value");
        doc.SetCellValue("Assumptions", 1, 0, "Revenue Growth");
        doc.SetCellValue("Assumptions", 1, 1, "8.5%");
        doc.SetCellValue("Outputs", 0, 0, "Metric");
        doc.SetCellValue("Outputs", 0, 1, "FY2025");
        doc.SetCellValue("Outputs", 1, 0, "EBITDA");
        doc.SetCellValue("Outputs", 1, 1, "£48.2m");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSheetProtection
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtection_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var ex = Record.Exception(() => doc.GetSheetProtection("Summary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSheetProtection_False_ForNewSheet()
    {
        var doc = CreateMultiSheetDoc();
        Assert.False(doc.GetSheetProtection("Summary"));
    }

    [Fact]
    public void GetSheetProtection_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetProtection("Summary", true);
        Assert.Equal(doc.GetSheetProtection("Summary"), doc.GetSheetProtection("Summary"));
    }

    [Fact]
    public void GetSheetProtection_SaveLoad_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetProtection("Assumptions", true);
        var before = doc.GetSheetProtection("Assumptions");
        var path = TempFile("gsp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSheetProtection("Assumptions"));
    }

    // -------------------------------------------------------------------------
    // SetSheetProtection
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSheetProtection_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var ex = Record.Exception(() => doc.SetSheetProtection("Summary", true));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSheetProtection_True_Then_GetSheetProtection_True()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetProtection("Summary", true);
        Assert.True(doc.GetSheetProtection("Summary"));
    }

    [Fact]
    public void SetSheetProtection_False_Then_GetSheetProtection_False()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetProtection("Summary", true);
        doc.SetSheetProtection("Summary", false);
        Assert.False(doc.GetSheetProtection("Summary"));
    }

    [Fact]
    public void SetSheetProtection_ValueUnchanged()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetCellValue("Assumptions", 1, 1);
        doc.SetSheetProtection("Assumptions", true);
        Assert.Equal(before, doc.GetCellValue("Assumptions", 1, 1));
    }

    [Fact]
    public void SetSheetProtection_SheetCount_Unchanged()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetCount();
        doc.SetSheetProtection("Summary", true);
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetSheetProtection_SaveLoad_Persists()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetProtection("Outputs", true);
        var path = TempFile("ssp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetSheetProtection("Outputs"));
    }

    [Fact]
    public void SetSheetProtection_Toggle()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetProtection("Summary", true);
        Assert.True(doc.GetSheetProtection("Summary"));
        doc.SetSheetProtection("Summary", false);
        Assert.False(doc.GetSheetProtection("Summary"));
        doc.SetSheetProtection("Summary", true);
        Assert.True(doc.GetSheetProtection("Summary"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSheetProtection_SetSheetProtection_SaveToFile_Pipeline()
    {
        // Finance — UK Financial Reporting Council: Board-approved Financial Model
        // Multi-sheet financial model where input assumptions are locked and outputs are open
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Instructions");
        doc.AddSheet("Macro Assumptions");
        doc.AddSheet("Revenue Model");
        doc.AddSheet("Cost Model");
        doc.AddSheet("P&L Summary");
        doc.AddSheet("Balance Sheet");

        // Instructions sheet
        doc.SetCellValue("Instructions", 0, 0, "FRC Integrated Financial Model v2.1");
        doc.SetCellValue("Instructions", 1, 0, "PROTECTED SHEETS: Macro Assumptions, P&L Summary, Balance Sheet");
        doc.SetCellValue("Instructions", 2, 0, "EDITABLE SHEETS: Revenue Model, Cost Model");
        doc.SetCellValue("Instructions", 3, 0, "Contact CFO for unlock password");

        // Macro Assumptions sheet — PROTECTED (Board-approved, not to be altered)
        doc.SetCellValue("Macro Assumptions", 0, 0, "Assumption");
        doc.SetCellValue("Macro Assumptions", 0, 1, "FY2025");
        doc.SetCellValue("Macro Assumptions", 0, 2, "FY2026");
        doc.SetCellValue("Macro Assumptions", 0, 3, "FY2027");
        string[,] macros = {
            { "UK GDP Growth (%)", "1.2", "1.8", "2.1" },
            { "CPI Inflation (%)", "2.5", "2.2", "2.0" },
            { "Bank Rate (%)", "4.5", "3.75", "3.25" },
            { "GBP/USD", "1.27", "1.29", "1.31" },
            { "Brent Crude ($/bbl)", "78", "75", "72" }
        };
        for (int i = 0; i < macros.GetLength(0); i++)
            for (int j = 0; j < macros.GetLength(1); j++)
                doc.SetCellValue("Macro Assumptions", i + 1, j, macros[i, j]);

        // Revenue Model — EDITABLE (FP&A team updates)
        doc.SetCellValue("Revenue Model", 0, 0, "Revenue Stream");
        doc.SetCellValue("Revenue Model", 0, 1, "FY2025E (£m)");
        doc.SetCellValue("Revenue Model", 0, 2, "FY2026E (£m)");
        doc.SetCellValue("Revenue Model", 1, 0, "UK Operations");
        doc.SetCellValue("Revenue Model", 1, 1, "245.8");
        doc.SetCellValue("Revenue Model", 1, 2, "265.5");
        doc.SetCellValue("Revenue Model", 2, 0, "International");
        doc.SetCellValue("Revenue Model", 2, 1, "112.4");
        doc.SetCellValue("Revenue Model", 2, 2, "128.6");

        // P&L Summary — PROTECTED (formula outputs)
        doc.SetCellValue("P&L Summary", 0, 0, "Line Item");
        doc.SetCellValue("P&L Summary", 0, 1, "FY2025E");
        doc.SetCellValue("P&L Summary", 1, 0, "Total Revenue (£m)");
        doc.SetCellValue("P&L Summary", 1, 1, "358.2");
        doc.SetCellValue("P&L Summary", 2, 0, "EBITDA (£m)");
        doc.SetCellValue("P&L Summary", 2, 1, "86.0");

        // Balance Sheet — PROTECTED
        doc.SetCellValue("Balance Sheet", 0, 0, "Item");
        doc.SetCellValue("Balance Sheet", 1, 0, "Total Assets (£m)");
        doc.SetCellValue("Balance Sheet", 1, 1, "524.3");

        // Apply protection
        doc.SetSheetProtection("Macro Assumptions", true);
        doc.SetSheetProtection("P&L Summary", true);
        doc.SetSheetProtection("Balance Sheet", true);
        // Revenue Model and Cost Model remain editable (false)
        doc.SetSheetProtection("Revenue Model", false);
        doc.SetSheetProtection("Cost Model", false);

        // Verify protection state
        Assert.True(doc.GetSheetProtection("Macro Assumptions"));
        Assert.True(doc.GetSheetProtection("P&L Summary"));
        Assert.True(doc.GetSheetProtection("Balance Sheet"));
        Assert.False(doc.GetSheetProtection("Revenue Model"));
        Assert.False(doc.GetSheetProtection("Cost Model"));
        Assert.False(doc.GetSheetProtection("Instructions")); // not explicitly set

        Assert.Equal(6, doc.GetSheetCount());
        Assert.Equal("1.2", doc.GetCellValue("Macro Assumptions", 1, 1));

        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        var path1 = TempFile("dogfood_frc_financial_model.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(6, loaded.GetSheetCount());
        Assert.True(loaded.GetSheetProtection("Macro Assumptions"));
        Assert.True(loaded.GetSheetProtection("P&L Summary"));
        Assert.True(loaded.GetSheetProtection("Balance Sheet"));
        Assert.False(loaded.GetSheetProtection("Revenue Model"));
        Assert.False(loaded.GetSheetProtection("Cost Model"));

        // Toggle: FP&A has CFO approval to temporarily unlock Macro Assumptions
        loaded.SetSheetProtection("Macro Assumptions", false);
        Assert.False(loaded.GetSheetProtection("Macro Assumptions"));
        loaded.SetCellValue("Macro Assumptions", 1, 1, "1.4"); // update GDP growth
        loaded.SetSheetProtection("Macro Assumptions", true); // re-lock
        Assert.True(loaded.GetSheetProtection("Macro Assumptions"));
        Assert.Equal("1.4", loaded.GetCellValue("Macro Assumptions", 1, 1));

        var path2 = TempFile("dogfood_frc_financial_model_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.True(final.GetSheetProtection("Macro Assumptions"));
        Assert.Equal("1.4", final.GetCellValue("Macro Assumptions", 1, 1));

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.SetSheetProtection("Cost Model", true));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
