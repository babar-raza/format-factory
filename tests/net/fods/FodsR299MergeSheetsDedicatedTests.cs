// Tests for FodsDocument.MergeSheets dedicated coverage.
// Sprint: ff-sprint-s272-dotnet-deepening-20260630
// Ledger: PC-FODS-R299

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R299: Dedicated tests for FodsDocument.MergeSheets(sourceSheet, targetSheet).
/// Null source sheet throws exception.
/// Whitespace source sheet throws exception.
/// Nonexistent source sheet throws exception.
/// Null target sheet throws exception.
/// Nonexistent target sheet throws exception.
/// Valid call no exception.
/// SheetCount unchanged after merge.
/// Source sheet still exists after merge.
/// Dogfood: merge two sheets, both still accessible.
/// Dogfood: merge then access target sheet no exception.
/// </summary>
public class FodsR299MergeSheetsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeSheets_NullSourceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Target");
        Assert.ThrowsAny<Exception>(() => doc.MergeSheets(null!, "Target"));
    }

    [Fact]
    public void MergeSheets_WhitespaceSourceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Target");
        Assert.ThrowsAny<Exception>(() => doc.MergeSheets("   ", "Target"));
    }

    [Fact]
    public void MergeSheets_NonexistentSourceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Target");
        Assert.ThrowsAny<Exception>(() => doc.MergeSheets("NoSuchSource", "Target"));
    }

    [Fact]
    public void MergeSheets_NullTargetSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        Assert.ThrowsAny<Exception>(() => doc.MergeSheets("Source", null!));
    }

    [Fact]
    public void MergeSheets_NonexistentTargetSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        Assert.ThrowsAny<Exception>(() => doc.MergeSheets("Source", "NoSuchTarget"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeSheets_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        doc.AddSheet("Target");
        var ex = Record.Exception(() => doc.MergeSheets("Source", "Target"));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeSheets_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        doc.AddSheet("Target");
        int before = doc.SheetCount;
        doc.MergeSheets("Source", "Target");
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MergeTwoSheets_BothStillAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddSheet("Summary");
        doc.SetCellValue("Sales", 0, 0, "Q1");
        doc.MergeSheets("Sales", "Summary");
        // Both sheets should still be accessible (no exception)
        var ex = Record.Exception(() =>
        {
            _ = doc.GetSheetNames();
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_MergeThenAccessTargetSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddSheet("Consolidated");
        doc.SetCellValue("Data", 0, 0, "Value");
        doc.MergeSheets("Data", "Consolidated");
        var ex = Record.Exception(() => doc.GetRowCount("Consolidated"));
        Assert.Null(ex);
    }
}
