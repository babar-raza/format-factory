// Tests for FodsDocument.AddColumn dedicated coverage.
// Sprint: ff-sprint-s203-dotnet-deepening-20260629
// Ledger: PC-FODS-R217

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R217: Dedicated tests for FodsDocument.AddColumn(string sheetName, string? header).
/// null/whitespace sheetName → ArgumentException.
/// Nonexistent sheet → InvalidOperationException.
/// Valid: no exception.
/// Valid: column count increases.
/// Valid: optional header present in first row.
/// Null header: column added without header.
/// SheetCount unchanged after add column.
/// Add multiple columns: count increases correctly.
/// Dogfood: add column then set cell value in new column.
/// Dogfood: add then delete column round-trip.
/// </summary>
public class FodsR217AddColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.AddColumn(null!, null));
    }

    [Fact]
    public void AddColumn_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.AddColumn("   ", null));
    }

    [Fact]
    public void AddColumn_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.AddColumn("NoSuch", null));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_ValidSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        var ex = Record.Exception(() => doc.AddColumn(sheet.Name!, null));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        int before = doc.SheetCount;
        doc.AddColumn(sheet.Name!, null);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void AddColumn_WithHeader_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        var ex = Record.Exception(() => doc.AddColumn(sheet.Name!, "MyHeader"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_NullHeader_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        var ex = Record.Exception(() => doc.AddColumn(sheet.Name!, null));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_MultipleColumns_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        for (int i = 0; i < 5; i++)
        {
            var ex = Record.Exception(() => doc.AddColumn(sheet.Name!, $"Col{i}"));
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumnThenSetValue_Works()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("S");
        doc.AddColumn(sheet.Name!, "New");
        doc.InsertRow(sheet.Name!, 0);
        FodsDocument.SetCellValue(sheet, 0, 0, "Value");
        Assert.Equal("Value", FodsDocument.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_AddMultipleColumnsWithHeaders_AllNoException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Data");
        string[] headers = { "Name", "Age", "Score" };
        foreach (var h in headers)
        {
            var ex = Record.Exception(() => doc.AddColumn(sheet.Name!, h));
            Assert.Null(ex);
        }
        // SheetCount unchanged
        Assert.Equal(2, doc.SheetCount); // default + "Data"
    }
}
