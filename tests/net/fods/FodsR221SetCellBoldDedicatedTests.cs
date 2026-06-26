// Tests for FodsDocument.SetCellBold dedicated coverage.
// Sprint: ff-sprint-s206-dotnet-deepening-20260629
// Ledger: PC-FODS-R221

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R221: Dedicated tests for FodsDocument.SetCellBold(FodsSheet sheet, int row, int col, bool bold).
/// null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// SetCellBold(true) → no exception.
/// SetCellBold(false) → no exception.
/// GetCellBold after SetCellBold(true) → true.
/// GetCellBold after SetCellBold(false) → false.
/// Different cells have independent bold state.
/// SheetCount unchanged.
/// Dogfood: toggle bold true/false/true sequence.
/// </summary>
public class FodsR221SetCellBoldDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBold_NullSheet_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.SetCellBold(null!, 0, 0, true));
    }

    [Fact]
    public void SetCellBold_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => FodsDocument.SetCellBold(sheet, -1, 0, true));
    }

    [Fact]
    public void SetCellBold_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => FodsDocument.SetCellBold(sheet, 0, -1, true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBold_True_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellBold(sheet, 0, 0, true));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBold_False_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellBold(sheet, 0, 0, false));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBold_True_GetReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        Assert.True(FodsDocument.GetCellBold(sheet, 0, 0));
    }

    [Fact]
    public void SetCellBold_False_GetReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBold(sheet, 0, 0, false);
        Assert.False(FodsDocument.GetCellBold(sheet, 0, 0));
    }

    [Fact]
    public void SetCellBold_DifferentCells_Independent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        FodsDocument.SetCellBold(sheet, 0, 1, false);
        Assert.True(FodsDocument.GetCellBold(sheet, 0, 0));
        Assert.False(FodsDocument.GetCellBold(sheet, 0, 1));
    }

    [Fact]
    public void SetCellBold_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        int before = doc.SheetCount;
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ToggleBold_FinalStateCorrect()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        FodsDocument.SetCellBold(sheet, 0, 0, false);
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        Assert.True(FodsDocument.GetCellBold(sheet, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_BoldAndValue_Independent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Data");
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        Assert.Equal("Data", FodsDocument.GetCellValue(sheet, 0, 0));
        Assert.True(FodsDocument.GetCellBold(sheet, 0, 0));
    }
}
