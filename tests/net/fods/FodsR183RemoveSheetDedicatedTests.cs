// Tests for FodsDocument.RemoveSheet dedicated coverage.
// Sprint: ff-sprint-s176-dotnet-deepening-20260628
// Ledger: PC-FODS-R183

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R183: Dedicated tests for FodsDocument.RemoveSheet(name).
/// Removes the named sheet from the document.
/// null/whitespace name throws ArgumentException.
/// Nonexistent name throws InvalidOperationException.
/// Valid remove: sheet is gone; SheetCount decrements.
/// Other sheets remain unaffected.
/// Covers: null throws; whitespace throws; nonexistent throws;
/// valid remove decrements SheetCount; removed sheet no longer findable;
/// other sheets unaffected; double remove throws; dogfood AddSheet→SetCellValue→RemoveSheet pipeline.
/// </summary>
public class FodsR183RemoveSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void RemoveSheet_NullOrWhitespaceName_ThrowsArgumentException(string name)
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.RemoveSheet(name));
    }

    [Fact]
    public void RemoveSheet_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.RemoveSheet("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSheet_ValidSheet_DecrementsSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        var before = doc.SheetCount;
        doc.RemoveSheet("Extra");
        Assert.Equal(before - 1, doc.SheetCount);
    }

    [Fact]
    public void RemoveSheet_ValidSheet_SheetNoLongerFindable()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("ToDelete");
        doc.RemoveSheet("ToDelete");
        Assert.Null(doc.GetSheetByName("ToDelete"));
    }

    [Fact]
    public void RemoveSheet_OtherSheets_Unaffected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Keep");
        doc.AddSheet("Remove");
        doc.SetCellValue("Keep", 0, 0, "StillHere");
        doc.RemoveSheet("Remove");
        Assert.Equal("StillHere", doc.GetCellValue("Keep", 0, 0));
    }

    [Fact]
    public void RemoveSheet_DoubleRemove_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Once");
        doc.RemoveSheet("Once");
        Assert.Throws<InvalidOperationException>(() => doc.RemoveSheet("Once"));
    }

    [Fact]
    public void RemoveSheet_SheetNames_NoLongerContainsRemoved()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Gone");
        doc.RemoveSheet("Gone");
        Assert.DoesNotContain("Gone", doc.GetSheetNames());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSetCellValueThenRemove_SheetGone()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Temp");
        doc.SetCellValue("Temp", 0, 0, "Ephemeral");
        doc.RemoveSheet("Temp");
        Assert.Null(doc.GetSheetByName("Temp"));
    }

    [Fact]
    public void DogfoodPipeline_RemoveAndReadd_WorksCorrectly()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Cycle");
        doc.RemoveSheet("Cycle");
        doc.AddSheet("Cycle");
        doc.SetCellValue("Cycle", 0, 0, "Fresh");
        Assert.Equal("Fresh", doc.GetCellValue("Cycle", 0, 0));
    }
}
