// Tests for FodsDocument.SetCellItalic dedicated coverage.
// Sprint: ff-sprint-s207-dotnet-deepening-20260629
// Ledger: PC-FODS-R222

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R222: Dedicated tests for FodsDocument.SetCellItalic(FodsSheet sheet, int row, int col, bool italic).
/// null sheet → ArgumentNullException.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// SetCellItalic(true) → no exception.
/// SetCellItalic(false) → no exception.
/// GetCellItalic after SetCellItalic(true) → true.
/// GetCellItalic after SetCellItalic(false) → false.
/// Different cells have independent italic state.
/// SheetCount unchanged.
/// Dogfood: toggle italic true/false; combine with bold.
/// </summary>
public class FodsR222SetCellItalicDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellItalic_NullSheet_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.SetCellItalic(null!, 0, 0, true));
    }

    [Fact]
    public void SetCellItalic_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => FodsDocument.SetCellItalic(sheet, -1, 0, true));
    }

    [Fact]
    public void SetCellItalic_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => FodsDocument.SetCellItalic(sheet, 0, -1, true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellItalic_True_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellItalic(sheet, 0, 0, true));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellItalic_False_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => FodsDocument.SetCellItalic(sheet, 0, 0, false));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellItalic_True_GetReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellItalic(sheet, 0, 0, true);
        Assert.True(FodsDocument.GetCellItalic(sheet, 0, 0));
    }

    [Fact]
    public void SetCellItalic_False_GetReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellItalic(sheet, 0, 0, false);
        Assert.False(FodsDocument.GetCellItalic(sheet, 0, 0));
    }

    [Fact]
    public void SetCellItalic_DifferentCells_Independent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellItalic(sheet, 0, 0, true);
        FodsDocument.SetCellItalic(sheet, 0, 1, false);
        Assert.True(FodsDocument.GetCellItalic(sheet, 0, 0));
        Assert.False(FodsDocument.GetCellItalic(sheet, 0, 1));
    }

    [Fact]
    public void SetCellItalic_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        int before = doc.SheetCount;
        FodsDocument.SetCellItalic(sheet, 0, 0, true);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ToggleItalic_FinalStateCorrect()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellItalic(sheet, 0, 0, true);
        FodsDocument.SetCellItalic(sheet, 0, 0, false);
        FodsDocument.SetCellItalic(sheet, 0, 0, true);
        Assert.True(FodsDocument.GetCellItalic(sheet, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_BoldAndItalicIndependent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellBold(sheet, 0, 0, true);
        FodsDocument.SetCellItalic(sheet, 0, 0, true);
        Assert.True(FodsDocument.GetCellBold(sheet, 0, 0));
        Assert.True(FodsDocument.GetCellItalic(sheet, 0, 0));
    }
}
