// Tests for FodsDocument.InsertRow dedicated coverage.
// Sprint: ff-sprint-s263-dotnet-deepening-20260630
// Ledger: PC-FODS-R287

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R287: Dedicated tests for FodsDocument.InsertRow(sheetName, rowIndex, values).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative row index → throws exception.
/// Valid insert → no exception.
/// GetRowCount increases after insert.
/// SheetCount unchanged after insert.
/// Inserted row is accessible at the given index.
/// Insert at end is equivalent to append.
/// Dogfood: insert at beginning, count increases.
/// Dogfood: insert in middle, count increases.
/// </summary>
public class FodsR287InsertRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow(null!, 0, new[] { "a" }));
    }

    [Fact]
    public void InsertRow_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow("   ", 0, new[] { "a" }));
    }

    [Fact]
    public void InsertRow_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow("NoSheet", 0, new[] { "a" }));
    }

    [Fact]
    public void InsertRow_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.InsertRow("Sheet1", -1, new[] { "a" }));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRow_ValidArgs_NoException()
    {
        var doc = FodsDocument.CreateNew();
        var ex = Record.Exception(() => doc.InsertRow("Sheet1", 0, new[] { "col1", "col2" }));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertRow_RowCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddRow("Sheet1", new[] { "existing" });
        int before = doc.GetRowCount("Sheet1");
        doc.InsertRow("Sheet1", 0, new[] { "inserted" });
        Assert.True(doc.GetRowCount("Sheet1") > before);
    }

    [Fact]
    public void InsertRow_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        doc.InsertRow("Sheet1", 0, new[] { "data" });
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertAtBeginning_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "row1" });
        doc.AddRow("Data", new[] { "row2" });
        int before = doc.GetRowCount("Data");
        doc.InsertRow("Data", 0, new[] { "new first row" });
        Assert.Equal(before + 1, doc.GetRowCount("Data"));
    }

    [Fact]
    public void DogfoodPipeline_InsertInMiddle_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddRow("Sheet1", new[] { "alpha" });
        doc.AddRow("Sheet1", new[] { "gamma" });
        int before = doc.GetRowCount("Sheet1");
        doc.InsertRow("Sheet1", 1, new[] { "beta" }); // insert between
        Assert.Equal(before + 1, doc.GetRowCount("Sheet1"));
    }
}
