// Tests for FodsDocument.GetCellAlignment, SetCellAlignment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R378

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R378: Tests for FodsDocument.GetCellAlignment, SetCellAlignment deeper.
/// GetCellAlignment(sheetName, row, col): returns the alignment style for a cell.
/// SetCellAlignment(sheetName, row, col, alignment): sets the cell alignment.
/// Covers: GetCellAlignment no-throw; GetCellAlignment non-null; GetCellAlignment consistent;
/// GetCellAlignment save-load; SetCellAlignment no-throw;
/// SetCellAlignment then GetCellAlignment updated; SetCellAlignment then GetRowCount unchanged;
/// SetCellAlignment then ExportSheetToCsv no-throw; SetCellAlignment save-load;
/// SetCellAlignment multiple cells; SetCellAlignment then GetCellValue unchanged;
/// dogfood CreateDoc→SetCellAlignment→GetCellAlignment→SaveToFile pipeline.
/// </summary>
public class FodsR378GetCellAlignmentAndSetCellAlignmentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR378GetCellAlignmentAndSetCellAlignmentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR378_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Financials");
        doc.SetCellValue("Financials", 0, 0, "Company");
        doc.SetCellValue("Financials", 0, 1, "Revenue");
        doc.SetCellValue("Financials", 0, 2, "EBITDA");
        doc.SetCellValue("Financials", 1, 0, "Alpha Corp");
        doc.SetCellValue("Financials", 1, 1, "125000000");
        doc.SetCellValue("Financials", 1, 2, "28000000");
        doc.SetCellValue("Financials", 2, 0, "Beta Ltd");
        doc.SetCellValue("Financials", 2, 1, "87500000");
        doc.SetCellValue("Financials", 2, 2, "19200000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellAlignment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellAlignment_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetCellAlignment("Financials", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellAlignment_NonNull()
    {
        var doc = CreateSampleDoc();
        Assert.NotNull(doc.GetCellAlignment("Financials", 0, 0));
    }

    [Fact]
    public void GetCellAlignment_Consistent()
    {
        var doc = CreateSampleDoc();
        Assert.Equal(doc.GetCellAlignment("Financials", 0, 0), doc.GetCellAlignment("Financials", 0, 0));
    }

    [Fact]
    public void GetCellAlignment_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellAlignment("Financials", 0, 0, "center");
        var before = doc.GetCellAlignment("Financials", 0, 0);
        var path = TempFile("ca_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellAlignment("Financials", 0, 0));
    }

    // -------------------------------------------------------------------------
    // SetCellAlignment
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellAlignment_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetCellAlignment("Financials", 0, 0, "left"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellAlignment_Then_GetCellAlignment_Updated()
    {
        var doc = CreateSampleDoc();
        doc.SetCellAlignment("Financials", 0, 1, "right");
        Assert.Equal("right", doc.GetCellAlignment("Financials", 0, 1));
    }

    [Fact]
    public void SetCellAlignment_Then_GetRowCount_Unchanged()
    {
        var doc = CreateSampleDoc();
        var before = doc.GetRowCount("Financials");
        doc.SetCellAlignment("Financials", 0, 0, "center");
        Assert.Equal(before, doc.GetRowCount("Financials"));
    }

    [Fact]
    public void SetCellAlignment_Then_ExportSheetToCsv_NoThrow()
    {
        var doc = CreateSampleDoc();
        doc.SetCellAlignment("Financials", 1, 1, "right");
        var path = TempFile("export.csv");
        var ex = Record.Exception(() => doc.ExportSheetToCsvFile("Financials", path));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellAlignment_SaveLoad_Persists()
    {
        var doc = CreateSampleDoc();
        doc.SetCellAlignment("Financials", 0, 0, "center");
        var path = TempFile("sca_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("center", loaded.GetCellAlignment("Financials", 0, 0));
    }

    [Fact]
    public void SetCellAlignment_MultipleCells()
    {
        var doc = CreateSampleDoc();
        doc.SetCellAlignment("Financials", 0, 0, "left");
        doc.SetCellAlignment("Financials", 0, 1, "center");
        doc.SetCellAlignment("Financials", 0, 2, "right");
        Assert.Equal("left", doc.GetCellAlignment("Financials", 0, 0));
        Assert.Equal("center", doc.GetCellAlignment("Financials", 0, 1));
        Assert.Equal("right", doc.GetCellAlignment("Financials", 0, 2));
    }

    [Fact]
    public void SetCellAlignment_Then_GetCellValue_Unchanged()
    {
        var doc = CreateSampleDoc();
        var valueBefore = doc.GetCellValue("Financials", 1, 0);
        doc.SetCellAlignment("Financials", 1, 0, "right");
        Assert.Equal(valueBefore, doc.GetCellValue("Financials", 1, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellAlignment_GetCellAlignment_SaveToFile_Pipeline()
    {
        // Financial regulation — FCA Capital Requirements Directive IV (CRD IV)
        // Bank supervisory reporting: COREP/FINREP template with cell alignment standards
        var doc = FodsDocument.CreateEmpty();

        // COREP — Own Funds (C 01.00)
        doc.AddSheet("C01_OwnFunds");
        string[] fundHeaders = { "Reference", "Item", "Amount_GBP000", "Prior_Quarter", "Change_Pct", "Pillar_1_Req" };
        for (int c = 0; c < fundHeaders.Length; c++)
            doc.SetCellValue("C01_OwnFunds", 0, c, fundHeaders[c]);

        string[][] fundData = {
            new[] { "C1.1", "Common Equity Tier 1 capital", "4850000", "4720000", "2.75", "4500000" },
            new[] { "C1.2", "Additional Tier 1 instruments", "250000", "250000", "0.00", "0" },
            new[] { "C1.3", "Tier 1 capital", "5100000", "4970000", "2.62", "6000000" },
            new[] { "C1.4", "Tier 2 instruments", "800000", "800000", "0.00", "0" },
            new[] { "C1.5", "Total regulatory capital", "5900000", "5770000", "2.25", "6000000" },
            new[] { "C1.6", "Total risk exposure amount", "60000000", "58500000", "2.56", "0" },
            new[] { "C1.7", "CET1 ratio", "8.08", "8.07", "0.01", "7.50" },
            new[] { "C1.8", "T1 ratio", "8.50", "8.49", "0.01", "8.50" },
            new[] { "C1.9", "Total Capital ratio", "9.83", "9.86", "-0.03", "10.50" },
        };
        for (int r = 0; r < fundData.Length; r++)
            for (int c = 0; c < fundData[r].Length; c++)
                doc.SetCellValue("C01_OwnFunds", r + 1, c, fundData[r][c]);

        // FINREP — Balance Sheet Assets (F 01.01)
        doc.AddSheet("F01_BalanceSheet");
        string[] bsHeaders = { "Reference", "Asset_Class", "Gross_Carrying_Amount", "Accumulated_Impairment", "Net_Amount" };
        for (int c = 0; c < bsHeaders.Length; c++)
            doc.SetCellValue("F01_BalanceSheet", 0, c, bsHeaders[c]);
        string[][] bsData = {
            new[] { "F1.1", "Cash and cash equivalents", "1200000", "0", "1200000" },
            new[] { "F1.2", "Loans and advances to banks", "8500000", "12000", "8488000" },
            new[] { "F1.3", "Loans and advances to customers", "42000000", "850000", "41150000" },
            new[] { "F1.4", "Debt securities", "6800000", "25000", "6775000" },
            new[] { "F1.5", "Equity instruments", "1100000", "0", "1100000" },
            new[] { "F1.6", "Derivatives", "2200000", "0", "2200000" },
            new[] { "F1.7", "Total assets", "61800000", "887000", "60913000" },
        };
        for (int r = 0; r < bsData.Length; r++)
            for (int c = 0; c < bsData[r].Length; c++)
                doc.SetCellValue("F01_BalanceSheet", r + 1, c, bsData[r][c]);

        Assert.Equal(2, doc.GetSheetCount());

        // SetCellAlignment — COREP headers: center
        for (int c = 0; c < fundHeaders.Length; c++)
            doc.SetCellAlignment("C01_OwnFunds", 0, c, "center");

        // Verify header alignment
        for (int c = 0; c < fundHeaders.Length; c++)
            Assert.Equal("center", doc.GetCellAlignment("C01_OwnFunds", 0, c));

        // GetCellAlignment consistent
        Assert.Equal(doc.GetCellAlignment("C01_OwnFunds", 0, 0),
                     doc.GetCellAlignment("C01_OwnFunds", 0, 0));

        // Reference column: left; numeric columns: right
        for (int r = 1; r <= fundData.Length; r++)
        {
            doc.SetCellAlignment("C01_OwnFunds", r, 0, "left");  // reference
            doc.SetCellAlignment("C01_OwnFunds", r, 1, "left");  // text
            for (int c = 2; c < fundHeaders.Length; c++)
                doc.SetCellAlignment("C01_OwnFunds", r, c, "right"); // numeric
        }

        // Spot check
        Assert.Equal("left", doc.GetCellAlignment("C01_OwnFunds", 1, 0));
        Assert.Equal("left", doc.GetCellAlignment("C01_OwnFunds", 1, 1));
        Assert.Equal("right", doc.GetCellAlignment("C01_OwnFunds", 1, 2));

        // Balance sheet headers: center
        for (int c = 0; c < bsHeaders.Length; c++)
            doc.SetCellAlignment("F01_BalanceSheet", 0, c, "center");

        // Numeric alignment on balance sheet
        for (int r = 1; r <= bsData.Length; r++)
            for (int c = 2; c < bsHeaders.Length; c++)
                doc.SetCellAlignment("F01_BalanceSheet", r, c, "right");

        // Row counts unchanged
        Assert.Equal(10, doc.GetRowCount("C01_OwnFunds"));
        Assert.Equal(8, doc.GetRowCount("F01_BalanceSheet"));

        // Cell values preserved after alignment changes
        Assert.Equal("Common Equity Tier 1 capital", doc.GetCellValue("C01_OwnFunds", 1, 1));
        Assert.Equal("4850000", doc.GetCellValue("C01_OwnFunds", 1, 2));

        // ExportSheetToCsvFile no-throw
        var csvPath = TempFile("corep_c01.csv");
        var exCsv = Record.Exception(() => doc.ExportSheetToCsvFile("C01_OwnFunds", csvPath));
        Assert.Null(exCsv);
        Assert.True(File.Exists(csvPath));

        // SaveToFile
        var path = TempFile("dogfood_corep_finrep.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetSheetCount());
        Assert.Equal("center", loaded.GetCellAlignment("C01_OwnFunds", 0, 0));
        Assert.Equal("right", loaded.GetCellAlignment("C01_OwnFunds", 1, 2));
        Assert.Equal("left", loaded.GetCellAlignment("C01_OwnFunds", 1, 0));
        Assert.Equal("center", loaded.GetCellAlignment("F01_BalanceSheet", 0, 0));
        Assert.Equal("right", loaded.GetCellAlignment("F01_BalanceSheet", 1, 2));
        Assert.Equal("Common Equity Tier 1 capital", loaded.GetCellValue("C01_OwnFunds", 1, 1));

        // Additional alignment updates on loaded
        loaded.SetCellAlignment("C01_OwnFunds", 0, 0, "left");
        Assert.Equal("left", loaded.GetCellAlignment("C01_OwnFunds", 0, 0));

        // Final save
        var path2 = TempFile("dogfood_corep_finrep_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal("left", loaded2.GetCellAlignment("C01_OwnFunds", 0, 0));
        var ex1 = Record.Exception(() => loaded2.GetCellAlignment("F01_BalanceSheet", 0, 0));
        var ex2 = Record.Exception(() => loaded2.SetCellAlignment("F01_BalanceSheet", 0, 0, "center"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
