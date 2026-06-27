// Tests for FodsDocument.GetCellIndent dedicated coverage.
// Sprint: ff-sprint-s351-dotnet-deepening-20260630
// Ledger: PC-FODS-R389

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R389: Dedicated tests for FodsDocument.GetCellIndent().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative indent.
/// SheetCount unchanged after GetCellIndent.
/// Idempotent (called twice same result).
/// Dogfood: SetCellIndent(2) then Get returns 2.
/// Dogfood: multiple cells with different indent levels.
/// </summary>
public class FodsR389GetCellIndentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellIndent_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent(null!, 0, 0));
    }

    [Fact]
    public void GetCellIndent_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent("  ", 0, 0));
    }

    [Fact]
    public void GetCellIndent_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellIndent_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Indent");
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndent("Indent", -1, 0));
    }

    [Fact]
    public void GetCellIndent_ValidCell_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int indent = doc.GetCellIndent("Data", 0, 0);
        Assert.True(indent >= 0);
    }

    [Fact]
    public void GetCellIndent_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Levels");
        int before = doc.SheetCount;
        _ = doc.GetCellIndent("Levels", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellIndent_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        int first = doc.GetCellIndent("Stable", 0, 0);
        int second = doc.GetCellIndent("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetIndentTwo_ReturnsTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Hierarchy");
        doc.SetCellIndent("Hierarchy", 0, 0, 2);
        int indent = doc.GetCellIndent("Hierarchy", 0, 0);
        Assert.Equal(2, indent);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentIndents()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Outline");
        doc.SetCellIndent("Outline", 0, 0, 0);
        doc.SetCellIndent("Outline", 1, 0, 1);
        doc.SetCellIndent("Outline", 2, 0, 2);
        Assert.Equal(0, doc.GetCellIndent("Outline", 0, 0));
        Assert.Equal(1, doc.GetCellIndent("Outline", 1, 0));
        Assert.Equal(2, doc.GetCellIndent("Outline", 2, 0));
    }
}
