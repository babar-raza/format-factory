// Tests for FodsDocument.InsertRow dedicated coverage.
// Sprint: ff-sprint-s224-dotnet-deepening-20260629
// Ledger: PC-FODS-R242

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R242: Dedicated tests for FodsDocument.InsertRow(sheetName, rowIndex, rowData).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row index → throws exception.
/// Null row data → throws exception.
/// Valid insert → no exception.
/// Row count increases after insert.
/// SheetCount unchanged after insert.
/// Insert at zero → no exception.
/// Dogfood: insert multiple rows, count grows.
/// </summary>
public class FodsR242InsertRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow(null!, 0, new[] { "A" }));
    }

    [Fact]
    public void InsertRow_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow("   ", 0, new[] { "A" }));
    }

    [Fact]
    public void InsertRow_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow("Ghost", 0, new[] { "A" }));
    }

    [Fact]
    public void InsertRow_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.InsertRow(sheetName, -1, new[] { "A" }));
    }

    [Fact]
    public void InsertRow_NullRowData_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.InsertRow(sheetName, 0, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_ValidInsert_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.InsertRow(sheetName, 0, new[] { "Val1", "Val2" }));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertRow_RowCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Existing" });
        int before = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0, new[] { "Inserted" });
        int after = doc.GetRowCount(sheetName);
        Assert.True(after > before);
    }

    [Fact]
    public void InsertRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "X" });
        doc.InsertRow(sheetName, 0, new[] { "Y" });
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void InsertRow_InsertAtZero_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Existing" });
        var ex = Record.Exception(() => doc.InsertRow(sheetName, 0, new[] { "AtZero" }));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertMultiple_CountGrows()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Base" });
        int start = doc.GetRowCount(sheetName);
        doc.InsertRow(sheetName, 0, new[] { "Insert1" });
        doc.InsertRow(sheetName, 0, new[] { "Insert2" });
        doc.InsertRow(sheetName, 0, new[] { "Insert3" });
        int end = doc.GetRowCount(sheetName);
        Assert.True(end >= start + 3);
    }
}
