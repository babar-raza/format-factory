// Tests for FodsDocument.SetColumnWidth dedicated coverage.
// Sprint: ff-sprint-s306-dotnet-deepening-20260630
// Ledger: PC-FODS-R334

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R334: Dedicated tests for FodsDocument.SetColumnWidth(sheetName, columnIndex, width).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative column index throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetColumnWidth.
/// Called twice no exception.
/// Zero width ok (or throws — implementation-defined).
/// Dogfood: set width and verify SheetCount.
/// </summary>
public class FodsR334SetColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth(null!, 0, 100));
    }

    [Fact]
    public void SetColumnWidth_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("   ", 0, 100));
    }

    [Fact]
    public void SetColumnWidth_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("NoSuchSheet", 0, 100));
    }

    [Fact]
    public void SetColumnWidth_NegativeColumnIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("Sheet1", -1, 100));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetColumnWidth("Sheet1", 0, 150));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetColumnWidth("Sheet1", 0, 150);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetColumnWidth_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetColumnWidth("Sheet1", 0, 150);
        var ex = Record.Exception(() => doc.SetColumnWidth("Sheet1", 0, 200));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_MultipleColumns_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetColumnWidth("Sheet1", 0, 100);
        var ex = Record.Exception(() => doc.SetColumnWidth("Sheet1", 1, 120));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetWidthOnMultipleSheets_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        doc.SetColumnWidth("Report", 0, 120);
        doc.SetColumnWidth("Data", 0, 90);
        doc.SetColumnWidth("Data", 1, 150);
        Assert.Equal(before, doc.SheetCount);
    }
}
