// Tests for FodsDocument.GetCellFontSize, SetCellFontSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R380

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R380: Tests for FodsDocument.GetCellFontSize, SetCellFontSize deeper.
/// GetCellFontSize(sheetName, row, col): returns the font point size for a cell.
/// SetCellFontSize(sheetName, row, col, size): sets the font point size for a cell.
/// Covers: GetCellFontSize no-throw; GetCellFontSize positive; GetCellFontSize consistent;
/// GetCellFontSize save-load; SetCellFontSize no-throw;
/// SetCellFontSize then GetCellFontSize updated; SetCellFontSize then GetRowCount unchanged;
/// SetCellFontSize then GetCellValue unchanged; SetCellFontSize save-load;
/// SetCellFontSize multiple cells; SetCellFontSize then ExportSheetToCsv no-throw;
/// dogfood CreateDoc→SetCellFontSize→GetCellFontSize→SaveToFile pipeline.
/// </summary>
public class FodsR380GetCellFontSizeAndSetCellFontSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR380GetCellFontSizeAndSetCellFontSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR380_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Metric");
        doc.SetCellValue("Report", 0, 1, "Q1");
        doc.SetCellValue("Report", 0, 2, "Q2");
        doc.SetCellValue("Report", 1, 0, "Revenue");
        doc.SetCellValue("Report", 1, 1, "4250000");
        doc.SetCellValue("Report", 1, 2, "4890000");
        doc.SetCellValue("Report", 2, 0, "EBITDA");
        doc.SetCellValue("Report", 2, 1, "980000");
        doc.SetCellValue("Report", 2, 2, "1120000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellFontSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontSize_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetCellFontSize("Report", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellFontSize_Positive()
    {
        var doc = CreateSampleDoc();
        Assert.True(doc.GetCellFontSize("Report", 0, 0) > 0);
    }

    [Fact]
    public void GetCellFontSize_Consistent()
    {
        var doc = CreateSampleDoc();
        Assert.Equal(doc.GetCellFontSize("Report", 0, 0), doc.GetCellFontSize("Report", 0, 0));
    }

    [Fact]
    public void GetCellFontSize_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellFontSize("Report", 0, 0, 14);
        var before = doc.GetCellFontSize("Report", 0, 0);
        var path = TempFile("fs_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellFontSize("Report", 0, 0));
    }

    // -------------------------------------------------------------------------
    // SetCellFontSize
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontSize_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetCellFontSize("Report", 0, 0, 12));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFontSize_Then_GetCellFontSize_Updated()
    {
        var doc = CreateSampleDoc();
        doc.SetCellFontSize("Report", 0, 1, 16);
        Assert.Equal(16, doc.GetCellFontSize("Report", 0, 1));
    }

    [Fact]
    public void SetCellFontSize_Then_GetRowCount_Unchanged()
    {
        var doc = CreateSampleDoc();
        var before = doc.GetRowCount("Report");
        doc.SetCellFontSize("Report", 0, 0, 14);
        Assert.Equal(before, doc.GetRowCount("Report"));
    }

    [Fact]
    public void SetCellFontSize_Then_GetCellValue_Unchanged()
    {
        var doc = CreateSampleDoc();
        var valueBefore = doc.GetCellValue("Report", 1, 0);
        doc.SetCellFontSize("Report", 1, 0, 11);
        Assert.Equal(valueBefore, doc.GetCellValue("Report", 1, 0));
    }

    [Fact]
    public void SetCellFontSize_SaveLoad_Persists()
    {
        var doc = CreateSampleDoc();
        doc.SetCellFontSize("Report", 0, 0, 18);
        var path = TempFile("sfs_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(18, loaded.GetCellFontSize("Report", 0, 0));
    }

    [Fact]
    public void SetCellFontSize_MultipleCells()
    {
        var doc = CreateSampleDoc();
        doc.SetCellFontSize("Report", 0, 0, 14);
        doc.SetCellFontSize("Report", 0, 1, 12);
        doc.SetCellFontSize("Report", 0, 2, 12);
        Assert.Equal(14, doc.GetCellFontSize("Report", 0, 0));
        Assert.Equal(12, doc.GetCellFontSize("Report", 0, 1));
        Assert.Equal(12, doc.GetCellFontSize("Report", 0, 2));
    }

    [Fact]
    public void SetCellFontSize_Then_ExportSheetToCsv_NoThrow()
    {
        var doc = CreateSampleDoc();
        doc.SetCellFontSize("Report", 1, 1, 10);
        var path = TempFile("export.csv");
        var ex = Record.Exception(() => doc.ExportSheetToCsvFile("Report", path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellFontSize_SetCellFontSize_SaveToFile_Pipeline()
    {
        // Investment banking — J-Curve model: Private Equity fund performance reporting
        // Standardised Excel-like template for LP investor relations reporting (ILPA templates)
        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Fund Summary
        doc.AddSheet("Fund_Summary");
        string[] summaryHeaders = { "Fund_Metrics", "Fund_I", "Fund_II", "Fund_III" };
        for (int c = 0; c < summaryHeaders.Length; c++)
            doc.SetCellValue("Fund_Summary", 0, c, summaryHeaders[c]);

        string[][] summaryData = {
            new[] { "Vintage Year", "2018", "2020", "2022" },
            new[] { "Fund Size (£m)", "500", "750", "1000" },
            new[] { "Invested Capital (£m)", "487", "612", "284" },
            new[] { "Realised Value (£m)", "312", "185", "18" },
            new[] { "Unrealised NAV (£m)", "428", "695", "297" },
            new[] { "Total Value (£m)", "740", "880", "315" },
            new[] { "TVPI (x)", "1.52", "1.44", "1.11" },
            new[] { "DPI (x)", "0.64", "0.30", "0.06" },
            new[] { "RVPI (x)", "0.88", "1.14", "1.05" },
            new[] { "Net IRR (%)", "14.8", "11.2", "N/A" },
        };
        for (int r = 0; r < summaryData.Length; r++)
            for (int c = 0; c < summaryData[r].Length; c++)
                doc.SetCellValue("Fund_Summary", r + 1, c, summaryData[r][c]);

        // Sheet 2: Portfolio Companies
        doc.AddSheet("Portfolio");
        string[] portHeaders = { "Company", "Sector", "Entry_Date", "Cost_Basis_Mm", "NAV_Mm", "MOIC", "Status" };
        for (int c = 0; c < portHeaders.Length; c++)
            doc.SetCellValue("Portfolio", 0, c, portHeaders[c]);

        string[][] portData = {
            new[] { "AlphaTech", "SaaS", "2019-03", "42.5", "98.2", "2.31", "Active" },
            new[] { "BetaHealth", "MedTech", "2019-11", "38.0", "72.1", "1.90", "Active" },
            new[] { "GammaLogistics", "Supply Chain", "2020-06", "55.0", "28.4", "0.52", "Active" },
            new[] { "DeltaFinance", "FinTech", "2020-02", "30.0", "89.5", "2.98", "Active" },
            new[] { "EpsilonRetail", "eCommerce", "2018-09", "45.0", "0.0", "0.00", "Written-Off" },
            new[] { "ZetaEnergy", "CleanTech", "2021-04", "60.0", "105.0", "1.75", "Active" },
            new[] { "EtaMedia", "Digital Media", "2019-07", "22.0", "68.0", "3.09", "Partially Realised" },
        };
        for (int r = 0; r < portData.Length; r++)
            for (int c = 0; c < portData[r].Length; c++)
                doc.SetCellValue("Portfolio", r + 1, c, portData[r][c]);

        Assert.Equal(2, doc.GetSheetCount());

        // GetCellFontSize — baseline
        var defaultFontSize = doc.GetCellFontSize("Fund_Summary", 0, 0);
        Assert.True(defaultFontSize > 0);

        // SetCellFontSize — title row larger
        for (int c = 0; c < summaryHeaders.Length; c++)
            doc.SetCellFontSize("Fund_Summary", 0, c, 14);

        // Verify title row font size
        for (int c = 0; c < summaryHeaders.Length; c++)
            Assert.Equal(14, doc.GetCellFontSize("Fund_Summary", 0, c));

        // Data rows: standard size
        for (int r = 1; r <= summaryData.Length; r++)
            for (int c = 0; c < summaryHeaders.Length; c++)
                doc.SetCellFontSize("Fund_Summary", r, c, 10);

        // IRR row: slightly larger for emphasis
        doc.SetCellFontSize("Fund_Summary", summaryData.Length, 0, 11);

        // Portfolio sheet headers
        for (int c = 0; c < portHeaders.Length; c++)
            doc.SetCellFontSize("Portfolio", 0, c, 12);

        // Written-off company: smaller font to de-emphasise
        doc.SetCellFontSize("Portfolio", 5, 0, 9); // EpsilonRetail

        // Consistent
        Assert.Equal(14, doc.GetCellFontSize("Fund_Summary", 0, 0));
        Assert.Equal(doc.GetCellFontSize("Fund_Summary", 0, 0),
                     doc.GetCellFontSize("Fund_Summary", 0, 0));

        // Row counts unchanged
        Assert.Equal(11, doc.GetRowCount("Fund_Summary"));
        Assert.Equal(8, doc.GetRowCount("Portfolio"));

        // Cell values preserved
        Assert.Equal("AlphaTech", doc.GetCellValue("Portfolio", 1, 0));
        Assert.Equal("2.31", doc.GetCellValue("Portfolio", 1, 5));

        // ExportSheetToCsvFile
        var csvPath = TempFile("portfolio.csv");
        var exCsv = Record.Exception(() => doc.ExportSheetToCsvFile("Portfolio", csvPath));
        Assert.Null(exCsv);

        // SaveToFile
        var path = TempFile("dogfood_pe_reporting.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetSheetCount());
        Assert.Equal(14, loaded.GetCellFontSize("Fund_Summary", 0, 0));
        Assert.Equal(10, loaded.GetCellFontSize("Fund_Summary", 1, 0));
        Assert.Equal(12, loaded.GetCellFontSize("Portfolio", 0, 0));
        Assert.Equal(9, loaded.GetCellFontSize("Portfolio", 5, 0));
        Assert.Equal("AlphaTech", loaded.GetCellValue("Portfolio", 1, 0));

        // Update on loaded
        loaded.SetCellFontSize("Fund_Summary", 0, 0, 16);
        Assert.Equal(16, loaded.GetCellFontSize("Fund_Summary", 0, 0));

        // Final save
        var path2 = TempFile("dogfood_pe_reporting_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(16, loaded2.GetCellFontSize("Fund_Summary", 0, 0));
        var ex1 = Record.Exception(() => loaded2.GetCellFontSize("Portfolio", 0, 0));
        var ex2 = Record.Exception(() => loaded2.SetCellFontSize("Portfolio", 0, 0, 13));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
