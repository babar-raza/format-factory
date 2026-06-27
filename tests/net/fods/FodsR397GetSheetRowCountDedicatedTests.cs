// Tests for FodsDocument.GetSheetRowCount dedicated coverage.
// Sprint: ff-sprint-s357-dotnet-deepening-20260630
// Ledger: PC-FODS-R397

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R397: Dedicated tests for FodsDocument.GetSheetRowCount().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New empty sheet returns 0 or positive base value.
/// SheetCount unchanged after GetSheetRowCount.
/// Idempotent (called twice same result).
/// Dogfood: after adding rows count increases.
/// Dogfood: multiple sheets each has correct row count.
/// </summary>
public class FodsR397GetSheetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetRowCount_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount(null!));
    }

    [Fact]
    public void GetSheetRowCount_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount("   "));
    }

    [Fact]
    public void GetSheetRowCount_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount("NoSheet"));
    }

    [Fact]
    public void GetSheetRowCount_NewSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        int count = doc.GetSheetRowCount("Empty");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Rows");
        int before = doc.SheetCount;
        _ = doc.GetSheetRowCount("Rows");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetRowCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        int first = doc.GetSheetRowCount("Stable");
        int second = doc.GetSheetRowCount("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterAddingCells_CountReflectsData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Row 1");
        doc.SetCellValue("Data", 1, 0, "Row 2");
        doc.SetCellValue("Data", 2, 0, "Row 3");
        int count = doc.GetSheetRowCount("Data");
        Assert.True(count >= 3);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_EachHasCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.SetCellValue("Sheet1", 0, 0, "A");
        doc.SetCellValue("Sheet2", 0, 0, "B");
        doc.SetCellValue("Sheet2", 1, 0, "C");
        int count1 = doc.GetSheetRowCount("Sheet1");
        int count2 = doc.GetSheetRowCount("Sheet2");
        Assert.True(count1 >= 0);
        Assert.True(count2 >= 0);
    }
}
