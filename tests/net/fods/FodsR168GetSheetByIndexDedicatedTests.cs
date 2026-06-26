// Tests for FodsDocument.GetSheetByIndex dedicated coverage.
// Sprint: ff-sprint-s161-dotnet-deepening-20260628
// Ledger: PC-FODS-R168

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R168: Dedicated tests for FodsDocument.GetSheetByIndex(int index).
/// GetSheetByIndex returns the sheet at the zero-based index, or null if out of range.
/// Returns null for negative index (does NOT throw).
/// Returns null for index >= SheetCount (does NOT throw).
/// Covers: empty document returns null; negative index returns null; index at count returns null;
/// index beyond count returns null; index 0 returns first sheet;
/// index 1 returns second sheet; returned sheet Name matches AddSheet name;
/// returned sheet is not null for valid index; SheetCount matches after adds;
/// dogfood CreateNew->AddSheet->GetSheetByIndex pipeline.
/// </summary>
public class FodsR168GetSheetByIndexDedicatedTests
{
    // -------------------------------------------------------------------------
    // Returns-null tests (no throws)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_EmptyDocument_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Null(doc.GetSheetByIndex(0));
    }

    [Fact]
    public void GetSheetByIndex_NegativeIndex_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(-1));
    }

    [Fact]
    public void GetSheetByIndex_IndexAtCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(1)); // count is 1, so index 1 is out of range
    }

    [Fact]
    public void GetSheetByIndex_IndexBeyondCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(10));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_IndexZero_ReturnsFirstSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        var result = doc.GetSheetByIndex(0);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetSheetByIndex_IndexOne_ReturnsSecondSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        var result = doc.GetSheetByIndex(1);
        Assert.NotNull(result);
        Assert.Equal("Beta", result.Name);
    }

    [Fact]
    public void GetSheetByIndex_ReturnedSheetName_MatchesAddSheetName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MySheet");
        var result = doc.GetSheetByIndex(0);
        Assert.Equal("MySheet", result!.Name);
    }

    [Fact]
    public void GetSheetByIndex_ValidIndex_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.NotNull(doc.GetSheetByIndex(0));
    }

    [Fact]
    public void GetSheetByIndex_SheetCount_MatchesAfterAdds()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.AddSheet("B");
        doc.AddSheet("C");
        Assert.Equal(3, doc.SheetCount);
        Assert.NotNull(doc.GetSheetByIndex(2));
        Assert.Null(doc.GetSheetByIndex(3));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_GetSheetByIndex()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        doc.AddSheet("Second");
        doc.AddSheet("Third");
        var first = doc.GetSheetByIndex(0);
        var second = doc.GetSheetByIndex(1);
        var third = doc.GetSheetByIndex(2);
        Assert.Equal("First", first!.Name);
        Assert.Equal("Second", second!.Name);
        Assert.Equal("Third", third!.Name);
    }
}
