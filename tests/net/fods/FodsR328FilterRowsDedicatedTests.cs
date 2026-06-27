// Tests for FodsDocument.FilterRows dedicated coverage.
// Sprint: ff-sprint-s300-dotnet-deepening-20260630
// Ledger: PC-FODS-R328

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R328: Dedicated tests for FodsDocument.FilterRows(sheetName, columnName, value).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Null column name throws exception.
/// Valid call no exception.
/// SheetCount unchanged after FilterRows.
/// Filter with no match no exception.
/// Filter with all match no exception.
/// Dogfood: add rows, filter by value, no exception.
/// Dogfood: two sheets filter independently.
/// </summary>
public class FodsR328FilterRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddColumn("Sheet1", "Status");
        Assert.ThrowsAny<Exception>(() => doc.FilterRows(null!, "Status", "Active"));
    }

    [Fact]
    public void FilterRows_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddColumn("Sheet1", "Status");
        Assert.ThrowsAny<Exception>(() => doc.FilterRows("   ", "Status", "Active"));
    }

    [Fact]
    public void FilterRows_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.FilterRows("DoesNotExist", "Col", "Val"));
    }

    [Fact]
    public void FilterRows_NullColumnName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddColumn("Sheet1", "Status");
        Assert.ThrowsAny<Exception>(() => doc.FilterRows("Sheet1", null!, "Active"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddColumn("Data", "Status");
        doc.AddRow("Data", new[] { "Active" });
        var ex = Record.Exception(() => doc.FilterRows("Data", "Status", "Active"));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterRows_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddColumn("Data", "Type");
        doc.AddRow("Data", new[] { "A" });
        int sheetsBefore = doc.SheetCount;
        doc.FilterRows("Data", "Type", "A");
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void FilterRows_NoMatchFilter_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddColumn("Data", "Status");
        doc.AddRow("Data", new[] { "Active" });
        var ex = Record.Exception(() => doc.FilterRows("Data", "Status", "NoSuchValue"));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterRows_AllMatchFilter_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddColumn("Data", "Status");
        doc.AddRow("Data", new[] { "Active" });
        doc.AddRow("Data", new[] { "Active" });
        var ex = Record.Exception(() => doc.FilterRows("Data", "Status", "Active"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowsFilterByValue_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.AddColumn("Report", "Category");
        doc.AddRow("Report", new[] { "Electronics" });
        doc.AddRow("Report", new[] { "Books" });
        doc.AddRow("Report", new[] { "Electronics" });
        var ex = Record.Exception(() => doc.FilterRows("Report", "Category", "Electronics"));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheetsFilterIndependently_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddColumn("Sheet1", "Type");
        doc.AddColumn("Sheet2", "Kind");
        doc.AddRow("Sheet1", new[] { "Alpha" });
        doc.AddRow("Sheet2", new[] { "Beta" });
        doc.FilterRows("Sheet1", "Type", "Alpha");
        var ex = Record.Exception(() => doc.FilterRows("Sheet2", "Kind", "Beta"));
        Assert.Null(ex);
    }
}
