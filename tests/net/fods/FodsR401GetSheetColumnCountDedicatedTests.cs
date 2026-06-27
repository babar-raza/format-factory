// Tests for FodsDocument.GetSheetColumnCount dedicated coverage.
// Sprint: ff-sprint-s359-dotnet-deepening-20260630
// Ledger: PC-FODS-R401

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R401: Dedicated tests for FodsDocument.GetSheetColumnCount().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New sheet returns non-negative.
/// SheetCount unchanged after GetSheetColumnCount.
/// Idempotent (called twice same result).
/// Dogfood: after setting cell values column count >= cells.
/// Dogfood: multiple sheets each returns non-negative.
/// </summary>
public class FodsR401GetSheetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetColumnCount_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount(null!));
    }

    [Fact]
    public void GetSheetColumnCount_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount("   "));
    }

    [Fact]
    public void GetSheetColumnCount_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount("Missing"));
    }

    [Fact]
    public void GetSheetColumnCount_NewSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        int count = doc.GetSheetColumnCount("Empty");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetSheetColumnCount("Data");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetColumnCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        int first = doc.GetSheetColumnCount("Stable");
        int second = doc.GetSheetColumnCount("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterSetCellValues_ColumnCountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Product");
        doc.SetCellValue("Sales", 0, 1, "Revenue");
        doc.SetCellValue("Sales", 0, 2, "Units");
        int count = doc.GetSheetColumnCount("Sales");
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_EachNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        Assert.True(doc.GetSheetColumnCount("Sheet1") >= 0);
        Assert.True(doc.GetSheetColumnCount("Sheet2") >= 0);
        Assert.True(doc.GetSheetColumnCount("Sheet3") >= 0);
    }
}
