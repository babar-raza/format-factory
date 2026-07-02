// Tests for FodsDocument.SetCellFontName dedicated coverage.
// Sprint: ff-sprint-s209-dotnet-deepening-20260629
// Ledger: PC-FODS-R224

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R224: Dedicated tests for FodsDocument.SetCellFontName / GetCellFontName.
/// Null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// Null font name → ArgumentNullException.
/// Set valid font name → no exception.
/// GetCellFontName returns set value.
/// Different cells independent.
/// SheetCount unchanged after set.
/// SetCellFontName twice → latest value returned.
/// Dogfood: multi-cell font name pipeline.
/// </summary>
public class FodsR224SetCellFontNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontName_NullSheet_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentNullException>(() =>
            FodsDocument.SetCellFontName(null!, 0, 0, "Arial"));
    }

    [Fact]
    public void SetCellFontName_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellFontName(sheet, -1, 0, "Arial"));
    }

    [Fact]
    public void SetCellFontName_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            FodsDocument.SetCellFontName(sheet, 0, -1, "Arial"));
    }

    [Fact]
    public void SetCellFontName_NullName_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentNullException>(() =>
            FodsDocument.SetCellFontName(sheet, 0, 0, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFontName_ValidName_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellFontName(sheet, 0, 0, "Arial"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFontName_GetReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontName(sheet, 0, 0, "Times New Roman");
        var name = FodsDocument.GetCellFontName(sheet, 0, 0);
        Assert.Equal("Times New Roman", name);
    }

    [Fact]
    public void SetCellFontName_DifferentCellsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontName(sheet, 0, 0, "Arial");
        FodsDocument.SetCellFontName(sheet, 1, 1, "Courier New");
        Assert.Equal("Arial", FodsDocument.GetCellFontName(sheet, 0, 0));
        Assert.Equal("Courier New", FodsDocument.GetCellFontName(sheet, 1, 1));
    }

    [Fact]
    public void SetCellFontName_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontName(sheet, 0, 0, "Arial");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellFontName_SetTwice_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellFontName(sheet, 0, 0, "Arial");
        FodsDocument.SetCellFontName(sheet, 0, 0, "Verdana");
        Assert.Equal("Verdana", FodsDocument.GetCellFontName(sheet, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachPreservesFontName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.Sheets[0];
        string[] fonts = { "Arial", "Calibri", "Helvetica", "Georgia", "Tahoma" };
        for (int i = 0; i < fonts.Length; i++)
            FodsDocument.SetCellFontName(sheet, i, 0, fonts[i]);
        for (int i = 0; i < fonts.Length; i++)
            Assert.Equal(fonts[i], FodsDocument.GetCellFontName(sheet, i, 0));
    }
}
