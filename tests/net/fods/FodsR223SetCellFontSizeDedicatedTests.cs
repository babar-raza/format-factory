// Tests for FodsDocument.SetCellFontSize dedicated coverage.
// Sprint: ff-sprint-s208-dotnet-deepening-20260629
// Ledger: PC-FODS-R223

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R223: Dedicated tests for FodsDocument.SetCellFontSize / GetCellFontSize.
/// Null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// Negative size → ArgumentOutOfRangeException (or ArgumentException).
/// Set valid size → no exception.
/// GetCellFontSize returns set value.
/// Different cells independent.
/// SheetCount unchanged after set.
/// SetCellFontSize twice → latest value returned.
/// Dogfood: multi-cell font size pipeline.
/// </summary>
public class FodsR223SetCellFontSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontSize_NullSheet_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentNullException>(() =>
            FodsDocument.SetCellFontSize(null!, 0, 0, 12));
    }

    [Fact]
    public void SetCellFontSize_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellFontSize(sheet, -1, 0, 12));
    }

    [Fact]
    public void SetCellFontSize_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellFontSize(sheet, 0, -1, 12));
    }

    [Fact]
    public void SetCellFontSize_NegativeSize_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.ThrowsAny<Exception>(() =>
            FodsDocument.SetCellFontSize(sheet, 0, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontSize_ValidSize_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellFontSize(sheet, 0, 0, 14));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFontSize_GetReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontSize(sheet, 0, 0, 18);
        var size = FodsDocument.GetCellFontSize(sheet, 0, 0);
        Assert.Equal(18, size);
    }

    [Fact]
    public void SetCellFontSize_DifferentCellsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontSize(sheet, 0, 0, 10);
        FodsDocument.SetCellFontSize(sheet, 1, 1, 20);
        Assert.Equal(10, FodsDocument.GetCellFontSize(sheet, 0, 0));
        Assert.Equal(20, FodsDocument.GetCellFontSize(sheet, 1, 1));
    }

    [Fact]
    public void SetCellFontSize_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontSize(sheet, 0, 0, 16);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFontSize_SetTwice_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontSize(sheet, 0, 0, 12);
        FodsDocument.SetCellFontSize(sheet, 0, 0, 24);
        Assert.Equal(24, FodsDocument.GetCellFontSize(sheet, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachPreservesSize()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        int[] sizes = { 8, 10, 12, 14, 16 };
        for (int i = 0; i < sizes.Length; i++)
            FodsDocument.SetCellFontSize(sheet, i, 0, sizes[i]);
        for (int i = 0; i < sizes.Length; i++)
            Assert.Equal(sizes[i], FodsDocument.GetCellFontSize(sheet, i, 0));
    }
}
