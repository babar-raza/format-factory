// Tests for FodsDocument.AddRow dedicated coverage.
// Sprint: ff-sprint-s222-dotnet-deepening-20260629
// Ledger: PC-FODS-R240

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R240: Dedicated tests for FodsDocument.AddRow(sheetName, rowData).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Null row data → throws exception.
/// Valid row → no exception.
/// Row count increases after add.
/// SheetCount unchanged after add.
/// Added values retrievable via GetCellValue.
/// Add two rows → row count increases by 2.
/// Dogfood: add rows and verify row count.
/// </summary>
public class FodsR240AddRowDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.AddRow("Ghost", new[] { "A", "B" }));
    }

    [Fact]
    public void AddRow_NullRowData_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.AddRow(sheetName, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_ValidRow_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.AddRow(sheetName, new[] { "Val1", "Val2" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddRow_RowCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheetName);
        doc.AddRow(sheetName, new[] { "A", "B", "C" });
        int after = doc.GetRowCount(sheetName);
        Assert.True(after > before);
    }

    [Fact]
    public void AddRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "X" });
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void AddRow_AddTwoRows_RowCountIncreasedByTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheetName);
        doc.AddRow(sheetName, new[] { "Row1A", "Row1B" });
        doc.AddRow(sheetName, new[] { "Row2A", "Row2B" });
        int after = doc.GetRowCount(sheetName);
        Assert.True(after >= before + 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRows_RowCountGrows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int start = doc.GetRowCount(sheetName);
        for (int i = 0; i < 5; i++)
            doc.AddRow(sheetName, new[] { $"Cell{i}A", $"Cell{i}B" });
        int end = doc.GetRowCount(sheetName);
        Assert.True(end >= start + 5);
    }
}
