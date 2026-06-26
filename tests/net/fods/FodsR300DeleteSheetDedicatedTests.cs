// Tests for FodsDocument.DeleteSheet dedicated coverage.
// Sprint: ff-sprint-s273-dotnet-deepening-20260630
// Ledger: PC-FODS-R300

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R300: Dedicated tests for FodsDocument.DeleteSheet(sheetName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Valid call no exception.
/// SheetCount decreases after delete.
/// Deleted sheet no longer in GetSheetNames.
/// Remaining sheets still accessible.
/// Dogfood: add two sheets, delete one, one remains.
/// Dogfood: delete sheet then verify names updated.
/// </summary>
public class FodsR300DeleteSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteSheet_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteSheet(null!));
    }

    [Fact]
    public void DeleteSheet_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteSheet("   "));
    }

    [Fact]
    public void DeleteSheet_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.DeleteSheet("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteSheet_ValidSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        var ex = Record.Exception(() => doc.DeleteSheet("Sheet1"));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteSheet_SheetCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.AddSheet("B");
        int before = doc.SheetCount;
        doc.DeleteSheet("A");
        Assert.Equal(before - 1, doc.SheetCount);
    }

    [Fact]
    public void DeleteSheet_DeletedSheetNotInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("ToDelete");
        doc.AddSheet("ToKeep");
        doc.DeleteSheet("ToDelete");
        Assert.DoesNotContain("ToDelete", doc.GetSheetNames());
    }

    [Fact]
    public void DeleteSheet_RemainingSheetStillAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("ToDelete");
        doc.AddSheet("Keeper");
        doc.DeleteSheet("ToDelete");
        var ex = Record.Exception(() => doc.GetRowCount("Keeper"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTwoDeleteOne_OneRemains()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        int before = doc.SheetCount;
        doc.DeleteSheet("Alpha");
        Assert.Equal(before - 1, doc.SheetCount);
        Assert.Contains("Beta", doc.GetSheetNames());
    }

    [Fact]
    public void DogfoodPipeline_DeleteSheet_NamesUpdated()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Draft");
        doc.AddSheet("Final");
        doc.DeleteSheet("Draft");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("Draft", names);
        Assert.Contains("Final", names);
    }
}
