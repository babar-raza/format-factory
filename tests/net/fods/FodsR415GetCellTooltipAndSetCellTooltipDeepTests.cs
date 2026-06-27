// Tests for FodsDocument.GetCellTooltip, SetCellTooltip deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R415

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R415: Tests for FodsDocument.GetCellTooltip, SetCellTooltip deeper.
/// GetCellTooltip(sheet, row, col): returns the tooltip/annotation string for the cell, or null if none.
/// SetCellTooltip(sheet, row, col, text): sets the tooltip text for the cell.
/// Covers: GetCellTooltip null for new cell; GetCellTooltip no-throw; SetCellTooltip no-throw;
/// GetCellTooltip non-null after Set; GetCellTooltip consistent after Set; GetCellTooltip save-load;
/// SetCellTooltip overwrite; SetCellTooltip multiple cells;
/// dogfood HMRC corporation tax computation model pipeline.
/// </summary>
public class FodsR415GetCellTooltipAndSetCellTooltipDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR415GetCellTooltipAndSetCellTooltipDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR415_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSampleDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Annotations");
        doc.SetCellValue("Annotations", 0, 0, "metric");
        doc.SetCellValue("Annotations", 0, 1, "value");
        doc.SetCellValue("Annotations", 0, 2, "notes");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellTooltip
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTooltip_Null_ForNewCell()
    {
        var doc = CreateSampleDoc();
        Assert.Null(doc.GetCellTooltip("Annotations", 1, 0));
    }

    [Fact]
    public void GetCellTooltip_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetCellTooltip("Annotations", 1, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellTooltip_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetCellTooltip("Annotations", 1, 0, "Annual revenue before deductions"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellTooltip_NonNull_AfterSet()
    {
        var doc = CreateSampleDoc();
        doc.SetCellTooltip("Annotations", 1, 0, "Annual revenue before deductions");
        Assert.NotNull(doc.GetCellTooltip("Annotations", 1, 0));
    }

    [Fact]
    public void GetCellTooltip_Consistent_AfterSet()
    {
        var doc = CreateSampleDoc();
        doc.SetCellTooltip("Annotations", 1, 0, "Revenue tooltip");
        var v1 = doc.GetCellTooltip("Annotations", 1, 0);
        var v2 = doc.GetCellTooltip("Annotations", 1, 0);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetCellTooltip_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellTooltip("Annotations", 1, 0, "Gross trading profit per CT600 Line 150");
        var before = doc.GetCellTooltip("Annotations", 1, 0);
        var path = TempFile("tt_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellTooltip("Annotations", 1, 0));
    }

    [Fact]
    public void SetCellTooltip_Overwrite()
    {
        var doc = CreateSampleDoc();
        doc.SetCellTooltip("Annotations", 1, 0, "Old tooltip");
        doc.SetCellTooltip("Annotations", 1, 0, "Updated tooltip with more detail");
        var tooltip = doc.GetCellTooltip("Annotations", 1, 0);
        Assert.NotNull(tooltip);
    }

    [Fact]
    public void SetCellTooltip_MultipleCells()
    {
        var doc = CreateSampleDoc();
        doc.SetCellTooltip("Annotations", 1, 0, "Metric name tooltip");
        doc.SetCellTooltip("Annotations", 1, 1, "Numeric value tooltip");
        doc.SetCellTooltip("Annotations", 1, 2, "Additional notes tooltip");
        Assert.NotNull(doc.GetCellTooltip("Annotations", 1, 0));
        Assert.NotNull(doc.GetCellTooltip("Annotations", 1, 1));
        Assert.NotNull(doc.GetCellTooltip("Annotations", 1, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellTooltip_SetCellTooltip_Pipeline()
    {
        // Tax — HMRC: Corporation Tax Computation Model (CT600 Supplement)
        // Financial model with cell-level documentation for tax adviser review
        // Tooltips provide statutory references and calculation methodology for each input

        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Trading profit computation
        doc.AddSheet("Trading_Profit");
        doc.SetCellValue("Trading_Profit", 0, 0, "line_ref");
        doc.SetCellValue("Trading_Profit", 0, 1, "description");
        doc.SetCellValue("Trading_Profit", 0, 2, "amount_gbp");
        doc.SetCellValue("Trading_Profit", 0, 3, "statutory_ref");

        // No tooltip on header
        Assert.Null(doc.GetCellTooltip("Trading_Profit", 0, 2));

        string[] lineRefs = { "L150", "L155", "L160", "L200", "L210", "L215", "L235", "L250" };
        string[] descs = { "Gross_trading_profit", "Trading_losses_brought_forward", "Net_trading_profit",
                           "Chargeable_gains", "Deductions_relief_claimed", "Total_profits_chargeable",
                           "R&D_enhanced_deduction", "Taxable_total_profits" };
        double[] amounts = { 12450000, -980000, 11470000, 340000, -1200000, 10610000, -500000, 10110000 };
        string[] statRefs = { "CTA2009_s.35", "CTA2010_s.37", "CTA2009_s.35-37",
                               "TCGA1992_s.1", "CTA2010_s.45", "CTA2010_s.4",
                               "CTA2009_s.1044", "CTA2010_s.4" };
        string[] tooltips = {
            "Gross trading profit per management accounts before any adjustments. See CT600 Box 150.",
            "Unrelieved trading losses from prior accounting periods. Carried forward under CTA 2010 s.37.",
            "Net trading profit after loss relief. Equals L150 minus L155.",
            "Chargeable gains arising in the period net of indexation allowance (pre-April 2008 assets).",
            "All allowable deductions including capital allowances and group relief claims.",
            "Total profits chargeable to corporation tax before R&D and patent box reliefs.",
            "Enhanced R&D deduction under SME scheme (230% of qualifying R&D expenditure).",
            "Taxable total profits after all reliefs. This figure determines the corporation tax liability."
        };

        for (int i = 0; i < lineRefs.Length; i++)
        {
            doc.SetCellValue("Trading_Profit", i + 1, 0, lineRefs[i]);
            doc.SetCellValue("Trading_Profit", i + 1, 1, descs[i]);
            doc.SetCellValue("Trading_Profit", i + 1, 2, amounts[i].ToString("F0"));
            doc.SetCellValue("Trading_Profit", i + 1, 3, statRefs[i]);
            doc.SetCellTooltip("Trading_Profit", i + 1, 2, tooltips[i]);
            doc.SetCellTooltip("Trading_Profit", i + 1, 3, $"Statutory authority: {statRefs[i]}");
        }

        var tt1 = doc.GetCellTooltip("Trading_Profit", 1, 2);
        Assert.NotNull(tt1);
        var tt2 = doc.GetCellTooltip("Trading_Profit", 1, 3);
        Assert.NotNull(tt2);
        Assert.Equal(tt1, doc.GetCellTooltip("Trading_Profit", 1, 2)); // consistent

        // Cells without tooltip
        Assert.Null(doc.GetCellTooltip("Trading_Profit", 0, 2)); // header

        // Sheet 2: Tax rate and payment
        doc.AddSheet("Tax_Computation");
        doc.SetCellValue("Tax_Computation", 0, 0, "item");
        doc.SetCellValue("Tax_Computation", 0, 1, "value");

        doc.SetCellValue("Tax_Computation", 1, 0, "Corporation_Tax_Rate_2024");
        doc.SetCellValue("Tax_Computation", 1, 1, "25%");
        doc.SetCellTooltip("Tax_Computation", 1, 1, "Main rate of corporation tax applicable to profits over £250,000. Reduced rates apply for associated companies. See Finance Act 2021 s.6.");

        doc.SetCellValue("Tax_Computation", 2, 0, "Corporation_Tax_Payable");
        doc.SetCellValue("Tax_Computation", 2, 1, "2527500");
        doc.SetCellTooltip("Tax_Computation", 2, 1, "CT payable = Taxable_Total_Profits × Main_Rate. 10,110,000 × 25% = 2,527,500. Due by 1 October 2025 under CTA2010 s.281.");

        var ttRate = doc.GetCellTooltip("Tax_Computation", 1, 1);
        Assert.NotNull(ttRate);
        var ttPayable = doc.GetCellTooltip("Tax_Computation", 2, 1);
        Assert.NotNull(ttPayable);

        // Overwrite tooltip
        doc.SetCellTooltip("Tax_Computation", 1, 1, "Main rate 25% (FY2024). Marginal relief applies £50k-£250k. See FA2023 s.5.");
        var updatedRate = doc.GetCellTooltip("Tax_Computation", 1, 1);
        Assert.NotNull(updatedRate);

        // SaveToFile
        var path = TempFile("hmrc_ct600_computation.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(tt1, loaded.GetCellTooltip("Trading_Profit", 1, 2));
        Assert.NotNull(loaded.GetCellTooltip("Trading_Profit", 1, 3));
        Assert.NotNull(loaded.GetCellTooltip("Tax_Computation", 2, 1));

        // Header cells still have no tooltip
        Assert.Null(loaded.GetCellTooltip("Trading_Profit", 0, 2));

        var ex1 = Record.Exception(() => loaded.GetCellTooltip("Trading_Profit", 1, 2));
        var ex2 = Record.Exception(() => loaded.SetCellTooltip("Trading_Profit", 9, 2, "Appendix note"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
