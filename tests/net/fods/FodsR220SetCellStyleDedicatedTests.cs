// Tests for FodsDocument.SetCellStyle dedicated coverage.
// Sprint: ff-sprint-s205-dotnet-deepening-20260629
// Ledger: PC-FODS-R220

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R220: Dedicated tests for FodsDocument.SetCellStyle(FodsSheet sheet, int row, int col, string styleName).
/// null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// null styleName → ArgumentNullException.
/// Valid: no exception.
/// After set, GetCellStyle returns same value.
/// Different cells independently styled.
/// Style unchanged for other cells.
/// SetCellStyle twice → latest style.
/// Dogfood: set multiple cells, verify each.
/// </summary>
public class FodsR220SetCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_NullSheet_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.SetCellStyle(null!, 0, 0, "Bold"));
    }

    [Fact]
    public void SetCellStyle_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => FodsDocument.SetCellStyle(sheet, -1, 0, "Bold"));
    }

    [Fact]
    public void SetCellStyle_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => FodsDocument.SetCellStyle(sheet, 0, -1, "Bold"));
    }

    [Fact]
    public void SetCellStyle_NullStyleName_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentNullException>(() => FodsDocument.SetCellStyle(sheet, 0, 0, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_ValidArgs_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellStyle(sheet, 0, 0, "Bold"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellStyle_AfterSet_GetReturnsStyle()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellStyle(sheet, 0, 0, "Italic");
        Assert.Equal("Italic", FodsDocument.GetCellStyle(sheet, 0, 0));
    }

    [Fact]
    public void SetCellStyle_DifferentCells_IndependentStyles()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellStyle(sheet, 0, 0, "Bold");
        FodsDocument.SetCellStyle(sheet, 0, 1, "Italic");
        Assert.Equal("Bold", FodsDocument.GetCellStyle(sheet, 0, 0));
        Assert.Equal("Italic", FodsDocument.GetCellStyle(sheet, 0, 1));
    }

    [Fact]
    public void SetCellStyle_SetTwice_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellStyle(sheet, 0, 0, "First");
        FodsDocument.SetCellStyle(sheet, 0, 0, "Second");
        Assert.Equal("Second", FodsDocument.GetCellStyle(sheet, 0, 0));
    }

    [Fact]
    public void SetCellStyle_OtherCellsUnaffected()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellStyle(sheet, 0, 0, "Bold");
        FodsDocument.SetCellStyle(sheet, 0, 1, "Italic");
        // Setting col 0 style again should not affect col 1
        FodsDocument.SetCellStyle(sheet, 0, 0, "Underline");
        Assert.Equal("Italic", FodsDocument.GetCellStyle(sheet, 0, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleCells_VerifyEach()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        string[] styles = { "Bold", "Italic", "Underline", "Default" };
        for (int i = 0; i < styles.Length; i++)
            FodsDocument.SetCellStyle(sheet, 0, i, styles[i]);
        for (int i = 0; i < styles.Length; i++)
            Assert.Equal(styles[i], FodsDocument.GetCellStyle(sheet, 0, i));
    }

    [Fact]
    public void DogfoodPipeline_SetAndValue_StyleAndValueIndependent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Content");
        FodsDocument.SetCellStyle(sheet, 0, 0, "Bold");
        Assert.Equal("Content", FodsDocument.GetCellValue(sheet, 0, 0));
        Assert.Equal("Bold", FodsDocument.GetCellStyle(sheet, 0, 0));
    }
}
