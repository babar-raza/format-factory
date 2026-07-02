// Tests for FodsDocument.GetColumnWidth dedicated coverage.
// Sprint: ff-sprint-s393-dotnet-deepening-20260701
// Ledger: PC-FODS-R442

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R442: Dedicated tests for FodsDocument.GetColumnWidth().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative column index throws.
/// Valid column returns non-negative width.
/// SheetCount unchanged after GetColumnWidth.
/// Idempotent (called twice same result).
/// SetColumnWidth + GetColumnWidth round-trips.
/// Dogfood: default column width non-negative.
/// Dogfood: multiple columns all non-negative.
/// </summary>
public class FodsR442GetColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWidth_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth(null!, 0));
    }

    [Fact]
    public void GetColumnWidth_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth("   ", 0));
    }

    [Fact]
    public void GetColumnWidth_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth("NoSuchSheet", 0));
    }

    [Fact]
    public void GetColumnWidth_NegativeColumn_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWidth_ValidColumn_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double width = doc.GetColumnWidth(sheetName, 0);
        Assert.True(width >= 0.0);
    }

    [Fact]
    public void GetColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetColumnWidth(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnWidth_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double first = doc.GetColumnWidth(sheetName, 0);
        double second = doc.GetColumnWidth(sheetName, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnWidth_SetWidth_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetColumnWidth(sheetName, 0, 15.0);
        double width = doc.GetColumnWidth(sheetName, 0);
        Assert.Equal(15.0, width, 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultColumn_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double width = doc.GetColumnWidth(sheetName, 0);
        Assert.True(width >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleColumns_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int col = 0; col < 5; col++)
        {
            Assert.True(doc.GetColumnWidth(sheetName, col) >= 0.0);
        }
    }
}
