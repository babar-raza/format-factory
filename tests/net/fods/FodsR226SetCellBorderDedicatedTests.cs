// Tests for FodsDocument.SetCellBorder dedicated coverage.
// Sprint: ff-sprint-s211-dotnet-deepening-20260629
// Ledger: PC-FODS-R226

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R226: Dedicated tests for FodsDocument.SetCellBorder / GetCellBorder.
/// Null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// Set valid border → no exception.
/// GetCellBorder returns set value.
/// Different cells independent.
/// SheetCount unchanged after set.
/// SetCellBorder twice → latest value returned.
/// Set border to empty string → no exception.
/// Dogfood: multi-cell border pipeline.
/// </summary>
public class FodsR226SetCellBorderDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBorder_NullSheet_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentNullException>(() =>
            FodsDocument.SetCellBorder(null!, 0, 0, "thin solid #000000"));
    }

    [Fact]
    public void SetCellBorder_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellBorder(sheet, -1, 0, "thin solid #000000"));
    }

    [Fact]
    public void SetCellBorder_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellBorder(sheet, 0, -1, "thin solid #000000"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBorder_ValidBorder_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellBorder(sheet, 0, 0, "thin solid #000000"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBorder_GetReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBorder(sheet, 0, 0, "thin solid #FF0000");
        var border = FodsDocument.GetCellBorder(sheet, 0, 0);
        Assert.Equal("thin solid #FF0000", border);
    }

    [Fact]
    public void SetCellBorder_DifferentCellsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBorder(sheet, 0, 0, "thin solid #000000");
        FodsDocument.SetCellBorder(sheet, 1, 1, "thick dashed #FF0000");
        Assert.Equal("thin solid #000000", FodsDocument.GetCellBorder(sheet, 0, 0));
        Assert.Equal("thick dashed #FF0000", FodsDocument.GetCellBorder(sheet, 1, 1));
    }

    [Fact]
    public void SetCellBorder_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBorder(sheet, 0, 0, "thin solid #000000");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellBorder_SetTwice_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBorder(sheet, 0, 0, "thin solid #000000");
        FodsDocument.SetCellBorder(sheet, 0, 0, "thick solid #FFFFFF");
        Assert.Equal("thick solid #FFFFFF", FodsDocument.GetCellBorder(sheet, 0, 0));
    }

    [Fact]
    public void SetCellBorder_EmptyString_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellBorder(sheet, 0, 0, ""));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachPreservesBorder()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        string[] borders = {
            "thin solid #000000",
            "medium dashed #FF0000",
            "thick dotted #0000FF",
            "thin solid #00FF00",
            "medium solid #FFFF00"
        };
        for (int i = 0; i < borders.Length; i++)
            FodsDocument.SetCellBorder(sheet, i, 0, borders[i]);
        for (int i = 0; i < borders.Length; i++)
            Assert.Equal(borders[i], FodsDocument.GetCellBorder(sheet, i, 0));
    }
}
