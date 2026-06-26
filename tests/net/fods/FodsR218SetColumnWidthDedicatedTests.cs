// Tests for FodsDocument.SetColumnWidth dedicated coverage.
// Sprint: ff-sprint-s204-dotnet-deepening-20260629
// Ledger: PC-FODS-R218

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R218: Dedicated tests for FodsDocument.SetColumnWidth(string sheetName, int colIndex, double width).
/// null/whitespace sheetName → ArgumentException.
/// Nonexistent sheet → InvalidOperationException.
/// Negative colIndex → ArgumentOutOfRangeException.
/// Negative width → ArgumentOutOfRangeException.
/// Valid: no exception.
/// SheetCount unchanged after set.
/// Set then GetColumnWidth returns same value.
/// Zero width is valid (hidden column).
/// Multiple columns set independently.
/// Dogfood: set width on multiple columns, verify no exception.
/// </summary>
public class FodsR218SetColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SetColumnWidth(null!, 0, 10.0));
    }

    [Fact]
    public void SetColumnWidth_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SetColumnWidth("   ", 0, 10.0));
    }

    [Fact]
    public void SetColumnWidth_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.SetColumnWidth("NoSuch", 0, 10.0));
    }

    [Fact]
    public void SetColumnWidth_NegativeColIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetColumnWidth(sheet.Name!, -1, 10.0));
    }

    [Fact]
    public void SetColumnWidth_NegativeWidth_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetColumnWidth(sheet.Name!, 0, -1.0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_ValidArgs_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        var ex = Record.Exception(() => doc.SetColumnWidth(sheet.Name!, 0, 20.0));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        int before = doc.SheetCount;
        doc.SetColumnWidth(sheet.Name!, 0, 15.0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetColumnWidth_SetThenGet_ReturnsSameValue()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        doc.SetColumnWidth(sheet.Name!, 0, 25.0);
        var width = doc.GetColumnWidth(sheet.Name!, 0);
        Assert.Equal(25.0, width, precision: 2);
    }

    [Fact]
    public void SetColumnWidth_ZeroWidth_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        var ex = Record.Exception(() => doc.SetColumnWidth(sheet.Name!, 0, 0.0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleColumns_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        for (int i = 0; i < 5; i++)
        {
            var ex = Record.Exception(() => doc.SetColumnWidth(sheet.Name!, i, (i + 1) * 10.0));
            Assert.Null(ex);
        }
    }

    [Fact]
    public void DogfoodPipeline_SetWidthTwice_FinalValueCorrect()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        doc.SetColumnWidth(sheet.Name!, 0, 10.0);
        doc.SetColumnWidth(sheet.Name!, 0, 30.0);
        var width = doc.GetColumnWidth(sheet.Name!, 0);
        Assert.Equal(30.0, width, precision: 2);
    }
}
