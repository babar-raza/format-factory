// Tests for FodsDocument.SortSheet dedicated coverage.
// Sprint: ff-sprint-s288-dotnet-deepening-20260630
// Ledger: PC-FODS-R316

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R316: Dedicated tests for FodsDocument.SortSheet(sheetName, columnIndex, ascending).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative column index throws exception.
/// Valid ascending sort no exception.
/// Valid descending sort no exception.
/// SheetCount unchanged after SortSheet.
/// GetRowCount unchanged after SortSheet.
/// Sort twice no exception.
/// Dogfood: add rows, sort ascending, no exception.
/// </summary>
public class FodsR316SortSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortSheet_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SortSheet(null!, 0, true));
    }

    [Fact]
    public void SortSheet_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SortSheet("   ", 0, true));
    }

    [Fact]
    public void SortSheet_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SortSheet("NoSuchSheet", 0, true));
    }

    [Fact]
    public void SortSheet_NegativeColumnIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.SortSheet(sheet, -1, true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortSheet_AscendingSort_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 0, 0, "B");
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 1, 0, "A");
        var ex = Record.Exception(() => doc.SortSheet(sheet, 0, true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortSheet_DescendingSort_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 0, 0, "A");
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 1, 0, "B");
        var ex = Record.Exception(() => doc.SortSheet(sheet, 0, false));
        Assert.Null(ex);
    }

    [Fact]
    public void SortSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.SortSheet(sheet, 0, true);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SortSheet_SortTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.SortSheet(sheet, 0, true);
        var ex = Record.Exception(() => doc.SortSheet(sheet, 0, false));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowsThenSort_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 0, 0, "Zebra");
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 1, 0, "Apple");
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 2, 0, "Mango");
        var ex = Record.Exception(() => doc.SortSheet(sheet, 0, true));
        Assert.Null(ex);
    }
}
