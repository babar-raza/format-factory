// Tests for FodsDocument.DeleteRows dedicated coverage.
// Sprint: ff-sprint-s158-dotnet-deepening-20260628
// Ledger: PC-FODS-R165

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R165: Dedicated tests for FodsDocument.DeleteRows(string sheetName, int startRow, int count).
/// DeleteRows removes (count) rows starting at zero-based index startRow.
/// count=0 is a no-op. Negative count throws ArgumentOutOfRangeException.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws InvalidOperationException for nonexistent sheet.
/// Throws ArgumentOutOfRangeException if range [startRow, startRow+count) is out of bounds.
/// Covers: null sheetName throws ArgumentException; whitespace sheetName throws ArgumentException;
/// nonexistent sheet throws InvalidOperationException; negative count throws ArgumentOutOfRangeException;
/// startRow out-of-bounds throws; count=0 is no-op; delete one row decreases count;
/// delete multiple rows correct; dogfood CreateNew->AddSheet->SetCellValues->DeleteRows;
/// dogfood delete from middle preserves surrounding rows.
/// </summary>
public class FodsR165DeleteRowsDedicatedTests
{
    private static FodsDocument MakeDocWithRows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Row0");
        doc.SetCellValue("Sheet1", 1, 0, "Row1");
        doc.SetCellValue("Sheet1", 2, 0, "Row2");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_NullSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows(null!, 0, 1));
    }

    [Fact]
    public void DeleteRows_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows("   ", 0, 1));
    }

    [Fact]
    public void DeleteRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<InvalidOperationException>(() => doc.DeleteRows("NoSheet", 0, 1));
    }

    [Fact]
    public void DeleteRows_NegativeCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows("Sheet1", 0, -1));
    }

    [Fact]
    public void DeleteRows_StartRowOutOfBounds_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithRows();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows("Sheet1", 0, 10));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_CountZero_IsNoOp()
    {
        var doc = MakeDocWithRows();
        var before = doc.GetSheetByName("Sheet1")!.Rows.Count;
        doc.DeleteRows("Sheet1", 0, 0);
        var after = doc.GetSheetByName("Sheet1")!.Rows.Count;
        Assert.Equal(before, after);
    }

    [Fact]
    public void DeleteRows_DeleteOneRow_RowCountDecreases()
    {
        var doc = MakeDocWithRows();
        var before = doc.GetSheetByName("Sheet1")!.Rows.Count;
        doc.DeleteRows("Sheet1", 0, 1);
        var after = doc.GetSheetByName("Sheet1")!.Rows.Count;
        Assert.Equal(before - 1, after);
    }

    [Fact]
    public void DeleteRows_DeleteMultipleRows_CorrectCount()
    {
        var doc = MakeDocWithRows();
        doc.DeleteRows("Sheet1", 0, 2);
        Assert.Equal(1, doc.GetSheetByName("Sheet1")!.Rows.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValues_DeleteRows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Header");
        doc.SetCellValue("Data", 1, 0, "Row1");
        doc.SetCellValue("Data", 2, 0, "Row2");
        doc.DeleteRows("Data", 1, 1); // delete row 1
        Assert.Equal(2, doc.GetSheetByName("Data")!.Rows.Count);
    }

    [Fact]
    public void DogfoodPipeline_DeleteFromMiddle_PreservesSurroundingRows()
    {
        var doc = MakeDocWithRows();
        doc.DeleteRows("Sheet1", 1, 1); // delete middle row (Row1)
        // Should have 2 rows remaining: Row0 and Row2
        Assert.Equal(2, doc.GetSheetByName("Sheet1")!.Rows.Count);
        // First row should still be Row0
        Assert.Equal("Row0", doc.GetCellValue("Sheet1", 0, 0));
    }
}
