// Tests for FodsDocument.SortRows dedicated coverage.
// Sprint: ff-sprint-s155-dotnet-deepening-20260628
// Ledger: PC-FODS-R162

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R162: Dedicated tests for FodsDocument.SortRows(string sheetName, int sortColumn, bool ascending = true).
/// SortRows sorts all rows in the sheet by the specified column.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws InvalidOperationException for nonexistent sheet.
/// Throws ArgumentOutOfRangeException for negative sortColumn.
/// Single-row and empty sheets are no-ops.
/// Covers: null sheetName throws ArgumentException; whitespace sheetName throws ArgumentException;
/// nonexistent sheet throws InvalidOperationException; negative sortColumn throws ArgumentOutOfRangeException;
/// single-row sheet no-op (no throw); ascending=true orders A->Z;
/// ascending=false orders Z->A; column index beyond row length uses empty string (no throw);
/// dogfood CreateNew->AddSheet->SetCellValues->SortRows ascending pipeline;
/// dogfood sort then verify first row is smallest.
/// </summary>
public class FodsR162SortRowsDedicatedTests
{
    private static FodsDocument MakeDocWithRows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Charlie");
        doc.SetCellValue("Sheet1", 1, 0, "Alice");
        doc.SetCellValue("Sheet1", 2, 0, "Bob");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_NullSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentException>(() => doc.SortRows(null!, 0));
    }

    [Fact]
    public void SortRows_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentException>(() => doc.SortRows("   ", 0));
    }

    [Fact]
    public void SortRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<InvalidOperationException>(() => doc.SortRows("NoSheet", 0));
    }

    [Fact]
    public void SortRows_NegativeSortColumn_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SortRows("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // No-op tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_SingleRowSheet_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Single");
        doc.SetCellValue("Single", 0, 0, "OnlyRow");
        // Should not throw for single row
        doc.SortRows("Single", 0);
        Assert.Equal(1, doc.GetSheetByName("Single")!.Rows.Count);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_Ascending_OrdersAlphabetically()
    {
        var doc = MakeDocWithRows();
        doc.SortRows("Sheet1", 0, ascending: true);
        // First row should be Alice (alphabetically first)
        Assert.Equal("Alice", doc.GetCellValue("Sheet1", 0, 0));
    }

    [Fact]
    public void SortRows_Descending_OrdersReverseAlphabetically()
    {
        var doc = MakeDocWithRows();
        doc.SortRows("Sheet1", 0, ascending: false);
        // First row should be Charlie (alphabetically last)
        Assert.Equal("Charlie", doc.GetCellValue("Sheet1", 0, 0));
    }

    [Fact]
    public void SortRows_ColumnBeyondRowLength_DoesNotThrow()
    {
        var doc = MakeDocWithRows();
        // Column 5 doesn't exist in rows that only have column 0
        // Should use empty string as sort key (no throw)
        doc.SortRows("Sheet1", 5);
        Assert.NotNull(doc.GetSheetByName("Sheet1"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValues_SortRows_Ascending()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Zebra");
        doc.SetCellValue("Data", 1, 0, "Apple");
        doc.SetCellValue("Data", 2, 0, "Mango");
        doc.SortRows("Data", 0, ascending: true);
        Assert.Equal("Apple", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_SortAscending_FirstRowIsSmallest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Nums");
        doc.SetCellValue("Nums", 0, 0, "300");
        doc.SetCellValue("Nums", 1, 0, "100");
        doc.SetCellValue("Nums", 2, 0, "200");
        doc.SortRows("Nums", 0, ascending: true);
        // Numerically sorted: 100 first
        Assert.Equal("100", doc.GetCellValue("Nums", 0, 0));
    }
}
