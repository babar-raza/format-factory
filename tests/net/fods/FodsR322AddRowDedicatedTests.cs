// Tests for FodsDocument.AddRow dedicated coverage.
// Sprint: ff-sprint-s294-dotnet-deepening-20260630
// Ledger: PC-FODS-R322

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R322: Dedicated tests for FodsDocument.AddRow(sheetName, values).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Valid call no exception.
/// Row count increases after AddRow.
/// SheetCount unchanged after AddRow.
/// Add row with multiple values no exception.
/// Add row with empty values no exception.
/// Dogfood: add header row then data row, row count matches.
/// Dogfood: two sheets AddRow independently.
/// </summary>
public class FodsR322AddRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddRow(null!, new[] { "A", "B" }));
    }

    [Fact]
    public void AddRow_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddRow("   ", new[] { "A", "B" }));
    }

    [Fact]
    public void AddRow_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddRow("DoesNotExist", new[] { "A" }));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() => doc.AddRow("Data", new[] { "Value1", "Value2" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddRow_RowCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.GetRowCount("Data");
        doc.AddRow("Data", new[] { "A", "B", "C" });
        int after = doc.GetRowCount("Data");
        Assert.True(after > before);
    }

    [Fact]
    public void AddRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int sheetsBefore = doc.SheetCount;
        doc.AddRow("Data", new[] { "X" });
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void AddRow_MultipleValues_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() => doc.AddRow("Data", new[] { "Col1", "Col2", "Col3", "Col4" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddRow_EmptyValues_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() => doc.AddRow("Data", Array.Empty<string>()));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeaderThenDataRow_RowCountMatches()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddRow("Sales", new[] { "Product", "Price", "Quantity" });
        doc.AddRow("Sales", new[] { "Widget", "9.99", "100" });
        int count = doc.GetRowCount("Sales");
        Assert.True(count >= 2);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheetsAddRowIndependently_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddRow("Sheet1", new[] { "A", "B" });
        var ex = Record.Exception(() => doc.AddRow("Sheet2", new[] { "X", "Y", "Z" }));
        Assert.Null(ex);
    }
}
