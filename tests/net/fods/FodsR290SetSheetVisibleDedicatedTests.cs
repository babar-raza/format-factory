// Tests for FodsDocument.SetSheetVisible dedicated coverage.
// Sprint: ff-sprint-s266-dotnet-deepening-20260630
// Ledger: PC-FODS-R290

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R290: Dedicated tests for FodsDocument.SetSheetVisible(sheetName, visible).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Valid call with visible=true → no exception.
/// Valid call with visible=false → no exception.
/// SheetCount unchanged after SetSheetVisible.
/// IsSheetVisible reflects the set state.
/// Set same sheet visible twice → no exception.
/// Dogfood: set visible=false, then IsSheetVisible returns false.
/// Dogfood: set visible=false then visible=true, IsSheetVisible returns true.
/// </summary>
public class FodsR290SetSheetVisibleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSheetVisible_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetSheetVisible(null!, true));
    }

    [Fact]
    public void SetSheetVisible_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetSheetVisible("   ", true));
    }

    [Fact]
    public void SetSheetVisible_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetSheetVisible("NoSheet", true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSheetVisible_ShowSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetSheetVisible("Sheet1", true));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSheetVisible_HideSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetSheetVisible("Sheet1", false));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSheetVisible_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetSheetVisible("Sheet1", false);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetSheetVisible_IsSheetVisible_ReflectsState()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetSheetVisible("Sheet1", false);
        bool visible = doc.IsSheetVisible("Sheet1");
        Assert.False(visible);
    }

    [Fact]
    public void SetSheetVisible_SetTwiceVisible_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetSheetVisible("Sheet1", true);
        var ex = Record.Exception(() => doc.SetSheetVisible("Sheet1", true));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HideSheet_IsVisibleReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("HiddenSheet");
        doc.SetSheetVisible("HiddenSheet", false);
        Assert.False(doc.IsSheetVisible("HiddenSheet"));
    }

    [Fact]
    public void DogfoodPipeline_HideThenShow_IsVisibleReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("FlippedSheet");
        doc.SetSheetVisible("FlippedSheet", false);
        doc.SetSheetVisible("FlippedSheet", true);
        Assert.True(doc.IsSheetVisible("FlippedSheet"));
    }
}
