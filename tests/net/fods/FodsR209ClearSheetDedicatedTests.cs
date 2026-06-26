// Tests for FodsDocument.ClearSheet dedicated coverage.
// Sprint: ff-sprint-s197-dotnet-deepening-20260629
// Ledger: PC-FODS-R209

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R209: Dedicated tests for FodsDocument.ClearSheet(string sheetName).
/// null/whitespace sheetName → ArgumentException.
/// Nonexistent sheet → InvalidOperationException.
/// Already-empty sheet: no exception.
/// Valid: removes all rows from sheet.
/// Valid: row count becomes 0.
/// SheetCount unchanged after clear.
/// Other sheets not affected.
/// Cell value not accessible after clear (GetCellValue returns null/empty).
/// Dogfood: clear then add data works; clear multiple times no exception.
/// </summary>
public class FodsR209ClearSheetDedicatedTests
{
    private static readonly string MinimalPath =
        System.IO.Path.Combine("samples", "by-format", "fods", "minimal-spreadsheet.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.ClearSheet(null!));
    }

    [Fact]
    public void ClearSheet_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.ClearSheet("   "));
    }

    [Fact]
    public void ClearSheet_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.ClearSheet("NoSuch"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_EmptySheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Empty");
        var ex = Record.Exception(() => doc.ClearSheet(sheet.Name!));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearSheet_SheetWithData_RowCountBecomesZero()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        // Ensure there are rows
        var rowsBefore = sheet.Rows.Count;
        Assert.True(rowsBefore > 0, "Expected non-empty sheet for this test.");
        doc.ClearSheet(sheet.Name!);
        Assert.Equal(0, sheet.Rows.Count);
    }

    [Fact]
    public void ClearSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        doc.ClearSheet(doc.Sheets[0].Name!);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ClearSheet_OtherSheetsNotAffected()
    {
        var doc = FodsDocument.CreateNew();
        var sheet1 = doc.GetSheetByName("Sheet1")!;
        var sheet2 = doc.AddSheet("Sheet2");
        FodsDocument.SetCellValue(sheet1, 0, 0, "A");
        FodsDocument.SetCellValue(sheet2, 0, 0, "B");
        doc.ClearSheet(sheet1.Name!);
        // Sheet2 should still have its data
        Assert.Equal("B", FodsDocument.GetCellValue(sheet2, 0, 0));
    }

    [Fact]
    public void ClearSheet_AfterClear_CellValueNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        doc.ClearSheet(sheet.Name!);
        var val = FodsDocument.GetCellValue(sheet, 0, 0);
        Assert.Null(val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ClearThenAddData_Works()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        doc.ClearSheet(sheet.Name!);
        // Now insert a row and set value
        doc.InsertRow(sheet.Name!, 0);
        FodsDocument.SetCellValue(sheet, 0, 0, "NewData");
        Assert.Equal("NewData", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_ClearTwice_NoException()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        doc.ClearSheet(sheet.Name!);
        var ex = Record.Exception(() => doc.ClearSheet(sheet.Name!));
        Assert.Null(ex);
    }
}
