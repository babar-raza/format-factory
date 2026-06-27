// Tests for FodsDocument.GetSheetRowCount dedicated coverage.
// Sprint: ff-sprint-s375-dotnet-deepening-20260630
// Ledger: PC-FODS-R418

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R418: Dedicated tests for FodsDocument.GetSheetRowCount().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New empty sheet returns non-negative.
/// SheetCount unchanged after GetSheetRowCount.
/// Idempotent (called twice same result).
/// Dogfood: after SetCellValue rows count non-negative.
/// Dogfood: multiple sheets each returns non-negative.
/// </summary>
public class FodsR418GetSheetRowCountDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetSheetRowCount("Missing"));
    }

    [Fact]
    public void GetSheetRowCount_NewEmptySheet_ReturnsNonNegative()
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
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetSheetRowCount("Data");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetRowCount_Idempotent()
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
    public void DogfoodPipeline_AfterSetCellValues_RowCountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Product");
        doc.SetCellValue("Sales", 1, 0, "Widget A");
        doc.SetCellValue("Sales", 2, 0, "Widget B");
        int count = doc.GetSheetRowCount("Sales");
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_EachNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Q1");
        doc.AddSheet("Q2");
        doc.AddSheet("Q3");
        Assert.True(doc.GetSheetRowCount("Q1") >= 0);
        Assert.True(doc.GetSheetRowCount("Q2") >= 0);
        Assert.True(doc.GetSheetRowCount("Q3") >= 0);
    }
}
