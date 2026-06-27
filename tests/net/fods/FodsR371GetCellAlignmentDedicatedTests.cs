// Tests for FodsDocument.GetCellAlignment dedicated coverage.
// Sprint: ff-sprint-s335-dotnet-deepening-20260630
// Ledger: PC-FODS-R371

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R371: Dedicated tests for FodsDocument.GetCellAlignment().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellAlignment.
/// Idempotent (called twice same result).
/// Dogfood: SetCellAlignment then Get returns alignment.
/// Dogfood: Multiple cells with different alignments.
/// </summary>
public class FodsR371GetCellAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellAlignment_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment(null!, 0, 0));
    }

    [Fact]
    public void GetCellAlignment_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("   ", 0, 0));
    }

    [Fact]
    public void GetCellAlignment_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("Phantom", 0, 0));
    }

    [Fact]
    public void GetCellAlignment_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Align");
        Assert.ThrowsAny<Exception>(() => doc.GetCellAlignment("Align", -1, 0));
    }

    [Fact]
    public void GetCellAlignment_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        string? alignment = doc.GetCellAlignment("Layout", 0, 0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void GetCellAlignment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("AlignSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellAlignment("AlignSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellAlignment_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Repeat");
        doc.SetCellAlignment("Repeat", 0, 0, "center");
        string? first = doc.GetCellAlignment("Repeat", 0, 0);
        string? second = doc.GetCellAlignment("Repeat", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellAlignmentThenGet_ReturnsAlignment()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Headers");
        doc.SetCellAlignment("Headers", 0, 0, "right");
        string? alignment = doc.GetCellAlignment("Headers", 0, 0);
        Assert.NotNull(alignment);
        Assert.Equal("right", alignment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsDifferentAlignments_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellAlignment("Grid", 0, 0, "left");
        doc.SetCellAlignment("Grid", 0, 1, "center");
        doc.SetCellAlignment("Grid", 0, 2, "right");
        Assert.NotNull(doc.GetCellAlignment("Grid", 0, 0));
        Assert.NotNull(doc.GetCellAlignment("Grid", 0, 1));
        Assert.NotNull(doc.GetCellAlignment("Grid", 0, 2));
    }
}
