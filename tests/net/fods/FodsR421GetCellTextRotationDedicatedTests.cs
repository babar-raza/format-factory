// Tests for FodsDocument.GetCellTextRotation dedicated coverage.
// Sprint: ff-sprint-s378-dotnet-deepening-20260630
// Ledger: PC-FODS-R421

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R421: Dedicated tests for FodsDocument.GetCellTextRotation().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns value in range.
/// SheetCount unchanged after GetCellTextRotation.
/// Idempotent (called twice same result).
/// Dogfood: SetRotation 45+Get=45.
/// Dogfood: multiple cells distinct rotations.
/// </summary>
public class FodsR421GetCellTextRotationDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("   ", 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("Missing", 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("Data", -1, 0));
    }

    [Fact]
    public void GetCellTextRotation_ValidCell_ReturnsInRange()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        int rotation = doc.GetCellTextRotation("Layout", 0, 0);
        Assert.InRange(rotation, -360, 360);
    }

    [Fact]
    public void GetCellTextRotation_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetCellTextRotation("Data", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellTextRotation_Idempotent()
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
    public void DogfoodPipeline_SetRotation45ThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Headers");
        doc.SetCellTextRotation("Headers", 0, 0, 45);
        int rotation = doc.GetCellTextRotation("Headers", 0, 0);
        Assert.Equal(45, rotation);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DistinctRotations()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellTextRotation("Grid", 0, 0, 0);
        doc.SetCellTextRotation("Grid", 1, 0, 45);
        doc.SetCellTextRotation("Grid", 2, 0, 90);
        Assert.Equal(0, doc.GetCellTextRotation("Grid", 0, 0));
        Assert.Equal(45, doc.GetCellTextRotation("Grid", 1, 0));
        Assert.Equal(90, doc.GetCellTextRotation("Grid", 2, 0));
    }
}
