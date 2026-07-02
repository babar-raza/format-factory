// Tests for FodsDocument.GetSheetByIndex dedicated coverage.
// Sprint: ff-sprint-s189-dotnet-deepening-20260628
// Ledger: PC-FODS-R196

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R196: Dedicated tests for FodsDocument.GetSheetByIndex(int index).
/// Returns the FodsSheet at the given zero-based index, or null if out of range.
/// Negative index returns null.
/// index >= SheetCount returns null.
/// index=0 returns the first sheet.
/// index=SheetCount-1 returns the last sheet.
/// Name of returned sheet matches the actual sheet name.
/// Covers: negative index returns null; index=SheetCount returns null;
/// index=0 returns first sheet; index=0 name matches; index=SheetCount-1 returns last;
/// middle index returns correct sheet; returns FodsSheet type;
/// after AddSheet index=1 returns new sheet; dogfood get and set cell via index;
/// dogfood multiple sheets correct index mapping.
/// </summary>
public class FodsR196GetSheetByIndexDedicatedTests
{
    // -------------------------------------------------------------------------
    // Boundary tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_NegativeIndex_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(-1));
    }

    [Fact]
    public void GetSheetByIndex_IndexEqualsSheetCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(doc.SheetCount));
    }

    [Fact]
    public void GetSheetByIndex_IndexZero_ReturnsFirstSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByIndex_IndexZero_NameMatchesFirstSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByIndex(0);
        Assert.Equal(doc.Sheets[0].Name, sheet!.Name);
    }

    [Fact]
    public void GetSheetByIndex_LastIndex_ReturnsLastSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Second");
        doc.AddSheet("Third");
        var last = doc.GetSheetByIndex(doc.SheetCount - 1);
        Assert.NotNull(last);
        Assert.Equal("Third", last!.Name);
    }

    [Fact]
    public void GetSheetByIndex_MiddleIndex_ReturnsCorrectSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        var middle = doc.GetSheetByIndex(1);
        Assert.NotNull(middle);
        Assert.Equal("Alpha", middle!.Name);
    }

    [Fact]
    public void GetSheetByIndex_ReturnsFodsSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var result = doc.GetSheetByIndex(0);
        Assert.IsType<FodsSheet>(result);
    }

    [Fact]
    public void GetSheetByIndex_AfterAddSheet_IndexOneReturnsNew()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("NewSheet");
        var sheet = doc.GetSheetByIndex(1);
        Assert.NotNull(sheet);
        Assert.Equal("NewSheet", sheet!.Name);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GetAndSetCellViaIndex()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "TestValue");
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
        // Access via doc using sheet name
        Assert.Equal("TestValue", doc.GetCellValue(sheet!.Name, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_CorrectIndexMapping()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var firstName = doc.Sheets[0].Name;
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        Assert.Equal(firstName, doc.GetSheetByIndex(0)!.Name);
        Assert.Equal("Sheet2", doc.GetSheetByIndex(1)!.Name);
        Assert.Equal("Sheet3", doc.GetSheetByIndex(2)!.Name);
    }
}
