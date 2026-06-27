// Tests for FodsDocument.GetCellTextRotation dedicated coverage.
// Sprint: ff-sprint-s350-dotnet-deepening-20260630
// Ledger: PC-FODS-R388

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R388: Dedicated tests for FodsDocument.GetCellTextRotation().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns value in valid rotation range.
/// SheetCount unchanged after GetCellTextRotation.
/// Idempotent (called twice same result).
/// Dogfood: SetCellTextRotation(45) then Get returns 45.
/// Dogfood: SetCellTextRotation(90) then Get returns 90.
/// </summary>
public class FodsR388GetCellTextRotationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTextRotation_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation(null!, 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("  ", 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Rotated");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("Rotated", -1, 0));
    }

    [Fact]
    public void GetCellTextRotation_ValidCell_ReturnsInRange()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int rotation = doc.GetCellTextRotation("Data", 0, 0);
        Assert.InRange(rotation, -360, 360);
    }

    [Fact]
    public void GetCellTextRotation_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Angles");
        int before = doc.SheetCount;
        _ = doc.GetCellTextRotation("Angles", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellTextRotation_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        int first = doc.GetCellTextRotation("Stable", 0, 0);
        int second = doc.GetCellTextRotation("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetRotation45_ReturnsFourtyFive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Headers");
        doc.SetCellTextRotation("Headers", 0, 0, 45);
        int rotation = doc.GetCellTextRotation("Headers", 0, 0);
        Assert.Equal(45, rotation);
    }

    [Fact]
    public void DogfoodPipeline_SetRotation90_ReturnsNinety()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Vertical");
        doc.SetCellTextRotation("Vertical", 0, 0, 90);
        int rotation = doc.GetCellTextRotation("Vertical", 0, 0);
        Assert.Equal(90, rotation);
    }
}
