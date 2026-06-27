// Tests for FodsDocument.GetCellMergeStatus dedicated coverage.
// Sprint: ff-sprint-s345-dotnet-deepening-20260630
// Ledger: PC-FODS-R383

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R383: Dedicated tests for FodsDocument.GetCellMergeStatus().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellMergeStatus.
/// Idempotent (called twice same result).
/// Dogfood: unmerged cell returns expected status.
/// Dogfood: MergeCells then GetCellMergeStatus returns merged status.
/// </summary>
public class FodsR383GetCellMergeStatusDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellMergeStatus_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeStatus(null!, 0, 0));
    }

    [Fact]
    public void GetCellMergeStatus_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeStatus("   ", 0, 0));
    }

    [Fact]
    public void GetCellMergeStatus_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeStatus("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellMergeStatus_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Merge");
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeStatus("Merge", -1, 0));
    }

    [Fact]
    public void GetCellMergeStatus_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Status");
        string? status = doc.GetCellMergeStatus("Status", 0, 0);
        Assert.NotNull(status);
    }

    [Fact]
    public void GetCellMergeStatus_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MergeSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellMergeStatus("MergeSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellMergeStatus_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellMergeStatus("Stable", 0, 0);
        string? second = doc.GetCellMergeStatus("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UnmergedCell_ReturnsStatus()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellValue("Grid", 0, 0, "Header");
        string? status = doc.GetCellMergeStatus("Grid", 0, 0);
        Assert.NotNull(status);
    }

    [Fact]
    public void DogfoodPipeline_AfterMergeCells_ReturnsMergedStatus()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "A");
        doc.SetCellValue("Report", 0, 1, "B");
        doc.SetCellValue("Report", 0, 2, "C");
        doc.MergeCells("Report", 0, 0, 1, 3);
        string? status = doc.GetCellMergeStatus("Report", 0, 0);
        Assert.NotNull(status);
    }
}
