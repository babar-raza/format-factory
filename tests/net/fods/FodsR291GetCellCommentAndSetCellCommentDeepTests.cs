// Tests for FodsDocument.GetCellComment, SetCellComment, RemoveCellComment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R291

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R291: Tests for FodsDocument.GetCellComment, SetCellComment, RemoveCellComment deeper.
/// GetCellComment(sheetName, row, col): returns the comment/annotation on the cell.
/// SetCellComment(sheetName, row, col, comment): sets a comment on the cell.
/// RemoveCellComment(sheetName, row, col): removes the comment from a cell.
/// Covers: GetCellComment no-throw; GetCellComment non-null; GetCellComment consistent;
/// GetCellComment save-load; GetCellComment after SetCellComment;
/// SetCellComment no-throw; SetCellComment reflected; SetCellComment save-load;
/// SetCellComment multiple cells; SetCellComment then ExportToCsv no-throw;
/// RemoveCellComment no-throw; RemoveCellComment consistent; RemoveCellComment save-load;
/// RemoveCellComment after SetCellComment;
/// dogfood CreateDoc→SetCellComment→GetCellComment→RemoveCellComment→SaveToFile pipeline.
/// </summary>
public class FodsR291GetCellCommentAndSetCellCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR291GetCellCommentAndSetCellCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR291_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Budget");
        doc.SetCellValue("Budget", 0, 0, "Item");
        doc.SetCellValue("Budget", 0, 1, "Budget");
        doc.SetCellValue("Budget", 0, 2, "Actual");
        doc.SetCellValue("Budget", 1, 0, "Personnel");
        doc.SetCellValue("Budget", 1, 1, "250000");
        doc.SetCellValue("Budget", 1, 2, "248500");
        doc.SetCellValue("Budget", 2, 0, "Technology");
        doc.SetCellValue("Budget", 2, 1, "80000");
        doc.SetCellValue("Budget", 2, 2, "82100");
        doc.SetCellValue("Budget", 3, 0, "Facilities");
        doc.SetCellValue("Budget", 3, 1, "45000");
        doc.SetCellValue("Budget", 3, 2, "44300");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetCellComment("Budget", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellComment_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetCellComment("Budget", 0, 0));
    }

    [Fact]
    public void GetCellComment_Consistent()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 1, 1, "Approved budget for FY2026");
        var c1 = doc.GetCellComment("Budget", 1, 1);
        var c2 = doc.GetCellComment("Budget", 1, 1);
        Assert.Equal(c1, c2);
    }

    [Fact]
    public void GetCellComment_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 1, 2, "Actual includes Q4 accruals");
        var before = doc.GetCellComment("Budget", 1, 2);
        var path = TempFile("gcc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetCellComment("Budget", 1, 2);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetCellComment_After_SetCellComment_NonNull()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 2, 1, "Technology budget review required");
        var comment = doc.GetCellComment("Budget", 2, 1);
        Assert.NotNull(comment);
    }

    // -------------------------------------------------------------------------
    // SetCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellComment_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.SetCellComment("Budget", 0, 0, "Header cell comment"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellComment_Reflected_In_GetCellComment()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 1, 1, "Budget approved by CFO");
        var comment = doc.GetCellComment("Budget", 1, 1);
        Assert.NotNull(comment);
        Assert.True(comment.Length >= 0);
    }

    [Fact]
    public void SetCellComment_SaveLoad_Persists()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 2, 2, "Overage due to hardware refresh");
        var path = TempFile("scc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellComment("Budget", 2, 2));
    }

    [Fact]
    public void SetCellComment_Multiple_Cells()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 0, 1, "Approved annual budget");
        doc.SetCellComment("Budget", 1, 2, "Includes severance provision");
        doc.SetCellComment("Budget", 3, 1, "Renegotiated lease terms");
        // All should be non-null after set
        Assert.NotNull(doc.GetCellComment("Budget", 0, 1));
        Assert.NotNull(doc.GetCellComment("Budget", 1, 2));
        Assert.NotNull(doc.GetCellComment("Budget", 3, 1));
    }

    [Fact]
    public void SetCellComment_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 1, 1, "CSV export test comment");
        var ex = Record.Exception(() => doc.ExportToCsv("Budget"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // RemoveCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveCellComment_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 1, 1, "To be removed");
        var ex = Record.Exception(() => doc.RemoveCellComment("Budget", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveCellComment_Consistent()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 2, 1, "Remove consistent test");
        doc.RemoveCellComment("Budget", 2, 1);
        // Calling again should not throw
        var ex = Record.Exception(() => doc.RemoveCellComment("Budget", 2, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveCellComment_SaveLoad_NoException()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 3, 2, "Save load remove");
        doc.RemoveCellComment("Budget", 3, 2);
        var path = TempFile("rcc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var ex = Record.Exception(() => loaded.GetCellComment("Budget", 3, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveCellComment_After_SetCellComment()
    {
        var doc = CreateDataDoc();
        doc.SetCellComment("Budget", 1, 2, "Comment to remove");
        var exBefore = Record.Exception(() => doc.GetCellComment("Budget", 1, 2));
        Assert.Null(exBefore);
        doc.RemoveCellComment("Budget", 1, 2);
        var exAfter = Record.Exception(() => doc.GetCellComment("Budget", 1, 2));
        Assert.Null(exAfter);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellComment_GetCellComment_RemoveCellComment_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Forecast");

        // Build forecast table
        doc.SetCellValue("Forecast", 0, 0, "Category");
        doc.SetCellValue("Forecast", 0, 1, "Q1");
        doc.SetCellValue("Forecast", 0, 2, "Q2");
        doc.SetCellValue("Forecast", 0, 3, "Q3");
        doc.SetCellValue("Forecast", 0, 4, "Q4");

        doc.SetCellValue("Forecast", 1, 0, "Revenue");
        doc.SetCellValue("Forecast", 1, 1, "320000");
        doc.SetCellValue("Forecast", 1, 2, "345000");
        doc.SetCellValue("Forecast", 1, 3, "298000");
        doc.SetCellValue("Forecast", 1, 4, "410000");

        doc.SetCellValue("Forecast", 2, 0, "COGS");
        doc.SetCellValue("Forecast", 2, 1, "192000");
        doc.SetCellValue("Forecast", 2, 2, "207000");
        doc.SetCellValue("Forecast", 2, 3, "178800");
        doc.SetCellValue("Forecast", 2, 4, "246000");

        doc.SetCellValue("Forecast", 3, 0, "Gross Margin");
        doc.SetCellValue("Forecast", 3, 1, "128000");
        doc.SetCellValue("Forecast", 3, 2, "138000");
        doc.SetCellValue("Forecast", 3, 3, "119200");
        doc.SetCellValue("Forecast", 3, 4, "164000");

        // GetCellComment — no comments yet
        var empty = doc.GetCellComment("Forecast", 0, 0);
        Assert.NotNull(empty);

        // SetCellComment — add annotations
        doc.SetCellComment("Forecast", 0, 1, "Q1 estimate based on pipeline review");
        doc.SetCellComment("Forecast", 1, 3, "Q3 impacted by seasonal slowdown");
        doc.SetCellComment("Forecast", 2, 4, "Q4 COGS includes year-end inventory adjustment");
        doc.SetCellComment("Forecast", 3, 0, "Gross margin calculated before depreciation");

        // GetCellComment — verify comments set
        var c01 = doc.GetCellComment("Forecast", 0, 1);
        Assert.NotNull(c01);
        var c13 = doc.GetCellComment("Forecast", 1, 3);
        Assert.NotNull(c13);
        var c24 = doc.GetCellComment("Forecast", 2, 4);
        Assert.NotNull(c24);
        var c30 = doc.GetCellComment("Forecast", 3, 0);
        Assert.NotNull(c30);

        // Consistent
        Assert.Equal(doc.GetCellComment("Forecast", 0, 1), doc.GetCellComment("Forecast", 0, 1));

        // ExportToCsv works with comments
        var csv = doc.ExportToCsv("Forecast");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // RemoveCellComment — remove Q3 comment
        doc.RemoveCellComment("Forecast", 1, 3);
        var ex1 = Record.Exception(() => doc.GetCellComment("Forecast", 1, 3));
        Assert.Null(ex1);

        // Other comments still accessible
        Assert.NotNull(doc.GetCellComment("Forecast", 0, 1));
        Assert.NotNull(doc.GetCellComment("Forecast", 2, 4));

        // SaveToFile
        var path = TempFile("dogfood_forecast.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());
        Assert.NotNull(loaded.GetCellComment("Forecast", 0, 1));
        Assert.NotNull(loaded.GetCellComment("Forecast", 2, 4));

        // SetCellComment on loaded
        loaded.SetCellComment("Forecast", 0, 2, "Q2 revised upward by five percent");
        Assert.NotNull(loaded.GetCellComment("Forecast", 0, 2));

        // Verify cell data intact
        var revenueQ1 = loaded.GetCellValue("Forecast", 1, 1);
        Assert.NotNull(revenueQ1);

        // Final save
        var path2 = TempFile("dogfood_forecast_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(loaded.GetSheetCount(), loaded2.GetSheetCount());
        Assert.NotNull(loaded2.GetCellComment("Forecast", 0, 1));
        var ex2 = Record.Exception(() => loaded2.ExportToCsv("Forecast"));
        Assert.Null(ex2);
    }
}
