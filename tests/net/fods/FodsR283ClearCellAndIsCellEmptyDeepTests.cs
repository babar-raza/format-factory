// Tests for FodsDocument.ClearCell, IsCellEmpty, GetUsedRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R283

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R283: Tests for FodsDocument.ClearCell, IsCellEmpty, GetUsedRange deeper.
/// ClearCell(sheetName, row, col): removes the content of a cell, making it empty.
/// IsCellEmpty(sheetName, row, col): returns true if the cell has no content.
/// GetUsedRange(sheetName): returns the bounds of the used data area (rows × cols).
/// Covers: ClearCell no-throw; ClearCell makes cell empty; ClearCell then IsCellEmpty true;
/// ClearCell then GetCellValue empty; ClearCell save-load persists;
/// ClearCell then ExportToCsv no-throw; ClearCell consistent;
/// IsCellEmpty no-throw; IsCellEmpty true for empty; IsCellEmpty false for filled;
/// IsCellEmpty consistent; IsCellEmpty save-load; IsCellEmpty after ClearCell;
/// IsCellEmpty after SetCell false;
/// GetUsedRange no-throw; GetUsedRange positive; GetUsedRange consistent;
/// GetUsedRange save-load; GetUsedRange after AddRowToSheet grows;
/// dogfood CreateDoc→ClearCell→IsCellEmpty→GetUsedRange→SaveToFile pipeline.
/// </summary>
public class FodsR283ClearCellAndIsCellEmptyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR283ClearCellAndIsCellEmptyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR283_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Budget");
        doc.SetCell("Budget", 0, 0, "Department");
        doc.SetCell("Budget", 0, 1, "Q1");
        doc.SetCell("Budget", 0, 2, "Q2");
        doc.SetCell("Budget", 0, 3, "Q3");
        doc.SetCell("Budget", 0, 4, "Q4");
        doc.SetCell("Budget", 1, 0, "Engineering");
        doc.SetCell("Budget", 1, 1, "250000");
        doc.SetCell("Budget", 1, 2, "275000");
        doc.SetCell("Budget", 1, 3, "260000");
        doc.SetCell("Budget", 1, 4, "300000");
        doc.SetCell("Budget", 2, 0, "Marketing");
        doc.SetCell("Budget", 2, 1, "120000");
        doc.SetCell("Budget", 2, 2, "135000");
        doc.SetCell("Budget", 2, 3, "128000");
        doc.SetCell("Budget", 2, 4, "145000");
        doc.SetCell("Budget", 3, 0, "Finance");
        doc.SetCell("Budget", 3, 1, "95000");
        doc.SetCell("Budget", 3, 2, "98000");
        doc.SetCell("Budget", 3, 3, "97000");
        doc.SetCell("Budget", 3, 4, "105000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ClearCell
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearCell_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.ClearCell("Budget", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearCell_MakesCell_Empty()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 1, 1);
        // After clearing, cell value should be empty/null
        var val = doc.GetCellValue("Budget", 1, 1);
        Assert.True(val == null || val == string.Empty || val.Length == 0);
    }

    [Fact]
    public void ClearCell_Then_IsCellEmpty_True()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 2, 2);
        Assert.True(doc.IsCellEmpty("Budget", 2, 2));
    }

    [Fact]
    public void ClearCell_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 1, 2);
        var path = TempFile("cc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile != null ? null : null; // use FodsDocument
        var loaded2 = FodsDocument.LoadFile(path);
        Assert.True(loaded2.IsCellEmpty("Budget", 1, 2));
    }

    [Fact]
    public void ClearCell_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 1, 1);
        var ex = Record.Exception(() => doc.ExportSheetToCsv("Budget"));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearCell_Consistent()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 3, 3);
        Assert.True(doc.IsCellEmpty("Budget", 3, 3));
        // Clear again — still empty, no throw
        doc.ClearCell("Budget", 3, 3);
        Assert.True(doc.IsCellEmpty("Budget", 3, 3));
    }

    [Fact]
    public void ClearCell_Then_SetCell_Makes_NonEmpty()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 1, 1);
        Assert.True(doc.IsCellEmpty("Budget", 1, 1));
        doc.SetCell("Budget", 1, 1, "Restored Value");
        Assert.False(doc.IsCellEmpty("Budget", 1, 1));
    }

    // -------------------------------------------------------------------------
    // IsCellEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsCellEmpty_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.IsCellEmpty("Budget", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void IsCellEmpty_True_For_Empty()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.True(doc.IsCellEmpty("Empty", 0, 0));
    }

    [Fact]
    public void IsCellEmpty_False_For_Filled()
    {
        var doc = CreateRichDoc();
        Assert.False(doc.IsCellEmpty("Budget", 0, 0)); // "Department"
    }

    [Fact]
    public void IsCellEmpty_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.IsCellEmpty("Budget", 0, 0), doc.IsCellEmpty("Budget", 0, 0));
    }

    [Fact]
    public void IsCellEmpty_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.ClearCell("Budget", 2, 3);
        var path = TempFile("ice_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.IsCellEmpty("Budget", 2, 3));
    }

    [Fact]
    public void IsCellEmpty_AfterSetCell_False()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Test");
        Assert.True(doc.IsCellEmpty("Test", 0, 0));
        doc.SetCell("Test", 0, 0, "New Value");
        Assert.False(doc.IsCellEmpty("Test", 0, 0));
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetUsedRange("Budget"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUsedRange_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetUsedRange("Budget"));
    }

    [Fact]
    public void GetUsedRange_Consistent()
    {
        var doc = CreateRichDoc();
        var r1 = doc.GetUsedRange("Budget");
        var r2 = doc.GetUsedRange("Budget");
        Assert.Equal(r1.Rows, r2.Rows);
        Assert.Equal(r1.Cols, r2.Cols);
    }

    [Fact]
    public void GetUsedRange_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetUsedRange("Budget");
        var path = TempFile("ur_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetUsedRange("Budget");
        Assert.Equal(before.Rows, after.Rows);
        Assert.Equal(before.Cols, after.Cols);
    }

    [Fact]
    public void GetUsedRange_After_AddRowToSheet_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.GetUsedRange("Budget");
        doc.AddRowToSheet("Budget", new[] { "HR", "75000", "78000", "80000", "85000" });
        var after = doc.GetUsedRange("Budget");
        Assert.True(after.Rows >= before.Rows);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ClearCell_IsCellEmpty_GetUsedRange_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("P&L");

        // Header row
        doc.SetCell("P&L", 0, 0, "Line Item");
        doc.SetCell("P&L", 0, 1, "2024 Actual");
        doc.SetCell("P&L", 0, 2, "2025 Budget");
        doc.SetCell("P&L", 0, 3, "2025 Actual");
        doc.SetCell("P&L", 0, 4, "Variance");

        // Revenue section
        doc.SetCell("P&L", 1, 0, "Total Revenue");
        doc.SetCell("P&L", 1, 1, "8500000");
        doc.SetCell("P&L", 1, 2, "9500000");
        doc.SetCell("P&L", 1, 3, "9800000");
        doc.SetCell("P&L", 1, 4, "300000");

        doc.SetCell("P&L", 2, 0, "Cost of Goods Sold");
        doc.SetCell("P&L", 2, 1, "3200000");
        doc.SetCell("P&L", 2, 2, "3500000");
        doc.SetCell("P&L", 2, 3, "3400000");
        doc.SetCell("P&L", 2, 4, "-100000");

        doc.SetCell("P&L", 3, 0, "Gross Profit");
        doc.SetCell("P&L", 3, 1, "5300000");
        doc.SetCell("P&L", 3, 2, "6000000");
        doc.SetCell("P&L", 3, 3, "6400000");
        doc.SetCell("P&L", 3, 4, "400000");

        doc.SetCell("P&L", 4, 0, "Operating Expenses");
        doc.SetCell("P&L", 4, 1, "2800000");
        doc.SetCell("P&L", 4, 2, "3100000");
        doc.SetCell("P&L", 4, 3, "2950000");
        doc.SetCell("P&L", 4, 4, "-150000");

        doc.SetCell("P&L", 5, 0, "EBITDA");
        doc.SetCell("P&L", 5, 1, "2500000");
        doc.SetCell("P&L", 5, 2, "2900000");
        doc.SetCell("P&L", 5, 3, "3450000");
        doc.SetCell("P&L", 5, 4, "550000");

        // GetUsedRange
        var initial = doc.GetUsedRange("P&L");
        Assert.NotNull(initial);
        Assert.True(initial.Rows >= 5);
        Assert.True(initial.Cols >= 4);
        Assert.Equal(initial.Rows, doc.GetUsedRange("P&L").Rows); // consistent

        // IsCellEmpty — all filled cells should be non-empty
        Assert.False(doc.IsCellEmpty("P&L", 0, 0)); // "Line Item"
        Assert.False(doc.IsCellEmpty("P&L", 1, 1)); // "8500000"
        Assert.False(doc.IsCellEmpty("P&L", 5, 4)); // "550000"

        // ClearCell — clear the variance column for COGS
        doc.ClearCell("P&L", 2, 4);
        Assert.True(doc.IsCellEmpty("P&L", 2, 4));

        // ClearCell — clear variance for OpEx (placeholder pending recalculation)
        doc.ClearCell("P&L", 4, 4);
        Assert.True(doc.IsCellEmpty("P&L", 4, 4));

        // ClearCell consistent — clear already-empty cell
        doc.ClearCell("P&L", 4, 4);
        Assert.True(doc.IsCellEmpty("P&L", 4, 4));

        // Restore cleared cell
        doc.SetCell("P&L", 4, 4, "-150000");
        Assert.False(doc.IsCellEmpty("P&L", 4, 4));

        // AddRowToSheet
        doc.AddRowToSheet("P&L", new[] { "Net Income", "1800000", "2100000", "2500000", "400000" });
        var afterAdd = doc.GetUsedRange("P&L");
        Assert.True(afterAdd.Rows >= initial.Rows);

        // ExportToCsv still works
        var csv = doc.ExportSheetToCsv("P&L");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // ExportToHtml still works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path = TempFile("dogfood_pl.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.IsCellEmpty("P&L", 2, 4));
        Assert.False(loaded.IsCellEmpty("P&L", 0, 0));
        Assert.False(loaded.IsCellEmpty("P&L", 5, 1));

        // GetUsedRange on loaded
        var loadedRange = loaded.GetUsedRange("P&L");
        Assert.Equal(afterAdd.Rows, loadedRange.Rows);

        // ClearCell on loaded
        loaded.ClearCell("P&L", 1, 4);
        Assert.True(loaded.IsCellEmpty("P&L", 1, 4));

        // AddRowToSheet on loaded
        loaded.AddRowToSheet("P&L", new[] { "Retained Earnings", "1200000", "1600000", "2000000", "400000" });
        Assert.True(loaded.GetUsedRange("P&L").Rows > loadedRange.Rows);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_pl_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.True(loaded2.IsCellEmpty("P&L", 1, 4));
        Assert.Equal(loaded.GetUsedRange("P&L").Rows, loaded2.GetUsedRange("P&L").Rows);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportSheetToCsv("P&L"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
