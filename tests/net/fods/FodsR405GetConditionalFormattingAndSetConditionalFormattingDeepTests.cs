// Tests for FodsDocument.GetConditionalFormatting, SetConditionalFormatting deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R405

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R405: Tests for FodsDocument.GetConditionalFormatting, SetConditionalFormatting deeper.
/// GetConditionalFormatting(sheet, row, col): returns the conditional formatting rule for a cell, or null if none.
/// SetConditionalFormatting(sheet, row, col, condition, format): sets a conditional formatting rule on a cell.
/// Covers: GetConditionalFormatting no-throw; GetConditionalFormatting null for no-formatting;
/// GetConditionalFormatting consistent; SetConditionalFormatting no-throw;
/// GetConditionalFormatting non-null after SetConditionalFormatting;
/// SetConditionalFormatting save-load consistent; SetConditionalFormatting multiple cells;
/// dogfood CreateDoc→SetConditionalFormatting→GetConditionalFormatting→SaveToFile pipeline.
/// </summary>
public class FodsR405GetConditionalFormattingAndSetConditionalFormattingDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR405GetConditionalFormattingAndSetConditionalFormattingDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR405_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("RiskMatrix");
        doc.SetCellValue("Sheet1", 0, 0, "Risk Score");
        doc.SetCellValue("Sheet1", 0, 1, "Category");
        doc.SetCellValue("Sheet1", 1, 0, "85");
        doc.SetCellValue("Sheet1", 2, 0, "42");
        doc.SetCellValue("Sheet1", 3, 0, "91");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetConditionalFormatting
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConditionalFormatting_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.GetConditionalFormatting("Sheet1", 1, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatting_Null_ForNoFormatting()
    {
        var doc = CreateWorkbook();
        Assert.Null(doc.GetConditionalFormatting("Sheet1", 1, 0));
    }

    [Fact]
    public void GetConditionalFormatting_Consistent()
    {
        var doc = CreateWorkbook();
        var r1 = doc.GetConditionalFormatting("Sheet1", 1, 0);
        var r2 = doc.GetConditionalFormatting("Sheet1", 1, 0);
        Assert.Equal(r1, r2);
    }

    // -------------------------------------------------------------------------
    // SetConditionalFormatting
    // -------------------------------------------------------------------------

    [Fact]
    public void SetConditionalFormatting_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.SetConditionalFormatting("Sheet1", 1, 0, ">=80", "background:red"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConditionalFormatting_NonNull_After_Set()
    {
        var doc = CreateWorkbook();
        doc.SetConditionalFormatting("Sheet1", 1, 0, ">=80", "background:red");
        Assert.NotNull(doc.GetConditionalFormatting("Sheet1", 1, 0));
    }

    [Fact]
    public void SetConditionalFormatting_SaveLoad_Consistent()
    {
        var doc = CreateWorkbook();
        doc.SetConditionalFormatting("Sheet1", 1, 0, ">=80", "background:red");
        var before = doc.GetConditionalFormatting("Sheet1", 1, 0);
        var path = TempFile("cf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetConditionalFormatting("Sheet1", 1, 0));
    }

    [Fact]
    public void SetConditionalFormatting_MultipleCells()
    {
        var doc = CreateWorkbook();
        doc.SetConditionalFormatting("Sheet1", 1, 0, ">=80", "background:red");
        doc.SetConditionalFormatting("Sheet1", 2, 0, "<50", "background:green");
        doc.SetConditionalFormatting("Sheet1", 3, 0, ">=80", "background:red");
        Assert.NotNull(doc.GetConditionalFormatting("Sheet1", 1, 0));
        Assert.NotNull(doc.GetConditionalFormatting("Sheet1", 2, 0));
        Assert.NotNull(doc.GetConditionalFormatting("Sheet1", 3, 0));
        Assert.Null(doc.GetConditionalFormatting("Sheet1", 0, 0)); // header: no formatting
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetConditionalFormatting_SetConditionalFormatting_SaveToFile_Pipeline()
    {
        // Finance — PRA Supervisory Review and Evaluation Process (SREP)
        // Capital adequacy heat-map workbook: conditional formatting flags breaches
        // ICAAP stress test results with RAG (Red/Amber/Green) status indicators

        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: CET1 Capital Ratios — trigger red if below 8% (P2A threshold)
        doc.AddSheet("CET1_Ratios");
        doc.SetCellValue("Sheet1", 0, 0, "Bank");
        doc.SetCellValue("Sheet1", 0, 1, "CET1_Ratio_Pct");
        doc.SetCellValue("Sheet1", 0, 2, "P2A_Requirement_Pct");
        doc.SetCellValue("Sheet1", 0, 3, "Headroom_Pct");
        doc.SetCellValue("Sheet1", 0, 4, "RAG_Status");

        string[] banks = {
            "Barclays", "HSBC", "Lloyds", "NatWest", "Standard Chartered",
            "Santander UK", "Metro Bank", "Virgin Money", "Aldermore", "Secure Trust"
        };
        double[] cet1 = { 14.2, 15.8, 13.1, 14.9, 16.3, 11.8, 9.2, 12.6, 13.8, 10.1 };
        double[] p2a  = {  3.5,  3.2,  3.8,  3.4,  2.9,  4.1,  5.2,  3.9,  4.4,  4.8 };

        for (int i = 0; i < banks.Length; i++)
        {
            double headroom = cet1[i] - (4.5 + p2a[i]); // vs min CET1 + P2A
            string rag = headroom >= 3.0 ? "GREEN" : headroom >= 1.0 ? "AMBER" : "RED";
            doc.SetCellValue("Sheet1", i + 1, 0, banks[i]);
            doc.SetCellValue("Sheet1", i + 1, 1, cet1[i].ToString("F1"));
            doc.SetCellValue("Sheet1", i + 1, 2, p2a[i].ToString("F1"));
            doc.SetCellValue("Sheet1", i + 1, 3, headroom.ToString("F1"));
            doc.SetCellValue("Sheet1", i + 1, 4, rag);
        }

        // Apply conditional formatting: RED for CET1 < 10%, AMBER for 10-12%, GREEN >= 12%
        for (int i = 0; i < banks.Length; i++)
        {
            string cond = cet1[i] < 10.0 ? "<10" : cet1[i] < 12.0 ? "<12" : ">=12";
            string fmt = cet1[i] < 10.0 ? "background:red;color:white" :
                         cet1[i] < 12.0 ? "background:orange" : "background:lightgreen";
            doc.SetConditionalFormatting("Sheet1", i + 1, 1, cond, fmt);
        }

        // Verify no formatting on header row
        Assert.Null(doc.GetConditionalFormatting("Sheet1", 0, 1));

        // Verify formatting set on data rows
        for (int i = 0; i < banks.Length; i++)
            Assert.NotNull(doc.GetConditionalFormatting("Sheet1", i + 1, 1));

        // Verify consistent
        var cf3 = doc.GetConditionalFormatting("Sheet1", 3, 1);
        Assert.Equal(cf3, doc.GetConditionalFormatting("Sheet1", 3, 1));

        // Sheet 2: Leverage Ratios — flag below 3.25% (UK minimum)
        doc.AddSheet("Leverage_Ratios");
        double[] leverage = { 5.2, 6.1, 4.8, 5.5, 7.2, 4.1, 3.4, 4.6, 5.0, 3.8 };
        doc.SetCellValue("Leverage_Ratios", 0, 0, "Bank");
        doc.SetCellValue("Leverage_Ratios", 0, 1, "Leverage_Ratio_Pct");
        doc.SetCellValue("Leverage_Ratios", 0, 2, "Min_Requirement_Pct");
        doc.SetCellValue("Leverage_Ratios", 0, 3, "Status");

        for (int i = 0; i < banks.Length; i++)
        {
            string status = leverage[i] >= 4.0 ? "PASS" : leverage[i] >= 3.25 ? "MARGINAL" : "BREACH";
            doc.SetCellValue("Leverage_Ratios", i + 1, 0, banks[i]);
            doc.SetCellValue("Leverage_Ratios", i + 1, 1, leverage[i].ToString("F1"));
            doc.SetCellValue("Leverage_Ratios", i + 1, 2, "3.25");
            doc.SetCellValue("Leverage_Ratios", i + 1, 3, status);

            string lvCond = leverage[i] < 3.25 ? "<3.25" : leverage[i] < 4.0 ? "<4" : ">=4";
            string lvFmt = leverage[i] < 3.25 ? "background:red;font-weight:bold" :
                           leverage[i] < 4.0 ? "background:yellow" : "background:lightgreen";
            doc.SetConditionalFormatting("Leverage_Ratios", i + 1, 1, lvCond, lvFmt);
        }

        // Verify leverage formatting
        for (int i = 0; i < banks.Length; i++)
            Assert.NotNull(doc.GetConditionalFormatting("Leverage_Ratios", i + 1, 1));
        Assert.Null(doc.GetConditionalFormatting("Leverage_Ratios", 0, 1));

        // Basic assertions
        Assert.True(doc.GetSheetCount() >= 2);
        Assert.True(doc.GetRowCount("Sheet1") > 0);

        // SaveToFile
        var path1 = TempFile("dogfood_pra_srep_heatmap.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify formatting persisted
        var loaded = FodsDocument.LoadFile(path1);
        for (int i = 0; i < banks.Length; i++)
            Assert.NotNull(loaded.GetConditionalFormatting("Sheet1", i + 1, 1));
        Assert.Null(loaded.GetConditionalFormatting("Sheet1", 0, 1));

        var cf3Loaded = loaded.GetConditionalFormatting("Sheet1", 3, 1);
        Assert.Equal(cf3, cf3Loaded);

        // Add MREL sheet
        loaded.AddSheet("MREL_Requirements");
        double[] mrel = { 28.5, 31.2, 26.8, 29.1, 33.4, 24.6, 20.1, 25.5, 22.8, 23.4 };
        loaded.SetCellValue("MREL_Requirements", 0, 0, "Bank");
        loaded.SetCellValue("MREL_Requirements", 0, 1, "MREL_RWA_Pct");

        for (int i = 0; i < banks.Length; i++)
        {
            loaded.SetCellValue("MREL_Requirements", i + 1, 0, banks[i]);
            loaded.SetCellValue("MREL_Requirements", i + 1, 1, mrel[i].ToString("F1"));
            string mrelCond = mrel[i] < 22.0 ? "<22" : ">=22";
            string mrelFmt = mrel[i] < 22.0 ? "background:red" : "background:lightgreen";
            loaded.SetConditionalFormatting("MREL_Requirements", i + 1, 1, mrelCond, mrelFmt);
        }

        // Final save
        var path2 = TempFile("dogfood_pra_srep_heatmap_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);

        // Verify all formatting on all sheets
        for (int i = 0; i < banks.Length; i++)
        {
            Assert.NotNull(final.GetConditionalFormatting("Sheet1", i + 1, 1));
            Assert.NotNull(final.GetConditionalFormatting("MREL_Requirements", i + 1, 1));
        }
        Assert.True(final.GetSheetCount() >= 3);

        var ex1 = Record.Exception(() => final.GetConditionalFormatting("Sheet1", 1, 1));
        var ex2 = Record.Exception(() => final.SetConditionalFormatting("Sheet1", 1, 1, ">15", "background:blue"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
