// Tests for FodsDocument.GetNamedRange, SetNamedRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R391

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R391: Tests for FodsDocument.GetNamedRange, SetNamedRange deeper.
/// GetNamedRange(name): returns the cell range reference string for a named range.
/// SetNamedRange(name, sheetName, startRow, startCol, endRow, endCol): defines a named range.
/// Covers: GetNamedRange no-throw; GetNamedRange non-null for defined; GetNamedRange consistent;
/// GetNamedRange save-load; SetNamedRange no-throw;
/// SetNamedRange then GetNamedRange returns reference; SetNamedRange value unchanged;
/// SetNamedRange then GetSheetCount unchanged; SetNamedRange then ExportToHtml no-throw;
/// SetNamedRange override; SetNamedRange save-load; SetNamedRange multiple names;
/// dogfood CreateDoc→SetNamedRange→GetNamedRange→SaveToFile pipeline.
/// </summary>
public class FodsR391GetNamedRangeAndSetNamedRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR391GetNamedRangeAndSetNamedRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR391_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("FinancialModel");
        doc.SetCellValue("FinancialModel", 0, 0, "Year");
        doc.SetCellValue("FinancialModel", 0, 1, "Revenue");
        doc.SetCellValue("FinancialModel", 0, 2, "EBITDA");
        doc.SetCellValue("FinancialModel", 0, 3, "CapEx");
        doc.SetCellValue("FinancialModel", 1, 0, "2022");
        doc.SetCellValue("FinancialModel", 1, 1, "42000000");
        doc.SetCellValue("FinancialModel", 1, 2, "9800000");
        doc.SetCellValue("FinancialModel", 1, 3, "3200000");
        doc.SetCellValue("FinancialModel", 2, 0, "2023");
        doc.SetCellValue("FinancialModel", 2, 1, "48500000");
        doc.SetCellValue("FinancialModel", 2, 2, "11200000");
        doc.SetCellValue("FinancialModel", 2, 3, "3800000");
        doc.SetCellValue("FinancialModel", 3, 0, "2024");
        doc.SetCellValue("FinancialModel", 3, 1, "55100000");
        doc.SetCellValue("FinancialModel", 3, 2, "13400000");
        doc.SetCellValue("FinancialModel", 3, 3, "4500000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRange_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        var ex = Record.Exception(() => doc.GetNamedRange("Revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRange_NonNull_ForDefined()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        Assert.NotNull(doc.GetNamedRange("Revenue"));
    }

    [Fact]
    public void GetNamedRange_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("EBITDA", "FinancialModel", 1, 2, 3, 2);
        Assert.Equal(doc.GetNamedRange("EBITDA"), doc.GetNamedRange("EBITDA"));
    }

    [Fact]
    public void GetNamedRange_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        var before = doc.GetNamedRange("Revenue");
        var path = TempFile("gnr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRange("Revenue"));
    }

    // -------------------------------------------------------------------------
    // SetNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void SetNamedRange_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.SetNamedRange("TestRange", "FinancialModel", 0, 0, 3, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void SetNamedRange_Then_GetNamedRange_Returns_Reference()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        Assert.NotNull(doc.GetNamedRange("Revenue"));
        Assert.True(doc.GetNamedRange("Revenue").Length > 0);
    }

    [Fact]
    public void SetNamedRange_ValueUnchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCellValue("FinancialModel", 1, 1);
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        Assert.Equal(before, doc.GetCellValue("FinancialModel", 1, 1));
    }

    [Fact]
    public void SetNamedRange_Then_GetSheetCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetSheetCount();
        doc.SetNamedRange("CapEx", "FinancialModel", 1, 3, 3, 3);
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetNamedRange_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("FinancialData", "FinancialModel", 0, 0, 3, 3);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetNamedRange_Override()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 1, 1);
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        var ref2 = doc.GetNamedRange("Revenue");
        Assert.NotNull(ref2);
    }

    [Fact]
    public void SetNamedRange_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("EBITDA", "FinancialModel", 1, 2, 3, 2);
        var path = TempFile("snr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetNamedRange("EBITDA"));
    }

    [Fact]
    public void SetNamedRange_MultipleNames()
    {
        var doc = CreatePlainDoc();
        doc.SetNamedRange("Revenue", "FinancialModel", 1, 1, 3, 1);
        doc.SetNamedRange("EBITDA", "FinancialModel", 1, 2, 3, 2);
        doc.SetNamedRange("CapEx", "FinancialModel", 1, 3, 3, 3);
        Assert.NotNull(doc.GetNamedRange("Revenue"));
        Assert.NotNull(doc.GetNamedRange("EBITDA"));
        Assert.NotNull(doc.GetNamedRange("CapEx"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNamedRange_SetNamedRange_SaveToFile_Pipeline()
    {
        // Investment banking — Private Equity Leveraged Buyout (LBO) Model
        // Named ranges for formula-driven financial model: inputs, assumptions, outputs
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Assumptions");
        doc.AddSheet("Income Statement");
        doc.AddSheet("Returns");

        // Assumptions sheet
        doc.SetCellValue("Assumptions", 0, 0, "Parameter");
        doc.SetCellValue("Assumptions", 0, 1, "Value");
        doc.SetCellValue("Assumptions", 0, 2, "Note");
        string[,] assumptions = {
            { "Entry EV (£m)", "425", "Based on 8.5x LTM EBITDA" },
            { "Entry Multiple (EV/EBITDA)", "8.5", "Comparable: 7.5x-9.5x" },
            { "LTM EBITDA (£m)", "50", "FY2024A adjusted" },
            { "Entry Equity (£m)", "170", "40% equity contribution" },
            { "Senior Debt (£m)", "212.5", "4.25x EBITDA leverage" },
            { "Junior Debt (£m)", "42.5", "0.85x EBITDA mezzanine" },
            { "Revenue CAGR", "8%", "Base case" },
            { "EBITDA Margin Exit", "24%", "Expansion from 22.5%" },
            { "Hold Period (years)", "5", "Standard PE hold" },
            { "Exit Multiple (EV/EBITDA)", "9.0", "Multiple expansion" }
        };
        for (int i = 0; i < assumptions.GetLength(0); i++)
            for (int j = 0; j < assumptions.GetLength(1); j++)
                doc.SetCellValue("Assumptions", i + 1, j, assumptions[i, j]);

        // Define named ranges for assumptions
        doc.SetNamedRange("EntryEV", "Assumptions", 1, 1, 1, 1);
        doc.SetNamedRange("EntryMultiple", "Assumptions", 2, 1, 2, 1);
        doc.SetNamedRange("LTM_EBITDA", "Assumptions", 3, 1, 3, 1);
        doc.SetNamedRange("EntryEquity", "Assumptions", 4, 1, 4, 1);
        doc.SetNamedRange("HoldPeriod", "Assumptions", 9, 1, 9, 1);
        doc.SetNamedRange("ExitMultiple", "Assumptions", 10, 1, 10, 1);
        doc.SetNamedRange("AllAssumptions", "Assumptions", 1, 0, 10, 2);

        Assert.NotNull(doc.GetNamedRange("EntryEV"));
        Assert.NotNull(doc.GetNamedRange("LTM_EBITDA"));
        Assert.NotNull(doc.GetNamedRange("AllAssumptions"));
        Assert.Equal(doc.GetNamedRange("EntryEV"), doc.GetNamedRange("EntryEV")); // consistent

        // Income Statement sheet
        doc.SetCellValue("Income Statement", 0, 0, "Metric (£m)");
        doc.SetCellValue("Income Statement", 0, 1, "FY2024A");
        doc.SetCellValue("Income Statement", 0, 2, "FY2025E");
        doc.SetCellValue("Income Statement", 0, 3, "FY2026E");
        doc.SetCellValue("Income Statement", 0, 4, "FY2027E");
        doc.SetCellValue("Income Statement", 0, 5, "FY2028E");
        doc.SetCellValue("Income Statement", 0, 6, "FY2029E");
        string[,] isData = {
            { "Revenue", "222.2", "240.0", "259.2", "279.9", "302.3", "326.5" },
            { "Gross Profit", "111.1", "120.0", "129.6", "139.9", "151.1", "163.2" },
            { "EBITDA", "50.0", "54.0", "58.3", "63.0", "68.0", "73.5" },
            { "D&A", "(8.5)", "(9.0)", "(9.5)", "(10.0)", "(10.5)", "(11.0)" },
            { "EBIT", "41.5", "45.0", "48.8", "53.0", "57.5", "62.5" },
            { "Interest", "(17.5)", "(16.5)", "(15.3)", "(14.0)", "(12.5)", "(10.8)" },
            { "PBT", "24.0", "28.5", "33.5", "39.0", "45.0", "51.7" }
        };
        for (int i = 0; i < isData.GetLength(0); i++)
            for (int j = 0; j < isData.GetLength(1); j++)
                doc.SetCellValue("Income Statement", i + 1, j, isData[i, j]);

        doc.SetNamedRange("Revenue_Projections", "Income Statement", 1, 1, 1, 6);
        doc.SetNamedRange("EBITDA_Projections", "Income Statement", 3, 1, 3, 6);
        doc.SetNamedRange("IS_Complete", "Income Statement", 0, 0, 7, 6);

        Assert.Equal("222.2", doc.GetCellValue("Income Statement", 1, 1));
        Assert.Equal("50.0", doc.GetCellValue("Income Statement", 3, 1));
        Assert.Equal(3, doc.GetSheetCount());

        // Returns sheet
        doc.SetCellValue("Returns", 0, 0, "Returns Metric");
        doc.SetCellValue("Returns", 0, 1, "Value");
        doc.SetCellValue("Returns", 1, 0, "Exit EV (£m)");
        doc.SetCellValue("Returns", 1, 1, "661.5");
        doc.SetCellValue("Returns", 2, 0, "Equity Value at Exit (£m)");
        doc.SetCellValue("Returns", 2, 1, "406.5");
        doc.SetCellValue("Returns", 3, 0, "MoIC (gross)");
        doc.SetCellValue("Returns", 3, 1, "2.4x");
        doc.SetCellValue("Returns", 4, 0, "IRR (gross)");
        doc.SetCellValue("Returns", 4, 1, "19.0%");

        doc.SetNamedRange("ExitEV", "Returns", 1, 1, 1, 1);
        doc.SetNamedRange("MoIC", "Returns", 3, 1, 3, 1);
        doc.SetNamedRange("IRR", "Returns", 4, 1, 4, 1);

        Assert.NotNull(doc.GetNamedRange("Revenue_Projections"));
        Assert.NotNull(doc.GetNamedRange("EBITDA_Projections"));
        Assert.NotNull(doc.GetNamedRange("ExitEV"));
        Assert.NotNull(doc.GetNamedRange("MoIC"));
        Assert.NotNull(doc.GetNamedRange("IRR"));

        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        var path1 = TempFile("dogfood_lbo_model.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        var loaded = FodsDocument.LoadFile(path1);
        Assert.NotNull(loaded.GetNamedRange("EntryEV"));
        Assert.NotNull(loaded.GetNamedRange("LTM_EBITDA"));
        Assert.NotNull(loaded.GetNamedRange("Revenue_Projections"));
        Assert.NotNull(loaded.GetNamedRange("EBITDA_Projections"));
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.Equal("222.2", loaded.GetCellValue("Income Statement", 1, 1));

        // Override named range: expand revenue range
        loaded.SetNamedRange("Revenue_Projections", "Income Statement", 1, 1, 1, 6);
        Assert.NotNull(loaded.GetNamedRange("Revenue_Projections"));

        // Add downside scenario named range
        loaded.SetNamedRange("Downside_Scenario", "Assumptions", 1, 1, 1, 1);
        Assert.NotNull(loaded.GetNamedRange("Downside_Scenario"));

        var path2 = TempFile("dogfood_lbo_model_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.NotNull(final.GetNamedRange("EntryEV"));
        Assert.NotNull(final.GetNamedRange("Downside_Scenario"));

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.SetNamedRange("Archived", "Returns", 0, 0, 4, 1));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
