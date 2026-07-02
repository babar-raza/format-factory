// Tests for FodsDocument.SetCellColor / GetCellColor dedicated coverage.
// Sprint: ff-sprint-s210-dotnet-deepening-20260629
// Ledger: PC-FODS-R225

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R225: Dedicated tests for FodsDocument.SetCellColor / GetCellColor.
/// Null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// Set valid color → no exception.
/// GetCellColor returns set value.
/// Different cells independent.
/// SheetCount unchanged after set.
/// SetCellColor twice → latest value returned.
/// Set background color no exception.
/// Dogfood: multi-cell color pipeline.
/// </summary>
public class FodsR225GetCellColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellColor_NullSheet_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentNullException>(() =>
            FodsDocument.SetCellColor(null!, 0, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellColor_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellColor(sheet, -1, 0, "#FF0000"));
    }

    [Fact]
    public void SetCellColor_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellColor(sheet, 0, -1, "#FF0000"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellColor_ValidColor_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellColor(sheet, 0, 0, "#FF0000"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellColor_GetReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellColor(sheet, 0, 0, "#00FF00");
        var color = FodsDocument.GetCellColor(sheet, 0, 0);
        Assert.Equal("#00FF00", color);
    }

    [Fact]
    public void SetCellColor_DifferentCellsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellColor(sheet, 0, 0, "#FF0000");
        FodsDocument.SetCellColor(sheet, 1, 1, "#0000FF");
        Assert.Equal("#FF0000", FodsDocument.GetCellColor(sheet, 0, 0));
        Assert.Equal("#0000FF", FodsDocument.GetCellColor(sheet, 1, 1));
    }

    [Fact]
    public void SetCellColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellColor(sheet, 0, 0, "#FF0000");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellColor_SetTwice_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellColor(sheet, 0, 0, "#FF0000");
        FodsDocument.SetCellColor(sheet, 0, 0, "#FFFFFF");
        Assert.Equal("#FFFFFF", FodsDocument.GetCellColor(sheet, 0, 0));
    }

    [Fact]
    public void SetCellBackgroundColor_ValidColor_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellBackgroundColor(sheet, 0, 0, "#FFFF00"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachPreservesColor()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        string[] colors = { "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF" };
        for (int i = 0; i < colors.Length; i++)
            FodsDocument.SetCellColor(sheet, i, 0, colors[i]);
        for (int i = 0; i < colors.Length; i++)
            Assert.Equal(colors[i], FodsDocument.GetCellColor(sheet, i, 0));
    }
}
