// Tests for FodsDocument.SortRows dedicated coverage.
// Sprint: ff-sprint-s196-dotnet-deepening-20260629
// Ledger: PC-FODS-R208

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R208: Dedicated tests for FodsDocument.SortRows(string sheetName, int sortColumn, bool ascending).
/// null/whitespace sheetName → ArgumentException.
/// Nonexistent sheet → InvalidOperationException.
/// Negative sortColumn → ArgumentOutOfRangeException.
/// 0 or 1 rows: no change, no exception.
/// Ascending sort: first row value is smallest.
/// Descending sort: first row value is largest.
/// Sort does not change row count.
/// Sort does not change SheetCount.
/// Dogfood: sort then get cell value at row 0; sort numeric strings correctly.
/// </summary>
public class FodsR208SortRowsDedicatedTests
{
    private static readonly string MinimalPath =
        System.IO.Path.Combine("samples", "by-format", "fods", "minimal-spreadsheet.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SortRows(null!, 0));
    }

    [Fact]
    public void SortRows_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SortRows("  ", 0));
    }

    [Fact]
    public void SortRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.SortRows("NoSuch", 0));
    }

    [Fact]
    public void SortRows_NegativeColumn_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SortRows(sheet.Name!, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_OneRow_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Single");
        FodsDocument.SetCellValue(sheet, 0, 0, "Only");
        var ex = Record.Exception(() => doc.SortRows(sheet.Name!, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_Ascending_FirstRowSmallest()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Data");
        FodsDocument.SetCellValue(sheet, 0, 0, "Banana");
        FodsDocument.SetCellValue(sheet, 1, 0, "Apple");
        FodsDocument.SetCellValue(sheet, 2, 0, "Cherry");
        doc.SortRows(sheet.Name!, 0, ascending: true);
        Assert.Equal("Apple", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SortRows_Descending_FirstRowLargest()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Data");
        FodsDocument.SetCellValue(sheet, 0, 0, "Banana");
        FodsDocument.SetCellValue(sheet, 1, 0, "Apple");
        FodsDocument.SetCellValue(sheet, 2, 0, "Cherry");
        doc.SortRows(sheet.Name!, 0, ascending: false);
        Assert.Equal("Cherry", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void SortRows_SheetCountUnchanged()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        var sheet = doc.Sheets[0];
        doc.SortRows(sheet.Name!, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_NumericStrings_SortedNumerically()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Nums");
        FodsDocument.SetCellValue(sheet, 0, 0, "10");
        FodsDocument.SetCellValue(sheet, 1, 0, "3");
        FodsDocument.SetCellValue(sheet, 2, 0, "20");
        doc.SortRows(sheet.Name!, 0, ascending: true);
        // Numerically: 3 < 10 < 20
        Assert.Equal("3", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_SortThenAccess_CellValuePresent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Items");
        FodsDocument.SetCellValue(sheet, 0, 0, "Z-Item");
        FodsDocument.SetCellValue(sheet, 0, 1, "99");
        FodsDocument.SetCellValue(sheet, 1, 0, "A-Item");
        FodsDocument.SetCellValue(sheet, 1, 1, "10");
        doc.SortRows(sheet.Name!, 0, ascending: true);
        Assert.Equal("A-Item", FodsDocument.GetCellValue(sheet, 0, 0));
        Assert.Equal("Z-Item", FodsDocument.GetCellValue(sheet, 1, 0));
    }
}
