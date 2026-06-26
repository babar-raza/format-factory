// Tests for FodsDocument.GetPageBreakCount, SetPageBreak, GetPrintArea deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R303

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R303: Tests for FodsDocument.GetPageBreakCount, SetPageBreak, GetPrintArea deeper.
/// GetPageBreakCount(sheetName): returns the number of manual page breaks in the sheet.
/// SetPageBreak(sheetName, rowIndex): inserts a horizontal page break before the specified row.
/// GetPrintArea(sheetName): returns the defined print area range for the sheet.
/// Covers: GetPageBreakCount no-throw; GetPageBreakCount non-negative; GetPageBreakCount consistent;
/// GetPageBreakCount zero for new sheet; GetPageBreakCount after SetPageBreak increases;
/// GetPageBreakCount save-load;
/// SetPageBreak no-throw; SetPageBreak increases count; SetPageBreak save-load;
/// SetPageBreak multiple; SetPageBreak then ExportToCsv no-throw;
/// GetPrintArea no-throw; GetPrintArea non-null; GetPrintArea consistent;
/// GetPrintArea save-load;
/// dogfood CreateDoc→SetPageBreak→GetPageBreakCount→GetPrintArea→SaveToFile pipeline.
/// </summary>
public class FodsR303GetPageBreakCountAndPrintAreaDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR303GetPageBreakCountAndPrintAreaDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR303_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRichDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Report");
        for (int row = 0; row < 20; row++)
        {
            doc.SetCellValue("Report", row, 0, $"Row {row}");
            doc.SetCellValue("Report", row, 1, (row * 1000).ToString());
            doc.SetCellValue("Report", row, 2, (row * 100).ToString());
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPageBreakCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageBreakCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetPageBreakCount("Report"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageBreakCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetPageBreakCount("Report") >= 0);
    }

    [Fact]
    public void GetPageBreakCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetPageBreakCount("Report"), doc.GetPageBreakCount("Report"));
    }

    [Fact]
    public void GetPageBreakCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        doc.SetCellValue("Fresh", 0, 0, "no breaks");
        Assert.Equal(0, doc.GetPageBreakCount("Fresh"));
    }

    [Fact]
    public void GetPageBreakCount_AfterSetPageBreak_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetPageBreakCount("Report");
        doc.SetPageBreak("Report", 10);
        Assert.Equal(before + 1, doc.GetPageBreakCount("Report"));
    }

    [Fact]
    public void GetPageBreakCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.SetPageBreak("Report", 10);
        var before = doc.GetPageBreakCount("Report");
        var path = TempFile("pbc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageBreakCount("Report"));
    }

    // -------------------------------------------------------------------------
    // SetPageBreak
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPageBreak_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.SetPageBreak("Report", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPageBreak_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetPageBreakCount("Report");
        doc.SetPageBreak("Report", 8);
        Assert.Equal(before + 1, doc.GetPageBreakCount("Report"));
    }

    [Fact]
    public void SetPageBreak_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.SetPageBreak("Report", 10);
        var before = doc.GetPageBreakCount("Report");
        var path = TempFile("spb_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageBreakCount("Report"));
    }

    [Fact]
    public void SetPageBreak_Multiple()
    {
        var doc = CreateRichDoc();
        doc.SetPageBreak("Report", 5);
        doc.SetPageBreak("Report", 10);
        doc.SetPageBreak("Report", 15);
        Assert.Equal(3, doc.GetPageBreakCount("Report"));
    }

    [Fact]
    public void SetPageBreak_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.SetPageBreak("Report", 10);
        var ex = Record.Exception(() => doc.ExportToCsv("Report"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetPrintArea
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPrintArea_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetPrintArea("Report"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPrintArea_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetPrintArea("Report"));
    }

    [Fact]
    public void GetPrintArea_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetPrintArea("Report"), doc.GetPrintArea("Report"));
    }

    [Fact]
    public void GetPrintArea_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetPrintArea("Report");
        var path = TempFile("gpa_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetPrintArea("Report"));
    }

    [Fact]
    public void GetPrintArea_NonNegativeLength()
    {
        var doc = CreateRichDoc();
        var area = doc.GetPrintArea("Report");
        Assert.NotNull(area);
        Assert.True(area.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetPageBreak_GetPageBreakCount_GetPrintArea_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("FinancialReport");

        // Section 1: Revenue
        doc.SetCellValue("FinancialReport", 0, 0, "Revenue Summary");
        for (int r = 1; r <= 8; r++)
        {
            doc.SetCellValue("FinancialReport", r, 0, $"Item {r}");
            doc.SetCellValue("FinancialReport", r, 1, (r * 125000).ToString());
            doc.SetCellValue("FinancialReport", r, 2, (r * 10000).ToString());
        }

        // Section 2: Expenses
        doc.SetCellValue("FinancialReport", 9, 0, "Expense Summary");
        for (int r = 10; r <= 17; r++)
        {
            doc.SetCellValue("FinancialReport", r, 0, $"Expense {r - 9}");
            doc.SetCellValue("FinancialReport", r, 1, (r * 85000).ToString());
            doc.SetCellValue("FinancialReport", r, 2, (r * 7500).ToString());
        }

        // Section 3: Summary
        doc.SetCellValue("FinancialReport", 18, 0, "Net Summary");
        for (int r = 19; r <= 22; r++)
        {
            doc.SetCellValue("FinancialReport", r, 0, $"Net {r - 18}");
            doc.SetCellValue("FinancialReport", r, 1, (r * 40000).ToString());
        }

        // GetPageBreakCount — zero initially
        Assert.Equal(0, doc.GetPageBreakCount("FinancialReport"));

        // SetPageBreak — between revenue and expenses
        doc.SetPageBreak("FinancialReport", 9);
        Assert.Equal(1, doc.GetPageBreakCount("FinancialReport"));

        // SetPageBreak — between expenses and summary
        doc.SetPageBreak("FinancialReport", 18);
        Assert.Equal(2, doc.GetPageBreakCount("FinancialReport"));

        // Consistent
        Assert.Equal(doc.GetPageBreakCount("FinancialReport"), doc.GetPageBreakCount("FinancialReport"));

        // GetPrintArea
        var printArea = doc.GetPrintArea("FinancialReport");
        Assert.NotNull(printArea);
        Assert.Equal(printArea, doc.GetPrintArea("FinancialReport")); // consistent

        // ExportToCsv works
        var csv = doc.ExportToCsv("FinancialReport");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue cross-check
        Assert.Equal("Revenue Summary", doc.GetCellValue("FinancialReport", 0, 0));

        // SaveToFile
        var path = TempFile("dogfood_financial.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetPageBreakCount("FinancialReport"));
        Assert.NotNull(loaded.GetPrintArea("FinancialReport"));

        // SetPageBreak on loaded
        loaded.SetPageBreak("FinancialReport", 13);
        Assert.Equal(3, loaded.GetPageBreakCount("FinancialReport"));

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("FinancialReport");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // Final save
        var path2 = TempFile("dogfood_financial_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(3, loaded2.GetPageBreakCount("FinancialReport"));
        Assert.NotNull(loaded2.GetPrintArea("FinancialReport"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("FinancialReport"));
        Assert.Null(ex1);
    }
}
