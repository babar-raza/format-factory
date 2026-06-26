// Tests for FodsDocument.DeleteRows dedicated coverage.
// Sprint: ff-sprint-s198-dotnet-deepening-20260629
// Ledger: PC-FODS-R211

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R211: Dedicated tests for FodsDocument.DeleteRows(string sheetName, int startRow, int count).
/// null/whitespace sheetName → ArgumentException.
/// Nonexistent sheet → InvalidOperationException.
/// Negative startRow → ArgumentOutOfRangeException.
/// count &lt;= 0 → ArgumentOutOfRangeException.
/// Valid: row count decreases by count.
/// Valid: specified rows removed from sheet.
/// Valid: rows after deleted region shift up.
/// SheetCount unchanged after delete.
/// Dogfood: delete-then-insert; delete all rows leaves empty sheet.
/// </summary>
public class FodsR211DeleteRowsDedicatedTests
{
    private static readonly string MinimalPath =
        System.IO.Path.Combine("samples", "by-format", "fods", "minimal-spreadsheet.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows(null!, 0, 1));
    }

    [Fact]
    public void DeleteRows_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows("   ", 0, 1));
    }

    [Fact]
    public void DeleteRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.DeleteRows("NoSuch", 0, 1));
    }

    [Fact]
    public void DeleteRows_NegativeStartRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        doc.InsertRow(sheet.Name!, 0);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows(sheet.Name!, -1, 1));
    }

    [Fact]
    public void DeleteRows_ZeroCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        doc.InsertRow(sheet.Name!, 0);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows(sheet.Name!, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_OneRow_RowCountDecreases()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        int before = sheet.Rows.Count;
        Assert.True(before > 0, "Expected non-empty sheet.");
        doc.DeleteRows(sheet.Name!, 0, 1);
        Assert.Equal(before - 1, sheet.Rows.Count);
    }

    [Fact]
    public void DeleteRows_SheetCountUnchanged()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        doc.DeleteRows(doc.Sheets[0].Name!, 0, 1);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void DeleteRows_RowsShiftUp_AfterDelete()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Data");
        doc.InsertRow(sheet.Name!, 0);
        doc.InsertRow(sheet.Name!, 1);
        doc.InsertRow(sheet.Name!, 2);
        FodsDocument.SetCellValue(sheet, 0, 0, "First");
        FodsDocument.SetCellValue(sheet, 1, 0, "Second");
        FodsDocument.SetCellValue(sheet, 2, 0, "Third");
        // Delete first row
        doc.DeleteRows(sheet.Name!, 0, 1);
        // "Second" should now be at row 0
        Assert.Equal("Second", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DeleteThenInsert_Works()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        doc.DeleteRows(sheet.Name!, 0, 1);
        doc.InsertRow(sheet.Name!, 0);
        FodsDocument.SetCellValue(sheet, 0, 0, "Fresh");
        Assert.Equal("Fresh", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_DeleteAllRows_EmptySheet()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        doc.InsertRow(sheet.Name!, 0);
        doc.InsertRow(sheet.Name!, 1);
        FodsDocument.SetCellValue(sheet, 0, 0, "A");
        FodsDocument.SetCellValue(sheet, 1, 0, "B");
        doc.DeleteRows(sheet.Name!, 0, 2);
        Assert.Equal(0, sheet.Rows.Count);
    }
}
