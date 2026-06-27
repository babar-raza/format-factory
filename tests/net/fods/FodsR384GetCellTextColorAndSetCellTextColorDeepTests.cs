// Tests for FodsDocument.GetCellTextColor, SetCellTextColor deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R384

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R384: Tests for FodsDocument.GetCellTextColor, SetCellTextColor deeper.
/// GetCellTextColor(sheetName, row, col): returns the text colour of the specified cell.
/// SetCellTextColor(sheetName, row, col, color): sets the text colour of the specified cell.
/// Covers: GetCellTextColor no-throw; GetCellTextColor non-null; GetCellTextColor consistent;
/// GetCellTextColor save-load; SetCellTextColor no-throw;
/// SetCellTextColor then GetCellTextColor updated; SetCellTextColor value unchanged;
/// SetCellTextColor then GetSheetCount unchanged; SetCellTextColor then ExportToHtml no-throw;
/// SetCellTextColor override; SetCellTextColor save-load; SetCellTextColor then GetRowCount unchanged;
/// dogfood CreateDoc→SetCellTextColor→GetCellTextColor→SaveToFile pipeline.
/// </summary>
public class FodsR384GetCellTextColorAndSetCellTextColorDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR384GetCellTextColorAndSetCellTextColorDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR384_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Metric");
        doc.SetCellValue("Report", 0, 1, "Q1");
        doc.SetCellValue("Report", 0, 2, "Q2");
        doc.SetCellValue("Report", 1, 0, "Revenue");
        doc.SetCellValue("Report", 1, 1, "1200000");
        doc.SetCellValue("Report", 1, 2, "1350000");
        doc.SetCellValue("Report", 2, 0, "Costs");
        doc.SetCellValue("Report", 2, 1, "900000");
        doc.SetCellValue("Report", 2, 2, "980000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellTextColor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTextColor_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetCellTextColor("Report", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellTextColor_NonNull()
    {
        var doc = CreatePlainDoc();
        Assert.NotNull(doc.GetCellTextColor("Report", 0, 0));
    }

    [Fact]
    public void GetCellTextColor_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetCellTextColor("Report", 1, 1), doc.GetCellTextColor("Report", 1, 1));
    }

    [Fact]
    public void GetCellTextColor_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.SetCellTextColor("Report", 0, 0, "#CC0000");
        var before = doc.GetCellTextColor("Report", 0, 0);
        var path = TempFile("gtc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellTextColor("Report", 0, 0));
    }

    // -------------------------------------------------------------------------
    // SetCellTextColor
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellTextColor_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.SetCellTextColor("Report", 0, 0, "#FF0000"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellTextColor_Then_GetCellTextColor_Updated()
    {
        var doc = CreatePlainDoc();
        doc.SetCellTextColor("Report", 1, 1, "#0000FF");
        Assert.Equal("#0000FF", doc.GetCellTextColor("Report", 1, 1));
    }

    [Fact]
    public void SetCellTextColor_ValueUnchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCellValue("Report", 1, 1);
        doc.SetCellTextColor("Report", 1, 1, "#008000");
        Assert.Equal(before, doc.GetCellValue("Report", 1, 1));
    }

    [Fact]
    public void SetCellTextColor_Then_GetSheetCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetSheetCount();
        doc.SetCellTextColor("Report", 0, 0, "#FF0000");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetCellTextColor_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetCellTextColor("Report", 0, 0, "#CC0000");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellTextColor_Override()
    {
        var doc = CreatePlainDoc();
        doc.SetCellTextColor("Report", 0, 0, "#FF0000");
        doc.SetCellTextColor("Report", 0, 0, "#0000FF");
        Assert.Equal("#0000FF", doc.GetCellTextColor("Report", 0, 0));
    }

    [Fact]
    public void SetCellTextColor_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.SetCellTextColor("Report", 1, 0, "#990000");
        var path = TempFile("stc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("#990000", loaded.GetCellTextColor("Report", 1, 0));
    }

    [Fact]
    public void SetCellTextColor_Then_GetRowCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetRowCount("Report");
        doc.SetCellTextColor("Report", 0, 0, "#FF0000");
        Assert.Equal(before, doc.GetRowCount("Report"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellTextColor_SetCellTextColor_SaveToFile_Pipeline()
    {
        // Financial regulatory — UK FCA ICARA (Internal Capital and Risk Assessment) dashboard
        // Traffic-light RAG status colouring for capital adequacy and liquidity metrics
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Capital Adequacy");
        doc.AddSheet("Liquidity");

        // Sheet 1: Capital Adequacy (ICARA metrics)
        doc.SetCellValue("Capital Adequacy", 0, 0, "ICARA Metric");
        doc.SetCellValue("Capital Adequacy", 0, 1, "Threshold");
        doc.SetCellValue("Capital Adequacy", 0, 2, "Actual");
        doc.SetCellValue("Capital Adequacy", 0, 3, "RAG Status");
        doc.SetCellValue("Capital Adequacy", 0, 4, "Action Required");

        string[,] capitalData = {
            { "CET1 Ratio", "12.0%", "14.7%", "GREEN", "None" },
            { "Tier 1 Capital Ratio", "13.5%", "15.2%", "GREEN", "None" },
            { "Total Capital Ratio", "15.5%", "16.1%", "GREEN", "None" },
            { "Leverage Ratio", "3.0%", "4.8%", "GREEN", "None" },
            { "SREP Capital Requirement", "£45.2m", "£62.1m", "GREEN", "None" },
            { "P1 Requirement (Pillar 1)", "£31.4m", "£31.4m", "AMBER", "Review P2A buffer" },
            { "P2A Requirement (Pillar 2A)", "£8.7m", "£7.3m", "RED", "URGENT: Submit capital plan" },
            { "Combined Buffer Requirement", "£5.1m", "£23.4m", "GREEN", "None" }
        };

        for (int i = 0; i < capitalData.GetLength(0); i++)
        {
            for (int j = 0; j < capitalData.GetLength(1); j++)
                doc.SetCellValue("Capital Adequacy", i + 1, j, capitalData[i, j]);
        }

        Assert.Equal(2, doc.GetSheetCount());

        // GetCellTextColor — initially default
        var initialColor = doc.GetCellTextColor("Capital Adequacy", 0, 0);
        Assert.NotNull(initialColor);
        Assert.Equal(doc.GetCellTextColor("Capital Adequacy", 0, 0),
                     doc.GetCellTextColor("Capital Adequacy", 0, 0)); // consistent

        // SetCellTextColor — header row in dark blue
        for (int j = 0; j < 5; j++)
            doc.SetCellTextColor("Capital Adequacy", 0, j, "#003366");

        // RAG colouring: GREEN = dark green, AMBER = orange, RED = dark red
        for (int i = 0; i < capitalData.GetLength(0); i++)
        {
            string rag = capitalData[i, 3];
            string color = rag == "RED" ? "#990000" : rag == "AMBER" ? "#CC6600" : "#006600";
            doc.SetCellTextColor("Capital Adequacy", i + 1, 3, color);
        }

        // Verify RED metric
        Assert.Equal("#990000", doc.GetCellTextColor("Capital Adequacy", 7, 3)); // P2A row
        // Verify GREEN metric
        Assert.Equal("#006600", doc.GetCellTextColor("Capital Adequacy", 1, 3)); // CET1 row
        // Verify AMBER metric
        Assert.Equal("#CC6600", doc.GetCellTextColor("Capital Adequacy", 6, 3)); // P1 row

        // Sheet 2: Liquidity
        doc.SetCellValue("Liquidity", 0, 0, "Liquidity Metric");
        doc.SetCellValue("Liquidity", 0, 1, "Regulatory Minimum");
        doc.SetCellValue("Liquidity", 0, 2, "Actual");
        doc.SetCellValue("Liquidity", 0, 3, "Status");

        string[,] liquidityData = {
            { "LCR (Liquidity Coverage Ratio)", "100%", "142%", "GREEN" },
            { "NSFR (Net Stable Funding Ratio)", "100%", "118%", "GREEN" },
            { "ILAAP Liquidity Stress Buffer", "£18.5m", "£24.3m", "GREEN" },
            { "Wholesale Funding Dependency", "<30%", "27%", "AMBER" },
            { "Customer Deposit Concentration", "<15%", "8%", "GREEN" }
        };

        for (int i = 0; i < liquidityData.GetLength(0); i++)
        {
            for (int j = 0; j < liquidityData.GetLength(1); j++)
                doc.SetCellValue("Liquidity", i + 1, j, liquidityData[i, j]);
        }

        // Header colour for liquidity sheet
        for (int j = 0; j < 4; j++)
            doc.SetCellTextColor("Liquidity", 0, j, "#003366");

        // RAG colouring liquidity
        for (int i = 0; i < liquidityData.GetLength(0); i++)
        {
            string rag = liquidityData[i, 3];
            string color = rag == "RED" ? "#990000" : rag == "AMBER" ? "#CC6600" : "#006600";
            doc.SetCellTextColor("Liquidity", i + 1, 3, color);
        }

        // AMBER funding dependency
        Assert.Equal("#CC6600", doc.GetCellTextColor("Liquidity", 4, 3));

        // Sheet counts unchanged
        Assert.Equal(2, doc.GetSheetCount());

        // Cell values unchanged
        Assert.Equal("CET1 Ratio", doc.GetCellValue("Capital Adequacy", 1, 0));
        Assert.Equal("GREEN", doc.GetCellValue("Capital Adequacy", 1, 3));

        // ExportToHtml no-throw
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile (initial ICARA report)
        var path1 = TempFile("dogfood_icara_rag.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify colours
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal("#990000", loaded.GetCellTextColor("Capital Adequacy", 7, 3));
        Assert.Equal("#006600", loaded.GetCellTextColor("Capital Adequacy", 1, 3));
        Assert.Equal(2, loaded.GetSheetCount());

        // Override: P2A remediated to AMBER after capital injection
        loaded.SetCellValue("Capital Adequacy", 7, 3, "AMBER");
        loaded.SetCellTextColor("Capital Adequacy", 7, 3, "#CC6600");
        Assert.Equal("#CC6600", loaded.GetCellTextColor("Capital Adequacy", 7, 3));
        Assert.Equal("AMBER", loaded.GetCellValue("Capital Adequacy", 7, 3));

        // Final save
        var path2 = TempFile("dogfood_icara_remediated.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var remediated = FodsDocument.LoadFile(path2);
        Assert.Equal("#CC6600", remediated.GetCellTextColor("Capital Adequacy", 7, 3));
        Assert.Equal("AMBER", remediated.GetCellValue("Capital Adequacy", 7, 3));

        var ex1 = Record.Exception(() => remediated.ExportToHtml());
        var ex2 = Record.Exception(() => remediated.SetCellTextColor("Capital Adequacy", 0, 0, "#000000"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
